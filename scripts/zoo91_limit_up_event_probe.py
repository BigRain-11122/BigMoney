#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo91_limit_up_event -- supply berth probe (event family: the moment a name is
forced to trade).

WHY THIS FILE EXISTS
--------------------
r1390 measured cross-sectional breadth as a TAX: on the wide A-share panel a
20-bar reversal book buying the worst 10 names loses -8.15%/yr against a
same-pool equal-weight universe, and a same-exposure random-rank null averages
-3.38pp/yr on its own (card E387).  The lesson is that "how many names to hold"
is exhausted as a free axis -- the only axis left is WHEN one specific name is
forced to trade, which is the event family the last round named as the next
berth (supply has been 0/3 for nine rounds: compute_audit supply_floor).

The cheapest event this panel can see is a sealed limit-up bar: the exchange
stops the tape at the ceiling (close == high at the board limit), so the name is
*forced* to trade tomorrow at whatever the open is, and nobody who wanted in
today got in.  That is an exogenous trading clock, not a rank.

    does a sealed limit-up bar carry forward information, after the cost of
    entering at the NEXT open (which is where you actually can enter), beyond a
    same-exposure null drawn from the same date in the same panel?

Everything here is a PROBE.  It burns no family, registers no seed, writes no
ledger row.  Its verdict is a *supply* verdict (ADMIT_TO_PREREG /
REFUSE_AS_CANDIDATE), never a research verdict.

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  panel             data/astock_daily/per/<sym>.csv (qfq, forward-accumulated),
                    window >= 2020-01-01 up to each file's own last bar
  event             bar t with close[t]/close[t-1]-1 >= LIMIT-0.005 AND
                    close[t] >= high[t] - 1e-9   (sealed AT the close)
  board limit       prefix 300/301/688/689 -> 0.20; 4/8/920 -> 0.30; else 0.10
                    (ST names trade at 5% and are therefore never events here --
                    they are excluded by construction, not by choice)
  entry             open[t+1] -- the first bar you could actually buy
  exit              close[t+h], h in {5, 10, 20}
  benchmark         cross-sectional mean of the same h-bar return over every
                    name with a valid value on the same date t
  excess            per-event (F[t,s] - pool[t]), then averaged: date-neutral
  null              K draws of the SAME per-date event counts, sampled from
                    cells of that date that are neither an event nor within h
                    bars AFTER an event of that same name
  cost              2 x COST_X1_RATE (enter + exit) charged on every event
  qfq caveat        on an ex-rights bar the adjusted ratio is not the traded
                    ratio, so a few limit-up bars near corporate actions can be
                    missed or mis-sealed; this is noise on the event SET, not a
                    look-ahead, and it is disclosed rather than patched.

Everything is a reading, not a claim: the verdict block says what the numbers
support and what they do not.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PER = os.path.join(ROOT, "data", "astock_daily", "per")
OUT = os.path.join(ROOT, "results", "supply_berth", "zoo91_limit_up_event_probe.json")

COST_PER_SIDE = 0.0013041  # COST_X1_RATE, same constant the book cards pay
START = "2020-01-01"
HORIZONS = (5, 10, 20)
DRAWS = 200
SEAL_TOL = 0.005  # 50bp: rounding on the printed limit sits inside this
MIN_POOL = 100    # a date needs this many valid names to have a benchmark


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def board_limit(sym: str) -> float:
    """Traded price limit for a board, read off the symbol prefix."""
    s = sym[:3]
    if s in ("300", "301", "688", "689"):
        return 0.20
    if sym[:1] in ("4", "8") or s == "920":
        return 0.30
    return 0.10


def _read_tail(path: str, start: str = START):
    """Read only the bars at/after `start` (dates are ascending in the archive)."""
    import pandas as pd

    with open(path, "rb") as fh:
        blob = fh.read()
    off = None
    for yr in range(int(start[:4]), 2027):
        pos = blob.find(("\n%d-" % yr).encode())
        if pos >= 0:
            off = pos + 1  # first bar of the first year that has data >= start
            break
    if off is None:  # whole history predates the window
        return None
    try:
        df = pd.read_csv(
            io.BytesIO(blob[off:]),
            header=None,
            names=["date", "open", "high", "low", "close", "volume", "amount", "os", "turn"],
            usecols=[0, 1, 2, 3, 4],
            dtype={0: str, 1: float, 2: float, 3: float, 4: float},
            engine="c",
        )
    except Exception:
        return None
    if len(df) < 30:
        return None
    df = df[df["date"] >= start]
    return df if len(df) >= 30 else None


def load_panel(per_dir: str = PER, start: str = START, max_symbols: int | None = None):
    files = sorted(f for f in os.listdir(per_dir) if f.endswith(".csv"))
    if max_symbols:
        files = files[:max_symbols]
    syms, frames, dates = [], [], set()
    for fn in files:
        sym = fn[:-4]
        df = _read_tail(os.path.join(per_dir, fn), start)
        if df is None:
            continue
        syms.append(sym)
        frames.append(df)
        dates.update(df["date"].tolist())
    order = sorted(dates)
    idx = {d: i for i, d in enumerate(order)}
    T, S = len(order), len(syms)
    op = np.full((T, S), np.nan, dtype=np.float32)
    hi = np.full((T, S), np.nan, dtype=np.float32)
    lo = np.full((T, S), np.nan, dtype=np.float32)
    cl = np.full((T, S), np.nan, dtype=np.float32)
    for j, df in enumerate(frames):
        rows = np.fromiter((idx[d] for d in df["date"]), dtype=np.int64, count=len(df))
        op[rows, j] = df["open"].to_numpy(dtype=np.float32)
        hi[rows, j] = df["high"].to_numpy(dtype=np.float32)
        lo[rows, j] = df["low"].to_numpy(dtype=np.float32)
        cl[rows, j] = df["close"].to_numpy(dtype=np.float32)
    return {"dates": order, "symbols": syms, "open": op, "high": hi, "low": lo, "close": cl}


# --------------------------------------------------------------------------- #
# probe core (single implementation; selftest feeds it synthetic panels)
# --------------------------------------------------------------------------- #
def limit_matrix(symbols) -> np.ndarray:
    return np.array([board_limit(s) for s in symbols], dtype=np.float32)


def event_mask(open_, high, close, limits, seal_tol: float = SEAL_TOL,
               low=None, direction: str = "up"):
    """A sealed bar at the traded price limit.

    direction="up"   close == high at the ceiling  -> the name is forced to trade
                     tomorrow because buyers could not get filled today.
    direction="down" close == low at the floor     -> the name is forced to trade
                     tomorrow because sellers could not get out today.
    One mask, two sides: the sealing test is the same "the tape stopped at the
    limit and the close sits on that edge" statement, read against the bar's own
    extreme (high for up, low for down).
    """
    prev = np.full_like(close, np.nan)
    prev[1:] = close[:-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        r = close / prev - 1.0
    if direction == "down":
        if low is None:
            raise ValueError("direction='down' needs the low matrix")
        sealed = close <= low + 1e-9
        ev = (r <= -(limits[None, :] - seal_tol)) & sealed & np.isfinite(r) & np.isfinite(open_)
    else:
        sealed = close >= high - 1e-9
        ev = (r >= (limits[None, :] - seal_tol)) & sealed & np.isfinite(r) & np.isfinite(open_)
    return ev


def forward_matrix(open_, close, h: int):
    """F[t,s] = close[t+h]/open[t+1] - 1  (enter next open, exit h bars later)."""
    T = close.shape[0]
    o1 = np.full_like(close, np.nan)
    if T > 1:
        o1[:-1] = open_[1:]
    F = np.full_like(close, np.nan)
    if T > h:
        with np.errstate(invalid="ignore", divide="ignore"):
            F[: T - h] = close[h:] / o1[: T - h] - 1.0
    return F


def pool_mean(F: np.ndarray, min_pool: int = MIN_POOL):
    ok = np.isfinite(F)
    n = ok.sum(axis=1)
    with np.errstate(invalid="ignore"):
        s = np.where(ok, F, 0.0).sum(axis=1)
    mean = np.full(F.shape[0], np.nan)
    good = n >= min_pool
    mean[good] = s[good] / n[good]
    return mean, n


def _adjacent_exclusion(ev: np.ndarray, h: int) -> np.ndarray:
    """Cells that are an event, or within h bars AFTER an event of that name."""
    excl = ev.copy()
    for k in range(1, h + 1):
        excl[k:] |= ev[:-k]
    return excl


def probe(open_, high, close, limits, horizons=HORIZONS, draws: int = DRAWS, seed: int = 0,
          min_pool: int = MIN_POOL, cost_per_side: float = COST_PER_SIDE,
          low=None, direction: str = "up"):
    ev = event_mask(open_, high, close, limits, low=low, direction=direction)
    n_events_total = int(ev.sum())
    rng = np.random.default_rng(seed)
    res = {"n_events_total": n_events_total, "n_bars": int(close.shape[0]),
           "n_symbols": int(close.shape[1]), "horizons": {}}
    for h in horizons:
        F = forward_matrix(open_, close, h)
        pool, n = pool_mean(F, min_pool)
        poolv = pool[:, None]
        with np.errstate(invalid="ignore"):
            ex = F - poolv
        usable = ev & np.isfinite(ex)
        n_ev = int(usable.sum())
        if n_ev == 0:
            res["horizons"][str(h)] = {"n_events": 0, "status": "no_usable_events"}
            continue
        per_event = ex[usable]
        gross = float(np.mean(per_event))
        cost = 2.0 * cost_per_side
        net = gross - cost
        # same-exposure null: same per-date event counts, cells far from any event
        excl = _adjacent_exclusion(ev, h)
        cand = np.isfinite(F) & ~excl
        ev_dates = np.flatnonzero(ev.any(axis=1))
        per_date_counts = [(t, int(usable[t].sum())) for t in ev_dates if usable[t].any()]
        null_means = np.empty(draws, dtype=np.float64)
        for d in range(draws):
            acc = 0.0
            cnt = 0
            for t, k in per_date_counts:
                row = np.flatnonzero(cand[t])
                if row.size == 0:
                    continue
                if row.size > k:
                    pick = rng.integers(0, row.size, size=k)
                elif row.size == k:
                    pick = rng.choice(row.size, size=k, replace=False)
                else:
                    # fewer candidate cells than events on this date (thin dates on
                    # the sell side): draw with replacement rather than raise -- the
                    # null is a mean of draws, not a set of distinct cells.
                    pick = rng.integers(0, row.size, size=k)
                acc += float(np.sum(ex[t, row[pick]]))
                cnt += k
            null_means[d] = acc / cnt if cnt else np.nan
        nm = null_means[np.isfinite(null_means)]
        null_mean = float(np.mean(nm)) if nm.size else float("nan")
        null_sd = float(np.std(nm, ddof=1)) if nm.size > 1 else float("nan")
        z = (gross - null_mean) / null_sd if null_sd and np.isfinite(null_sd) else float("nan")
        res["horizons"][str(h)] = {
            "n_events": n_ev,
            "excess_gross": gross,
            "excess_net": net,
            "cost_roundtrip": cost,
            "null_mean": null_mean,
            "null_sd": null_sd,
            "null_draws_used": int(nm.size),
            "z_vs_null": z,
            "ex_matched_exposure": gross - null_mean,
            "median_event_excess": float(np.median(per_event)),
            "share_events_positive": float(np.mean(per_event > 0)),
        }
    return res, ev


def per_year_reading(open_, high, close, limits, h: int, years, min_pool: int = MIN_POOL,
                     low=None, direction: str = "up"):
    F = forward_matrix(open_, close, h)
    pool, _ = pool_mean(F, min_pool)
    ev = event_mask(open_, high, close, limits, low=low, direction=direction)
    with np.errstate(invalid="ignore"):
        ex = F - pool[:, None]
    usable = ev & np.isfinite(ex)
    out = {}
    for y in sorted(set(years)):
        rows = np.array([i for i, yy in enumerate(years) if yy == y])
        sub = usable[rows]
        n = int(sub.sum())
        if n == 0:
            continue
        out[str(y)] = {"n_events": n, "excess_gross": float(np.mean(ex[rows][sub])),
                       "hit_rate": float(np.mean(ex[rows][sub] > 0))}
    return out


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _synth(nT=320, nS=60, seed=7, inject=False):
    """Hermetic panel. Sealed bars are marked explicitly so `high == close` there."""
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, 0.015, size=(nT, nS)).astype(np.float64)
    sealed = np.zeros((nT, nS), dtype=bool)
    if inject:
        for s in range(0, nS, 6):
            for t0 in (60, 140, 220):
                r[t0, s] = 0.10                      # the sealed limit-up bar
                r[t0 + 1:t0 + 21, s] += 0.012        # real continuation after it
                sealed[t0, s] = True
    close = 10.0 * np.cumprod(1.0 + r, axis=0)
    open_ = np.empty_like(close)
    open_[0] = 10.0
    open_[1:] = close[:-1] * (1.0 + rng.normal(0, 0.002, size=(nT - 1, nS)))
    high = np.maximum(open_, close) * 1.001      # a wick above every close ...
    high[sealed] = close[sealed]                 # ... except on a sealed bar
    limits = np.full(nS, 0.10, dtype=np.float32)
    return (open_.astype(np.float32), high.astype(np.float32),
            close.astype(np.float32), limits)


def selftest() -> int:
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "pass": bool(ok), "detail": detail})
        if not ok:
            fails.append(name)

    # L1 board limits
    leg("L1 board limit map", board_limit("300001") == 0.20 and board_limit("830001") == 0.30
        and board_limit("600000") == 0.10 and board_limit("688001") == 0.20)

    # L2 engineered panel must be admitted with a positive excess
    o, hi, c, lim = _synth(inject=True)
    res, ev = probe(o, hi, c, lim, horizons=(5,), draws=60, min_pool=10)
    h5 = res["horizons"]["5"]
    leg("L2 engineered limit-ups are found", res["n_events_total"] >= 30, f"n={res['n_events_total']}")
    leg("L2 engineered excess is positive and beats the null",
        h5["excess_net"] > 0 and h5["ex_matched_exposure"] > 0 and h5["z_vs_null"] > 2,
        f"net={h5['excess_net']:.4f} z={h5['z_vs_null']:.2f}")

    # L3 random walk must not be admitted
    o2, hi2, c2, lim2 = _synth(inject=False, seed=11)
    r2, ev2 = probe(o2, hi2, c2, lim2, horizons=(5,), draws=60, min_pool=10)
    h2 = r2["horizons"]["5"]
    leg("L3 random walk is not admitted",
        h2.get("status") == "no_usable_events" or
        not (h2["ex_matched_exposure"] > 0 and h2["z_vs_null"] > 2),
        f"ex={h2.get('ex_matched_exposure')} z={h2.get('z_vs_null')}")

    # L4 pool basis: vectorised pool mean reproduces a naive per-date loop
    F = forward_matrix(o2, c2, 5)
    pool, n = pool_mean(F, min_pool=10)
    t = int(np.argmax(n))
    naive = float(np.nanmean(F[t]))
    leg("L4 pool basis", abs(pool[t] - naive) < 1e-6, f"{pool[t]:.8f} vs {naive:.8f}")

    # L5 gaps are not zeros: a missing next-open must leave F NaN
    o3 = o2.copy()
    o3[10, 3] = np.nan
    F3 = forward_matrix(o3, c2, 5)
    leg("L5 missing bar is NaN, not 0", not np.isfinite(F3[9, 3]) and np.isfinite(F3[9, 4]))

    # L6 a +10% day with a high above the close is NOT a sealed event
    o4, hi4, c4, lim4 = _synth(inject=True)
    hi4 = hi4.copy()
    hi4[:, 0] = hi4[:, 0] * np.float32(1.05)
    ev4 = event_mask(o4, hi4, c4, lim4)
    leg("L6 sealing is required", int(ev4[:, 0].sum()) == 0 and int(ev4[:, 6].sum()) > 0,
        f"col0={int(ev4[:, 0].sum())} col6={int(ev4[:, 6].sum())}")

    passed = sum(1 for x in legs if x["pass"])
    print(json.dumps({"selftest": f"{passed}/{len(legs)}", "legs": legs}, ensure_ascii=False, indent=1))
    return 0 if not fails else 1


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--max-symbols", type=int, default=0)
    ap.add_argument("--draws", type=int, default=DRAWS)
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    t0 = time.time()
    panel = load_panel(max_symbols=(args.max_symbols or None))
    dates = panel["dates"]
    op, hi, cl = panel["open"], panel["high"], panel["close"]
    limits = limit_matrix(panel["symbols"])
    res, ev = probe(op, hi, cl, limits, draws=args.draws)
    years = [d[:4] for d in dates]
    for h in HORIZONS:
        res["horizons"][str(h)]["per_year"] = per_year_reading(op, hi, cl, limits, h, years)

    # the entry reality: the gap you pay to get in on a sealed bar
    prev = np.full_like(cl, np.nan)
    prev[1:] = cl[:-1]
    nxt = np.full_like(op, np.nan)
    nxt[:-1] = op[1:]
    with np.errstate(invalid="ignore", divide="ignore"):
        gap = nxt / prev - 1.0
    evg = ev & np.isfinite(gap)
    gap_stats = {"mean_gap": float(np.mean(gap[evg])) if evg.any() else None,
                 "median_gap": float(np.median(gap[evg])) if evg.any() else None,
                 "share_gap_above_5pct": float(np.mean(gap[evg] > 0.05)) if evg.any() else None,
                 "n": int(evg.sum())}

    h5 = res["horizons"].get("5", {})
    h10 = res["horizons"].get("10", {})
    h20 = res["horizons"].get("20", {})
    adm = []
    if h5.get("excess_net", -1) > 0 and h5.get("z_vs_null", 0) > 2:
        adm.append("h5")
    if h10.get("excess_net", -1) > 0 and h10.get("z_vs_null", 0) > 2:
        adm.append("h10")
    if h20.get("excess_net", -1) > 0 and h20.get("z_vs_null", 0) > 2:
        adm.append("h20")
    py5 = h5.get("per_year", {})
    pos_years = sum(1 for v in py5.values() if v["excess_gross"] > 0)
    majority = pos_years >= (len(py5) + 1) // 2 and len(py5) > 0
    verdict = "ADMIT_TO_PREREG" if (adm and majority) else "REFUSE_AS_CANDIDATE"

    out = {
        "artifact": "zoo91_limit_up_event supply berth probe",
        "batch": "SUPPLY_BERTH_EVENT_FAMILY_CANDIDATE",
        "family": "zoo91_limit_up_event",
        "machine": "bm-c",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": dates[-1] if dates else None,
        "panel": {"symbols": len(panel["symbols"]), "bars": len(dates),
                  "first_date": dates[0] if dates else None, "last_date": dates[-1] if dates else None},
        "construct": {
            "event": "close/prev_close-1 >= limit-0.005 AND close >= high-1e-9 (sealed at the close)",
            "board_limit": {"300/301/688/689": 0.20, "4/8/920": 0.30, "else": 0.10},
            "entry": "open[t+1] (the first bar you can actually buy)",
            "exit": "close[t+h], h in {5,10,20}",
            "benchmark": "cross-sectional mean of the same h-bar return on the same date",
            "excess": "per-event (F - pool) then averaged (date-neutral)",
            "null": "same per-date event counts drawn from cells that are neither an event nor within h bars after one",
            "cost_per_side": COST_PER_SIDE,
            "draws": args.draws,
        },
        "summary": res,
        "entry_gap": gap_stats,
        "verdict_block": {
            "verdict": verdict,
            "admitted_horizons": adm,
            "positive_years_h5": pos_years,
            "n_years_h5": len(py5),
            "reason": ("net excess beats a same-exposure null by >2 sd at an admitted horizon and the "
                       "year count is majority-positive" if verdict == "ADMIT_TO_PREREG" else
                       "either the net excess is not positive, or it does not clear a same-exposure "
                       "null by 2 sd, or the year split is not majority-positive"),
        },
        "honest": [
            "probe only: one construct, one sealing rule, three horizons -- a positive here buys a frozen prereg and a proper judge, not a claim that the rule makes money",
            "qfq panel: on an ex-rights bar the adjusted ratio is not the traded ratio, so a few limit-up bars near corporate actions are missed or mis-sealed; noise on the event SET, not look-ahead",
            "ST names trade at a 5% limit and are therefore never events here -- the reading covers the non-ST tape only",
            "events cluster: 200 independent draws of the same per-date counts give the sampling spread of the null, but consecutive events in one name are not independent; the per-year split is the honest companion reading",
            "the benchmark is the equal-weight A-share panel on the same date, so any excess is relative to 'own the tape', which is itself a claim that has to be cashed later",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"artifact": out["artifact"], "verdict": verdict, "admitted": adm,
                      "panel": out["panel"], "h5": {k: h5.get(k) for k in
                      ("n_events", "excess_gross", "excess_net", "null_mean", "null_sd", "z_vs_null")},
                      "entry_gap": gap_stats, "secs": round(time.time() - t0, 1)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())