"""CTA_WAVE1 (T-65 s2 wave-1 futures revival) pre-registration probes.

跑前探针纪律 (PREREG_TEMPLATE §2): panel facts must be probed, not assumed.
Faces:
  P1 disk audit     -- per-variety start/end/rows/cols, OHLCV negativity,
                       NaN holes within each variety's own span (R167: real
                       head/tail repr evidence, not row counts alone)
  P2 union calendar -- deep-window (2008+) union-calendar missing-cell census
                       per variety -> frozen source-gap exemption candidates
  P3 TS pull         -- futures_zh_daily_sina('TS0') -> data/futures_daily/TS.csv
                       (futures_main_sina lacks the TS face; census probe R184
                       verified rows=1967 cut 2026-09-24). Idempotent: on-disk
                       file fresh to cutoff = no-op. Overlap row-check on pull.
  P4 spot proxy     -- 510300/510500 ETF daily close face for the IF/IC basis
                       leg (futures-vs-ETF premium proxy, honest proxy law)
  P5 treasury yield  -- bond_china_yield probe (chinabond face) for the wave-1b
                       treasury-carry data gate -- NON-BLOCKING, blocked face
                       = honest annotation, never a terminal verdict (r186)
  P6 seed scan      -- SEED_REGISTRY local dict scan: 62_000 must be free
Laws: direct-connection recipe (census probe), r167 head/tail repr,
evidence_cutoff top-level field (science_audit C2 legal key).
Output: results/cta_wave1_probe.json
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
          "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import urllib.request  # noqa: E402

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

import akshare as ak  # noqa: E402
import pandas as pd  # noqa: E402

OUT = os.path.join("results", "cta_wave1_probe.json")
FUT_DIR = os.path.join("data", "futures_daily")
EVIDENCE_CUTOFF = "2026-09-24"  # latest completed trading bar (09-25 Mid-Autumn holiday)


def p1_disk_audit() -> dict:
    faces = {}
    for path in sorted(os.listdir(FUT_DIR)):
        if not path.endswith(".csv"):
            continue
        v = path[:-4]
        df = pd.read_csv(os.path.join(FUT_DIR, path), index_col=0, parse_dates=True).sort_index()
        span = df.loc[df.index[0]:df.index[-1]]
        nan_holes = {}
        for fld in ("open", "high", "low", "close", "volume"):
            if fld in df.columns:
                n = int(span[fld].isna().sum())
                if n:
                    nan_holes[fld] = n
        neg = {fld: int((span[fld] < 0).sum()) for fld in ("open", "high", "low", "close", "volume")
               if fld in df.columns and (span[fld] < 0).any()}
        faces[v] = {
            "start": str(df.index[0].date()), "end": str(df.index[-1].date()),
            "rows": int(len(df)), "cols": list(map(str, df.columns)),
            "nan_holes_in_span": nan_holes or "none",
            "negative_cells": neg or "none",
            "head_repr": [repr(x)[:160] for x in df.head(1).to_dict("records")],
            "tail_repr": [repr(x)[:160] for x in df.tail(1).to_dict("records")],
        }
    return faces


def p2_union_calendar() -> dict:
    frames = {}
    for path in sorted(os.listdir(FUT_DIR)):
        if path.endswith(".csv"):
            v = path[:-4]
            frames[v] = pd.read_csv(os.path.join(FUT_DIR, path), index_col=0, parse_dates=True).sort_index()
    all_dates = sorted(set().union(*[set(f.index) for f in frames.values()]))
    idx = pd.DatetimeIndex(all_dates)
    out = {"union_start": str(idx[0].date()), "union_end": str(idx[-1].date()),
           "union_days": int(len(idx)), "in_span_missing": {}}
    # R167 truncation law: in-span gaps must be FULL lists (a [:400] cap on the
    # vs-union list hid true post-2017 gaps in the first run -- measurement bug
    # caught by direct CSV recheck, fixed here); pre-listing absence counts are
    # disclosed as numbers only.
    for v, f in frames.items():
        inspan = [d for d in idx.difference(f.index) if d >= f.index[0]]
        pre_listing = int(len(idx.difference(f.index)) - len(inspan))
        out["in_span_missing"][v] = {
            "n_days": int(len(inspan)),
            "dates": [str(d.date()) for d in inspan],
            "pre_listing_absence_days": pre_listing,
            "start": str(f.index[0].date()),
        }
    # alive-breadth by year (deep window concentration disclosure)
    alive = pd.DataFrame({v: f["close"].reindex(idx).notna() for v, f in frames.items()})
    breadth = alive.sum(axis=1)
    out["alive_breadth_first_date_ge2"] = str(breadth[breadth >= 2].index[0].date()) if (breadth >= 2).any() else None
    out["alive_breadth_first_date_ge4"] = str(breadth[breadth >= 4].index[0].date()) if (breadth >= 4).any() else None
    out["alive_breadth_min"] = int(breadth.min())
    yearly = breadth.groupby(breadth.index.year).mean().round(2)
    out["alive_breadth_yearly_mean"] = {str(k): float(vv) for k, vv in yearly.items()}
    return out


def p3_ts_pull() -> dict:
    """Idempotent TS leg: on-disk fresh to cutoff = no-op; else pull+write."""
    dest = os.path.join(FUT_DIR, "TS.csv")
    t0 = time.time()
    if os.path.exists(dest):
        old = pd.read_csv(dest, index_col=0, parse_dates=True).sort_index()
        if str(old.index[-1].date()) >= EVIDENCE_CUTOFF:
            return {"status": "NOOP_FRESH", "rows": int(len(old)),
                    "end": str(old.index[-1].date()), "sec": round(time.time() - t0, 1)}
    try:
        df = ak.futures_zh_daily_sina(symbol="TS0")
        if df is None or len(df) == 0:
            return {"status": "EMPTY", "sec": round(time.time() - t0, 1)}
        df = df.sort_values("date").set_index("date")
        df.index = pd.to_datetime(df.index)
        cols = [c for c in ("open", "high", "low", "close", "volume", "hold", "settle") if c in df.columns]
        rec = {"status": "OK", "rows": int(len(df)),
               "start": str(df.index[0].date()), "end": str(df.index[-1].date()),
               "cols_written": cols, "sec": round(time.time() - t0, 1),
               "head_repr": [repr(x)[:160] for x in df.head(2).reset_index().to_dict("records")],
               "tail_repr": [repr(x)[:160] for x in df.tail(1).reset_index().to_dict("records")]}
        if os.path.exists(dest):
            old = pd.read_csv(dest, index_col=0, parse_dates=True).sort_index()
            both = old.index.intersection(df.index)
            if len(both):
                drift = (old.loc[both, "close"].astype(float) - df.loc[both, "close"].astype(float)).abs().max()
                rec["overlap_rows"] = int(len(both))
                rec["overlap_max_abs_close_drift"] = float(drift)
                if drift > 1e-9:
                    rec["status"] = "OVERLAP_MISMATCH_LOCAL_NOT_TOUCHED"
                    return rec
        df[cols].to_csv(dest, index_label="date")
        rec["written"] = dest
        return rec
    except Exception as e:  # noqa: BLE001
        return {"status": "FAIL", "err": f"{type(e).__name__}: {e}"[:200],
                "sec": round(time.time() - t0, 1)}


def p4_spot_proxy() -> dict:
    out = {}
    for code in ("510300", "510500"):
        path = os.path.join("data", "daily", f"{code}.csv")
        if not os.path.exists(path):
            out[code] = {"status": "MISSING"}
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        out[code] = {"status": "OK", "rows": int(len(df)),
                     "start": str(df.index[0].date()), "end": str(df.index[-1].date()),
                     "head_repr": [repr(x)[:140] for x in df.head(1).to_dict("records")],
                     "tail_repr": [repr(x)[:140] for x in df.tail(1).to_dict("records")]}
    # overlap of ETF calendar with futures union calendar (basis-leg window)
    if all(out.get(c, {}).get("status") == "OK" for c in ("510300", "510500")):
        fut_idx = set()
        for path in sorted(os.listdir(FUT_DIR)):
            if path.endswith(".csv"):
                fut_idx |= set(pd.read_csv(os.path.join(FUT_DIR, path), index_col=0, parse_dates=True).index)
        for code in ("510300", "510500"):
            df = pd.read_csv(os.path.join("data", "daily", f"{code}.csv"), index_col=0, parse_dates=True)
            ov = df.index.intersection(pd.DatetimeIndex(sorted(fut_idx)))
            out[code]["futures_calendar_overlap"] = int(len(ov))
            out[code]["futures_overlap_ratio"] = round(len(ov) / max(1, len(df.loc[df.index >= pd.Timestamp("2017-01-17")])), 4)
    return out


def p5_treasury_yield() -> dict:
    """chinabond yield-curve face probe -- wave-1b treasury-carry data gate.
    NON-BLOCKING: blocked/empty = honest annotation only (r186 symmetry law:
    a blocked face never sets a terminal verdict either way)."""
    t0 = time.time()
    try:
        df = ak.bond_china_yield(start_date="2026-09-01", end_date="2026-09-24")
        if df is None or len(df) == 0:
            return {"status": "EMPTY", "sec": round(time.time() - t0, 1)}
        return {"status": "OK", "rows": int(len(df)),
                "cols": list(map(str, df.columns))[:16],
                "head_repr": [repr(x)[:160] for x in df.head(1).to_dict("records")],
                "sec": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"status": "FAIL", "err": f"{type(e).__name__}: {e}"[:200],
                "sec": round(time.time() - t0, 1)}


def p6_seed_scan() -> dict:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import science_gates as sg  # noqa: PLC0415
    vals = [v for v in sg.SEED_REGISTRY.values() if isinstance(v, int)]
    hits = [v for v in vals if 62_000 <= v < 62_500]
    return {"candidate_base": 62_000, "band": "62000..62049",
            "registry_overlapping_values": hits,
            "free": not hits}


def main() -> int:
    out = {
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "probe_ts": dt.datetime.now().isoformat(timespec="seconds"),
        "batch": "CTA_WAVE1",
        "ticket": "T-2026-09-25-65-P1 s2",
        "p1_disk_audit": p1_disk_audit(),
        "p2_union_calendar": p2_union_calendar(),
        "p3_ts_pull": p3_ts_pull(),
        "p4_spot_proxy": p4_spot_proxy(),
        "p5_treasury_yield": p5_treasury_yield(),
        "p6_seed_scan": p6_seed_scan(),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"probe written: {OUT}")
    for k in ("p3_ts_pull", "p5_treasury_yield", "p6_seed_scan"):
        print(k, "->", json.dumps(out[k], ensure_ascii=False)[:220])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
