"""Breadth as its own axis: how wide should this ETF book be?  [CROSS-CHECK ARM]

ROLE NOTE (2026-10-25 r1263): this file was written before the parallel executor's
`scripts/etf_breadth_sweep.py` was discovered in the same worktree, so it is NOT a
planned independent replication -- it is a duplicate build that is being kept for the
one thing it now provides: a second, independently written implementation of the same
surface (flat 8bp + p90 capacity). The two agree exactly on the flat arm (5/8/12/16 =
7.62/6.88/6.41/5.15 %/yr) and on every capacity cell (941k/1.283M/1.845M/2.387M);
`etf_breadth_sweep.py` is the primary face (it also prices 10M/50M/100M and solves the
crossover NAV), and this arm contributes the stagger-vs-single deltas at 12 and 16
names, which the primary face does not tabulate. Do not extend both -- extend the
primary face.

Original description follows.

Breadth as its own axis: how wide should this ETF book be?

r1262 answered the cadence question and, while correcting the r1261 stagger mistake,
found that widening the book 5 -> 8 names buys +36% of capacity but costs 0.74pp of
return. That is one point on a curve, and a book with one point cannot say where the
curve turns. This script sweeps width directly:

  * WIDTH      N in (5, 8, 12, 16) names, one sleeve, flat 8bp;
  * PHASING    the same N split into two sleeves half-names-each, the second sleeve
               clocked half a period late (reuses the r1262 stagger construction);
  * CAPACITY   each line is run once at a reference NAV through the r1260
               participation cost, and capacity is derived from its own p90
               participation under a 1%-of-ADV discipline: NAV_ref * 1% / p90.

The output is a width x phasing surface of (return, capacity) plus the trade rate
that sits behind both -- capacity bought per pp of return given up, relative to the
narrow 5-name book.

What is reused, never rewritten:
  * selection / fills / leg maths   = `F.run_next_open` (r1250 next-open basis);
  * score face and panel            = `F.build_score` / `F.build_panel`;
  * participation cost              = `ImpactCost` (scripts/etf_book_capacity.py, r1260);
  * sleeve split, phase shift, blend = `top_slice` / `phase_start` / `blend`
    (scripts/etf_book_turnover.py, r1262) -- the same code that produced the
    matched-breadth stagger number, so this sweep cannot drift from it.

Honest limits:
  * costs are the flat 8bp interior; the priced arm exists only to measure
    participation for the capacity column, not to price the return column;
  * capacity is a participation discipline, not a fills model: it says "at what NAV
    would p90 single-day participation reach 1% of that name's 20d turnover";
  * exploratory: no preregistration, no verdict, no ledger booking, +0 marks.

  python scripts/etf_book_breadth.py run [--out=...]
  python scripts/etf_book_breadth.py --selftest
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F
from scripts.etf_book_capacity import ImpactCost
from scripts.etf_book_turnover import blend, phase_start, top_slice, turns_per_year

BREADTH_GRID = (5, 8, 12, 16)
STAGGER_BREADTH = (8, 12, 16)   # N=5 staggers as 3+2; kept for completeness
REBAL = 20
START = "2020-01-01"
NAV_REF = 1e7
ADV_DISCIPLINE = 0.01           # r1260 / r1262 discipline: p90 participation <= 1% ADV
BASE_N = 5                      # the narrow book every trade-off is measured against


def sleeve_split(n):
    """Two rank slices that partition ranks 1..n with sizes differing by <= 1.

    Odd widths are allowed (n=5 -> 3+2) so the sweep can include the engine default
    rather than starting at 8. Ranks are 1-based and inclusive on both ends.
    """
    if n < 2:
        raise ValueError("breadth must be >= 2 to split into two sleeves")
    hi_a = int(math.ceil(n / 2.0))
    return (1, hi_a), (hi_a + 1, n)


def capacity_nav(p90_participation, nav_ref=NAV_REF, discipline=ADV_DISCIPLINE):
    """NAV at which p90 participation would just reach the ADV discipline.

    Participation is linear in NAV at fixed weights, so p90 measured at one NAV
    scales the capacity line directly. Missing or non-positive p90 -> None, never 0.
    """
    if p90_participation is None or not np.isfinite(p90_participation) or p90_participation <= 0:
        return None
    return round(float(nav_ref) * discipline / float(p90_participation), 0)


def capacity_per_pp(cap, cap_base, cagr, cagr_base):
    """Capacity gained per pp of annual return given up versus the narrow book.

    Returns None when the wider book actually makes MORE return (nothing was given
    up, so the ratio is not defined) or when either capacity is missing.
    """
    if cap is None or cap_base is None or cagr is None or cagr_base is None:
        return None
    lost_pp = 100.0 * (cagr_base - cagr)
    if lost_pp <= 0:
        return None
    return round((cap - cap_base) / lost_pp, 0)


def _p90(rows):
    vals = [r["participation_max"] for r in rows if r["participation_max"] is not None]
    return round(float(pd.Series(vals).quantile(0.9)), 6) if vals else None


def single_line(close, openp, amt, feats, score, n, cagr_only=False):
    """One book holding the top `n` names, rebalanced every REBAL bars."""
    ser, turn, gap = F.run_next_open(close, openp, amt, feats, REBAL, n_hold=n,
                                     cost=F.COST, start=START, score=score)
    m = F.metrics(ser, "single n=%d" % n)
    m.update({"n_hold": n, "turnover_per_decision": round(turn, 4),
              "turns_per_year": turns_per_year(turn, REBAL), "open_gapfill": gap})
    if cagr_only:
        return m
    # participation arm: same book, reference NAV, only read for participation
    cm = ImpactCost(amt, NAV_REF)
    F.run_next_open(close, openp, amt, feats, REBAL, n_hold=n, cost=cm,
                    start=START, score=score)
    p90 = _p90(cm.rows)
    m.update({"participation_p90": p90, "capacity_nav": capacity_nav(p90),
              "missing_adv_legs": cm.missing_names})
    return m


def stagger_line(close, openp, amt, feats, score, n):
    """The same n names as two sleeves, the second clocked half a period late."""
    (lo_a, hi_a), (lo_b, hi_b) = sleeve_split(n)
    size_a, size_b = hi_a - lo_a + 1, hi_b - lo_b + 1
    off = REBAL // 2
    sa, ta, _ = F.run_next_open(close, openp, amt, feats, REBAL, n_hold=size_a,
                                cost=F.COST, start=START,
                                score=top_slice(score, lo_a, hi_a))
    st_b = phase_start(close.index, START, off)
    sb, tb, _ = F.run_next_open(close, openp, amt, feats, REBAL, n_hold=size_b,
                                cost=F.COST, start=st_b,
                                score=top_slice(score, lo_b, hi_b))
    m = F.metrics(blend([sa, sb]), "stagger n=%d" % n)
    turn = 0.5 * (ta + tb)
    m.update({"n_hold": n, "sleeves": [size_a, size_b], "phase_offset_bars": off,
              "sleeve_turnover_per_decision": {"a": round(ta, 4), "b": round(tb, 4)},
              "turnover_per_decision": round(turn, 4),
              "turns_per_year": turns_per_year(turn, REBAL)})

    ca, cb = ImpactCost(amt, NAV_REF * 0.5), ImpactCost(amt, NAV_REF * 0.5)
    F.run_next_open(close, openp, amt, feats, REBAL, n_hold=size_a, cost=ca,
                    start=START, score=top_slice(score, lo_a, hi_a))
    F.run_next_open(close, openp, amt, feats, REBAL, n_hold=size_b, cost=cb,
                    start=st_b, score=top_slice(score, lo_b, hi_b))
    p90 = _p90(ca.rows + cb.rows)
    m.update({"participation_p90": p90, "capacity_nav": capacity_nav(p90),
              "missing_adv_legs": ca.missing_names + cb.missing_names})
    return m


def run():
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    ew = F.metrics(F.run_ew(close, amt, REBAL, start=START), "ew rebal=%d" % REBAL)
    mkt = F.bench_series(close, START)
    mkt_m = F.metrics(mkt, "510300") if mkt is not None else None

    rows = {}
    for n in BREADTH_GRID:
        print("[single] n=%d" % n, flush=True)
        rows["single_%d" % n] = single_line(close, openp, amt, feats, score, n)
    for n in STAGGER_BREADTH:
        print("[stagger] n=%d" % n, flush=True)
        rows["stagger_%d" % n] = stagger_line(close, openp, amt, feats, score, n)

    base = rows["single_%d" % BASE_N]
    for key, m in rows.items():
        m["excess_vs_ew_pp"] = (None if (m.get("cagr") is None or ew.get("cagr") is None)
                               else round(100.0 * (m["cagr"] - ew["cagr"]), 3))
        m["delta_cagr_vs_base_pp"] = (None if (m.get("cagr") is None
                                               or base.get("cagr") is None)
                                      else round(100.0 * (m["cagr"] - base["cagr"]), 3))
        m["capacity_vs_base_pct"] = (None if (m.get("capacity_nav") is None
                                              or base.get("capacity_nav") is None)
                                     else round(100.0 * (m["capacity_nav"]
                                                         / base["capacity_nav"] - 1.0), 2))
        m["capacity_per_pp_return"] = capacity_per_pp(m.get("capacity_nav"),
                                                      base.get("capacity_nav"),
                                                      m.get("cagr"), base.get("cagr"))

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_breadth.py",
        "config": {"breadth_grid": list(BREADTH_GRID),
                   "stagger_breadth": list(STAGGER_BREADTH), "rebal": REBAL,
                   "start": START, "nav_ref": NAV_REF,
                   "adv_discipline_pct": 100.0 * ADV_DISCIPLINE,
                   "base_breadth": BASE_N, "flat_cost_bp": 1e4 * F.COST},
        "controls": {"pool_equal_weight": ew, "market_510300": mkt_m},
        "lines": rows,
        "readings": readings(rows, ew),
    }
    return out


def readings(rows, ew):
    """Derived sentences only -- every number below is computed, never typed."""
    singles = {n: rows["single_%d" % n] for n in BREADTH_GRID if "single_%d" % n in rows}
    by_cap = sorted(((m.get("capacity_per_pp_return"), k) for k, m in rows.items()
                     if m.get("capacity_per_pp_return") is not None),
                    key=lambda t: t[0], reverse=True)
    best = by_cap[0] if by_cap else (None, None)
    stagger_delta = {}
    for k, m in rows.items():
        if not k.startswith("stagger_"):
            continue
        n = int(k.split("_")[1])
        ref = singles.get(n)
        if ref is None or m.get("cagr") is None or ref.get("cagr") is None:
            continue
        stagger_delta[str(n)] = {
            "delta_cagr_pp": round(100.0 * (m["cagr"] - ref["cagr"]), 3),
            "delta_mdd_pp": round(100.0 * (m["maxdd"] - ref["maxdd"]), 3),
            "delta_capacity_pct": (None if m.get("capacity_nav") is None
                                   or ref.get("capacity_nav") is None
                                   else round(100.0 * (m["capacity_nav"]
                                                       / ref["capacity_nav"] - 1.0), 2)),
        }
    out = {
        "single_cagr_by_breadth": {str(n): m.get("cagr") for n, m in singles.items()},
        "single_capacity_by_breadth": {str(n): m.get("capacity_nav") for n, m in singles.items()},
        "single_turns_per_year_by_breadth": {str(n): m.get("turns_per_year")
                                            for n, m in singles.items()},
        "best_capacity_per_pp_line": best[1],
        "best_capacity_per_pp_value": best[0],
        "capacity_per_pp_by_line": {k: m.get("capacity_per_pp_return")
                                    for k, m in rows.items()},
        "stagger_vs_single_same_breadth": stagger_delta,
        "ew_cagr": ew.get("cagr"),
    }
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1-2: the two rank slices partition 1..n exactly, sizes differ by <= 1
    partitions_ok, sizes_ok = True, True
    for n in list(BREADTH_GRID) + [2, 3, 5, 9, 15]:
        (lo_a, hi_a), (lo_b, hi_b) = sleeve_split(n)
        covered = list(range(lo_a, hi_a + 1)) + list(range(lo_b, hi_b + 1))
        partitions_ok &= covered == list(range(1, n + 1))
        sizes_ok &= abs((hi_a - lo_a + 1) - (hi_b - lo_b + 1)) <= 1
    leg("L1 sleeve split partitions ranks 1..n, no gap no overlap", partitions_ok)
    leg("L2 sleeve sizes differ by at most one name", sizes_ok)

    # 3: breadth below 2 cannot be split -- must raise, not silently return one sleeve
    try:
        sleeve_split(1)
        leg("L3 breadth<2 rejected", False)
    except ValueError:
        leg("L3 breadth<2 rejected", True)

    # 4: turnover arithmetic matches bars-per-year / rebal
    leg("L4 turns_per_year(1.0, 20) == 252/20", turns_per_year(1.0, REBAL) == 12.6)

    # 5: blending one series returns that series unchanged
    s = pd.Series([1.0, 1.1, 1.21], index=pd.date_range("2020-01-01", periods=3))
    leg("L5 blend of a single curve is an identity", np.allclose(blend([s]).values, s.values))

    # 6: a sleeve that starts late must not dilute the early curve
    a = pd.Series([1.0, 1.02, 1.04, 1.06], index=pd.date_range("2020-01-01", periods=4))
    b = pd.Series([1.0, 1.10], index=pd.date_range("2020-01-03", periods=2))
    bl = blend([a, b])
    leg("L6 late-starting sleeve leaves the burn-in curve untouched",
        abs(bl.iloc[1] - 1.02) < 1e-12 and abs(bl.iloc[0] - 1.0) < 1e-12)

    # 7: capacity formula inverts participation
    leg("L7 capacity at p90=1% of a 10M reference is 10M",
        capacity_nav(0.01) == float(NAV_REF))
    leg("L8 capacity is None (never zero) when p90 is missing or non-positive",
        capacity_nav(None) is None and capacity_nav(0.0) is None)

    # 9: capacity per pp refuses to divide when the wider book gave nothing up
    leg("L9 capacity-per-pp is None when no return was given up",
        capacity_per_pp(2e6, 1e6, 0.09, 0.08) is None
        and capacity_per_pp(2e6, 1e6, 0.07, 0.08) == 1e6)

    # 10: rank slicing is deterministic on ties (method='first')
    idx = pd.date_range("2020-01-01", periods=2)
    tied = pd.DataFrame(1.0, index=idx, columns=list("abcdefgh"))
    first = top_slice(tied, 1, 4)
    second = top_slice(tied, 1, 4)
    nonnan = first.notna().sum(axis=1).tolist()
    leg("L10 tied scores slice to a fixed four names per row",
        first.equals(second) and nonnan == [4, 4])

    # 11: the sweep's own breadth labels never collide with the stagger labels
    keys = ["single_%d" % n for n in BREADTH_GRID] + ["stagger_%d" % n for n in STAGGER_BREADTH]
    leg("L11 sweep line keys are unique and disjoint", len(keys) == len(set(keys)))

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--out", default="results/etf_book_breadth.json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if a.selftest or a.cmd == "selftest":
        return selftest()
    out = run()
    path = a.out if os.path.isabs(a.out) else os.path.join(root, a.out)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(out["readings"], indent=1, ensure_ascii=False))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())