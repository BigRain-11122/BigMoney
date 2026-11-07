#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""zoo92_limit_down_event -- supply berth probe, the SELL side of the same clock.

WHY THIS FILE EXISTS
--------------------
r1391 (zoo91) tested the buy side of the forced-trade clock: a bar sealed at the
board ceiling forces the name to trade at the next open, and the reading was that
the premium is *paid at that open* (median gap +12.29%, 97.2% of events open more
than 5% higher), so following the event loses -1.18pp/yr after cost.  The axis
that round named as the next berth was the other side: the event that forces a
name to be SOLD.

    does a bar sealed at the FLOOR -- close == low at the board limit, i.e. the
    sellers could not get out today -- carry information for someone who BUYS at
    the next open, beyond a same-exposure null on the same date?

The two sides are not mirror images by construction.  On the up side the queue is
of buyers who were refused, and they pay the gap.  On the down side the queue is
of sellers who were refused; whoever steps in at the next open is being offered
the paper at (presumably) a discount, and the question is whether that discount
is an overreaction or the first leg of a decline.

Everything here is a PROBE, sharing zoo91's panel reader, forward-return
matrix, pool benchmark, adjacency exclusion and null machinery -- the *only*
thing that differs is the event mask (zoo91.event_mask(..., direction="down")).
Carbon-copying that machinery into a second file is exactly the E289 defect.

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  panel      data/astock_daily/per/<sym>.csv (qfq, forward-accumulated), >= 2020-01-01
  event      bar t with close[t]/close[t-1]-1 <= -(LIMIT-0.005) AND close[t] <= low[t] + 1e-9
  board      prefix 300/301/688/689 -> 0.20; 4/8/920 -> 0.30; else 0.10
  entry      open[t+1] -- the first bar you could actually buy
  exit       close[t+h], h in {5, 10, 20}
  benchmark  cross-sectional mean of the same h-bar return on the same date t
  excess     per-event (F[t,s] - pool[t]) averaged (date-neutral)
  null       K draws of the same per-date event counts from cells that are
             neither an event nor within h bars AFTER one of the same name
  cost       2 x COST_X1_RATE
  qfq caveat as zoo91: ex-rights bars can move the sealing test; noise on the
             event SET, not look-ahead, disclosed rather than patched.
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
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import zoo91_limit_up_event_probe as z91  # one implementation of panel/null/engine

OUT = os.path.join(ROOT, "results", "supply_berth", "zoo92_limit_down_event_probe.json")
HORIZONS = z91.HORIZONS
DRAWS = z91.DRAWS
COST_PER_SIDE = z91.COST_PER_SIDE
MIN_POOL = z91.MIN_POOL


# --------------------------------------------------------------------------- #
# selftest fixtures
# --------------------------------------------------------------------------- #
def _synth_down(nT=320, nS=60, seed=7, inject=False):
    """Hermetic panel where sealed FLOOR bars have low == close."""
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, 0.015, size=(nT, nS)).astype(np.float64)
    sealed = np.zeros((nT, nS), dtype=bool)
    if inject:
        for s in range(0, nS, 6):
            for t0 in (60, 140, 220):
                r[t0, s] = -0.10                      # the sealed limit-down bar
                r[t0 + 1:t0 + 21, s] += 0.012         # real bounce after it
                sealed[t0, s] = True
    close = 10.0 * np.cumprod(1.0 + r, axis=0)
    open_ = np.empty_like(close)
    open_[0] = 10.0
    open_[1:] = close[:-1] * (1.0 + rng.normal(0, 0.002, size=(nT - 1, nS)))
    high = np.maximum(open_, close) * 1.001
    low = np.minimum(open_, close) * 0.999       # a wick below every close ...
    low[sealed] = close[sealed]                  # ... except on a sealed bar
    limits = np.full(nS, 0.10, dtype=np.float32)
    return (open_.astype(np.float32), high.astype(np.float32),
            low.astype(np.float32), close.astype(np.float32), limits)


def selftest() -> int:
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "pass": bool(ok), "detail": detail})
        if not ok:
            fails.append(name)

    leg("L1 board limit map (shared with zoo91)",
        z91.board_limit("300001") == 0.20 and z91.board_limit("830001") == 0.30
        and z91.board_limit("600000") == 0.10 and z91.board_limit("688001") == 0.20)

    o, hi, lo, c, lim = _synth_down(inject=True)
    res, ev = z91.probe(o, hi, c, lim, horizons=(5,), draws=60, min_pool=10,
                        low=lo, direction="down")
    h5 = res["horizons"]["5"]
    leg("L2 engineered sealed floors are found", res["n_events_total"] >= 30,
        f"n={res['n_events_total']}")
    leg("L2 engineered bounce is positive and beats the null",
        h5["excess_net"] > 0 and h5["ex_matched_exposure"] > 0 and h5["z_vs_null"] > 2,
        f"net={h5['excess_net']:.4f} z={h5['z_vs_null']:.2f}")

    o2, hi2, lo2, c2, lim2 = _synth_down(inject=False, seed=11)
    r2, _ = z91.probe(o2, hi2, c2, lim2, horizons=(5,), draws=60, min_pool=10,
                      low=lo2, direction="down")
    h2 = r2["horizons"]["5"]
    leg("L3 random walk is not admitted",
        h2.get("status") == "no_usable_events" or
        not (h2["ex_matched_exposure"] > 0 and h2["z_vs_null"] > 2),
        f"ex={h2.get('ex_matched_exposure')} z={h2.get('z_vs_null')}")

    # L4 the down mask is not the up mask: the same engineered panel read as "up"
    # must find (almost) nothing, otherwise the direction switch is decorative.
    up_res, _ = z91.probe(o, hi, c, lim, horizons=(5,), draws=10, min_pool=10)
    leg("L4 direction switch is real", up_res["n_events_total"] < res["n_events_total"] * 0.2,
        f"up={up_res['n_events_total']} down={res['n_events_total']}")

    # L5 a floor that was touched but NOT sealed (close above the low) is not an event
    lo3 = lo.copy()
    lo3[:, 6] = lo3[:, 6] * np.float32(0.95)
    ev3 = z91.event_mask(o, hi, c, lim, low=lo3, direction="down")
    leg("L5 sealing is required on the down side",
        int(ev3[:, 6].sum()) == 0 and int(ev3[:, 0].sum()) > 0,
        f"col6={int(ev3[:, 6].sum())} col0={int(ev3[:, 0].sum())}")

    # L6 a missing next-open must leave the forward return NaN, never 0%
    o4 = o2.copy()
    o4[10, 3] = np.nan
    F4 = z91.forward_matrix(o4, c2, 5)
    leg("L6 missing bar is NaN, not 0", not np.isfinite(F4[9, 3]) and np.isfinite(F4[9, 4]))

    passed = sum(1 for x in legs if x["pass"])
    print(json.dumps({"selftest": f"{passed}/{len(legs)}", "legs": legs},
                     ensure_ascii=False, indent=1))
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
    panel = z91.load_panel(max_symbols=(args.max_symbols or None))
    dates = panel["dates"]
    op, hi, lo, cl = panel["open"], panel["high"], panel["low"], panel["close"]
    limits = z91.limit_matrix(panel["symbols"])
    res, ev = z91.probe(op, hi, cl, limits, draws=args.draws, low=lo, direction="down")
    years = [d[:4] for d in dates]
    for h in HORIZONS:
        res["horizons"][str(h)]["per_year"] = z91.per_year_reading(
            op, hi, cl, limits, h, years, low=lo, direction="down")

    # the entry reality: the discount you are handed at the next open
    prev = np.full_like(cl, np.nan)
    prev[1:] = cl[:-1]
    nxt = np.full_like(op, np.nan)
    nxt[:-1] = op[1:]
    with np.errstate(invalid="ignore", divide="ignore"):
        gap = nxt / prev - 1.0
    evg = ev & np.isfinite(gap)
    gap_stats = {"mean_gap": float(np.mean(gap[evg])) if evg.any() else None,
                 "median_gap": float(np.median(gap[evg])) if evg.any() else None,
                 "share_gap_below_minus5pct": float(np.mean(gap[evg] < -0.05)) if evg.any() else None,
                 "n": int(evg.sum())}

    h5 = res["horizons"].get("5", {})
    h10 = res["horizons"].get("10", {})
    h20 = res["horizons"].get("20", {})
    adm = [f"h{k}" for k, v in (("5", h5), ("10", h10), ("20", h20))
           if v.get("excess_net", -1) > 0 and v.get("z_vs_null", 0) > 2]
    py5 = h5.get("per_year", {})
    pos_years = sum(1 for v in py5.values() if v["excess_gross"] > 0)
    majority = pos_years >= (len(py5) + 1) // 2 and len(py5) > 0
    verdict = "ADMIT_TO_PREREG" if (adm and majority) else "REFUSE_AS_CANDIDATE"

    out = {
        "artifact": "zoo92_limit_down_event supply berth probe (sell side of the forced-trade clock)",
        "batch": "SUPPLY_BERTH_EVENT_FAMILY_CANDIDATE",
        "family": "zoo92_limit_down_event",
        "machine": "bm-c",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": dates[-1] if dates else None,
        "panel": {"symbols": len(panel["symbols"]), "bars": len(dates),
                  "first_date": dates[0] if dates else None, "last_date": dates[-1] if dates else None},
        "construct": {
            "event": "close/prev_close-1 <= -(limit-0.005) AND close <= low+1e-9 (sealed at the floor)",
            "board_limit": {"300/301/688/689": 0.20, "4/8/920": 0.30, "else": 0.10},
            "entry": "open[t+1] (the first bar you can actually buy)",
            "exit": "close[t+h], h in {5,10,20}",
            "benchmark": "cross-sectional mean of the same h-bar return on the same date",
            "excess": "per-event (F - pool) then averaged (date-neutral)",
            "null": "same per-date event counts drawn from cells that are neither an event nor within h bars after one",
            "cost_per_side": COST_PER_SIDE,
            "draws": args.draws,
            "engine": "zoo91_limit_up_event_probe (panel reader / forward matrix / pool / null reused verbatim)",
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
            "the down-side event is rarer than the up side in this panel, so the per-horizon sample is smaller; the null spread is reported beside every headline for that reason",
            "qfq panel: on an ex-rights bar the adjusted ratio is not the traded ratio, so a few floor bars near corporate actions are missed or mis-sealed; noise on the event SET, not look-ahead",
            "ST names trade at a 5% limit and are therefore never events here -- the reading covers the non-ST tape only",
            "buying a sealed floor is buying into a refused-seller queue: the fill assumption (next open, 2 x 13.041bp) ignores that the open itself can be a gap-down with no size, which is a liquidity claim this probe cannot test",
            "the benchmark is the equal-weight A-share panel on the same date, so any excess is relative to 'own the tape'",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"artifact": out["artifact"], "verdict": verdict, "admitted": adm,
                      "panel": out["panel"],
                      "h5": {k: h5.get(k) for k in ("n_events", "excess_gross", "excess_net",
                                                    "null_mean", "null_sd", "z_vs_null")},
                      "h10_net": h10.get("excess_net"), "h20_net": h20.get("excess_net"),
                      "entry_gap": gap_stats, "secs": round(time.time() - t0, 1)},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())