"""E33 ladder-baseline family (descriptive; NO judgment, NO prereg).

E24-E32 answered every *how* question on the five-member desk ladder: weighting
schemes, trend filters, drift bands, timing overlays and the whole weighting
tilt family all wash to zero or worse versus plain monthly equal weight, and
the 2018+ window kills every tilt. What the family never asked is the *whether*
and the *clock*:

  Q1 LADDER-VS-510300 : does the five-rung ladder earn anything over simply
                        holding 510300 (buy-and-hold CSI300)?
  Q2 LADDER-CADENCE   : the monthly rebalance is an assumption nobody tested --
                        monthly vs quarterly vs semiannual vs annual, cost paid
                        against drift given up, at cost x1 and x3.
  Q3 LADDER-MEMBERSHIP: are the five frozen members the right expression of the
                        idea, or a hindsight free lunch? Re-select the top-5 by
                        trailing liquidity from the full ETF panel and compare.

All accounting is imported, never re-implemented:
  * e24_ladder_weighting.simulate    -> the ladder curve (equal scheme)
  * e27_universe_expansion.simulate  -> monthly selection + cadence override
  * e24_ladder_weighting.monthly_relative / metrics / era_of -> same stats

Honest notes baked into the faces:
  * the ETF population is today's surviving listing set (listing survivorship);
    the frozen five are the ladder desk's own book, so Q3's comparison is
    "fixed hindsight set" vs "causal liquidity rule", not a clean attribution.
  * buy-and-hold 510300 pays one side of cost at entry and nothing after; the
    ladder pays turnover cost at every rebalance, so Q1 is a net-of-cost read.
  * 2018+ is reported for every question because E30-E32 showed long-sample
    excesses die in the recent window.
  * descriptive census only: no gate, no verdict, no prereg, no trial count.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e24_ladder_weighting as base  # noqa: E402  (shared accounting/metrics)
import e27_universe_expansion as e27  # noqa: E402  (universe + selection engine)

OUTDIR = os.path.join(ROOT, "results", "e33_ladder_baseline")
BENCH = "sh510300"
CADENCES = ["monthly", "quarterly", "semiannual", "annual"]
CADENCE_STEP = {"quarterly": 3, "semiannual": 6, "annual": 12}


def cadence_indices(cal, cadence):
    """decision indices for a rebalance clock; monthly = every month end."""
    me = base.month_end_indices(cal)
    if cadence == "monthly":
        return set(me)
    step = CADENCE_STEP[cadence]
    return {i for i in me if int(cal[i][5:7]) % step == 0}


def buy_and_hold(cal, closes, sym, cost_mult=1.0):
    """constant-holding curve: enter at the first bar, pay one side of cost.

    Returns (curve, meta). Curve is aligned with base.simulate output
    (starts at cal[1]). Capital before entry sits at 1.0 (the benchmark starts
    at the calendar's first bar by construction, so this only matters for a
    benchmark listed later -- disclosed in meta).
    """
    series = [closes.get(sym, {}).get(d) for d in cal]
    start = next((i for i, v in enumerate(series) if v), None)
    if start is None:
        return [], {"error": "benchmark has no bars"}
    entry_cost = base.COST_BP_SIDE * cost_mult / 1e4
    port = 1.0 - entry_cost
    curve = []
    for i in range(1, len(cal)):
        if i > start and series[i] and series[i - 1]:
            port *= series[i] / series[i - 1]
        curve.append((cal[i], port))
    return curve, {"symbol": sym, "entry_index": start, "entry_date": cal[start],
                   "entry_cost_frac": round(entry_cost, 8),
                   "trades": 1}


def _metrics(face_curve, years):
    m = base.metrics(face_curve, years)
    return m


def _delta_bp(curve, base_curve, years):
    bmap = dict(base_curve)
    d = [v / bmap[d0] - 1.0 for d0, v in curve if d0 in bmap and bmap[d0] > 0]
    return round(d[-1] / years * 1e4, 1) if d and years else None


def _aux(aux, years):
    out = dict(aux)
    out["turnover_per_year"] = round(aux["turnover_total"] / years, 3) if years else None
    out["cost_per_year_bp"] = round(aux["cost_paid_frac"] / years * 1e4, 1) if years else None
    return out


def window(cal, closes, amounts, start=None):
    if not start:
        return cal, closes, amounts
    cal2 = [d for d in cal if d >= start]
    closes2 = {s: {d: v for d, v in c.items() if d >= start} for s, c in closes.items()}
    amounts2 = {s: {d: v for d, v in a.items() if d >= start} for s, a in amounts.items()}
    return cal2, closes2, amounts2


def q1_ladder_vs_bench(cal, closes, amounts, cash, cost_mult=1.0):
    prices = {s: [closes[s].get(d) for d in cal] for s in closes}
    ams = {s: [amounts[s].get(d) for d in cal] for s in closes}
    ladder_curve, ladder_aux, _ = e27.simulate(cal, prices, ams, base.LADDER, cash,
                                               None, cost_mult, {})
    bh_curve, bh_meta = buy_and_hold(cal, closes, BENCH, cost_mult)
    years = len(cal) / 252.0
    return {
        "ladder": {"metrics": _metrics(ladder_curve, years), "aux": _aux(ladder_aux, years)},
        "benchmark": {"meta": bh_meta, "metrics": _metrics(bh_curve, years)},
        "ladder_minus_bench_bp_annualised": _delta_bp(ladder_curve, bh_curve, years),
        "ladder_vs_bench_monthly": base.monthly_relative(ladder_curve, bh_curve),
    }, ladder_curve


def q2_cadence(cal, closes, amounts, cash, cost_mult=1.0):
    prices = {s: [closes[s].get(d) for d in cal] for s in closes}
    ams = {s: [amounts[s].get(d) for d in cal] for s in closes}
    years = len(cal) / 252.0
    faces = {}
    curves = {}
    for cad in CADENCES:
        rebal = cadence_indices(cal, cad)
        curve, aux, _ = e27.simulate(cal, prices, ams, base.LADDER, cash, None,
                                     cost_mult, {}, rebal=rebal)
        curves[cad] = curve
        faces[cad] = {"rebalance_days": len(rebal), "metrics": _metrics(curve, years),
                      "aux": _aux(aux, years)}
    mcurve = curves["monthly"]
    for cad, f in faces.items():
        if cad == "monthly":
            continue
        f["vs_monthly_bp_annualised"] = _delta_bp(curves[cad], mcurve, years)
        f["vs_monthly"] = base.monthly_relative(curves[cad], mcurve)
    return faces


def q3_membership(cal, closes, amounts, cash, cost_mult=1.0):
    """frozen five vs causal top-5-by-liquidity, at monthly and quarterly clocks."""
    raw = e27.load_universe()
    all_syms = sorted(set(base.LADDER) | set(raw))
    prices, ams = {}, {}
    for s in all_syms:
        if s in raw:
            c, a = raw[s]
        else:
            c, a = {}, {}
        prices[s] = [c.get(d) for d in cal]
        ams[s] = [a.get(d) for d in cal]
    universe = [s for s in all_syms if s in raw]
    years = len(cal) / 252.0
    # one rank cache per universe: the cache is keyed by calendar index only,
    # so sharing it across universes would replay the wide ranking into the
    # equity-only leg (caught in-window: top5eq came back identical to top5).
    rank_caches = {}
    faces = {}
    curves = {}
    # sh511* is the SH money-market/bond block: a pure liquidity ranking drags
    # cash-like funds into the book, so the equity-only leg isolates membership
    # choice from "bonds are liquid".
    equity = [s for s in universe if not s.startswith("sh511")]
    specs = [("frozen5_monthly", base.LADDER, None, "monthly"),
             ("frozen5_quarterly", base.LADDER, None, "quarterly"),
             ("top5_monthly", universe, 5, "monthly"),
             ("top5_quarterly", universe, 5, "quarterly"),
             ("top5eq_monthly", equity, 5, "monthly"),
             ("top5eq_quarterly", equity, 5, "quarterly")]
    for name, univ, pick, cad in specs:
        rebal = cadence_indices(cal, cad)
        cache = rank_caches.setdefault(tuple(univ), {})
        curve, aux, holdings = e27.simulate(cal, prices, ams, univ, cash, pick,
                                            cost_mult, cache, rebal=rebal)
        curves[name] = curve
        faces[name] = {"pick_n": pick, "cadence": cad,
                       "metrics": _metrics(curve, years), "aux": _aux(aux, years),
                       "last_holdings": holdings,
                       "last_holdings_n": len(holdings or [])}
    for name in ("frozen5_quarterly", "top5_monthly", "top5_quarterly",
                 "top5eq_monthly", "top5eq_quarterly"):
        faces[name]["vs_frozen5_monthly_bp_annualised"] = _delta_bp(
            curves[name], curves["frozen5_monthly"], years)
        faces[name]["vs_frozen5_monthly"] = base.monthly_relative(
            curves[name], curves["frozen5_monthly"])
    return {"universe_size": len(universe), "equity_universe_size": len(equity),
            "schemes": faces}


def run(start=None, cost_mult=1.0):
    cal, closes, amounts = base.load_panel()
    cal, closes, amounts = window(cal, closes, amounts, start)
    years = len(cal) / 252.0
    cash = base.load_cash_series(cal)
    if not cal:
        raise SystemExit("empty calendar")

    q1, _ = q1_ladder_vs_bench(cal, closes, amounts, cash, cost_mult)
    q2_x1 = q2_cadence(cal, closes, amounts, cash, 1.0)
    q2_x3 = q2_cadence(cal, closes, amounts, cash, 3.0)
    q3 = q3_membership(cal, closes, amounts, cash, cost_mult)

    head = {
        "study": "e33_ladder_baseline",
        "evidence_cutoff": cal[-1],
        "start": cal[0],
        "bars": len(cal),
        "years": round(years, 2),
        "members": base.LADDER,
        "benchmark": BENCH,
        "cost_bp_per_side": base.COST_BP_SIDE,
        "cash_leg": ({"source": "data/repo_daily/GC001.csv close (annualised %)",
                      "covered_days": cash["covered_days"],
                      "ffilled_days": cash["ffilled_days"],
                      "last_rate_date": cash["last"]} if cash else None),
        "honest": [
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
            "ETF population is today's surviving listing set (listing survivorship); the frozen five "
            "are the desk's own book, so Q3 compares a hindsight set against a causal rule",
            "buy-and-hold benchmark pays one side of cost at entry; the ladder pays turnover cost each rebalance",
            "13.041bp/side on turnover; un-invested share accrues at the GC001 repo close",
            "quarterly/semiannual/annual clocks rebalance on the last trading day of the 3rd/6th/12th month",
        ],
    }
    faces = {
        "Q1-LADDER-VS-510300": dict(head, question="ladder equal-weight vs 510300 buy-and-hold",
                                    result=q1),
        "Q2-LADDER-CADENCE": dict(head, question="rebalance clock: monthly vs quarterly vs semiannual vs annual",
                                  cost_mult=1.0, result_x1=q2_x1,
                                  result_x3=q2_x3),
        "Q3-LADDER-MEMBERSHIP": dict(head, question="frozen five vs causal top-5-by-liquidity",
                                     result=q3),
    }
    return faces


def write_faces(faces, tag):
    os.makedirs(OUTDIR, exist_ok=True)
    names = []
    for key, face in faces.items():
        p = os.path.join(OUTDIR, "%s-%s.json" % (key, tag))
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        names.append(os.path.basename(p))
    ptr = os.path.join(OUTDIR, "latest.json")
    with open(ptr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "tag": tag, "faces": names}, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return names


def selftest():
    ok = 0
    tot = 0

    def cal_of(n=800):
        # 800 pseudo-trading days spanning ~3 calendar years of month ends
        out = []
        d = datetime(2020, 1, 1)
        from datetime import timedelta
        while len(out) < n:
            if d.weekday() < 5:
                out.append(d.strftime("%Y-%m-%d"))
            d += timedelta(days=1)
        return out

    cal = cal_of()
    # 1. monthly clock = every month end; quarterly is a subset; annual ⊂ quarterly
    me = set(base.month_end_indices(cal))
    m = cadence_indices(cal, "monthly")
    q = cadence_indices(cal, "quarterly")
    a = cadence_indices(cal, "annual")
    assert m == me
    assert q and q < m
    assert a and a < q
    assert all(int(cal[i][5:7]) % 3 == 0 for i in q)
    assert all(int(cal[i][5:7]) == 12 for i in a)
    ok += 1; tot += 1

    # 2. buy-and-hold reproduces the price ratio exactly at zero cost
    sym = "sh510300"
    closes = {sym: {d: 4.0 * (1.001 ** k) for k, d in enumerate(cal)}}
    c0, meta0 = buy_and_hold(cal, closes, sym, 0.0)
    assert meta0["entry_index"] == 0
    assert abs(c0[-1][1] - closes[sym][cal[-1]] / closes[sym][cal[0]]) < 1e-12
    # 3. one side of cost is charged exactly once at entry
    c1, _ = buy_and_hold(cal, closes, sym, 1.0)
    assert abs(c1[-1][1] - c0[-1][1] * (1.0 - base.COST_BP_SIDE / 1e4)) < 1e-12
    ok += 1; tot += 1

    # 4. a later listing stays flat (no lookahead) until its first bar
    sym2 = "sh588000"
    late = {sym: closes[sym], sym2: {d: v for d, v in closes[sym].items() if d >= cal[400]}}
    c2, meta2 = buy_and_hold(cal, late, sym2, 0.0)
    assert meta2["entry_index"] == 400
    assert all(abs(v - 1.0) < 1e-12 for _, v in c2[:399])
    ok += 1; tot += 1

    # 5. the cadence override actually cuts rebalance count (engine parity leg lives in e27)
    syms = ["sh51030%d" % k for k in range(5)]
    prices, ams = {}, {}
    for j, s in enumerate(syms):
        prices[s] = [10.0 * (1.0 + 0.0005 * (j + 1)) ** k for k in range(len(cal))]
        ams[s] = [1e8] * len(cal)
    _, a_m, _ = e27.simulate(cal, prices, ams, syms, None, None, 1.0, {},
                             rebal=cadence_indices(cal, "monthly"))
    _, a_q, _ = e27.simulate(cal, prices, ams, syms, None, None, 1.0, {},
                             rebal=cadence_indices(cal, "quarterly"))
    _, a_d, _ = e27.simulate(cal, prices, ams, syms, None, None, 1.0, {})
    assert a_q["rebalances"] < a_m["rebalances"]
    assert a_d["rebalances"] == a_m["rebalances"]  # default is still monthly
    ok += 1; tot += 1

    # 6. an explicit monthly set equals the default clock bit-for-bit
    c_def, _, _ = e27.simulate(cal, prices, ams, syms, None, None, 1.0, {})
    c_exp, _, _ = e27.simulate(cal, prices, ams, syms, None, None, 1.0, {},
                               rebal=set(base.month_end_indices(cal)))
    assert all(abs(x[1] - y[1]) < 1e-15 for x, y in zip(c_def, c_exp))
    ok += 1; tot += 1

    # 7. delta helper signs: identical curves -> 0
    assert _delta_bp(c_def, c_def, 3.0) == 0.0
    ok += 1; tot += 1

    # 8. the rank cache is keyed by calendar index only: sharing one across two
    #    universes replays the wide ranking into the narrow leg (E33 in-window pit)
    narrow = [s for s in syms if s != "sh510300"]
    _, _, h_wide = e27.simulate(cal, prices, ams, syms, None, 2, 1.0, {})
    _, _, h_narrow = e27.simulate(cal, prices, ams, narrow, None, 2, 1.0, {})
    assert h_wide == ["sh510300", "sh510301"], h_wide
    assert h_narrow == ["sh510301", "sh510302"], h_narrow
    shared = {}
    _, _, h_w2 = e27.simulate(cal, prices, ams, syms, None, 2, 1.0, shared)
    _, _, h_n2 = e27.simulate(cal, prices, ams, narrow, None, 2, 1.0, shared)
    assert h_n2 == h_w2, (h_w2, h_n2)  # the leak, pinned as a documented property
    ok += 1; tot += 1

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--start", default=None)
    ap.add_argument("--cost-mult", type=float, default=1.0)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args(argv)

    if args.mode == "selftest":
        return selftest()

    faces = run(start=args.start, cost_mult=args.cost_mult)
    tag = args.tag or "WIN-%s" % (faces["Q1-LADDER-VS-510300"]["evidence_cutoff"].replace("-", ""))
    names = write_faces(faces, tag)
    print(json.dumps({"tag": tag, "faces": names}, ensure_ascii=False))
    q1 = faces["Q1-LADDER-VS-510300"]["result"]
    print("Q1 ladder %s vs bench %s: %s bp/yr" % (
        q1["ladder"]["metrics"].get("ann_return_pct"),
        q1["benchmark"]["metrics"].get("ann_return_pct"),
        q1["ladder_minus_bench_bp_annualised"]))
    for cad in CADENCES:
        f = faces["Q2-LADDER-CADENCE"]["result_x1"][cad]
        print("Q2 %-10s ann %s cost %s bp/yr rebal %s" % (
            cad, f["metrics"].get("ann_return_pct"), f["aux"].get("cost_per_year_bp"),
            f["aux"].get("rebalances")))
    for k, v in faces["Q3-LADDER-MEMBERSHIP"]["result"]["schemes"].items():
        print("Q3 %-18s ann %s vs frozen %s bp/yr holdings %s" % (
            k, v["metrics"].get("ann_return_pct"),
            v.get("vs_frozen5_monthly_bp_annualised"), v.get("last_holdings_n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))