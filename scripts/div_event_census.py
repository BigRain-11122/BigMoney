"""Dividend ex-date event census (exploratory, zero judged claims).

Product purpose: measure what actually happens to the total-return price face
around dividend ex-dates on the local A-share panel, so the next trial batch
(supply floor leg) can be registered against a measured prior instead of a
folklore claim about "抢权 / 填权" (pre-ex run-up / post-ex fill).

Face discipline:
  * panel = data/cache/p1c_local (qfq, cutoff 2026-10-19) - qfq neutralises the
    mechanical ex-date drop, so the measured abnormal return is the economic
    move *net of* the dividend. That is the only face this script claims.
  * market adjustment = same-day / same-window cross-sectional median return
    (equal-weight proxy), subtracted from the event symbol's window return.
  * zero judged lines, zero prereg gates, zero pool writes. Exploratory census
    only; any judged batch must open via research/PREREG_TEMPLATE.md.
  * yield proxy = cash_div_per_10 / 10 / qfq_close(ex-date-1); qfq back-adjusts
    historical prices, so the proxy OVERSTATES yield for older events. Used
    only for relative bucketing and disclosed as such.

Usage:
  python scripts/div_event_census.py            # run census -> results/div_event_census/
  python scripts/div_event_census.py --selftest # offline math self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT_DIR = os.path.join(ROOT, "results", "div_event_census")
DIV_FACE = os.path.join(ROOT, "data", "fund_history_export", "div_events_faces.parquet")

PRE_DAYS = 10
POST5_DAYS = 5
POST20_DAYS = 20
ERAS = [(1990, 2009), (2010, 2015), (2016, 2020), (2021, 2099)]
CONTROL_SEED = 20261020
CONTROL_N = 20000


# ------------------------------------------------------------------ statistics
def window_stats(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = int(x.size)
    if n < 2:
        return {"n": n, "mean": None, "sd": None, "t": None, "win_rate": None}
    mean = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    t = float(mean / (sd / np.sqrt(n))) if sd > 0 else None
    return {"n": n, "mean": round(mean, 6), "sd": round(sd, 6),
            "t": None if t is None else round(t, 3),
            "win_rate": round(float(np.mean(x > 0)), 4)}


# ------------------------------------------------------------------ panel math
def _logret(close: np.ndarray) -> np.ndarray:
    ret = np.full(close.shape, np.nan)
    ret[1:] = close[1:] / close[:-1] - 1.0
    with np.errstate(invalid="ignore", divide="ignore"):
        ret[~np.isfinite(ret)] = np.nan
    ret[np.abs(ret) > 5.0] = np.nan          # corporate-action / data spikes
    return ret


def _nan_cumsum(a: np.ndarray) -> np.ndarray:
    z = np.where(np.isfinite(a), a, 0.0)
    return np.cumsum(z, axis=0)


def _nan_cumcount(a: np.ndarray) -> np.ndarray:
    return np.cumsum(np.isfinite(a).astype(np.int32), axis=0)


def window_abnormal(lr: np.ndarray, mkt_lr: np.ndarray, rows: np.ndarray,
                    cols: np.ndarray, start_off: int, end_off: int) -> np.ndarray:
    """Compounded window return minus the market's same-window return.

    ``rows``/``cols`` are the event coordinates (time axis, symbol axis); offsets
    are relative to the event row (0 = ex-date row). A window with any missing
    day is dropped (honest NaN, never fabricated).
    """
    n = lr.shape[0]
    csum = _nan_cumsum(lr)
    ccnt = _nan_cumcount(lr)
    mfin = np.isfinite(mkt_lr)
    msum = np.cumsum(np.where(mfin, mkt_lr, 0.0))
    mcnt = np.cumsum(mfin.astype(np.int32))
    lo = rows + start_off
    hi = rows + end_off
    ok = (lo >= 0) & (hi < n)
    out = np.full(rows.shape, np.nan)
    if not np.any(ok):
        return out
    lo_ok, hi_ok, row_ok, col_ok = lo[ok], hi[ok], rows[ok], cols[ok]
    prev = lo_ok > 0
    lp = np.clip(lo_ok - 1, 0, n - 1)
    s_lo = np.where(prev, csum[lp, col_ok], 0.0)
    s_hi = csum[hi_ok, col_ok]
    c_lo = np.where(prev, ccnt[lp, col_ok], 0)
    c_hi = ccnt[hi_ok, col_ok]
    width = (hi_ok - lo_ok + 1)
    full = (c_hi - c_lo) == width
    m_lo = np.where(prev, msum[lp], 0.0)
    m_hi = msum[hi_ok]
    mc_lo = np.where(prev, mcnt[lp], 0)
    mc_hi = mcnt[hi_ok]
    m_full = (mc_hi - mc_lo) == width
    both = full & m_full
    vals = np.full(row_ok.shape, np.nan)
    if np.any(both):
        ev = np.exp(s_hi[both] - s_lo[both]) - 1.0
        mk = np.exp(m_hi[both] - m_lo[both]) - 1.0
        vals[both] = ev - mk
    out[ok] = vals
    return out


def census(close: np.ndarray, dates: np.ndarray, syms: list, events: list) -> dict:
    lr = _logret(close)
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mkt = np.nanmedian(lr, axis=1)
    col = {s: i for i, s in enumerate(syms)}
    day = {d: i for i, d in enumerate(dates)}
    rows, cols, codes, years, yields = [], [], [], [], []
    for code, ex_date, per10 in events:
        j = col.get(code)
        i = day.get(ex_date)
        if j is None or i is None or i < 1:
            continue
        if not (np.isfinite(close[i - 1, j]) and close[i - 1, j] > 0):
            continue
        rows.append(i)
        cols.append(j)
        codes.append(code)
        years.append(int(ex_date[:4]))
        y = float(per10) / 10.0 / float(close[i - 1, j])
        yields.append(y if np.isfinite(y) and y >= 0 else np.nan)
    rows = np.asarray(rows, dtype=np.int64)
    cols = np.asarray(cols, dtype=np.int64)
    years = np.asarray(years, dtype=np.int32)
    yields = np.asarray(yields, dtype=float)
    if rows.size == 0:
        return {"n_events": 0, "windows": {}}
    pre = window_abnormal(lr, mkt, rows, cols, -PRE_DAYS, -1)
    exd = window_abnormal(lr, mkt, rows, cols, 0, 0)
    post5 = window_abnormal(lr, mkt, rows, cols, 1, POST5_DAYS)
    post20 = window_abnormal(lr, mkt, rows, cols, 1, POST20_DAYS)
    wins = {"pre10": pre, "ex_date": exd, "post5": post5, "post20": post20}

    face = {"n_events": int(rows.size),
            "windows": {k: window_stats(v) for k, v in wins.items()},
            "by_era": {}, "by_yield_quintile": {}}

    # Matched random-date control: the same windows measured on random
    # (day, symbol) pairs. Absolute window means on this panel carry a
    # panel-wide drift baseline; only event-minus-control is attributed to
    # the dividend event itself.
    rng = np.random.default_rng(CONTROL_SEED)
    c_rows = rng.integers(POST20_DAYS + 5, lr.shape[0] - POST20_DAYS - 5, CONTROL_N)
    c_cols = rng.integers(0, lr.shape[1], CONTROL_N)
    ctrl = {
        "pre10": window_abnormal(lr, mkt, c_rows, c_cols, -PRE_DAYS, -1),
        "ex_date": window_abnormal(lr, mkt, c_rows, c_cols, 0, 0),
        "post5": window_abnormal(lr, mkt, c_rows, c_cols, 1, POST5_DAYS),
        "post20": window_abnormal(lr, mkt, c_rows, c_cols, 1, POST20_DAYS),
    }
    face["control_random_dates"] = {
        "seed": CONTROL_SEED, "draws": CONTROL_N,
        "windows": {k: window_stats(v) for k, v in ctrl.items()}}
    face["event_minus_control"] = {}
    for k in wins:
        e, c = window_stats(wins[k]), window_stats(ctrl[k])
        if e["mean"] is None or c["mean"] is None:
            face["event_minus_control"][k] = None
            continue
        face["event_minus_control"][k] = {
            "delta_mean": round(e["mean"] - c["mean"], 6),
            "event_t": e["t"], "control_t": c["t"],
            "se_approx": round(float(np.sqrt(
                (e["sd"] ** 2) / max(e["n"], 1) + (c["sd"] ** 2) / max(c["n"], 1))), 6),
        }
    for lo, hi in ERAS:
        mask = (years >= lo) & (years <= hi)
        if int(mask.sum()) < 20:
            continue
        face["by_era"][f"{lo}-{hi}"] = {
            "n": int(mask.sum()),
            "windows": {k: window_stats(v[mask]) for k, v in wins.items()}}
    ok = np.isfinite(yields)
    if int(ok.sum()) >= 50:
        qs = np.quantile(yields[ok], [0.2, 0.4, 0.6, 0.8])
        b = np.digitize(np.where(ok, yields, -1.0), qs)
        for k in range(5):
            mask = ok & (b == k)
            if int(mask.sum()) < 20:
                continue
            face["by_yield_quintile"][f"Q{k + 1}"] = {
                "n": int(mask.sum()),
                "mean_yield_proxy": round(float(np.nanmean(yields[mask])), 5),
                "windows": {kk: window_stats(v[mask]) for kk, v in wins.items()}}
    return face


# ------------------------------------------------------------------ selftest
def _selftest() -> int:
    """Offline math checks: abnormal-return sign, market subtraction, NaN drop."""
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # synthetic: 6 symbols x 40 days, all flat, then inject a +1% drift on a
    # single symbol over the 5 days after row 20 -> post5 abnormal must be > 0.
    close = np.ones((40, 6))
    close[20:, 0] = np.array([1.0, 1.002, 1.004, 1.006, 1.008, 1.010] + [1.010] * 14)
    lr = _logret(close)
    mkt = np.nanmedian(lr, axis=1)
    rows = np.array([20])
    cols = np.array([0])
    post5 = window_abnormal(lr, mkt, rows, cols, 1, 5)
    check("post5 positive drift detected", np.isfinite(post5[0]) and post5[0] > 0.008)
    check("market leg is flat", abs(float(np.nanmedian(np.diff(np.log(close[:, 1]))))) < 1e-12)

    # ex-date window on a flat panel must be ~0 after market subtraction
    exd = window_abnormal(lr, mkt, np.array([3]), np.array([1]), 0, 0)
    check("flat ex-date abnormal ~0", np.isfinite(exd[0]) and abs(exd[0]) < 1e-9)

    # missing day inside a window must drop the event (honest NaN)
    c2 = close.copy()
    c2[23, 0] = np.nan
    lr2 = _logret(c2)
    mkt2 = np.nanmedian(lr2, axis=1)
    v2 = window_abnormal(lr2, mkt2, np.array([20]), np.array([0]), 1, 5)
    check("gap in window -> NaN", np.isnan(v2[0]))

    # stats helper
    s = window_stats(np.array([0.01, 0.01, 0.01, 0.01]))
    check("stats mean", abs(s["mean"] - 0.01) < 1e-9)
    check("stats win rate 1.0", s["win_rate"] == 1.0)
    check("stats tiny n", window_stats(np.array([0.01]))["mean"] is None)

    if fails:
        print(f"SELFTEST FAIL: {fails}")
        return 1
    print("SELFTEST 6/6 PASS")
    return 0


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    import pandas as pd
    from stagestyle_combo_p1_backtest import load_local_panel

    t0 = time.time()
    panel = load_local_panel()
    if panel is None:
        print("PANEL_MISSING: data/cache/p1c_local not readable -> honest exit 3")
        return 3
    idx, syms, arrays, meta = panel
    close = np.asarray(arrays["close"], dtype=np.float64)
    dates = [str(d)[:10] for d in np.asarray(idx)]
    df = pd.read_parquet(DIV_FACE, columns=["code", "ex_date", "cash_div_per_10"])
    df = df[df["cash_div_per_10"].fillna(0) > 0]
    df = df[df["ex_date"].astype(str) >= dates[0]]
    events = [(str(c).zfill(6), str(d)[:10], float(v))
              for c, d, v in zip(df["code"], df["ex_date"], df["cash_div_per_10"])]
    print(f"panel {close.shape} cutoff={meta.get('cutoff')} events_candidates={len(events)}")

    face = census(close, dates, syms, events)
    out = {
        "face": "DIV-EVENT-CENSUS",
        "status": "EXPLORATORY_ZERO_JUDGED_CLAIMS",
        "evidence_cutoff": meta.get("cutoff"),
        "panel": {"path": "data/cache/p1c_local", "shape": list(close.shape),
                  "start": dates[0], "end": dates[-1]},
        "dividend_face": "data/fund_history_export/div_events_faces.parquet",
        "windows": {"pre10": [-10, -1], "ex_date": [0, 0], "post5": [1, 5],
                    "post20": [1, 20]},
        "method": ("qfq close (dividend drop neutralised) minus same-window "
                   "cross-sectional median return; any missing day drops the event"),
        "disclosures": [
            "yield proxy uses qfq close -> overstates yield for older events; "
            "quintiles are relative buckets only",
            "no cost model applied (census descriptive, not a tradeable edge)",
            "zero prereg gates / zero pool writes; judged face requires "
            "research/PREREG_TEMPLATE.md",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": face,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    cutoff = str(meta.get("cutoff"))
    path = os.path.join(OUT_DIR, f"CENSUS-{cutoff}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    latest = os.path.join(OUT_DIR, "latest.json")
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"n_events": face.get("n_events"),
                      "windows": face.get("windows"),
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())