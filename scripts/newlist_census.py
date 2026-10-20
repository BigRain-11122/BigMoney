"""New-listing (次新股) return-structure census (exploratory, zero judged claims).

Product purpose: A-share folklore treats 次新股 (first-year listings) as a
tradable bucket ("次新炒作"). This repo has never measured the *listing-age*
face of the local stock panel: the only prior trace is `l3_age250` used as an
exclusion filter (EXCLUSION_MARGINAL.md), never as a measured object.

This census produces the measured prior so that any future trial batch
(supply-floor leg) is registered against numbers instead of a slogan.

Face discipline:
  * panel = data/cache/p1c_local (qfq, cutoff 2026-10-19, 8745 x 5225).
  * listing date proxy = the first valid bar of a symbol in the panel. A
    symbol delisted before the panel start, or listed before 1990-12-19,
    is absent/mis-dated by construction -> UPPER-bound disclosure.
  * survivorship: delisted names are absent from the qfq panel axis, so every
    long-horizon bucket reads an upper bound, not an expectation.
  * measures, log-space, market-adjusted by the equal-weight cross-sectional
    median cumulated over the identical window:
      d1   = first-bar close / first-bar open - 1     (listing-day intraday)
      h    = close[L+h-1] / open[L] - 1               for h in 5, 20, 60, 250
    entry = first-bar OPEN (optimistic: listing-day limit-up rules differ by
    era and name; disclosed, no cost claims made at census level).
  * control leg = random (symbol, date) pairs drawn from stock-days with age
    >= 250 bars, same windows, n = 20000, seed 20261020 (same kernel) ->
    separates "new listing" from "panel-wide baseline drift".
  * zero judged lines, zero prereg gates, zero pool writes, zero network.

Usage:
  python scripts/newlist_census.py            # run -> results/newlist_census/
  python scripts/newlist_census.py --selftest # offline math self-test
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

PANEL = os.path.join(ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(ROOT, "results", "newlist_census")

HORIZONS = (5, 20, 60, 250)
ERAS = [(1990, 2009), (2010, 2015), (2016, 2020), (2021, 2099)]
CONTROL_N = 20000
CONTROL_SEED = 20261020
CONTROL_MIN_AGE = 250


# ------------------------------------------------------------------ panel math
def market_log_curve(close: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Equal-weight cross-sectional median cumulative log return, per row."""
    prev = np.full_like(close, np.nan)
    prev[1:] = close[:-1]
    prev_valid = np.zeros_like(valid)
    prev_valid[1:] = valid[:-1]
    with np.errstate(all="ignore"):
        r = np.log(close / prev)
    ok = valid & prev_valid & np.isfinite(r)
    day = np.where(ok, r, np.nan)
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nanmedian(day, axis=1)
    med = np.where(np.isfinite(med), med, 0.0)
    return np.cumsum(med)


def first_valid_row(valid: np.ndarray) -> np.ndarray:
    """Index of the first valid row per column, -1 when the column is empty."""
    any_ = valid.any(axis=0)
    idx = valid.argmax(axis=0).astype(np.int64)
    idx[~any_] = -1
    return idx


def window_excess(open_: np.ndarray, close: np.ndarray, mkt: np.ndarray,
                  rows: np.ndarray, cols: np.ndarray, h: int) -> np.ndarray:
    """Market-adjusted log return of open[L] -> close[L+h-1] for each pair."""
    end = rows + h - 1
    n = close.shape[0]
    keep = end < n
    rows_k, cols_k, end_k = rows[keep], cols[keep], end[keep]
    with np.errstate(all="ignore"):
        stk = np.log(close[end_k, cols_k] / open_[rows_k, cols_k])
        mret = mkt[end_k] - mkt[rows_k]
    out = stk - mret
    out[~np.isfinite(out)] = np.nan
    return out, keep


def summarize(x: np.ndarray) -> dict:
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {"n": 0}
    return {
        "n": int(x.size),
        "median_pct": round(float(np.median(x)) * 100.0, 3),
        "mean_pct": round(float(np.mean(x)) * 100.0, 3),
        "p10_pct": round(float(np.percentile(x, 10)) * 100.0, 3),
        "p90_pct": round(float(np.percentile(x, 90)) * 100.0, 3),
        "hit_positive_pct": round(float(np.mean(x > 0)) * 100.0, 1),
    }


# ------------------------------------------------------------------ selftest
def _selftest() -> int:
    legs = []

    # L1 first_valid_row picks the true first valid row
    v = np.array([[False, True], [True, False], [True, True]])
    legs.append(("L1 first_valid_row", list(first_valid_row(v)) == [1, 0]))

    # L2 market curve is cumulative and flat when every stock returns 0
    close = np.array([[10.0, 10.0], [10.0, 10.0], [10.0, 10.0]])
    valid = np.ones_like(close, dtype=bool)
    m = market_log_curve(close, valid)
    legs.append(("L2 market curve flat", np.allclose(m, 0.0)))

    # L3 market curve doubles -> +log(2) per day
    close2 = np.array([[10.0], [20.0], [40.0]])
    m2 = market_log_curve(close2, np.ones_like(close2, dtype=bool))
    legs.append(("L3 market curve doubles", np.allclose(m2, np.log(2.0) * np.arange(3))))

    # L4 window excess is 0 when the name IS the market (open == close path)
    close3 = np.array([[10.0], [12.0], [14.0]])
    open_ = close3.copy()
    mkt = market_log_curve(close3, np.ones_like(close3, dtype=bool))
    out, keep = window_excess(open_, close3, mkt, np.array([0]), np.array([0]), 3)
    legs.append(("L4 window excess = 0 for index-tracking name", keep[0] and abs(out[0]) < 1e-12))

    # L5 window excess refuses rows that run past the panel end
    out5, keep5 = window_excess(open_, close3, mkt, np.array([2]), np.array([0]), 5)
    legs.append(("L5 tail guard", not keep5[0] and out5.size == 0))

    # L6 summarize is sign-symmetric and hit-rate exact
    s = summarize(np.array([-0.01, 0.01, 0.02, np.nan]))
    legs.append(("L6 summary", s["n"] == 3 and s["hit_positive_pct"] == 66.7
                 and abs(s["median_pct"] - 1.0) < 1e-9))

    # L7 control sampling is seed-deterministic
    rng_a = np.random.default_rng(CONTROL_SEED)
    rng_b = np.random.default_rng(CONTROL_SEED)
    legs.append(("L7 control seed", np.array_equal(rng_a.integers(0, 10 ** 6, 5),
                                                   rng_b.integers(0, 10 ** 6, 5))))

    ok = all(v for _, v in legs)
    for name, v in legs:
        print(("PASS " if v else "FAIL ") + name)
    print(f"selftest: {sum(v for _, v in legs)}/{len(legs)} {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------------------------------------ main
def run() -> int:
    t0 = time.time()
    meta = json.load(open(os.path.join(PANEL, "meta.json"), encoding="utf-8"))
    close = np.load(os.path.join(PANEL, "close.npy"))
    open_ = np.load(os.path.join(PANEL, "open.npy"))
    raw_dates = np.load(os.path.join(PANEL, "dates.npy"), allow_pickle=True)
    dates = [str(np.datetime_as_string(np.datetime64(int(d), "us"), unit="D"))
             for d in raw_dates]
    years = np.array([int(d[:4]) for d in dates], dtype=np.int64)

    valid = np.isfinite(close) & (close > 0) & np.isfinite(open_) & (open_ > 0)
    n_days, n_sym = close.shape
    first = first_valid_row(valid)

    listed = np.nonzero(first >= 0)[0]
    rows = first[listed]
    cols = listed
    list_years = years[rows]

    mkt = market_log_curve(close, valid)

    face = {
        "generated_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": meta.get("cutoff"),
        "panel_shape": list(meta.get("shape", [])),
        "kernel": "log-space, market-adjusted by equal-weight cross-sectional median curve",
        "listing_proxy": "first valid bar in panel",
        "entry_assumption": "first-bar open (optimistic; era limit-up rules differ)",
        "survivorship": "delisted names absent -> long buckets are upper bounds",
        "n_listings": int(listed.size),
        "control": {"n_requested": CONTROL_N, "seed": CONTROL_SEED,
                    "min_age_bars": CONTROL_MIN_AGE},
        "eras": {},
        "horizons": {},
    }

    # listing-day intraday
    with np.errstate(all="ignore"):
        d1 = np.log(close[rows, cols] / open_[rows, cols])
    face["d1_listing_day_intraday"] = summarize(d1)

    # horizon buckets, pooled and per era
    rng = np.random.default_rng(CONTROL_SEED)
    for h in HORIZONS:
        out, keep = window_excess(open_, close, mkt, rows, cols, h)
        keep_rows = rows[keep]
        keep_years = years[keep_rows]
        face["horizons"][f"h{h}"] = summarize(out)

        per_era = {}
        for lo, hi in ERAS:
            sel = (keep_years >= lo) & (keep_years <= hi)
            per_era[f"{lo}-{hi if hi < 2099 else 'now'}"] = summarize(out[sel])
        face["eras"][f"h{h}"] = per_era

        # control leg: random stock-days with age >= CONTROL_MIN_AGE
        age = np.arange(n_days)[:, None] - first[None, :]
        ctrl_mask = valid & (age >= CONTROL_MIN_AGE)
        ctrl_rows, ctrl_cols = np.nonzero(ctrl_mask)
        if ctrl_rows.size:
            pick = rng.integers(0, ctrl_rows.size, size=min(CONTROL_N, ctrl_rows.size))
            c_out, c_keep = window_excess(open_, close, mkt,
                                          ctrl_rows[pick], ctrl_cols[pick], h)
            face["horizons"][f"control_h{h}"] = summarize(c_out)

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = meta.get("cutoff")
    with open(os.path.join(OUT_DIR, f"CENSUS-{stamp}.json"), "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)

    # era x horizon CSV for eyeballing
    lines = ["era,horizon,n,median_pct,mean_pct,hit_positive_pct"]
    for h in HORIZONS:
        for era, s in face["eras"][f"h{h}"].items():
            if s.get("n"):
                lines.append(f"{era},h{h},{s['n']},{s['median_pct']},{s['mean_pct']},"
                             f"{s['hit_positive_pct']}")
    with open(os.path.join(OUT_DIR, f"by-era-{stamp}.csv"), "w", encoding="utf-8",
              newline="") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({
        "evidence_cutoff": stamp,
        "n_listings": face["n_listings"],
        "d1": face["d1_listing_day_intraday"],
        "h20": face["horizons"]["h20"],
        "h250": face["horizons"]["h250"],
        "control_h20": face["horizons"].get("control_h20"),
        "elapsed_sec": round(time.time() - t0, 1),
    }, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    return _selftest() if a.selftest else run()


if __name__ == "__main__":
    sys.exit(main())