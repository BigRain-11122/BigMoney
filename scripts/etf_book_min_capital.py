"""How small an account can run the delivered book before the 5-yuan floor eats it?

Every cost number on the shelf is a *rate* per side: 8bp base + square-root impact
(`etf_book_capacity.py`), applied to traded notional. A rate has no floor, and a real
brokerage charge does: the A-share/ETF commission carries a **minimum of 5 CNY per
trade** on most retail accounts. For a book that holds `k = min(1, 0.20/beta)` of NAV
in twelve names, one rebalance buys or sells ~1.5% of NAV per name, so the trade
notional is small and the floor stops being negligible -- the 8bp assumption is then
optimistic, and the published 8.46%/yr is not reachable at that size.

The question this face answers is therefore two-sided, and both halves are money:

  * below the fee-neutral NAV the modelled 8bp is too cheap (the floor binds);
  * above it the same model is too expensive, because 万2.5 is 2.5bp, not 8bp.

Both are measured on the SAME weight path as the published arm, so the delta is
attributable to the fee schedule and nothing else (the r1290/r1291 lesson).

Cost model (one arm per schedule, identical impact term):

    bp_side = max(prop_bp, 1e4 * min_fee_cny / notional) + K * sqrt(p / 1%)

with `notional = dw * capital`, `p = notional / ADV20` known one bar before the fill
(`C.adv_at`, punitive 100bp for a name with no ADV -- reused, never re-typed).
Capital is held constant over the window so each ladder rung is comparable to the
published `@8bp` arm at the same NAV; compounding the account size would confound the
fee question with a second, unrelated one.

Frozen reading rule (written before the run, per the r1325 adoption discipline):

  * `fee_neutral_vs_model` = the capital at which the *median* traded leg's real
    commission equals the modelled 8bp (closed form: 1e4*min_fee/(8bp*dw_median)).
  * `fee_neutral_vs_real` = the capital at which it equals the plain 万2.5 rate.
  * verdict tokens:
      - `FLOOR_BINDS_BELOW_<X>` when fee_neutral_vs_model is inside the ladder and
        the small-capital rungs actually lose CAGR against the 8bp arm;
      - `NO_FLOOR_EFFECT` when even the smallest rung reproduces the 8bp arm;
      - `INSUFFICIENT_LADDER` when the neutral point lies outside the tested sizes
        (then no claim is made -- a size we did not price is not a finding).

  python scripts/etf_book_min_capital.py run
  python scripts/etf_book_min_capital.py --check        # re-derive from published rows
  python scripts/etf_book_min_capital.py --selftest

Exit contract: 0 ok | 2 mechanism failure | 3 published face disagrees with its own
rows (drifted, refuse to print a verdict).
Outputs results/etf_book_min_capital.json.
Exploratory: no preregistration, no verdict adjudication, no ledger booking.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F
from scripts import etf_book_capacity as C
from scripts import etf_book_capacity_rule as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_book_min_capital.json")
EPS = 1e-12

# Retail brokerage assumptions, stated as parameters rather than buried in the cost line.
MIN_FEE_CNY = 5.0
SCHEDULES = (
    {"name": "wan2.5+5", "prop_bp": 2.5, "min_fee_cny": MIN_FEE_CNY},
    {"name": "wan1.5+5", "prop_bp": 1.5, "min_fee_cny": MIN_FEE_CNY},
    {"name": "wan2.5+0", "prop_bp": 2.5, "min_fee_cny": 0.0},
)
CAPITALS = (1e4, 2e4, 5e4, 1e5, 2e5, 4e5, 1e6, 1.5e6, 3e6, 1e7)
BASE_BP = C.BASE_BP            # the published flat assumption (imported, not retyped)


def fee_bp(prop_bp, min_fee_cny, notional):
    """Per-side commission in bp: the proportional rate with a cash floor."""
    if notional is None or not np.isfinite(notional) or notional <= EPS:
        return float(prop_bp) if not min_fee_cny else float(min_fee_cny) * 1e4
    floor_bp = 1e4 * float(min_fee_cny) / float(notional)
    return float(max(float(prop_bp), floor_bp))


def neutral_nav(dw, prop_bp, min_fee_cny):
    """Capital at which the cash floor stops binding for a leg of weight `dw`.

    `fee_bp == prop_bp` exactly at notional = 1e4*min_fee/prop_bp, and notional = NAV*dw.
    Without a floor the neutral point is 0 (nothing to neutralise).
    """
    dw = float(dw)
    if not min_fee_cny or dw <= EPS or prop_bp <= 0:
        return 0.0
    return 1e4 * float(min_fee_cny) / (float(prop_bp) * dw)


def curve(face, capital, prop_bp, min_fee_cny, k_bp=C.IMPACT_BP_PER_PCT,
          path=None, trace=False):
    """Daily NAV of the delivered rule at `capital`, priced with a commission floor.

    Returns (level series, per-decision rows, counters). The impact term is the
    published one; only the base rate is replaced by `max(prop, floor)`, so the delta
    against the `@8bp` arm is the fee schedule and nothing else.
    """
    if path is None:
        path = R.weight_path(face)
    amt = face["amt"]
    rp, rf = face["rp"], face["rf"]
    prev_w = {}
    equity = 1.0
    levels = []
    rows = []
    below_floor = 0
    legs_total = 0
    fee_cny = 0.0
    dws = []
    for d, w, cash in path:
        k = 1.0 - cash
        adv_row = C.adv_at(amt, d, back=1)
        cost = 0.0
        day_legs = 0
        for s in sorted(set(prev_w) | set(w)):
            dw = abs(w.get(s, 0.0) - prev_w.get(s, 0.0))
            if dw <= R.EPS:
                continue
            day_legs += 1
            dws.append(dw)
            notional = dw * capital
            base = fee_bp(prop_bp, min_fee_cny, notional)
            if min_fee_cny and base > float(prop_bp) + 1e-12:
                below_floor += 1
            adv = np.nan if adv_row is None else float(adv_row.get(s, np.nan))
            if not np.isfinite(adv) or adv <= 0:
                bp = C.PUNITIVE_BP
            else:
                bp = base + k_bp * np.sqrt((notional / adv) / 0.01)
            cost += dw * bp
            fee_cny += dw * base * capital / 1e4
        legs_total += day_legs
        cost /= 1e4
        if trace and day_legs:
            rows.append({"date": str(pd.Timestamp(d).date()), "legs": day_legs,
                         "cost_frac": round(cost, 10)})
        r = k * float(rp.get(d, 0.0)) + cash * float(rf.get(d, 0.0))
        equity *= (1.0 + r) * (1.0 - cost)
        levels.append((d, equity))
        prev_w = w
    ser = pd.Series(dict(levels))
    dws = np.asarray(dws, dtype=float)
    cnt = {"legs": legs_total, "legs_below_floor": below_floor,
           "share_below_floor": (float(below_floor) / legs_total) if legs_total else None,
           "fee_cny_total": round(fee_cny, 2),
           "dw_median": float(np.median(dws)) if len(dws) else None,
           "dw_mean": float(np.mean(dws)) if len(dws) else None}
    return ser, rows, cnt


def _verdict(rows, fee_neutral_model, fee_neutral_real, ladder_bounds):
    """Frozen reading rule -- no hand-written verdict, it is derived from the rows."""
    lo, hi = ladder_bounds
    small = rows[0]
    if small.get("cagr") is None:
        return "INSUFFICIENT_LADDER"
    worsens = small["cagr"] < small["ref_cagr"] - 1e-9
    if fee_neutral_model is None:
        return "INSUFFICIENT_LADDER"
    if not worsens:
        return "NO_FLOOR_EFFECT"
    if not (lo < fee_neutral_model <= hi):
        return "INSUFFICIENT_LADDER"
    token = "FLOOR_BINDS_BELOW_%d" % int(round(fee_neutral_model))
    if fee_neutral_real and fee_neutral_real > fee_neutral_model:
        token += "_AND_MODEL_GENEROUS_ABOVE_%d" % int(round(fee_neutral_real))
    return token


def run(start=R.START):
    face = R.build_face(start=start)
    path = R.weight_path(face)
    # reference: the published flat-8bp assumption, same path, same impact term
    ref_rows = {}
    for capital in CAPITALS:
        ser, _r, _c = curve(face, capital, BASE_BP, 0.0, path=path)
        ref_rows[capital] = F.metrics(ser, "8bp @ %.0e" % capital)

    ladder = []
    dw_median = None
    for sched in SCHEDULES:
        for capital in CAPITALS:
            ser, rows, cnt = curve(face, capital, sched["prop_bp"],
                                   sched["min_fee_cny"], path=path, trace=True)
            m = F.metrics(ser, "%s @ %.0e" % (sched["name"], capital))
            ref = ref_rows[capital]
            row = {"schedule": sched["name"], "capital": capital,
                   "cagr": m.get("cagr"), "vol": m.get("vol"),
                   "sharpe": m.get("sharpe"), "maxdd": m.get("maxdd"),
                   "ref_cagr": ref.get("cagr"), "ref_sharpe": ref.get("sharpe"),
                   "legs": cnt["legs"],
                   "share_below_floor": (None if cnt["share_below_floor"] is None
                                         else round(cnt["share_below_floor"], 6)),
                   "fee_cny_total": cnt["fee_cny_total"],
                   "dw_median": (None if cnt["dw_median"] is None
                                 else round(cnt["dw_median"], 8))}
            if m.get("cagr") is not None and ref.get("cagr") is not None:
                row["delta_vs_8bp_pp"] = round(100.0 * (m["cagr"] - ref["cagr"]), 4)
                row["annual_delta_cny"] = round(capital * (m["cagr"] - ref["cagr"]), 0)
            if row["dw_median"]:
                dw_median = row["dw_median"]
            ladder.append(row)

    primary = SCHEDULES[0]
    fee_neutral_model = neutral_nav(dw_median, BASE_BP, primary["min_fee_cny"])
    fee_neutral_real = neutral_nav(dw_median, primary["prop_bp"], primary["min_fee_cny"])
    primary_rows = [r for r in ladder if r["schedule"] == primary["name"]]
    verdict = _verdict(primary_rows, fee_neutral_model, fee_neutral_real,
                       (min(CAPITALS), max(CAPITALS)))

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(face["idx"][-1]).date()),
        "script": "scripts/etf_book_min_capital.py",
        "config": {"capital_grid": list(CAPITALS), "schedules": list(SCHEDULES),
                   "base_bp_published": BASE_BP,
                   "impact_bp_per_pct": C.IMPACT_BP_PER_PCT,
                   "punitive_bp": C.PUNITIVE_BP,
                   "rebal": R.REBAL, "start": start,
                   "dw_median_all_legs": (None if dw_median is None
                                          else round(dw_median, 8))},
        "fee_neutral_vs_model_nav": (None if fee_neutral_model is None
                                     else round(fee_neutral_model, 2)),
        "fee_neutral_vs_real_nav": (None if fee_neutral_real is None
                                    else round(fee_neutral_real, 2)),
        "verdict": verdict,
        "ladder": ladder,
        "method_note": ("one engine, one weight path, one window; only the base "
                        "per-side rate is replaced by max(prop, 5 CNY / notional), "
                        "impact term identical. Capital held constant per rung so each "
                        "delta is attributable to the fee schedule (compare vs the "
                        "same-NAV @8bp arm, not across rungs)."),
        "scope_note": ("fees only: spread is inside the 8bp reference and is NOT added "
                       "here; a broker with no 5-yuan floor is the wan2.5+0 row; the "
                       "delivered rule's own turnover is imported from the engine."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def check():
    """Re-derive the verdict and the neutral points from the published rows."""
    if not os.path.exists(OUT):
        print("min_capital: published face missing")
        return 2
    with open(OUT, encoding="utf-8") as fh:
        d = json.load(fh)
    cfg = d["config"]
    dw = cfg["dw_median_all_legs"]
    primary = cfg["schedules"][0]
    model = neutral_nav(dw, cfg["base_bp_published"], primary["min_fee_cny"])
    real = neutral_nav(dw, primary["prop_bp"], primary["min_fee_cny"])
    problems = []
    # published precision is 0.01 CNY: compare at that resolution, not at float equality
    if d["fee_neutral_vs_model_nav"] is not None and \
            abs(model - d["fee_neutral_vs_model_nav"]) > 0.02:
        problems.append("fee_neutral_vs_model_nav %.2f != %.2f"
                        % (d["fee_neutral_vs_model_nav"], model))
    if d["fee_neutral_vs_real_nav"] is not None and \
            abs(real - d["fee_neutral_vs_real_nav"]) > 0.02:
        problems.append("fee_neutral_vs_real_nav %.2f != %.2f"
                        % (d["fee_neutral_vs_real_nav"], real))
    rows = [r for r in d["ladder"] if r["schedule"] == primary["name"]]
    want = _verdict(rows, model, real, (min(cfg["capital_grid"]), max(cfg["capital_grid"])))
    if want != d["verdict"]:
        problems.append("verdict %s != recomputed %s" % (d["verdict"], want))
    if problems:
        for p in problems:
            print("DRIFT: " + p)
        return 3
    print("min_capital: check OK (%s, neutral vs model %s CNY, vs real %s CNY)"
          % (d["verdict"], d["fee_neutral_vs_model_nav"], d["fee_neutral_vs_real_nav"]))
    return 0


def selftest():
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[1] += 1
        ok[0] += int(bool(cond))
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             "" if not detail else " | " + str(detail)))

    # L1-L4: the fee function itself, exact
    chk("L1 a 1,000 CNY trade pays the 5-yuan floor, not 2.5bp",
        abs(fee_bp(2.5, 5.0, 1000.0) - 50.0) < 1e-12, fee_bp(2.5, 5.0, 1000.0))
    chk("L2 a 1,000,000 CNY trade pays the proportional rate",
        abs(fee_bp(2.5, 5.0, 1e6) - 2.5) < 1e-12, fee_bp(2.5, 5.0, 1e6))
    chk("L3 the crossover notional is exactly 20,000 CNY (floor == 2.5bp)",
        abs(fee_bp(2.5, 5.0, 20000.0) - 2.5) < 1e-12)
    chk("L4 no floor means the proportional rate at any size",
        abs(fee_bp(2.5, 0.0, 1.0) - 2.5) < 1e-12 and abs(fee_bp(2.5, 0.0, 1e9) - 2.5) < 1e-12)

    # L5-L6: the closed form, both sides of the boundary
    n = neutral_nav(0.02, 2.5, 5.0)
    chk("L5 neutral NAV = 1e4*min_fee/(prop*dw) = 1,000,000 for dw=2% at 2.5bp",
        abs(n - 1e6) < 1e-9, n)
    chk("L6 exactly at the neutral NAV the floor does not bind; a hair below it, it does",
        abs(fee_bp(2.5, 5.0, n * 0.02) - 2.5) < 1e-12
        and fee_bp(2.5, 5.0, n * 0.02 * 0.999) > 2.5 + 1e-9)

    # L7-L9: a curve on a hand-built fixture, so the arithmetic is pinned, not trusted
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    face = {"idx": idx, "rp": pd.Series([0.0, 0.01, 0.0], index=idx),
            "rf": pd.Series(0.0, index=idx),
            "amt": pd.DataFrame({"A": [1e12, 1e12, 1e12]}, index=idx)}
    path = [(idx[0], {}, 1.0), (idx[1], {"A": 1.0}, 0.0), (idx[2], {"A": 1.0}, 0.0)]
    ser, rows, cnt = curve(face, 1000.0, 2.5, 5.0, k_bp=0.0, path=path)
    # one buy of the whole account: notional 1,000 -> 50bp on the traded weight 1.0
    want = (1 + 0.01) * (1 - 50.0 / 1e4)
    chk("L7 a 1,000 CNY account pays 50bp on the entry bar (fixture, exact)",
        abs(float(ser.iloc[-1]) - want) < 1e-12, float(ser.iloc[-1]))
    chk("L8 the fixture trade is counted as below the floor", cnt["legs_below_floor"] == 1,
        cnt)
    ser2, _r2, cnt2 = curve(face, 1e6, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L9 the same trade at 1,000,000 CNY pays 2.5bp and is not below the floor",
        abs(float(ser2.iloc[-1]) - (1 + 0.01) * (1 - 2.5 / 1e4)) < 1e-12
        and cnt2["legs_below_floor"] == 0, (float(ser2.iloc[-1]), cnt2))

    # L10: with the floor switched off the two schedules must be bit-identical
    ser3, _r3, _c3 = curve(face, 1000.0, 2.5, 0.0, k_bp=0.0, path=path)
    ser4, _r4, _c4 = curve(face, 1000.0, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L10 the floor is the only difference between the two arms (no-floor is cheaper)",
        float(ser3.iloc[-1]) > float(ser4.iloc[-1]) + 1e-9)

    # L11: a bigger account never earns less under a floor (monotone in capital)
    small, _a, _b = curve(face, 1e3, 2.5, 5.0, k_bp=0.0, path=path)
    big, _c, _d = curve(face, 5e5, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L11 monotone in capital: 500,000 beats 1,000 on the same path (50bp -> 2.5bp)",
        float(big.iloc[-1]) > float(small.iloc[-1]) + 1e-9)

    # L12: a size we did not price yields no claim
    chk("L12 an out-of-ladder neutral point refuses a verdict",
        _verdict([{"cagr": 0.05, "ref_cagr": 0.06}], 5e8, 1e9, (1e4, 1e7))
        == "INSUFFICIENT_LADDER")
    chk("L13 a small rung that matches the 8bp arm reports no floor effect",
        _verdict([{"cagr": 0.06, "ref_cagr": 0.06}], 1e5, 1e6, (1e4, 1e7))
        == "NO_FLOOR_EFFECT")

    print("selftest %d/%d" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def main(argv):
    argv = [a for a in argv[1:]]
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    out = run()
    print("min capital: %s | neutral vs 8bp model %.0f CNY | vs real %.0f CNY"
          % (out["verdict"], out["fee_neutral_vs_model_nav"] or 0,
             out["fee_neutral_vs_real_nav"] or 0))
    print("\n capital      schedule   cagr   vs 8bp    below-floor   fee CNY")
    for r in out["ladder"]:
        print(" %9.0f  %-10s %6.2f%%  %+6.2fpp  %8.2f%%   %9.0f"
              % (r["capital"], r["schedule"], 100 * (r["cagr"] or 0),
                 r.get("delta_vs_8bp_pp") or 0,
                 100 * (r["share_below_floor"] or 0), r["fee_cny_total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))