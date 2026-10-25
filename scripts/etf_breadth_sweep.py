"""Breadth as its own axis: which name count buys the most capacity per unit of return given up.

r1262 measured a single point -- 5 names vs 8 names, flat vs 10/50/100M -- and had to
report that widening 5 -> 8 costs 0.74pp of return while buying 36% of capacity. One
point cannot answer "what is the right width", so this face is a sweep:

    breadth  in {5, 8, 12, 16}
    structure in {single, staggered}        (staggered = two sleeves of N//2, phased R//2)

and for every cell it records the return leg (flat 8bp + participation-priced at
10M/50M/100M), the turnover that drives the cost, the p90 single-session participation,
and the capacity implied by the 1%-ADV discipline. Everything is derived per line from
its own measured p90 -- nothing is inherited from a neighbouring row, which is exactly
the mistake r1261 made when it graded a staggered 8-name book against a 5-name
reference.

The output number that answers the question is `capacity_per_pp_sacrificed`: capacity
gained relative to the 5-name book, divided by the CAGR given up relative to it. A cell
whose return does not fall is reported as unbounded rather than divided by zero.

What is reused, never rewritten:
  * selection / fills / leg maths = `F.run_next_open` (r1250 next-open basis);
  * the score face                = `F.build_score`;
  * the participation cost        = `ImpactCost` from scripts/etf_book_capacity.py (r1260);
  * the stagger machinery         = `top_slice` / `blend` / `phase_start` /
                                    `turns_per_year` from scripts/etf_book_turnover.py
                                    (r1262), imported so the two faces cannot drift.

Honest limits stated up front:
  * exploratory: no preregistration, no verdict, no ledger booking, no admission;
  * the staggered blend assumes a daily rebalance between sleeves (weights 50/50 by
    construction) -- an approximation shared with the single-sleeve book, not a fill model;
  * breadth and phasing are both priced off the same score face, so this says nothing
    about whether a *different* face would support more names;
  * the ETF universe is today's surviving set (survivorship caveat carried from r1249).

  python scripts/etf_breadth_sweep.py run [--out=...]
  python scripts/etf_breadth_sweep.py --selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F
from scripts.etf_book_capacity import BASE_BP, IMPACT_BP_PER_PCT, ImpactCost
from scripts.etf_book_turnover import blend, phase_start, top_slice, turns_per_year

BREADTH_GRID = (5, 8, 12, 16)
NAV_GRID = (1e7, 5e7, 1e8)
REBAL = 20
START = "2020-01-01"
REF_BREADTH = BREADTH_GRID[0]
ADV_DISCIPLINE_PCT = 1.0


def capacity_from_p90(ref_nav, p90):
    """NAV at which p90 single-session participation hits the ADV discipline.

    p = |dw| * NAV / ADV is linear in NAV, so this is exact algebra given a measured
    p90 -- and because it is computed per line, a breadth or phasing change can never
    inherit a neighbour's capacity figure.
    """
    if not p90:
        return None
    return round(ref_nav * (ADV_DISCIPLINE_PCT / 100.0) / p90)


def eff(cap_new, cap_ref, cagr_new, cagr_ref):
    """Capacity gained per pp of CAGR given up, relative to the reference breadth.

    Returns (delta_capacity_pct, cagr_given_up_pp, capacity_per_pp_sacrificed). When the
    wider book does not give up return, `capacity_per_pp_sacrificed` is None (infinite):
    the honest reading there is "free capacity", not a huge ratio.
    """
    if cap_new is None or cap_ref is None:
        return None, None, None
    d_cap_pct = round(100.0 * (cap_new / cap_ref - 1.0), 1)
    if cagr_new is None or cagr_ref is None:
        return d_cap_pct, None, None
    given_up = round(100.0 * (cagr_ref - cagr_new), 3)
    if given_up <= 0.0:
        return d_cap_pct, given_up, None
    return d_cap_pct, given_up, round(d_cap_pct / given_up, 2)


def _priced(close, openp, amt, feats, nav, score, n_hold, start=START):
    cm = ImpactCost(amt, nav)
    ser, turn, gap = F.run_next_open(close, openp, amt, feats, REBAL, n_hold=n_hold,
                                     cost=cm, start=start, score=score)
    m = F.metrics(ser, "nav=%.0e n=%d" % (nav, n_hold))
    pmax = pd.Series([r["participation_max"] for r in cm.rows
                      if r["participation_max"] is not None])
    m.update({
        "turnover_per_decision": round(turn, 4),
        "turns_per_year": turns_per_year(turn, REBAL),
        "open_gapfill": gap,
        "missing_adv_legs": cm.missing_names,
        "participation_max_p90": round(float(pmax.quantile(0.9)), 6) if len(pmax) else None,
        "decisions_over_1pct": int((pmax > 0.01).sum()) if len(pmax) else 0,
    })
    return m, ser, cm


def _stagger(close, openp, amt, feats, nav, score, n, priced=True):
    """Two n/2 sleeves phased half a period; each sleeve carries half the capital.

    A sleeve's cost is the SAME cost object the single-sleeve line would use at the
    matching NAV -- F.COST for the flat 8bp leg, ImpactCost(nav/2) for the priced leg.
    Grading a staggered book on participation-priced cost while its reference sits on
    flat 8bp (or vice versa) is the r1261 mistake in another costume.
    """
    half = n // 2
    lo_a, hi_a = 1, half
    lo_b, hi_b = half + 1, n
    off = REBAL // 2
    st_b = phase_start(close.index, START, off)
    if st_b is None:
        return None

    def one(score_slice, start):
        cm = ImpactCost(amt, nav * 0.5) if priced else F.COST
        ser, turn, gap = F.run_next_open(close, openp, amt, feats, REBAL, n_hold=half,
                                        cost=cm, start=start, score=score_slice)
        pmax = None
        if priced:
            pmax = pd.Series([r["participation_max"] for r in cm.rows
                              if r["participation_max"] is not None])
        return ser, turn, gap, cm, pmax

    ser_a, ta, gap_a, cm_a, pmax_a = one(top_slice(score, lo_a, hi_a), START)
    ser_b, tb, gap_b, cm_b, pmax_b = one(top_slice(score, lo_b, hi_b), st_b)
    blended = blend([ser_a, ser_b])
    m = F.metrics(blended, "stagger nav=%.0e n=%d" % (nav, n))
    turn = 0.5 * (ta + tb)
    m.update({
        "turnover_per_decision": round(turn, 4),
        "turns_per_year": turns_per_year(turn, REBAL),
        "open_gapfill": gap_a + gap_b,
        "missing_adv_legs": (cm_a.missing_names + cm_b.missing_names) if priced else 0,
        "sleeve_turnover_per_decision": {"a": round(ta, 4), "b": round(tb, 4)},
        "sleeve_b_start": str(pd.Timestamp(st_b).date()),
    })
    if priced:
        pmax = pd.concat([pmax_a, pmax_b])
        m.update({
            "participation_max_p90": round(float(pmax.quantile(0.9)), 6) if len(pmax) else None,
            "decisions_over_1pct": int((pmax > 0.01).sum()) if len(pmax) else 0,
        })
    return m


def run(start=START):
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    mkt = F.bench_series(close, start)
    mkt_m = F.metrics(mkt, "510300") if mkt is not None else None
    ew = F.metrics(F.run_ew(close, amt, REBAL, start=start), "ew rebal=%d" % REBAL)

    ref_nav = float(min(NAV_GRID))
    rows = []
    for n in BREADTH_GRID:
        print("[breadth] n=%d single" % n, flush=True)
        ser_s, turn_s, gap_s = F.run_next_open(close, openp, amt, feats, REBAL,
                                              n_hold=n, cost=F.COST, start=start,
                                              score=score)
        ms = F.metrics(ser_s, "single flat n=%d" % n)
        row = {
            "breadth": n,
            "single": {
                "flat_8bp": dict(ms,
                                 turnover_per_decision=round(turn_s, 4),
                                 turns_per_year=turns_per_year(turn_s, REBAL),
                                 open_gapfill=gap_s,
                                 excess_vs_ew_pp=(None if (ms.get("cagr") is None
                                                           or ew.get("cagr") is None) else
                                                  round(100.0 * (ms["cagr"] - ew["cagr"]), 3))),
                "priced": {},
            },
            "staggered": None,
        }
        for nav in NAV_GRID:
            m, _s, _c = _priced(close, openp, amt, feats, nav, score, n)
            m["excess_vs_ew_pp"] = (None if (m.get("cagr") is None or ew.get("cagr") is None)
                                    else round(100.0 * (m["cagr"] - ew["cagr"]), 3))
            row["single"]["priced"]["%.0e" % nav] = m
        if n % 2 == 0:
            print("[breadth] n=%d staggered" % n, flush=True)
            st_flat = _stagger(close, openp, amt, feats, ref_nav, score, n, priced=False)
            st = {"sleeve_top": n // 2, "phase_offset_bars": REBAL // 2,
                  "flat_8bp": st_flat, "priced": {}}
            if st_flat:
                st_flat["excess_vs_ew_pp"] = (
                    None if st_flat.get("cagr") is None else
                    round(100.0 * (st_flat["cagr"] - ew["cagr"]), 3))
            for nav in NAV_GRID:
                st["priced"]["%.0e" % nav] = _stagger(close, openp, amt, feats, nav, score, n)
            row["staggered"] = st
        rows.append(row)

    # ---- the answer surface: capacity per pp of return given up, at the ref NAV ----
    ref_key = "%.0e" % ref_nav
    base = next(r for r in rows if r["breadth"] == REF_BREADTH)
    base_cap_single = capacity_from_p90(
        ref_nav, (base["single"]["priced"][ref_key] or {}).get("participation_max_p90"))
    base_cagr_single = (base["single"]["priced"][ref_key] or {}).get("cagr")

    surface = []
    for r in rows:
        for struct in ("single", "staggered"):
            blk = r[struct]
            if not blk:
                continue
            p = (blk["priced"].get(ref_key) or {})
            flat = blk.get("flat_8bp") or {}
            cap = capacity_from_p90(ref_nav, p.get("participation_max_p90"))
            d_cap, given_up, per_pp = eff(cap, base_cap_single,
                                          p.get("cagr"), base_cagr_single)
            surface.append({
                "breadth": r["breadth"],
                "structure": struct,
                "flat_cagr": flat.get("cagr"),
                "priced_cagr": p.get("cagr"),
                "sharpe": p.get("sharpe"),
                "max_dd": p.get("maxdd"),
                "turns_per_year": p.get("turns_per_year"),
                "p90_participation": p.get("participation_max_p90"),
                "decisions_over_1pct": p.get("decisions_over_1pct"),
                "capacity_nav": cap,
                "delta_capacity_pct_vs_ref": d_cap,
                "cagr_sacrificed_pp_vs_ref": given_up,
                "capacity_pct_per_pp_sacrificed": per_pp,
            })

    ex = [s for s in surface if s["capacity_pct_per_pp_sacrificed"] is not None]
    best = max(ex, key=lambda s: s["capacity_pct_per_pp_sacrificed"]) if ex else None
    best_free = [s for s in surface if s["cagr_sacrificed_pp_vs_ref"] is not None
                 and s["cagr_sacrificed_pp_vs_ref"] <= 0
                 and (s["delta_capacity_pct_vs_ref"] or 0) > 0]

    # where does each wider/staggered line overtake the narrow reference? A width that
    # loses at 10M and wins at 100M is the interesting case -- it means the cost decay
    # from spreading outweighs the signal decay from going deeper.
    crossovers = {}
    for r in rows:
        for struct in ("single", "staggered"):
            blk = r[struct]
            if not blk or (r["breadth"] == REF_BREADTH and struct == "single"):
                continue
            x = crossover_nav(base["single"]["priced"], blk["priced"], NAV_GRID)
            crossovers["n%d_%s" % (r["breadth"], struct)] = x

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_breadth_sweep.py",
        "config": {"breadth_grid": list(BREADTH_GRID), "rebal": REBAL,
                   "nav_grid": list(NAV_GRID), "base_bp": BASE_BP,
                   "impact_bp_per_pct": IMPACT_BP_PER_PCT,
                   "adv_discipline_pct": ADV_DISCIPLINE_PCT,
                   "reference_breadth": REF_BREADTH, "start": start},
        "market_510300": mkt_m,
        "pool_equal_weight": ew,
        "rows": rows,
        "surface": surface,
        "readings": {
            "best_capacity_per_pp": best,
            "free_capacity_cells": [{"breadth": s["breadth"], "structure": s["structure"],
                                     "delta_capacity_pct": s["delta_capacity_pct_vs_ref"],
                                     "cagr_sacrificed_pp": s["cagr_sacrificed_pp_vs_ref"]}
                                    for s in best_free],
            "reference_capacity_nav": base_cap_single,
            "crossover_nav_vs_ref": crossovers,
            "crossover_method": "linear in NAV between grid brackets, on priced CAGR",
        },
    }
    return out


def crossover_nav(ref_priced, other_priced, naves):
    """NAV at which `other` overtakes `ref` on CAGR, interpolated between grid points.

    Interpolation is linear in NAV (not in log NAV) because participation cost is linear
    in NAV: p = |dw| * NAV / ADV. It is a bracket estimate, not a fitted model, and
    returns None when the two lines do not change order anywhere on the grid.
    """
    pts = []
    for nav in naves:
        key = "%.0e" % nav
        a = (ref_priced.get(key) or {}).get("cagr")
        b = (other_priced.get(key) or {}).get("cagr")
        if a is None or b is None:
            continue
        pts.append((nav, b - a))
    for (n1, d1), (n2, d2) in zip(pts, pts[1:]):
        if d1 == 0 or d2 == 0:
            continue
        if (d1 < 0) != (d2 < 0):
            return round(n1 + (n2 - n1) * (d1 / (d1 - d2)))
    return None


def _synthetic_check():
    """Hand-checkable fixture for eff()/capacity_from_p90 used by the selftest legs."""
    cap5 = capacity_from_p90(1e7, 0.1063)          # ~941k, reproduces r1260's 94 wan
    cap8 = capacity_from_p90(1e7, 0.0780)          # ~1.282M
    return cap5, cap8, eff(cap8, cap5, 0.0688, 0.0762)


def selftest():
    fails = []
    ran = []

    def check(name, cond, detail=""):
        ran.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1: the grid is strictly increasing and the reference is its floor -- the surface
    # is meaningless if the baseline is not the narrowest book.
    check("L1a", list(BREADTH_GRID) == sorted(BREADTH_GRID) and len(set(BREADTH_GRID)) == len(BREADTH_GRID))
    check("L1b", REF_BREADTH == BREADTH_GRID[0])

    # L2: capacity is its own line's p90, never a neighbour's. Two different p90s must
    # give two different capacities, and the arithmetic must be exact.
    check("L2a", capacity_from_p90(1e7, 0.1063) == round(1e7 * 0.01 / 0.1063))
    check("L2b", capacity_from_p90(1e7, None) is None)
    c_small = capacity_from_p90(1e7, 0.20)
    c_large = capacity_from_p90(1e7, 0.05)
    check("L2c", c_large == 4 * c_small, "%s vs %s" % (c_large, c_small))
    # a zero/None p90 must not silently become infinite capacity
    check("L2d", capacity_from_p90(1e7, 0.0) is None)

    # L3: the efficiency ratio -- capacity gained divided by CAGR given up.
    cap5, cap8, (d_cap, given_up, per_pp) = _synthetic_check()
    # 10M * 1% / 10.63% = 941k reproduces r1260's published 94 wan capacity exactly
    check("L3a", cap5 == round(1e7 * 0.01 / 0.1063) == 940734, "cap5=%s" % cap5)
    check("L3b", d_cap == round(100.0 * (cap8 / cap5 - 1.0), 1))
    check("L3c", given_up == round(100.0 * (0.0762 - 0.0688), 3))
    check("L3d", per_pp == round(d_cap / given_up, 2))
    # r1262's published pair (5 names 7.62%, 8 names 6.88%, +36% capacity) must land in
    # the same shape, so the surface is graded on the same arithmetic the prose used
    d2, g2, p2 = eff(cap8, cap5, 0.0688, 0.0762)
    check("L3e", d2 > 0 and g2 > 0 and p2 == round(d2 / g2, 2))
    # a wider book that does NOT give up return must be reported as free capacity, not
    # divided by zero into an absurd ratio
    d3, g3, p3 = eff(cap8, cap5, 0.0800, 0.0762)
    check("L3f", g3 <= 0 and p3 is None, "given_up=%s per_pp=%s" % (g3, p3))

    # L4: missing legs degrade to None instead of raising or inventing a number
    check("L4a", eff(None, cap5, 0.05, 0.07) == (None, None, None))
    check("L4b", eff(cap8, None, 0.05, 0.07) == (None, None, None))
    check("L4c", eff(cap8, cap5, None, 0.07)[2] is None)

    # L5: the stagger machinery imported from r1262 must still partition the top-N, so
    # this face cannot be built on a broken split.
    cols = ["s%02d" % i for i in range(24)]
    rows = pd.bdate_range("2021-01-01", periods=5)
    rng = np.random.RandomState(13)
    sc = pd.DataFrame(rng.rand(5, 24), index=rows, columns=cols)
    for n in [x for x in BREADTH_GRID if x % 2 == 0]:
        half = n // 2
        a = top_slice(sc, 1, half)
        b = top_slice(sc, half + 1, n)
        check("L5_%d_a" % n, int((a.notna() & b.notna()).sum().sum()) == 0)
        ref = sc.rank(axis=1, ascending=False, method="first") <= n
        check("L5_%d_b" % n, bool(((a.notna() | b.notna()) == ref).all().all()))
        check("L5_%d_c" % n, int(a.notna().sum(axis=1).min()) == half)

    # L6: phase_start still hands back a bar offset (the stagger clock) and refuses
    # offsets past the end, so a short panel degrades honestly.
    idx = pd.bdate_range("2020-01-01", periods=60)
    check("L6a", phase_start(idx, "2020-01-01", REBAL // 2) == idx[REBAL // 2])
    check("L6b", phase_start(idx, "2020-01-01", 9999) is None)

    # L7: the blend of two identical sleeves is the sleeve (imported behaviour must not
    # have drifted, else every staggered row is mispriced).
    d = pd.bdate_range("2022-01-03", periods=40)
    r = pd.Series(rng.randn(40) * 0.01, index=d)
    one = (1.0 + r).cumprod()
    one.iloc[0] = 1.0
    check("L7a", np.allclose(blend([one, one]).values, one.values, atol=1e-12))

    # L8: the stagger legs must be cost-matched, not just breadth-matched. A staggered
    # book graded on participation cost while its reference sits on flat 8bp produces a
    # number that looks like phasing but is really cost -- the r1261 error in a new
    # costume. Functional proof: on a panel whose ADV is far too small for the NAV, the
    # priced stagger must come in strictly below the flat stagger.
    n_bars2, n_names2 = 200, 12
    d2idx = pd.bdate_range("2020-01-01", periods=n_bars2)
    p2 = np.random.RandomState(23)
    px2 = pd.DataFrame(100.0 * np.exp(np.cumsum(p2.randn(n_bars2, n_names2) * 0.01, axis=0)),
                       index=d2idx, columns=cols[:n_names2])
    op2 = px2.shift(1).fillna(px2.iloc[0])
    amt2 = pd.DataFrame(1e6, index=d2idx, columns=cols[:n_names2])
    feats2 = {"mom_12_1": px2}
    sc2 = px2.pct_change(120)
    st_flat_m = _stagger(px2, op2, amt2, feats2, 1e7, sc2, 8, priced=False)
    st_pr_m = _stagger(px2, op2, amt2, feats2, 1e7, sc2, 8, priced=True)
    check("L8a", st_flat_m is not None and st_pr_m is not None)
    check("L8b", "participation_max_p90" not in st_flat_m, "flat leg leaked a priced field")
    check("L8c", st_pr_m.get("participation_max_p90") is not None)
    check("L8d", st_flat_m["cagr"] > st_pr_m["cagr"], "flat=%s priced=%s"
          % (st_flat_m["cagr"], st_pr_m["cagr"]))
    # and the flat stagger's turnover must still be a real number, i.e. the book traded
    check("L8e", st_flat_m["turnover_per_decision"] > 0.0,
          "turn=%.4f" % st_flat_m["turnover_per_decision"])

    # L9: the crossover bracket. A wider book that loses at 10M and wins at 100M must
    # return an interpolated NAV inside that bracket; one that never changes order must
    # return None rather than the edge of the grid.
    ref_p = {"1e+07": {"cagr": 0.0558}, "5e+07": {"cagr": 0.0311}, "1e+08": {"cagr": 0.0129}}
    wide = {"1e+07": {"cagr": 0.0509}, "5e+07": {"cagr": 0.0348}, "1e+08": {"cagr": 0.0228}}
    x = crossover_nav(ref_p, wide, NAV_GRID)
    check("L9a", x is not None and 1e7 < x < 5e7, "x=%s" % x)
    # hand-checkable: d1 = 5.09-5.58 = -0.49pp, d2 = 3.48-3.11 = +0.37pp
    check("L9b", x == round(1e7 + 4e7 * (-0.49 / (-0.49 - 0.37))), "x=%s" % x)
    always = {"1e+07": {"cagr": 0.01}, "5e+07": {"cagr": 0.01}, "1e+08": {"cagr": 0.01}}
    check("L9c", crossover_nav(ref_p, always, NAV_GRID) is None)
    check("L9d", crossover_nav(ref_p, {"1e+07": {"cagr": None}}, NAV_GRID) is None)

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("selftest %d/%d PASS" % (len(ran), len(ran)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    out = run()
    path = args.out or os.path.join(PATHS.results_dir, "etf_breadth_sweep.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", path)
    print("cutoff", out["evidence_cutoff"])
    for s in out["surface"]:
        print("n=%-2d %-9s flat %6.2f%% priced %6.2f%% cap %8s dcap %+6s%% "
              "givenup %+6spp per-pp %s" % (
                  s["breadth"], s["structure"],
                  100 * (s["flat_cagr"] or 0), 100 * (s["priced_cagr"] or 0),
                  s["capacity_nav"], s["delta_capacity_pct_vs_ref"],
                  s["cagr_sacrificed_pp_vs_ref"], s["capacity_pct_per_pp_sacrificed"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())