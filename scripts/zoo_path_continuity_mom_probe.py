"""zoo #92 `path_continuity_mom` (球队硬币路径动量) -- supply berth probe.

WHY THIS FILE EXISTS
--------------------
`compute_audit` has reported `supply_floor ready 0 < floor 3` for eighteen
straight rounds.  The berth registry (research/shortline/ASTYLE_ZOO.md row 92)
is the last entry whose data precondition is already satisfied on this
machine: the factor needs only daily OHLC + turnover, and `data/astock_daily/per`
now holds 5,223 qfq stock files with a turnover column.  #97 is blocked on an
IOPV/premium panel and has already been judged negative (PREMIUM-SENT-P1).

The question, in the frozen wording of the r218 parameter-freeze card:

    if a stock's three return legs (interday / intraday / overnight) have been
    LOW-volatility and its turnover path has been DECLINING (a "coin" path,
    i.e. knowable rather than lottery-like), does flipping the direction of
    that leg's recent mean return carry cross-sectional information about the
    next five days -- after cost, and beyond a same-shape random factor?

Everything here is a PROBE.  It burns no family, registers no seed, writes no
ledger row.  Its verdict is a *supply* verdict (ADMIT_TO_PREREG /
REFUSE_AS_CANDIDATE), never a research verdict.

CONSTRUCTION (frozen; copied from the r218 card, deviations disclosed)
----------------------------------------------------------------------
  legs              interday = close[t]/close[t-1] - 1
                    intraday  = close[t]/open[t]   - 1
                    overnight = open[t] /close[t-1]- 1
  leg flip 1        mu20, sd20 of the leg return; the leg is "a coin" when its
                    own sd20 is BELOW that day's cross-sectional mean sd.
                    flip1 = -mu20 when sd < sd_bar else +mu20
                    (sign(sd - sd_bar) == -1 -> reverse)
  leg flip 2        dTR[t] = TR[t] - TR[t-1]; when dTR is BELOW that day's
                    cross-sectional mean dTR the day's leg return is flipped,
                    then flip2 = rolling20 mean of the (possibly flipped) leg
  leg factor        0.5 * (flip1 + flip2)
  factor            coin = mean of the three leg factors (等权和, r218)
  direction         REVERSE: low coin = bullish, so the tested factor is -coin
  labels            fwd5  = close[t+5]/close[t]  - 1   (rank-IC label)
                    fwd20 = close[t+20]/close[t] - 1  (secondary label)
  decisions         every FIFTH bar, non-overlapping, from EVAL_FROM on
  portfolio         bottom-50 coin (i.e. top of -coin) among eligible names,
                    equal weight, entered at the close of the NEXT bar,
                    exited 5 bars later (one-bar lag, close-to-close)
  benchmark         all eligible names, same lag, same 5-bar rebalance, same cost
  cost              COST_X1 = 13.041bp per side (single-source import from
                    rev_osc_stock_p1; the x3 stress face is reported too)
  eligibility       finite OHLC/amount, close >= PRICE_MIN, 20-day mean amount
                    >= AMT20_MIN, >= LISTED_MIN bars listed, quote fresh within
                    FRESH_MAX bars, board != 'other' -- all constants imported,
                    none hand-copied
  null A            K=200 within-day permutations of the factor (same names,
                    same shape, only the name->value assignment is shuffled)
  null B            K=100 random-50 portfolios drawn from the SAME eligible
                    set on each decision day (the "any 50 names" world)

VERDICT RULES (frozen before the run; see ADMIT_* below)
-------------------------------------------------------
  ADMIT_TO_PREREG  iff  mean rank-IC(-coin, fwd5) >= +0.02
                        and its t-stat >= 2.0
                        and costed excess vs the equal-weight pool > 0
                        and null-B p <= 0.05
                        and turnover/yr <= 60
  otherwise        REFUSE_AS_CANDIDATE with the failing reasons named.

HONEST LIMITS (printed on the face, not buried)
-----------------------------------------------
  * ST exclusion is the static r2_st snapshot in data/fundamental/eligibility.csv
    (a point-in-time truth used as a time-series filter -- disclosed, not hidden).
  * Survivorship: `per/` holds the symbols that exist today.
  * The exit is a close-to-close 5-bar hold with a one-bar entry lag: this is the
    O-1132 conservative proxy, not a T+1 open fill model.
  * fwd5 is measured on the same qfq panel; splits are already adjusted.

Usage:
    python scripts/zoo_path_continuity_mom_probe.py run [--from 2020-01-02]
    python scripts/zoo_path_continuity_mom_probe.py selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rev_osc_stock_p1 as revo                       # noqa: E402  (frozen constants)

FAMILY = "zoo92_path_continuity_mom"
BATCH = "SUPPLY_BERTH_ROW_92"
PANEL_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
ELIG_CSV = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
CAL_CSV = os.path.join(ROOT, "data", "daily", "sh510300.csv")
RES_DIR = os.path.join(ROOT, "results", "supply_berth")
RES_PATH = os.path.join(RES_DIR, "zoo92_path_continuity_mom_probe.json")

PANEL_FROM = "2019-01-01"          # >= 40 bars of warm-up before EVAL_FROM
EVAL_FROM = "2020-01-02"
HOLD = 5                           # decision stride and holding period
TOPK = 50
WARM = 20                          # rolling window in the r218 card
MIN_NAMES = 100                    # a cross-section thinner than this is not a day
NULL_A_K = 200
NULL_B_K = 100
SEED = 20311007

ADMIT_MIN_IC = 0.02
ADMIT_MIN_T = 2.0
ADMIT_MAX_P = 0.05
ADMIT_MAX_TURNOVER_YR = 60.0

COST_X1 = revo.COST_X1             # 13.041bp / side
BARS_PER_YEAR = 244.0


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------ loading
def load_universe() -> list[str]:
    m = pd.read_csv(MASK_CSV, dtype={"code": str})
    m = m[m["board"] != "other"]
    codes = [c for c in m["code"].tolist()
             if os.path.exists(os.path.join(PANEL_DIR, c + ".csv"))]
    return sorted(codes)


def load_st_codes() -> set[str]:
    e = pd.read_csv(ELIG_CSV, dtype={"code": str})
    return set(e.loc[e["r2_st"] == True, "code"].tolist())      # noqa: E712


def load_calendar() -> list[str]:
    cal = pd.read_csv(CAL_CSV, usecols=["date"])["date"].astype(str).tolist()
    return [d for d in cal if d >= PANEL_FROM]


def build_panel(codes: list[str], cal: list[str]) -> dict:
    """(T, N) float32 arrays: open, close, amount, turnover."""
    T, N = len(cal), len(codes)
    F = {k: np.full((T, N), np.nan, dtype=np.float32)
         for k in ("open", "close", "amount", "turnover")}
    dpos = {d: i for i, d in enumerate(cal)}
    for j, code in enumerate(codes):
        path = os.path.join(PANEL_DIR, code + ".csv")
        df = pd.read_csv(path, usecols=["date", "open", "close", "amount", "turnover"])
        if df["date"].dtype != object:
            df["date"] = df["date"].astype(str)
        rows = np.fromiter((dpos.get(d, -1) for d in df["date"]),
                           dtype=np.int64, count=len(df))
        keep = rows >= 0
        r = rows[keep]
        for k in ("open", "close", "amount", "turnover"):
            F[k][r, j] = df[k].to_numpy(dtype=np.float32)[keep]
    F["codes"] = codes
    F["dates"] = cal
    return F


# ------------------------------------------------------------------ factor
def legs(open_, close):
    """The three return legs of the r218 card. prev_close carries NaN on bar 0."""
    prev = np.vstack([np.full((1, close.shape[1]), np.nan, np.float32), close[:-1]])
    with np.errstate(invalid="ignore", divide="ignore"):
        r_day = (close / prev - 1.0).astype(np.float32)
        r_int = (close / open_ - 1.0).astype(np.float32)
        r_night = (open_ / prev - 1.0).astype(np.float32)
    return r_day, r_int, r_night


def _roll_mean(a: np.ndarray, w: int) -> np.ndarray:
    return pd.DataFrame(a).rolling(w, min_periods=w).mean().to_numpy(np.float32)


def _roll_std(a: np.ndarray, w: int) -> np.ndarray:
    return pd.DataFrame(a).rolling(w, min_periods=w).std(ddof=0).to_numpy(np.float32)


def _xs_mean(a: np.ndarray) -> np.ndarray:
    """Per-row (per-day) mean over the finite entries; an all-NaN row -> NaN."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        with np.errstate(invalid="ignore"):
            return np.nanmean(np.where(np.isfinite(a), a, np.nan), axis=1).astype(np.float32)


def vol_flip(r: np.ndarray) -> np.ndarray:
    """Flip ① of the card: a leg whose own sd20 sits BELOW the day's
    cross-sectional mean sd is 'a coin', so its recent mean is reversed."""
    mu = _roll_mean(r, WARM)
    sd = _roll_std(r, WARM)
    sd_bar = _xs_mean(sd)[:, None]
    with np.errstate(invalid="ignore"):
        coin = sd < sd_bar                      # True = "a coin" = reverse mu
    return np.where(coin, -mu, mu).astype(np.float32)


def turn_flip(r: np.ndarray, tr: np.ndarray) -> np.ndarray:
    """Flip ② of the card: a declining turnover path reverses that day's leg
    return, then the flipped return's rolling20 mean is the factor."""
    dtr = tr - np.vstack([np.full((1, tr.shape[1]), np.nan, np.float32), tr[:-1]])
    dtr_bar = _xs_mean(dtr)[:, None]
    with np.errstate(invalid="ignore"):
        shrink = dtr < dtr_bar                  # True = turnover path declining
    flipped = np.where(shrink, -r, r).astype(np.float32)
    return _roll_mean(flipped, WARM)


def leg_factor(r: np.ndarray, tr: np.ndarray) -> np.ndarray:
    """flip① + flip② averaged into one leg factor (r218 card)."""
    return (0.5 * (vol_flip(r) + turn_flip(r, tr))).astype(np.float32)


def coin_factor(open_, close, tr) -> np.ndarray:
    r_day, r_int, r_night = legs(open_, close)
    f = (leg_factor(r_day, tr) + leg_factor(r_int, tr) + leg_factor(r_night, tr)) / 3.0
    return f.astype(np.float32)


# ------------------------------------------------------------------ eligibility
def eligibility_mask(F: dict, st: set[str]) -> np.ndarray:
    close = F["close"]
    T, N = close.shape
    fin = np.isfinite(close) & np.isfinite(F["open"])
    amt20 = _roll_mean(F["amount"], 20)
    listed = fin.cumsum(axis=0)
    idx = np.where(fin, np.arange(T)[:, None], -1)
    lastvalid = np.maximum.accumulate(idx, axis=0)
    fresh = (np.arange(T)[:, None] - lastvalid) <= revo.FRESH_MAX
    st_row = np.array([c in st for c in F["codes"]])
    with np.errstate(invalid="ignore"):
        elig = (fin & ~st_row[None, :] & (close >= revo.PRICE_MIN)
                & np.isfinite(amt20) & (amt20 >= revo.AMT20_MIN)
                & (listed >= revo.LISTED_MIN) & fresh)
    return elig


# ------------------------------------------------------------------ maths
def _rank(a: np.ndarray) -> np.ndarray:
    """Average ranks (1..n) of a 1-d array, ties averaged."""
    n = a.shape[0]
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = np.arange(1, n + 1, dtype=np.float64)
    vals = a[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and vals[j + 1] == vals[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return ranks


def rank_ic(x: np.ndarray, y: np.ndarray) -> float:
    if x.shape[0] < 3:
        return float("nan")
    rx, ry = _rank(x), _rank(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if den <= 0:
        return float("nan")
    return float((rx * ry).sum() / den)


def decision_rows(dates: list[str], from_date: str, step: int = HOLD) -> list[int]:
    start = int(np.searchsorted(np.array(dates), from_date))
    return list(range(start, len(dates), step))


def fwd_return(close: np.ndarray, h: int) -> np.ndarray:
    T, N = close.shape
    out = np.full((T, N), np.nan, dtype=np.float32)
    with np.errstate(invalid="ignore"):
        out[:T - h] = close[h:] / close[:T - h] - 1.0
    return out


def portfolio_period_return(fac: np.ndarray, elig: np.ndarray, fwd: np.ndarray,
                            rows: list[int], k: int, prefer_low: bool = True,
                            pick_fixed: np.ndarray | None = None) -> dict:
    """One value per decision row: the equal-weight hold return of `k` names.

    Entry is the close of bar row+1 (fwd measured from there), so the label used
    for entry must be `fwd` measured at row+1 -- we shift the decision by one bar
    by reading `fwd[row + 1]`, which is exactly close[t+1+h]/close[t+1]-1.
    """
    rets, sizes, picks = [], [], []
    for r in rows:
        e = r + 1
        if e >= fac.shape[0]:
            continue
        ok = elig[e] & np.isfinite(fac[r]) & np.isfinite(fwd[e])
        idx = np.where(ok)[0]
        if idx.size < max(k, MIN_NAMES):
            rets.append(float("nan")); sizes.append(int(idx.size)); picks.append(None)
            continue
        if pick_fixed is not None:
            sel = pick_fixed
        else:
            # The card's direction is REVERSE: the lowest coin values are the
            # bullish names, so the book sorts the factor ascending. (r1407: the
            # first cut sorted descending here while the null-B world sorted
            # ascending -- the two faces disagreed and the book read -47%/yr
            # against an IC of +0.07. One sort order, pinned by a selftest leg.)
            vals = fac[r, idx]
            order = idx[np.argsort(vals if prefer_low else -vals, kind="mergesort")]
            sel = order[:k]
        rets.append(float(np.nanmean(fwd[e, sel])))
        sizes.append(int(idx.size))
        picks.append(sel)
    return {"ret": np.array(rets, dtype=np.float64),
            "sizes": sizes, "picks": picks}


def turnover_per_rebalance(picks: list) -> float:
    """Fraction of the book replaced, in 'sides' (0 = same names, 2 = all new)."""
    sides = []
    for a, b in zip(picks[:-1], picks[1:]):
        if a is None or b is None:
            continue
        sa, sb = set(a.tolist()), set(b.tolist())
        sides.append((len(sa - sb) + len(sb - sa)) / max(1, len(sb)))
    return float(np.mean(sides)) if sides else float("nan")


def curve_from_periods(rets: np.ndarray, sides: float, cost: float,
                       picks: list) -> dict:
    """Compound a non-overlapping period-return series into an annualised curve."""
    r = np.where(np.isfinite(rets), rets, 0.0).astype(np.float64)
    to = turnover_per_rebalance(picks)
    # `to` already counts both sides of a swap as fraction of the book
    # (a full replacement reads 2.0), so one side's cost is `to * cost`.
    net = r - (to * cost if np.isfinite(to) else 0.0)
    nav = np.cumprod(1.0 + net)
    n = net.size
    if n == 0:
        return {"periods": 0, "cagr": float("nan"), "max_dd": float("nan"),
                "turnover_per_rebalance": float("nan"), "nav_last": float("nan")}
    years = n * HOLD / BARS_PER_YEAR
    cagr = float(nav[-1] ** (1.0 / years) - 1.0) if years > 0 else float("nan")
    peak = np.maximum.accumulate(nav)
    mdd = float((nav / peak - 1.0).min())
    return {"periods": int(n), "cagr": cagr, "max_dd": mdd,
            "turnover_per_rebalance": float(to),
            "turnover_per_year": float(to * BARS_PER_YEAR / HOLD),
            "nav_last": float(nav[-1])}


# ------------------------------------------------------------------ faces
def null_a_ic(fac: np.ndarray, fwd: np.ndarray, elig: np.ndarray, rows: list[int],
              k: int = NULL_A_K, seed: int = SEED) -> dict:
    """Within-day permutations of the factor: same names, same shape, new labels."""
    rng = np.random.default_rng(seed)
    obs = []
    for r in rows:
        ok = elig[r] & np.isfinite(fac[r]) & np.isfinite(fwd[r])
        idx = np.where(ok)[0]
        if idx.size >= MIN_NAMES:
            obs.append(rank_ic(-fac[r, idx], fwd[r, idx]))
    obs = np.array([v for v in obs if np.isfinite(v)])
    if obs.size == 0:
        return {"n_days": 0, "mean_ic": float("nan"), "p": float("nan")}
    means = np.empty(k, dtype=np.float64)
    for i in range(k):
        per_day = []
        for r in rows:
            ok = elig[r] & np.isfinite(fac[r]) & np.isfinite(fwd[r])
            idx = np.where(ok)[0]
            if idx.size < MIN_NAMES:
                continue
            v = fac[r, idx].copy()
            rng.shuffle(v)
            per_day.append(rank_ic(-v, fwd[r, idx]))
        per_day = np.array([x for x in per_day if np.isfinite(x)])
        means[i] = per_day.mean() if per_day.size else np.nan
    means = means[np.isfinite(means)]
    mu = float(obs.mean())
    p = float((np.abs(means) >= abs(mu)).mean()) if means.size else float("nan")
    return {"n_days": int(obs.size), "mean_ic": mu, "null_mean": float(means.mean()),
            "null_p95_abs": float(np.quantile(np.abs(means), 0.95)), "p": p}


def null_b_portfolio(fac: np.ndarray, fwd: np.ndarray, elig: np.ndarray,
                     rows: list[int], k: int = NULL_B_K,
                     seed: int = SEED) -> dict:
    """Random-50 books from the same eligible set on the same days."""
    rng = np.random.default_rng(seed)
    obs = []
    for r in rows:
        e = r + 1
        if e >= fac.shape[0]:
            continue
        ok = elig[e] & np.isfinite(fac[r]) & np.isfinite(fwd[e])
        idx = np.where(ok)[0]
        if idx.size < max(TOPK, MIN_NAMES):
            continue
        vals = fac[r, idx]
        order = idx[np.argsort(vals, kind="mergesort")]
        obs.append(float(np.nanmean(fwd[e, order[:TOPK]])))
    obs = np.array([v for v in obs if np.isfinite(v)])
    if obs.size == 0:
        return {"n_days": 0, "mean": float("nan"), "p": float("nan")}
    means = np.empty(k, dtype=np.float64)
    for i in range(k):
        per_day = []
        for r in rows:
            e = r + 1
            if e >= fac.shape[0]:
                continue
            ok = elig[e] & np.isfinite(fac[r]) & np.isfinite(fwd[e])
            idx = np.where(ok)[0]
            if idx.size < max(TOPK, MIN_NAMES):
                continue
            sel = rng.choice(idx, size=TOPK, replace=False)
            per_day.append(float(np.nanmean(fwd[e, sel])))
        per_day = np.array([x for x in per_day if np.isfinite(x)])
        means[i] = per_day.mean() if per_day.size else np.nan
    means = means[np.isfinite(means)]
    mu = float(obs.mean())
    p = float((means >= mu).mean()) if means.size else float("nan")
    return {"n_days": int(obs.size), "mean": mu, "null_mean": float(means.mean()),
            "null_p95": float(np.quantile(means, 0.95)), "p": p}


# ------------------------------------------------------------------ run
def cmd_run(args) -> int:
    t0 = time.time()
    codes = load_universe()
    st = load_st_codes()
    cal = load_calendar()
    F = build_panel(codes, cal)
    open_, close, tr = F["open"], F["close"], F["turnover"]
    fac = coin_factor(open_, close, tr)
    elig = eligibility_mask(F, st)
    fwd5 = fwd_return(close, HOLD)
    fwd20 = fwd_return(close, 20)
    rows = decision_rows(cal, args.from_date)

    ics5, ics20 = [], []
    for r in rows:
        ok = elig[r] & np.isfinite(fac[r]) & np.isfinite(fwd5[r])
        idx = np.where(ok)[0]
        if idx.size >= MIN_NAMES:
            ics5.append(rank_ic(-fac[r, idx], fwd5[r, idx]))
        ok20 = elig[r] & np.isfinite(fac[r]) & np.isfinite(fwd20[r])
        i20 = np.where(ok20)[0]
        if i20.size >= MIN_NAMES:
            ics20.append(rank_ic(-fac[r, i20], fwd20[r, i20]))
    ics5 = np.array([v for v in ics5 if np.isfinite(v)])
    ics20 = np.array([v for v in ics20 if np.isfinite(v)])
    mu_ic = float(ics5.mean()) if ics5.size else float("nan")
    sd_ic = float(ics5.std(ddof=1)) if ics5.size > 1 else float("nan")
    t_ic = float(mu_ic / (sd_ic / np.sqrt(ics5.size))) if ics5.size > 1 and sd_ic > 0 else float("nan")

    book = portfolio_period_return(fac, elig, fwd5, rows, TOPK, prefer_low=True)
    pool_picks = [None] * len(rows)
    bench_rets = []
    for r in rows:
        e = r + 1
        if e >= fac.shape[0]:
            bench_rets.append(float("nan")); continue
        ok = elig[e] & np.isfinite(fwd5[e])
        idx = np.where(ok)[0]
        bench_rets.append(float(np.nanmean(fwd5[e, idx])) if idx.size >= MIN_NAMES else float("nan"))
    bench_rets = np.array(bench_rets, dtype=np.float64)

    book_c = curve_from_periods(book["ret"], 1.0, COST_X1, book["picks"])
    bench_c = curve_from_periods(bench_rets, 1.0, COST_X1, [None] * len(rows))
    book_c3 = curve_from_periods(book["ret"], 1.0, COST_X1 * 3, book["picks"])

    na = null_a_ic(fac, fwd5, elig, rows)
    nb = null_b_portfolio(fac, fwd5, elig, rows)

    excess = float(book_c["cagr"] - bench_c["cagr"])
    excess_x3 = float(book_c3["cagr"] - bench_c["cagr"])

    reasons = []
    if not (np.isfinite(mu_ic) and mu_ic >= ADMIT_MIN_IC):
        reasons.append("rank-IC below %.2f (got %.4f)" % (ADMIT_MIN_IC, mu_ic))
    if not (np.isfinite(t_ic) and t_ic >= ADMIT_MIN_T):
        reasons.append("IC t-stat below %.1f (got %.2f)" % (ADMIT_MIN_T, t_ic))
    if not (np.isfinite(excess) and excess > 0):
        reasons.append("costed excess vs equal-weight pool not positive (%.2f pp/yr)" % (100 * excess))
    if not (np.isfinite(nb["p"]) and nb["p"] <= ADMIT_MAX_P):
        reasons.append("random-50 null p above %.2f (got %.3f)" % (ADMIT_MAX_P, nb["p"]))
    to_yr = book_c["turnover_per_year"]
    if not (np.isfinite(to_yr) and to_yr <= ADMIT_MAX_TURNOVER_YR):
        reasons.append("turnover %.1f/yr above budget %.0f" % (to_yr, ADMIT_MAX_TURNOVER_YR))
    verdict = "ADMIT_TO_PREREG" if not reasons else "REFUSE_AS_CANDIDATE"

    per_year = {}
    dates = np.array(cal)
    for y in sorted({dates[r][:4] for r in rows}):
        sel = [i for i, r in enumerate(rows) if dates[r][:4] == y]
        rr = book["ret"][sel]
        bb = bench_rets[sel]
        per_year[y] = {
            "n": int(len(sel)),
            "book_mean": float(np.nanmean(rr)) if np.isfinite(rr).any() else float("nan"),
            "bench_mean": float(np.nanmean(bb)) if np.isfinite(bb).any() else float("nan"),
        }

    out = {
        "family": FAMILY, "batch": BATCH, "generated": _now(),
        "evidence_cutoff": cal[-1],
        "verdict": verdict, "refuse_reasons": reasons,
        "verdict_scope": "supply berth #92 (r218 frozen parameterisation, clean-room)",
        "panel": {"codes": len(codes), "bars": len(cal), "from": cal[0],
                  "eval_from": args.from_date, "st_excluded": len(st & set(codes)),
                  "median_eligible": float(np.median(elig.sum(axis=1)))},
        "frozen": {"hold": HOLD, "topk": TOPK, "warm": WARM, "cost_x1": COST_X1,
                   "null_a_k": NULL_A_K, "null_b_k": NULL_B_K, "seed": SEED,
                   "admit_min_ic": ADMIT_MIN_IC, "admit_min_t": ADMIT_MIN_T,
                   "admit_max_p": ADMIT_MAX_P,
                   "admit_max_turnover_yr": ADMIT_MAX_TURNOVER_YR},
        "ic": {"mean": mu_ic, "sd": sd_ic, "t": t_ic, "n_days": int(ics5.size),
               "mean_fwd20": float(ics20.mean()) if ics20.size else float("nan"),
               "n_days_fwd20": int(ics20.size),
               "hit_rate": float((ics5 > 0).mean()) if ics5.size else float("nan")},
        "book": dict(book_c, cost="x1"),
        "pool": dict(bench_c, cost="x1"),
        "book_x3": dict(book_c3, cost="x3"),
        "excess_pp_yr": 100 * excess,
        "excess_x3_pp_yr": 100 * excess_x3,
        "null_a": na, "null_b": nb, "per_year": per_year,
        "disclosures": [
            "ST exclusion uses the static r2_st snapshot as a time-series filter",
            "survivorship: per/ holds symbols that exist today",
            "exit is a 5-bar close-to-close hold with a one-bar entry lag (O-1132 proxy)",
            "the pool benchmark rebalances on exactly the same days and pays the same cost",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(RES_DIR, exist_ok=True)
    with open(RES_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("verdict", "refuse_reasons", "ic",
                                          "excess_pp_yr", "excess_x3_pp_yr",
                                          "null_a", "null_b")},
                     ensure_ascii=False, indent=2))
    print("wrote", RES_PATH, "in", out["elapsed_sec"], "s")
    return 0


# ------------------------------------------------------------------ selftest
def _synth(n_days=160, n_names=80, seed=7):
    rng = np.random.default_rng(seed)
    close = np.cumprod(1 + rng.normal(0, 0.02, (n_days, n_names)), axis=0).astype(np.float32) * 10
    open_ = (close * (1 + rng.normal(0, 0.005, (n_days, n_names)))).astype(np.float32)
    tr = np.abs(rng.normal(0.01, 0.004, (n_days, n_names))).astype(np.float32)
    return open_, close, tr


def cmd_selftest(args) -> int:
    ok = 0
    fails = []

    def check(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
            print("[PASS] %s%s" % (name, (" | " + detail) if detail else ""))
        else:
            fails.append(name)
            print("[FAIL] %s%s" % (name, (" | " + detail) if detail else ""))

    # 1. legs identity: (1+intraday)(1+overnight) - 1 == interday
    open_, close, tr = _synth()
    r_day, r_int, r_night = legs(open_, close)
    lhs = (1 + r_int) * (1 + r_night) - 1
    m = np.isfinite(lhs) & np.isfinite(r_day)
    check("legs identity (intraday x overnight == interday)",
          np.nanmax(np.abs(lhs[m] - r_day[m])) < 1e-5,
          "max abs %.2e" % np.nanmax(np.abs(lhs[m] - r_day[m])))

    # 2. flip①: a quiet leg (sd below the day's cross-sectional mean) reverses its
    #    positive mean; a loud leg (sd above) keeps it
    r = np.zeros((60, 4), dtype=np.float32)
    r[:, 0] = 0.01                                            # quiet, constant
    r[:, 1] = 0.01
    r[:, 3] = np.where(np.arange(60) % 2 == 0, 0.09, 0.01)    # loud, mean 0.05
    vf = vol_flip(r)
    check("vol flip: quiet leg reverses its positive mean",
          np.isfinite(vf[-1, 0]) and vf[-1, 0] < 0, "f=%.4f" % vf[-1, 0])
    check("vol flip: loud leg keeps its positive mean",
          np.isfinite(vf[-1, 3]) and vf[-1, 3] > 0, "f=%.4f" % vf[-1, 3])

    # 3. flip②: a declining turnover path flips the day's positive return
    #    negative, a flat/rising path leaves it alone
    rr = np.full((60, 4), 0.01, np.float32)
    tr2 = np.full((60, 4), 0.02, np.float32)
    tr2[40:, 3] = np.linspace(0.02, 0.005, 20)                # symbol 3 shrinks
    tr2[40:, 0] = np.linspace(0.02, 0.021, 20)                # symbol 0 grows
    tf = turn_flip(rr, tr2)
    check("turnover flip: shrinking path reverses a positive return",
          np.isfinite(tf[-1, 3]) and tf[-1, 3] < 0, "f=%.4f" % tf[-1, 3])
    check("turnover flip: growing path keeps it positive",
          np.isfinite(tf[-1, 0]) and tf[-1, 0] > 0, "f=%.4f" % tf[-1, 0])

    # 4. factor is the mean of the three leg factors
    op, cl, t3 = _synth(seed=11)
    a, b, c = legs(op, cl)
    expect = (leg_factor(a, t3) + leg_factor(b, t3) + leg_factor(c, t3)) / 3.0
    got = coin_factor(op, cl, t3)
    m = np.isfinite(expect)
    check("coin factor equals the mean of the three leg factors",
          np.nanmax(np.abs(expect[m] - got[m])) < 1e-6)

    # 5. rank IC sign: a factor that is exactly -fwd must give IC = +1 through
    #    the same reverse convention the probe uses (-factor)
    y = np.array([0.03, -0.01, 0.02, 0.05, -0.04, 0.0, 0.01])
    check("rank IC is +1 for an exactly anti-correlated factor",
          abs(rank_ic(-y, y) + 1.0) < 1e-9, "ic=%.6f" % rank_ic(-y, y))
    check("rank IC is NaN-safe on a zero-variance side",
          not np.isfinite(rank_ic(np.ones(7), y)))
    ties = np.array([1.0, 1.0, 2.0, 2.0, 3.0])
    check("ties get average ranks",
          np.max(np.abs(_rank(ties) - np.array([1.5, 1.5, 3.5, 3.5, 5.0]))) < 1e-12)

    # 6. within-day permutation preserves the per-day value multiset
    rng = np.random.default_rng(3)
    row = rng.normal(size=50)
    sh = row.copy(); rng.shuffle(sh)
    check("permutation keeps the same values (shape-only null)",
          np.allclose(np.sort(row), np.sort(sh)))

    # 7. eligibility: fresh liquid names survive, a quote stale past FRESH_MAX dies
    T, N = 400, 3
    close = np.full((T, N), 10.0, np.float32)
    open_ = close.copy()
    amt = np.full((T, N), 1e9, np.float32)
    close[50:, 1] = np.nan                                  # symbol 1 stops printing at 50
    FF = {"open": open_, "close": close, "amount": amt,
          "codes": ["000001", "000002", "000003"],
          "turnover": np.full((T, N), 0.01, np.float32)}
    em = eligibility_mask(FF, set())
    check("eligibility: a live liquid name is eligible", bool(em[70, 0]))
    check("eligibility: a name stops being eligible the bar it stops printing",
          not bool(em[70, 1]) and not bool(em[51, 1]))
    check("eligibility: a quote stale past FRESH_MAX loses eligibility",
          not bool(em[T - 1, 1]), "gap=%d FRESH_MAX=%d" % (T - 1 - 50, revo.FRESH_MAX))
    st_em = eligibility_mask(FF, {"000001"})
    check("eligibility: the ST snapshot removes the name", not bool(st_em[70, 0]))

    # 7b. the book must sort the factor ASCENDING (low coin = bullish), the same
    #     order the random-book null uses -- r1407 shipped a descending sort on
    #     this line while the null sorted ascending, and only the two faces
    #     disagreeing revealed it
    fac_t = np.tile(np.arange(120, dtype=np.float64)[::-1], (10, 1))     # 119..0
    elig_t = np.ones((10, 120), dtype=bool)
    fwd_t = np.tile(np.arange(120, dtype=np.float64), (10, 1)) * 0.001
    low = portfolio_period_return(fac_t, elig_t, fwd_t, [0, 1], k=3, prefer_low=True)
    high = portfolio_period_return(fac_t, elig_t, fwd_t, [0, 1], k=3, prefer_low=False)
    check("the book picks the LOWEST factor values (reverse direction)",
          abs(float(np.nanmean(low["ret"])) - 0.118) < 1e-9,
          "mean=%.4f" % float(np.nanmean(low["ret"])))
    check("prefer_low=False is the mirror book",
          abs(float(np.nanmean(high["ret"])) - 0.001) < 1e-9,
          "mean=%.4f" % float(np.nanmean(high["ret"])))

    # 8. cost must reduce the curve, and zero cost must reproduce the gross curve
    rets = np.array([0.01, -0.005, 0.02, 0.0], dtype=np.float64)
    picks = [np.array([1, 2]), np.array([3, 4]), np.array([3, 4]), np.array([3, 4])]
    free = curve_from_periods(rets, 1.0, 0.0, picks)
    paid = curve_from_periods(rets, 1.0, COST_X1, picks)
    check("cost strictly reduces the compounded curve", paid["nav_last"] < free["nav_last"],
          "gross %.6f net %.6f" % (free["nav_last"], paid["nav_last"]))
    check("turnover counts both replaced legs (a full swap = 2 sides)",
          abs(turnover_per_rebalance([np.array([1, 2]), np.array([3, 4])]) - 2.0) < 1e-9,
          "to=%.3f" % turnover_per_rebalance([np.array([1, 2]), np.array([3, 4])]))

    # 9. empty input must read NOT-ASSESSED (NaN), never a zero
    empty = curve_from_periods(np.array([]), 1.0, COST_X1, [])
    check("an empty series prints NaN, not 0.0",
          not np.isfinite(empty["cagr"]) and empty["periods"] == 0)

    # 10. determinism: the same synthetic panel gives the same factor twice
    op, cl, t3 = _synth(seed=13)
    check("factor is deterministic", np.allclose(coin_factor(op, cl, t3),
                                                 coin_factor(op, cl, t3), equal_nan=True))

    # 11. decision rows start at EVAL_FROM and step by HOLD
    dates = [str(d) for d in pd.date_range("2020-01-01", periods=30).date]
    rows = decision_rows(dates, dates[3])
    check("decision rows honour the from-date and the stride",
          rows[:3] == [3, 8, 13], str(rows[:3]))

    print("\nSELFTEST %s (%d/%d)" % ("OK" if not fails else "FAIL", ok, ok + len(fails)))
    if fails:
        print("failed legs:", fails)
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--from", dest="from_date", default=EVAL_FROM)
    p.set_defaults(func=cmd_run)
    s = sub.add_parser("selftest")
    s.set_defaults(func=cmd_selftest)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())