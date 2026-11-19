#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual-reversal census (exploratory, no prereg, no adoption).

Why this face exists
--------------------
results/stock_composite_pf.json closed the *same-factor, same-pool* stock track with a
negative verdict: raw 20d reversal / low-vol ICs are weak (vol_20 -0.051, mom_20 -0.036)
and a 20-name book loses to equal weight after 1.5-1.8x turnover cost. The documented
next step was "change the track: neutralize, then look at residuals", not "add more
parameters to the same recipe".

This probe asks exactly one question with data already on disk:

    after removing the market beta and the log-size exposure cross-sectionally,
    does the 20-day reversal residual predict the next 20 days any better than the
    raw 20-day return does?

It is a census: no prereg, no registration, no pool burn, no adoption. It prints both
readings side by side so a negative answer is as readable as a positive one.

Data
----
data/astock_daily/per/<sym>.csv  (sina stock_zh_a_daily, qfq, columns
date,open,high,low,close,volume,amount,outstanding_share,turnover).
Market cap at date t = close[t] * outstanding_share[t] -- the same file carries the
share count, so the size control needs no second source.

Design (frozen in this file, not tuned on results)
--------------------------------------------------
* rebalance every 20 trading rows of the global calendar, first at 2020-01-02
* universe per rebalance: close at t and t-20 present, >=100 non-null returns in the
  trailing 120-row window, 20d average amount >= 20,000,000 CNY
* beta = OLS slope of the stock's daily returns on the equal-weight market return over
  the trailing 120 rows
* logsize = log(close * outstanding_share) at t
* residual = r20 - fit[1, beta, logsize]  (cross-sectional OLS on the eligible set)
* forward = close[t+20]/close[t] - 1   (evaluation only; never enters the signal)
* cost = 8bp per side (16bp per rebalance round trip), charged on every quintile and
  on the long-short spread

Usage
-----
    python scripts/astock_resid_reversal_probe.py run [--stride 20]
    python scripts/astock_resid_reversal_probe.py selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER = os.path.join(ROOT, "data", "astock_daily", "per")
OUT = os.path.join(ROOT, "results", "astock_resid_reversal_probe.json")

COST_ONE_SIDE = 0.0008
MIN_AMOUNT_20D = 20_000_000.0
LOOKBACK_BETA = 120
HOLD = 20
FIRST_DATE = "2020-01-02"
MIN_BARS = 100


# ---------------------------------------------------------------- loading
def load_panel(per_dir: str = PER, first_date: str = FIRST_DATE):
    """Return (dates, close, amount, shares) numpy views over the union calendar."""
    files = sorted(glob.glob(os.path.join(per_dir, "*.csv")))
    if not files:
        raise SystemExit("no per-symbol csv under %s" % per_dir)

    per_sym = {}
    all_dates = set()
    for path in files:
        sym = os.path.basename(path)[:-4]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                header = fh.readline().strip().split(",")
            if "date" not in header or "close" not in header:
                continue
            idx = {name: i for i, name in enumerate(header)}
            c_i, d_i = idx["close"], idx["date"]
            a_i = idx.get("amount")
            s_i = idx.get("outstanding_share")
            dates, close, amount, shares = [], [], [], []
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                fh.readline()
                for line in fh:
                    parts = line.rstrip("\n").split(",")
                    if len(parts) <= max(c_i, d_i):
                        continue
                    d = parts[d_i]
                    if d < first_date:
                        continue
                    try:
                        c = float(parts[c_i])
                    except ValueError:
                        continue
                    if c <= 0:
                        continue
                    dates.append(d)
                    close.append(c)
                    amount.append(_f(parts[a_i]) if a_i is not None else float("nan"))
                    shares.append(_f(parts[s_i]) if s_i is not None else float("nan"))
        except OSError:
            continue
        if len(dates) >= HOLD + LOOKBACK_BETA:
            per_sym[sym] = (dates, close, amount, shares)
            all_dates.update(dates)

    if not per_sym:
        raise SystemExit("no usable symbol after parse")

    dates = sorted(all_dates)
    date_pos = {d: i for i, d in enumerate(dates)}
    n_t, n_s = len(dates), len(per_sym)
    close = np.full((n_t, n_s), np.nan, dtype=np.float64)
    amount = np.full((n_t, n_s), np.nan, dtype=np.float64)
    shares = np.full((n_t, n_s), np.nan, dtype=np.float64)
    symbols = list(per_sym)
    for j, sym in enumerate(symbols):
        d, c, a, s = per_sym[sym]
        rows = np.fromiter((date_pos[x] for x in d), dtype=np.int64, count=len(d))
        close[rows, j] = c
        amount[rows, j] = a
        shares[rows, j] = s
    return dates, symbols, close, amount, shares


def _f(text: str) -> float:
    try:
        return float(text)
    except (TypeError, ValueError):
        return float("nan")


# ---------------------------------------------------------------- maths
def daily_returns(close: np.ndarray) -> np.ndarray:
    prev = np.empty_like(close)
    prev[1:] = close[:-1]
    prev[0] = np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        r = close / prev - 1.0
    r[~np.isfinite(r)] = np.nan
    return r


def market_return(rets: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore"):
        cnt = np.sum(np.isfinite(rets), axis=1)
        tot = np.nansum(rets, axis=1)
    m = np.full(rets.shape[0], np.nan)
    ok = cnt > 0
    m[ok] = tot[ok] / cnt[ok]
    return m


def rank01(values: np.ndarray) -> np.ndarray:
    """Average-tie ranks scaled to (0,1]."""
    n = len(values)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = np.arange(1, n + 1, dtype=np.float64)
    # average ties
    sorted_vals = values[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return ranks / n


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 5:
        return float("nan")
    ra, rb = rank01(a), rank01(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    den = math.sqrt(float(np.dot(ra, ra)) * float(np.dot(rb, rb)))
    if den <= 0:
        return float("nan")
    return float(np.dot(ra, rb) / den)


def cross_sectional_residual(r20, beta, logsize) -> np.ndarray:
    """Residual of r20 on [1, beta, logsize]."""
    n = len(r20)
    X = np.column_stack([np.ones(n), beta, logsize])
    coef, *_ = np.linalg.lstsq(X, r20, rcond=None)
    return r20 - X @ coef


def beta_window(rets: np.ndarray, mkt: np.ndarray) -> np.ndarray:
    """OLS slope of each column on the market over the given rows."""
    rm = mkt - np.nanmean(mkt)
    den = float(np.nansum(rm * rm))
    if den <= 0:
        return np.full(rets.shape[1], np.nan)
    R = rets - np.nanmean(rets, axis=0)
    cov = np.nansum(R * rm[:, None], axis=0)
    return cov / den


# ---------------------------------------------------------------- core
def run(dates, symbols, close, amount, shares, stride: int = HOLD):
    rets = daily_returns(close)
    mkt = market_return(rets)
    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rows = []
    t = start
    while t + HOLD < len(dates):
        d = dates[t]
        c0 = close[t]
        c_past = close[t - HOLD]
        c_fwd = close[t + HOLD]
        with np.errstate(invalid="ignore", divide="ignore"):
            r20 = c0 / c_past - 1.0
            f20 = c_fwd / c0 - 1.0
        amt_win = amount[max(0, t - HOLD + 1):t + 1]
        with np.errstate(invalid="ignore"):
            amt20 = np.nanmean(amt_win, axis=0)
        win = rets[t - LOOKBACK_BETA + 1:t + 1]
        nbars = np.sum(np.isfinite(win), axis=0)
        beta = beta_window(win, mkt[t - LOOKBACK_BETA + 1:t + 1])
        with np.errstate(invalid="ignore", divide="ignore"):
            logsize = np.log(c0 * shares[t])

        ok = (
            np.isfinite(r20)
            & np.isfinite(f20)
            & np.isfinite(beta)
            & np.isfinite(logsize)
            & (nbars >= MIN_BARS)
            & (amt20 >= MIN_AMOUNT_20D)
        )
        if np.sum(ok) >= 60:
            rr = r20[ok]
            bb = beta[ok]
            ll = logsize[ok]
            ff = f20[ok]
            resid = cross_sectional_residual(rr, bb, ll)
            q = np.clip((rank01(resid) * 5).astype(int), 0, 4)
            qmeans = [float(np.mean(ff[q == k])) if np.any(q == k) else float("nan")
                      for k in range(5)]
            qcounts = [int(np.sum(q == k)) for k in range(5)]
            rows.append({
                "date": d,
                "n": int(np.sum(ok)),
                "ic_resid": spearman(resid, ff),
                "ic_raw": spearman(rr, ff),
                "ic_beta": spearman(bb, ff),
                "ic_size": spearman(ll, ff),
                "q_resid": qmeans,
                "q_raw": [float(np.mean(ff[np.clip((rank01(rr) * 5).astype(int), 0, 4) == k]))
                          if np.any(np.clip((rank01(rr) * 5).astype(int), 0, 4) == k) else float("nan")
                          for k in range(5)],
                "q_counts": qcounts,
                "ls_resid_net": qmeans[0] - qmeans[4] - 2 * COST_ONE_SIDE,
                "q1_excess": qmeans[0] - float(np.mean(ff)),
                "q5_excess": qmeans[4] - float(np.mean(ff)),
                "beta_expo": float(np.mean(bb[q == 0])) - float(np.mean(bb[q == 4])),
                "size_expo": float(np.mean(ll[q == 0])) - float(np.mean(ll[q == 4])),
            })
        t += stride

    return rows


def summarise(rows, key="ic_resid"):
    vals = np.array([r[key] for r in rows if np.isfinite(r.get(key, float("nan")))])
    if len(vals) < 3:
        return {"n": int(len(vals)), "mean": None, "t": None}
    sd = float(vals.std(ddof=1))
    mean = float(vals.mean())
    t = mean / (sd / math.sqrt(len(vals))) if sd > 0 else None
    return {"n": int(len(vals)), "mean": mean, "t": t, "hit": float(np.mean(vals > 0))}


def compound(period_returns, per_year=252.0 / HOLD):
    if not period_returns:
        return None
    arr = np.array(period_returns, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        return None
    return float((np.prod(1 + arr) ** (per_year / len(arr)) - 1))


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    # L1 rank01 average-tie
    r = rank01(np.array([3.0, 1.0, 1.0, 2.0]))
    legs.append(("rank ties averaged", abs(r[1] - r[2]) < 1e-12 and r[0] == 1.0 and abs(r[3] - 0.75) < 1e-12))

    # L2 spearman on monotone data
    legs.append(("spearman monotone == 1", abs(spearman(np.arange(10.0), np.arange(10.0) * 3 + 1) - 1.0) < 1e-12))

    # L3 residual of a pure beta/size plane is zero
    n = 200
    rng = np.random.default_rng(7)
    beta = rng.normal(1.0, 0.3, n)
    size = rng.normal(10.0, 0.5, n)
    r20 = 0.5 * beta + 0.02 * size + 0.01
    res = cross_sectional_residual(r20, beta, size)
    legs.append(("residual removes beta+size plane", float(np.max(np.abs(res))) < 1e-10))

    # L4 residual keeps what the controls cannot explain
    r20b = r20 + rng.normal(0, 0.05, n)
    resb = cross_sectional_residual(r20b, beta, size)
    legs.append(("residual keeps orthogonal part", float(np.std(resb)) > 1e-3))

    # L5 beta of a stock that is exactly 2x market
    mkt = rng.normal(0.0, 0.01, 120)
    two = np.column_stack([mkt * 2, mkt * 0.5])
    b = beta_window(two, mkt)
    legs.append(("beta slope 2.0 / 0.5", abs(b[0] - 2.0) < 1e-9 and abs(b[1] - 0.5) < 1e-9))

    # L6 daily_returns first row is nan, rest exact
    cl = np.array([[10.0], [11.0], [11.0]])
    dr = daily_returns(cl)
    legs.append(("daily returns", np.isnan(dr[0, 0]) and abs(dr[1, 0] - 0.1) < 1e-12 and abs(dr[2, 0]) < 1e-12))

    # L7 cost is charged on both sides of the spread
    q = [0.02, 0.01, 0.0, -0.01, -0.02]
    legs.append(("ls net charges 2 sides", abs((q[0] - q[4] - 2 * COST_ONE_SIDE) - 0.0384) < 1e-9))

    # L8 compound of flat zero is zero
    legs.append(("compound flat", abs(compound([0.0] * 10)) < 1e-12))

    bad = [name for name, ok in legs if not ok]
    print("astock_resid_reversal selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    for name, ok in legs:
        print("  %s %s" % ("PASS" if ok else "FAIL", name))
    return 0 if not bad else 1


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    global FIRST_DATE
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--stride", type=int, default=HOLD)
    ap.add_argument("--first-date", default=FIRST_DATE)
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    FIRST_DATE = args.first_date
    started = datetime.now(timezone.utc).astimezone()
    dates, symbols, close, amount, shares = load_panel(first_date=args.first_date)
    print("panel %d dates x %d symbols (%s..%s)" % (len(dates), len(symbols), dates[0], dates[-1]))
    rows = run(dates, symbols, close, amount, shares, stride=args.stride)
    if len(rows) < 6:
        print("NOT_ENOUGH_REBALANCES rows=%d" % len(rows))
        return 2

    s_resid = summarise(rows, "ic_resid")
    s_raw = summarise(rows, "ic_raw")
    s_beta = summarise(rows, "ic_beta")
    s_size = summarise(rows, "ic_size")
    ls = [r["ls_resid_net"] for r in rows]
    ls_raw = [r["q_raw"][0] - r["q_raw"][4] - 2 * COST_ONE_SIDE for r in rows]
    quint = [float(np.nanmean([r["q_resid"][k] for r in rows])) for k in range(5)]

    verdict = "NOT_SEPARABLE"
    if s_resid["t"] is not None and s_raw["t"] is not None:
        better = s_resid["mean"] < s_raw["mean"] and abs(s_resid["t"]) >= 2.0
        if better and ls and compound(ls) is not None and compound(ls) > 0:
            verdict = "RESIDUAL_REVERSAL_HAS_EDGE"
        elif abs(s_resid["mean"]) < abs(s_raw["mean"]):
            verdict = "NEUTRALISING_DID_NOT_HELP"

    payload = {
        "generated": started.isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "census",
        "prereg": None,
        "adoption": None,
        "spec": {
            "hold": HOLD,
            "stride": args.stride,
            "lookback_beta": LOOKBACK_BETA,
            "min_amount_20d": MIN_AMOUNT_20D,
            "min_bars": MIN_BARS,
            "cost_one_side": COST_ONE_SIDE,
            "controls": ["market beta", "log size"],
            "residual": "r20 on [1, beta, logsize] cross-sectional OLS",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "ic": {"residual": s_resid, "raw_r20": s_raw, "beta": s_beta, "logsize": s_size},
        "quintile_mean_forward": quint,
        "quintile_monotone": _monotone(quint),
        "ls_net_annual": compound(ls),
        "ls_net_annual_raw": compound(ls_raw),
        "ls_per_rebalance_mean": float(np.nanmean(ls)),
        "long_only": {
            "q1_excess_per_rebalance": float(np.nanmean([r["q1_excess"] for r in rows])),
            "q5_excess_per_rebalance": float(np.nanmean([r["q5_excess"] for r in rows])),
            "q1_excess_annual_compound": compound([r["q1_excess"] for r in rows]),
            "note": "long-only is the implementable leg in A-shares; margin short balance is thin",
        },
        "beta_exposure_ls_mean": float(np.nanmean([r["beta_expo"] for r in rows])),
        "size_exposure_ls_mean": float(np.nanmean([r["size_expo"] for r in rows])),
        "rows": rows,
        "verdict": verdict,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print("rebalances=%d n_median=%d" % (len(rows), int(np.median([r["n"] for r in rows]))))
    print("IC residual mean=%.4f t=%s hit=%.2f" % (s_resid["mean"], _fmt(s_resid["t"]), s_resid["hit"]))
    print("IC raw r20  mean=%.4f t=%s hit=%.2f" % (s_raw["mean"], _fmt(s_raw["t"]), s_raw["hit"]))
    print("IC beta=%.4f IC logsize=%.4f" % (s_beta["mean"], s_size["mean"]))
    print("quintiles(loser->winner)=%s monotone=%s" % (
        " ".join("%.4f" % v for v in quint), _monotone(quint)))
    print("LS net annual=%s raw-reversal=%s per-rebalance=%+.5f" % (
        _pct(compound(ls)), _pct(compound(ls_raw)), float(np.nanmean(ls))))
    print("LS exposures beta=%+.3f size=%+.3f" % (
        float(np.nanmean([r["beta_expo"] for r in rows])),
        float(np.nanmean([r["size_expo"] for r in rows]))))
    lo = payload["long_only"]
    print("long-only Q1 excess=%+.5f/reb (%s/yr)  Q5=%+.5f/reb" % (
        lo["q1_excess_per_rebalance"], _pct(lo["q1_excess_annual_compound"]),
        lo["q5_excess_per_rebalance"]))
    print("VERDICT=%s" % verdict)
    print("wrote %s" % OUT)
    return 0


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id") or "unknown"
    except (OSError, ValueError):
        return "unknown"


def _monotone(q) -> bool:
    if any(v is None or not math.isfinite(v) for v in q):
        return False
    return all(q[i] < q[i + 1] for i in range(len(q) - 1))


def _fmt(v):
    return "n/a" if v is None else "%.2f" % v


def _pct(v):
    return "n/a" if v is None else "%+.2f%%" % (v * 100)


if __name__ == "__main__":
    sys.exit(main())
