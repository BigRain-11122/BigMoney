"""E26 band-rebalance family (descriptive; NO judgment, NO prereg).

E25 closed the trend-filter question: every hard 0/1 filter is a wash to
-180bp/yr, the half-weight 150-200d variants are +60..+97bp/yr at t 0.43-0.59
and flip negative in 2024-now, so the apparent edge is a volatility effect,
not a return edge. What that family did settle is an accounting fact: the
equal-weight ladder only turns over 0.32x/yr (4.2bp/yr of cost), while every
filter tried so far paid 9-38bp/yr of turnover and bought nothing.

That leaves a pure cost question, which is what this runner answers:

    would rebalancing LESS often than monthly -- only when a member's weight
    drifts outside a band -- keep the same exposure at lower cost?

Schemes here are all "hold the five members", the only difference is WHEN the
weights are restored to equal:

  monthly_<N> : the E24/E25 baseline, rebalance on the last trading day of the
                month (band_pp = None)
  band_<N>pp  : rebalance only when any |w_s - target_s| > N percentage points,
                or when the eligible membership set changes (a new member
                clearing the 250-bar gate must be bought in regardless)

Everything else is shared with the E24 runner: same panel, same 13.041bp/side
cost, same GC001 cash leg on the un-invested share, same causal weights (the
decision is read at the close and takes effect from the next bar).

Honest notes baked into the face:
  * descriptive census only: no gate, no verdict, no prereg, no trial count.
  * the band is a mechanical rule, so it is NOT a fitted parameter -- but the
    grid of bands is still a multiple-comparison surface; only a band that
    beats monthly across every band size would be a real effect.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e24_ladder_weighting as base  # noqa: E402  (shared panel/cash/metrics)

OUTDIR = os.path.join(ROOT, "results", "e26_band_rebalance")
DEFAULT_BANDS = [0.5, 1.0, 2.0, 5.0, 10.0]


def _live(prices, i):
    return [s for s in base.LADDER if s in prices and base.elig(prices[s], i)]


def simulate_band(cal, closes, amounts, cash=None, band_pp=None, cost_mult=1.0):
    """Simulate one scheme.

    band_pp is None -> monthly rebalance on the last trading day of the month
    (identical to base.simulate("equal")); otherwise a drift band in
    percentage points (2.0 = rebalance when any weight is off by > 2pp).
    """
    prices = {s: [closes[s].get(d) for d in cal] for s in closes}
    # the month-end set is needed in BOTH modes: it gates the very first
    # investment so that band and monthly schemes enter on the same day.
    # Without that gate the band scheme enters at the first eligible bar while
    # the monthly scheme waits for the month end, and in 2013-06 that accident
    # alone put the band family 6% behind (it bought the liquidity-crunch top).
    rebal = set(base.month_end_indices(cal))
    band = (band_pp / 100.0) if band_pp is not None else None
    port = 1.0
    weights = {}
    curve = []
    cost_paid = 0.0
    turnover_total = 0.0
    n_rebal = 0
    prev_live = None
    cash_series = cash["series"] if cash else None

    for i in range(1, len(cal)):
        # drift existing weights with today's returns (cash share accrues repo)
        if weights or cash_series is not None:
            growth = 0.0
            neww = {}
            for s, w in weights.items():
                a, b = prices[s][i], prices[s][i - 1]
                if a is None or b is None or b <= 0:
                    neww[s] = w
                    continue
                r = a / b - 1.0
                neww[s] = w * (1.0 + r)
                growth += w * r
            cw = 1.0 - sum(weights.values())
            if cw < 1e-12:
                cw = 0.0
            rc = cash_series.get(cal[i], 0.0) if cash_series else 0.0
            growth += cw * rc
            tv = sum(neww.values()) + cw * (1.0 + rc)
            weights = {s: v / tv for s, v in neww.items()} if tv > 0 else weights
            port *= (1.0 + growth)

        decide = False
        if band_pp is None:
            decide = (i - 1) in rebal
        else:
            live = _live(prices, i - 1)
            if not live:
                prev_live = live
                curve.append((cal[i], port))
                continue
            target = {s: 1.0 / len(live) for s in live}
            if prev_live != live and weights:
                decide = True           # membership change always rebalances
            elif not weights:
                decide = (i - 1) in rebal   # first entry, shared with monthly
            else:
                cw = max(0.0, 1.0 - sum(weights.values()))
                dev = cw
                for s in set(target) | set(weights):
                    dev = max(dev, abs(target.get(s, 0.0) - weights.get(s, 0.0)))
                decide = dev > band
            prev_live = live

        if decide:
            if band_pp is None:
                target = base.scheme_weights("equal", i - 1, prices, None)
            if target:
                if weights:
                    turnover = sum(abs(target.get(s, 0.0) - weights.get(s, 0.0))
                                   for s in set(target) | set(weights)) / 2.0
                else:
                    turnover = 1.0
                fee = turnover * base.COST_BP_SIDE * cost_mult / 1e4
                port *= (1.0 - fee)
                cost_paid += fee
                turnover_total += turnover
                n_rebal += 1
                weights = dict(target)
        curve.append((cal[i], port))

    return curve, {
        "rebalances": n_rebal,
        "turnover_total": turnover_total,
        "cost_paid_frac": cost_paid,
    }


def _scheme_specs(bands):
    return [("monthly", None)] + [("band_%gpp" % b, b) for b in bands]


def run(bands=None, start=None, cost_mult=1.0):
    bands = DEFAULT_BANDS if not bands else bands
    cal, closes, amounts = base.load_panel()
    if start:
        cal = [d for d in cal if d >= start]
        closes = {s: {d: v for d, v in c.items() if d >= start} for s, c in closes.items()}
        amounts = {s: {d: v for d, v in a.items() if d >= start} for s, a in amounts.items()}
    years = len(cal) / 252.0
    cash = base.load_cash_series(cal)

    faces = {}
    curves = {}
    for name, band in _scheme_specs(bands):
        curve, aux = simulate_band(cal, closes, amounts, cash, band, cost_mult)
        curves[name] = curve
        m = base.metrics(curve, years)
        aux["turnover_per_year"] = round(aux["turnover_total"] / years, 3) if years else None
        aux["cost_per_year_bp"] = round(aux["cost_paid_frac"] / years * 1e4, 1) if years else None
        faces[name] = {"band_pp": band, "metrics": m, "aux": aux}

    base_curve = curves["monthly"]
    for name, f in faces.items():
        if name == "monthly":
            continue
        bmap = dict(base_curve)
        d = []
        for d0, v in curves[name]:
            if d0 in bmap and bmap[d0] > 0:
                d.append(v / bmap[d0] - 1.0)
        f["vs_monthly_bp_annualised"] = round(d[-1] / years * 1e4, 1) if d and years else None
        f["vs_monthly"] = base.monthly_relative(curves[name], base_curve)

    return {
        "study": "e26_band_rebalance",
        "evidence_cutoff": cal[-1] if cal else None,
        "start": cal[0] if cal else None,
        "bars": len(cal),
        "years": round(years, 2),
        "members": base.LADDER,
        "cost_bp_per_side": base.COST_BP_SIDE,
        "cost_mult": cost_mult,
        "schemes": faces,
        "cash_leg": ({"source": "data/repo_daily/GC001.csv close (annualised %)",
                      "units_per_year": base.CASH_UNITS_PER_YEAR,
                      "covered_days": cash["covered_days"],
                      "ffilled_days": cash["ffilled_days"],
                      "first_rate_date": cash["first"],
                      "last_rate_date": cash["last"]}
                     if cash else None),
        "honest": [
            "all schemes hold the same five members; only the rebalance trigger differs",
            "universe grows over time -- membership changes force a rebalance in every band scheme",
            "13.041bp/side charged on turnover; the un-invested share accrues at the GC001 repo close",
            "the band grid (0.5/1/2/5/10pp) is a multiple-comparison surface; a single winning band "
            "is not evidence, a band family with a consistent sign would be",
            "descriptive census only: no gate, no verdict, no prereg, no trial count consumed",
        ],
    }


def selftest():
    ok = 0
    tot = 0

    def cal_of(n=320):
        return ["%d-%02d-%02d" % (2020 + k // 300, (k % 12) + 1, (k % 25) + 1)
                for k in range(n)]

    # 1. an impossible band (100pp) invests once and never rebalances again
    cal = cal_of()
    shares = {"sh510300": 0.002, "sh510050": -0.001, "sh510500": 0.003,
              "sh512100": 0.001, "sh588000": -0.002}
    closes = {s: {} for s in base.LADDER}
    px = {s: 10.0 for s in base.LADDER}
    for d in cal:
        for s in base.LADDER:
            px[s] *= (1.0 + shares[s])
            closes[s][d] = px[s]
    amounts = {s: {d: 1e6 for d in cal} for s in base.LADDER}
    _, aux = simulate_band(cal, closes, amounts, None, 100.0, 1.0)
    assert aux["rebalances"] == 1, aux
    ok += 1; tot += 1

    # 2. a zero band rebalances on essentially every bar after eligibility
    _, aux0 = simulate_band(cal, closes, amounts, None, 0.0, 1.0)
    assert aux0["rebalances"] > 40, aux0
    ok += 1; tot += 1

    # 3. wider band -> weakly lower turnover and cost (same data, same universe)
    _, a05 = simulate_band(cal, closes, amounts, None, 0.5, 1.0)
    _, a10 = simulate_band(cal, closes, amounts, None, 10.0, 1.0)
    assert a10["cost_paid_frac"] <= a05["cost_paid_frac"] + 1e-15
    assert a10["rebalances"] <= a05["rebalances"]
    ok += 1; tot += 1

    # 4. monthly mode reproduces the E24 baseline exactly (shared accounting)
    bcal = [d for d in cal if d >= "2021-01-01"]
    bcloses = {s: {d: v for d, v in c.items() if d in bcal} for s, c in closes.items()}
    bam = {s: {d: 1e6 for d in bcal} for s in base.LADDER}
    c_band, aux_band = simulate_band(bcal, bcloses, bam, None, None, 1.0)
    c_base, aux_base = base.simulate("equal", bcal, bcloses, bam, None, 1.0)
    assert aux_band["rebalances"] == aux_base["rebalances"]
    assert all(abs(a[1] - b[1]) < 1e-12 for a, b in zip(c_band, c_base))
    ok += 1; tot += 1

    # 5. cost_mult scales the fee linearly
    _, a1 = simulate_band(cal, closes, amounts, None, 2.0, 1.0)
    _, a3 = simulate_band(cal, closes, amounts, None, 2.0, 3.0)
    assert abs(a3["cost_paid_frac"] - 3.0 * a1["cost_paid_frac"]) < 1e-12
    ok += 1; tot += 1

    # 6. no weight ever exceeds 1 and the curve stays positive
    curve, _ = simulate_band(cal, closes, amounts, None, 1.0, 1.0)
    assert curve[-1][1] > 0 and all(v > 0 for _, v in curve)
    ok += 1; tot += 1

    # 7. a zero-rate cash panel is a no-op for a fully invested scheme
    cash = {"series": {d: 0.0 for d in cal}, "ffilled_days": 0,
            "covered_days": len(cal), "first": cal[0], "last": cal[-1]}
    c_none, _ = simulate_band(cal, closes, amounts, None, 2.0, 1.0)
    c_zero, _ = simulate_band(cal, closes, amounts, cash, 2.0, 1.0)
    assert all(abs(a[1] - b[1]) < 1e-12 for a, b in zip(c_none, c_zero))
    ok += 1; tot += 1

    # 8. a membership change forces a rebalance even inside the band
    #    (600 bars, sh588000 prints only from bar 300 -> clears the 250-bar gate at ~550)
    late_cal = cal_of(600)
    lcloses = {s: {} for s in base.LADDER}
    px = {s: 10.0 for s in base.LADDER}
    for k, d in enumerate(late_cal):
        for s in base.LADDER:
            # sh588000 only starts printing at bar 300 -> joins the live set late
            if s == "sh588000" and k < 300:
                continue
            px[s] *= 1.001
            lcloses[s][d] = px[s]
    lam = {s: {d: 1e6 for d in lcloses[s]} for s in base.LADDER if lcloses[s]}
    _, aux_l = simulate_band(late_cal, lcloses, lam, None, 50.0, 1.0)
    assert aux_l["rebalances"] >= 2, aux_l
    ok += 1; tot += 1

    ok += 1; tot += 1

    # 9. band and monthly schemes enter on the SAME day (shared first-entry gate);
    #    otherwise the comparison is contaminated by a single entry-date accident
    c_m, _ = simulate_band(cal, closes, amounts, None, None, 0.0)
    c_b, _ = simulate_band(cal, closes, amounts, None, 10.0, 0.0)
    first_m = next(k for k, (_, v) in enumerate(c_m) if abs(v - 1.0) > 1e-9)
    first_b = next(k for k, (_, v) in enumerate(c_b) if abs(v - 1.0) > 1e-9)
    assert abs(first_m - first_b) <= 1, (first_m, first_b)
    ok += 1; tot += 1

    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--bands", default=None,
                    help="comma list of band sizes in percentage points (default 0.5,1,2,5,10)")
    ap.add_argument("--start", default=None)
    ap.add_argument("--cost-mult", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    bands = [float(x) for x in args.bands.split(",")] if args.bands else None
    face = run(bands, args.start, args.cost_mult)
    outdir = os.path.join(ROOT, args.out) if args.out else OUTDIR
    os.makedirs(outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    tag = "BAND"
    if bands:
        import hashlib
        tag += "-" + hashlib.sha1(",".join("%g" % b for b in bands).encode()).hexdigest()[:6]
    if args.cost_mult != 1.0:
        tag += "-x%s" % ("%g" % args.cost_mult).replace(".", "p")
    path = os.path.join(outdir, "%s-%s.json" % (tag, stamp))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"start": face["start"], "cutoff": face["evidence_cutoff"],
                      "years": face["years"], "bars": face["bars"]}, ensure_ascii=False))
    for sch, f in face["schemes"].items():
        print(sch, json.dumps(f, ensure_ascii=False))
    print("face:", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))