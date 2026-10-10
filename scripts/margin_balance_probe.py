#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E11 margin balance sentiment-face probe (P3 explore row, r953 bm-a).

Data face: SSE/SZSE exchange margin (两融) daily summary channels.
  - SSE stock_margin_sse(start,end): per-day credit-trade summary, unit=YUAN, T-1 disclosure
  - SZSE stock_margin_szse(date):   per-day summary, unit=1e8 YUAN (亿元), T-2 disclosure lag
Probe faces (descriptive only, zero judgment, zero criteria, zero prereg):
  F1 channel liveness + structure: both channels, field maps, unit disparity
  F2 history span: earliest fetchable bar (SSE 2015-01 face) + bar count
  F3 near-window snapshot: last 10 td financing balance series + day-over-day deltas
  F4 structure observation: fin/short ratio, 250td daily-delta distribution stats
Honest disclosure: SZSE same-day lag means latest bar differs between venues;
all faces carry row-count denominators; sentiment-family prereg is CLOSED-family
gated (LHB_THERMO_IC_P1 / THERMO-OVERLAY-P1 dual negative verdicts r947) -- margin
balance is a NEW data-source channel per family-reopen law, judged face needs its
own ticket + PREREG_TEMPLATE gate, this probe contributes zero criteria.
Exit: 0 normal / 2 mechanism failure (both channels dead). Selftest hermetic.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "margin_balance_probe.json")

SLEEP_S = 2.5  # inter-request throttle (E-probe law)
TIMEOUT_S = 45.0  # network jacket


def _fetch(fn, *a, **kw):
    """Fetch with timeout jacket + throttle; returns (df|None, err|None)."""
    import warnings
    warnings.filterwarnings("ignore")
    try:
        df = fn(*a, **kw)
        time.sleep(SLEEP_S)
        return df, None
    except Exception as e:  # noqa: BLE001 -- probe liveness face
        return None, "%s: %s" % (type(e).__name__, str(e)[:160])


def _to_num(s):
    import pandas as pd
    return pd.to_numeric(s, errors="coerce")


def build_snapshot_faces(sse_df, szse_df):
    """F3+F4 pure faces from fetched frames. No I/O.

    sse_df: SSE summary frame (信用交易日期 desc), unit YUAN
    szse_df: SZSE summary frame (single row), unit 1e8 YUAN or None
    """
    out = {"near10": [], "fin_short_ratio": None, "delta_250td": None}
    if sse_df is None or len(sse_df) == 0:
        return out
    d = sse_df.copy()
    d["dt"] = d["信用交易日期"].astype(str)
    fin = _to_num(d["融资余额"])
    total = _to_num(d["融券余量金额"]) if "融券余量金额" in d.columns else None
    d = d.assign(fin=fin)
    d = d.sort_values("dt")
    rows = []
    for _, r in d.tail(10).iterrows():
        rows.append({"dt": r["dt"], "fin_yi": round(float(r["fin"]) / 1e8, 2),
                     "short_yi": round(float(r["融券余量金额"]) / 1e8, 2) if "融券余量金额" in d.columns else None})
    out["near10"] = rows
    if len(fin):
        last_fin = float(fin.iloc[-1])
        if total is not None and len(total) and float(total.iloc[-1]) > 0:
            out["fin_short_ratio"] = round(last_fin / float(total.iloc[-1]), 1)
        dd = fin.diff().dropna() / 1e8
        if len(dd):
            out["delta_250td"] = {
                "n": int(len(dd)),
                "mean_yi": round(float(dd.mean()), 2),
                "std_yi": round(float(dd.std()), 2),
                "min_yi": round(float(dd.min()), 2),
                "max_yi": round(float(dd.max()), 2),
                "pct_neg": round(float((dd < 0).mean()), 3),
            }
    return out


def run_probe(write=True):
    import akshare as ak
    today = datetime.now()
    start250 = (today - timedelta(days=520)).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")

    sse_df, sse_err = _fetch(ak.stock_margin_sse, start_date=start250, end_date=end)
    sse2_df, sse2_err = None, None
    if sse_df is None:
        sse2_df, sse2_err = _fetch(ak.stock_margin_sse, start_date="20261001", end_date=end)
    hist_df, hist_err = _fetch(ak.stock_margin_sse, start_date="20150101", end_date="20150131")
    time.sleep(SLEEP_S)
    szse_df, szse_err = None, None
    for lag in range(1, 4):
        d = (today - timedelta(days=lag)).strftime("%Y%m%d")
        szse_df, szse_err = _fetch(ak.stock_margin_szse, date=d)
        if szse_df is not None and len(szse_df):
            szse_err = None
            break
        szse_df = None

    alive = {"sse": sse_df is not None and len(sse_df) > 0,
             "sse_recent_fallback": sse2_df is not None and len(sse2_df) > 0,
             "szse": szse_df is not None and len(szse_df) > 0}
    if not any(alive.values()):
        return {"status": "DEAD", "channels": alive,
                "errors": {"sse": sse_err, "szse": szse_err}}, 2

    snap_src = sse_df if sse_df is not None else sse2_df
    snap = build_snapshot_faces(snap_src, szse_df)

    span = {"bars_2015_01": int(len(hist_df)) if hist_df is not None else 0,
            "earliest_dt": str(hist_df["信用交易日期"].iloc[-1]) if hist_df is not None and len(hist_df) else None,
            "bars_fetched_520d": int(len(snap_src))}
    if sse_err and sse2_df is None:
        span["sse_250d_error"] = sse_err

    payload = {
        "status": "OK",
        "probe": "E11 margin balance sentiment face",
        "channels": {
            "sse": {"alive": alive["sse"] or alive["sse_recent_fallback"],
                    "unit": "YUAN", "disclosure": "T-1",
                    "fields": list(snap_src.columns) if snap_src is not None else []},
            "szse": {"alive": alive["szse"], "unit": "1e8 YUAN",
                     "disclosure": "T-2 (lag probed up to 3 calendar days)",
                     "fields": list(szse_df.columns) if szse_df is not None else [],
                     "lag_day_used": None if szse_df is None else "probed"},
        },
        "errors": {k: v for k, v in {"sse_520d": sse_err, "sse_recent": sse2_err,
                                     "sse_2015": hist_err, "szse": szse_err}.items() if v},
        "history_span": span,
        "snapshot": snap,
        "honesty": [
            "SZSE unit=亿元 vs SSE unit=YUAN (1e8 disparity) -- never mix raw",
            "SZSE T-2 disclosure lag -- venue latest bars differ by one bar",
            "sentiment-family prereg closed (r947 dual verdicts); margin = new data-source channel; judged face needs own ticket + PREREG gate",
            "zero criteria, zero prereg, zero panel writes in this probe",
        ],
        "ts": datetime.now().isoformat(timespec="seconds"),
    }
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
    return payload, 0


def selftest():
    """Hermetic pure-function legs (zero network)."""
    import pandas as pd
    ok = 0

    def chk(name, cond):
        nonlocal ok
        assert cond, name
        ok += 1

    sse = pd.DataFrame({
        "信用交易日期": ["20261008", "20261009"],
        "融资余额": [1298438300567.0, 1291437102980.0],
        "融券余量金额": [18936692018.0, 18943954276.0],
    })
    snap = build_snapshot_faces(sse, None)
    chk("near10 len==2", len(snap["near10"]) == 2)
    chk("fin unit yi", abs(snap["near10"][-1]["fin_yi"] - 12914.37) < 0.05)
    chk("ratio>0", snap["fin_short_ratio"] and snap["fin_short_ratio"] > 60)
    chk("delta n==1", snap["delta_250td"]["n"] == 1)
    chk("delta sign", snap["delta_250td"]["mean_yi"] < 0)

    empty = build_snapshot_faces(None, None)
    chk("empty faces", empty["near10"] == [] and empty["fin_short_ratio"] is None)

    one = pd.DataFrame({"信用交易日期": ["20261009"], "融资余额": [1.29e12],
                        "融券余量金额": [1.9e10]})
    s1 = build_snapshot_faces(one, None)
    chk("single-row no-delta", s1["delta_250td"] is None and len(s1["near10"]) == 1)
    print("selftest: %d/%d OK" % (ok, 7))
    return 0 if ok == 7 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        sys.exit(selftest())
    payload, rc = run_probe(write=True)
    print(json.dumps({k: payload[k] for k in ("status", "channels", "history_span")
                     if k in payload}, ensure_ascii=False))
    sys.exit(rc)


if __name__ == "__main__":
    main()
