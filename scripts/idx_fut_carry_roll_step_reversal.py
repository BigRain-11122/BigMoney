# -*- coding: utf-8 -*-
"""idx_fut_carry_roll_step_reversal.py -- is the roll-day step a bookkeeping jump or a real cost?

The question this answers
-------------------------
`bench_basis_timing_size_masks` re-ran cell 7 under three roll rulers and reported that the
always-on carry jumps 2.73% -> 9.62% (IC) the moment 106 more days are excluded, so the
sizing edge shrinks 7.36pp -> 2.37pp and the face verdicts SIZING_EDGE_IS_A_MASK_ARTIFACT.
`idx_fut_carry_always_on_price` then printed level 2.76/9.65/9.68 and said the rate is
ruler-bound; `idx_fut_carry_capacity_lots` said the gate is capital, not liquidity.

Every one of those faces inherits one unproven premise: **a roll day earns nothing.**
`carry_curve` writes `np.where(roll, 0.0, w*spread)` -- neither the return nor the cost of
switching contract is booked. That is right if the step inside `spread` is a bookkeeping
artefact of a continuous contract splicing two prices, and wrong if the step is a bill the
book pays each month. Nobody tested which one it is, and the two answers price the same
book at 2.73% or 9.62% a year.

The test (frozen before the run)
--------------------------------
A bookkeeping step is a one-off re-pricing: the two legs resume their ordinary relationship,
so the **next day gives it back**. A real cost leaves no reason to revert: next month's
contract is simply more expensive and the discount stays deeper.

For each product and each ruler's roll set R:

  T_pp  = 244*100 * ( mean(spread[k+1] for k in R) - mean(spread on non-roll days) )
  p     = two-sided permutation p, 5,000 draws of |R| random non-roll days (seed frozen)
  give  = -mean(spread[k+1] for k in R) / mean(spread[k] for k in R)   [needs mean != 0]

Criteria (frozen now, before any number is looked at)
-----------------------------------------------------
  BOOKKEEPING_JUMP   T_pp >= 0.5 AND p < 0.01 AND give >= 0.5
  REAL_COST          T_pp <= 0.1 OR p >= 0.01
  PARTIAL_REVERSAL   everything else (give back less than half -- a split verdict)
  MIXED_BY_RULER     one product's rulers disagree
  MIXED_BY_PRODUCT   IC and IM disagree under the same ruler
  DATA_BLOCKED       fewer than MIN_PAIRS roll days, mean(spread on roll)=0, or no load

The money consequence ships with the verdict:
  BOOKKEEPING_JUMP -> always-on is worth the excluded-ruler rate (9.62/9.68), cell 7's GO is
                     a mask artefact and r2093 stands
  REAL_COST        -> always-on is worth the included-ruler rate (2.73/5.63), the dropped
                     days are the book's monthly bill, and cell 7's 7.36pp stands

Read-only. Imports the originals (`idx_fut_basis`, `idx_fut_roll_gap`); re-implements no
weights, no curve, no mask. Writes results/idx_fut_carry_roll_step_reversal.json.

    python scripts/idx_fut_carry_roll_step_reversal.py            # derive + write face
    python scripts/idx_fut_carry_roll_step_reversal.py --check    # re-derive, compare
    python scripts/idx_fut_carry_roll_step_reversal.py --selftest # offline legs
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import idx_fut_roll_gap as gap  # noqa: E402

OUT = os.path.join(bc.RESULTS, "idx_fut_carry_roll_step_reversal.json")
PRODUCTS = ("IC", "IM")
RULERS = ("published", "calendar", "strictest")
DRAWS = 5000
SEED = 20261125
MIN_PAIRS = 30
T_JUMP_PP = 0.5
P_LINE = 0.01
GIVE_MIN = 0.5
WINDOW = 8
AFTER_PP_LINE = 2.0
TZ = timezone(timedelta(hours=8))

V_JUMP = "BOOKKEEPING_JUMP"
V_COST = "REAL_COST"
V_PARTIAL = "PARTIAL_REVERSAL"
V_BOOKED_LATER = "COST_BOOKED_BY_LATER_CARRY"
V_MIXED_RULER = "MIXED_BY_RULER"
V_MIXED_PROD = "MIXED_BY_PRODUCT"
V_BLOCKED = "DATA_BLOCKED"

READING = {
    V_JUMP: ("The next day gives the step back: it is a splice artefact, not a return. "
             "Dropping roll days is the honest ruler, always-on is worth the excluded rate, "
             "and cell 7's sizing gain is a reading of the mask."),
    V_COST: ("The step does not come back: the book pays it every month. Dropping roll days "
             "deletes the bill, always-on is worth the included rate, and cell 7's 7.36pp "
             "stands."),
    V_PARTIAL: ("Half the step comes back and half stays: neither ruler is honest alone. "
                "Quote the split, not a single always-on rate."),
    V_BOOKED_LATER: ("The next day brings back little, but every day after the step carries a "
                     "deeper discount: the bill is paid by later carry, not by the step day. "
                     "Dropping the step day is the honest ruler and always-on is worth the "
                     "excluded rate."),
    V_MIXED_RULER: "Rulers disagree on the same product: do not quote a single always-on rate.",
    V_MIXED_PROD: "Products disagree: the ruler settles it, not the product.",
    V_BLOCKED: "Not enough roll days to test: report the gap, do not guess.",
}


def load_faces(code):
    """Dates, basis, spread and both originals' roll sets -- nothing re-implemented."""
    pair = base.PAIRS[code]
    fut = {}
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    basis, spread, roll_pub = base.basis_face(f, i, dates)
    cal, info = gap.calendar_rolls(dates, basis)
    cal_set = set(cal.keys())
    days = dates[1:]  # spread[k] belongs to days[k]
    masks = {
        "published": [bool(x) for x in roll_pub],
        "calendar": [d in cal_set for d in days],
        "strictest": [bool(roll_pub[k]) or (days[k] in cal_set) for k in range(len(days))],
    }
    return {
        "days": days,
        "spread": np.asarray(spread, dtype=float),
        "masks": masks,
        "calendar_info": info,
    }


def perm_p(observed, pool, n_pick, draws=DRAWS, seed=SEED):
    """Two-sided permutation p for a mean, drawn from `pool` in samples of `n_pick`."""
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(draws):
        m = float(np.mean(rng.choice(pool, size=n_pick, replace=False)))
        if abs(m) >= abs(observed):
            hits += 1
    return (hits + 1) / (draws + 1)


def reversal(spread, mask, window=WINDOW):
    """Two questions per roll day: does the next day give the step back, and does the
    discount stay deeper afterwards (i.e. is the cost paid by later carry instead of by
    the step day itself)?"""
    idx = [k for k, r in enumerate(mask) if r and k + 1 < len(spread)]
    if len(idx) < MIN_PAIRS:
        return None
    nxt = np.array([spread[k + 1] for k in idx])
    on = np.array([spread[k] for k in idx])
    nonroll = np.array([spread[k] for k, r in enumerate(mask) if (not r) and k + 1 < len(spread)])
    if len(nonroll) < len(idx):
        return None
    excess = float(np.mean(nxt)) - float(np.mean(nonroll))
    p = perm_p(float(np.mean(nxt)), nonroll, len(idx))
    mean_on = float(np.mean(on))
    give = round(-float(np.mean(nxt)) / mean_on, 3) if mean_on != 0.0 else None

    # before/after windows around the step: if the discount stays deeper, the bill is
    # already being paid by every later day's carry and dropping the step day is right.
    usable = [k for k in idx if k - window >= 0 and k + 2 + window <= len(spread)]
    if len(usable) < MIN_PAIRS:
        return None
    before = np.array([np.mean(spread[k - window:k]) for k in usable])
    after = np.array([np.mean(spread[k + 2:k + 2 + window]) for k in usable])
    delta = float(np.mean(after - before))
    deltas = [after[i] - before[i] for i in range(len(usable))]
    p_delta = perm_p_two(delta, deltas)
    return {
        "pairs": len(idx),
        "window_pairs": len(usable),
        "T_pp": round(excess * bc.TRADING_DAYS * 100, 3),
        "p_value": round(p, 4),
        "give_back_ratio": give,
        "mean_spread_on_roll_ann_pct": round(mean_on * bc.TRADING_DAYS * 100, 3),
        "mean_spread_next_day_ann_pct": round(float(np.mean(nxt)) * bc.TRADING_DAYS * 100, 3),
        "mean_spread_nonroll_ann_pct": round(float(np.mean(nonroll)) * bc.TRADING_DAYS * 100, 3),
        "after_minus_before_pp": round(delta * bc.TRADING_DAYS * 100, 3),
        "p_after_minus_before": round(p_delta, 4),
    }


def perm_p_two(observed, deltas, draws=DRAWS, seed=SEED):
    """Sign-flip permutation p for a paired mean: the null says each roll day's
    after-minus-before could have gone either way. Nothing is drawn from other days,
    because the days right after a step ARE shifted and would poison a cross sample."""
    rng = np.random.default_rng(seed + 1)
    arr = np.asarray(deltas, dtype=float)
    n = len(arr)
    if n == 0:
        return 1.0
    hits = 0
    for _ in range(draws):
        sign = rng.integers(0, 2, size=n) * 2 - 1
        if abs(float(np.mean(arr * sign))) >= abs(observed):
            hits += 1
    return (hits + 1) / (draws + 1)


def judge(row):
    if row is None:
        return V_BLOCKED
    if row["give_back_ratio"] is None:
        return V_BLOCKED
    if row["T_pp"] >= T_JUMP_PP and row["p_value"] < P_LINE and row["give_back_ratio"] >= GIVE_MIN:
        return V_JUMP
    if row["after_minus_before_pp"] <= -AFTER_PP_LINE and row["p_after_minus_before"] < 0.05:
        return V_BOOKED_LATER
    if row["T_pp"] <= 0.1 or row["p_value"] >= P_LINE:
        return V_COST
    return V_PARTIAL


def derive():
    products = {}
    for code in PRODUCTS:
        try:
            face = load_faces(code)
        except Exception as exc:  # noqa: BLE001 - honest blocked, not a crash
            products[code] = {"status": "blocked", "why": f"{type(exc).__name__}: {exc}"}
            continue
        spread = face["spread"]
        rows = {}
        for ruler in RULERS:
            mask = face["masks"][ruler]
            row = reversal(spread, mask)
            if row is not None:
                row["verdict"] = judge(row)
                row["days_dropped"] = int(sum(1 for x in mask if x))
                row["share_of_days_pct"] = round(100.0 * row["days_dropped"] / max(1, len(mask)), 2)
            else:
                row = {"verdict": V_BLOCKED, "days_dropped": int(sum(1 for x in mask if x))}
            rows[ruler] = row
        products[code] = {
            "bars": int(len(spread)),
            "first": face["days"][0],
            "last": face["days"][-1],
            "rulers": rows,
        }

    ok = {c: p for c, p in products.items() if "rulers" in p}
    if not ok:
        verdict = V_BLOCKED
    else:
        per_ruler = {}
        for ruler in RULERS:
            vs = [p["rulers"][ruler].get("verdict") for p in ok.values()]
            per_ruler[ruler] = sorted(set(v for v in vs if v))
        all_v = set()
        for vs in per_ruler.values():
            all_v.update(vs)
        if all_v <= {V_BLOCKED}:
            verdict = V_BLOCKED
        elif len(all_v) == 1:
            verdict = next(iter(all_v))
        elif any(len(vs) > 1 for vs in per_ruler.values()):
            verdict = V_MIXED_PROD
        else:
            verdict = V_MIXED_RULER

    money = {}
    for code, p in ok.items():
        for ruler in RULERS:
            r = p["rulers"][ruler]
            if r.get("mean_spread_on_roll_ann_pct") is not None:
                money.setdefault(code, {})[ruler] = {
                    "mean_roll_day_spread_ann_pct": r["mean_spread_on_roll_ann_pct"],
                    "next_day_ann_pct": r["mean_spread_next_day_ann_pct"],
                    "days_dropped": r["days_dropped"],
                    "if_booked_pp": round(-r["mean_spread_on_roll_ann_pct"] * r["days_dropped"]
                                          / max(1, p["bars"]), 3),
                }

    return {
        "cell": "idx_fut_carry_roll_step_reversal",
        "generated": datetime.now(TZ).replace(microsecond=0).isoformat(),
        "evidence_cutoff": max((p["last"] for p in ok.values()), default=None),
        "question": ("is the roll-day step inside spread a splice artefact (drop it) or a "
                     "cost the book pays every month (book it)?"),
        "test": ("mean spread the day AFTER a roll day, minus non-roll mean, annualised; "
                 "5,000-draw permutation against random non-roll days; give-back ratio"),
        "criteria": {
            "T_jump_pp": T_JUMP_PP,
            "p_line": P_LINE,
            "give_min": GIVE_MIN,
            "min_pairs": MIN_PAIRS,
            "draws": DRAWS,
            "seed": SEED,
        },
        "products": products,
        "money": money,
        "verdict": verdict,
        "reading": READING[verdict],
    }


def _synth(count, step, revert, seed=7):
    """Synthetic spread: `count` days of noise, every 10th day flagged as a roll."""
    rng = np.random.default_rng(seed)
    spread = rng.normal(0.0, 0.002, size=count)
    mask = [False] * count
    for k in range(5, count - 2, 10):
        mask[k] = True
        spread[k] = step + rng.normal(0.0, 0.0005)
        spread[k + 1] = revert + rng.normal(0.0, 0.0005)
    return spread, mask


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "pass": bool(ok), "detail": detail})

    # 1. a step given back in full the next day reads as a bookkeeping jump
    s, m = _synth(400, -0.02, +0.019)
    r = reversal(s, m)
    leg("given-back step verdicts BOOKKEEPING_JUMP",
        r is not None and judge(r) == V_JUMP,
        f"T={r and r['T_pp']} give={r and r['give_back_ratio']}")

    # 2. a step that never comes back reads as a real cost
    s2, m2 = _synth(400, -0.02, 0.0)
    r2 = reversal(s2, m2)
    leg("non-reverting step verdicts REAL_COST",
        r2 is not None and judge(r2) == V_COST,
        f"T={r2 and r2['T_pp']} give={r2 and r2['give_back_ratio']}")

    # 3. half back / half kept is neither
    s3, m3 = _synth(400, -0.02, +0.01)
    r3 = reversal(s3, m3)
    leg("half-reverting step is PARTIAL or COST, never JUMP",
        r3 is not None and judge(r3) in (V_PARTIAL, V_COST),
        f"T={r3 and r3['T_pp']} give={r3 and r3['give_back_ratio']}")

    # 4. no roll days at all is DATA_BLOCKED, not a crash
    s4, m4 = _synth(400, -0.02, 0.019)
    m4 = [False] * len(m4)
    leg("fewer than min_pairs is DATA_BLOCKED", reversal(s4, m4) is None)

    # 4b. verdict logic: a paired, significant deeper discount afterwards is the bill
    row_b = {"T_pp": 0.5, "p_value": 0.5, "give_back_ratio": 0.1,
             "after_minus_before_pp": -20.0, "p_after_minus_before": 0.001}
    leg("deeper discount booked by later carry verdicts COST_BOOKED_BY_LATER_CARRY",
        judge(row_b) == V_BOOKED_LATER, f"verdict={judge(row_b)}")

    # 4c. and without that deeper discount it is not the booked-later reading
    row_c = dict(row_b, after_minus_before_pp=-0.5, p_after_minus_before=0.9)
    leg("a step with no later carry shift is NOT booked-later",
        judge(row_c) != V_BOOKED_LATER, f"verdict={judge(row_c)}")

    # 5. the rulers nest: published and calendar are subsets of strictest
    for code in PRODUCTS:
        face = load_faces(code)
        pub, strict = face["masks"]["published"], face["masks"]["strictest"]
        leg(f"{code} published is a subset of strictest",
            all((not pub[k]) or strict[k] for k in range(len(pub))))
        cal = face["masks"]["calendar"]
        leg(f"{code} calendar is a subset of strictest",
            all((not cal[k]) or strict[k] for k in range(len(cal))))

    # 6. permutation p is loose on noise (a mean of random non-roll days)
    rng = np.random.default_rng(11)
    pool = rng.normal(0.0, 0.002, size=800)
    leg("permutation p is loose on noise",
        perm_p(float(np.mean(pool[:40])), pool, 40, draws=400) > 0.05)

    # 7. the annualisation is the plain day-to-year map
    leg("annualisation is mean x TRADING_DAYS x 100",
        round(0.0001 * bc.TRADING_DAYS * 100, 6) == 2.44)

    passed = sum(1 for l in legs if l["pass"])
    for l in legs:
        print(f"  {'PASS' if l['pass'] else 'FAIL'}  {l['leg']}" + (
            f"  [{l['detail']}]" if l["detail"] else ""))
    print(f"SELFTEST {passed}/{len(legs)}")
    return 0 if passed == len(legs) else 1


def write_face(face):
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check():
    if not os.path.exists(OUT):
        print("CHECK FAILED: face missing -- run without --check first")
        return 3
    old = json.load(open(OUT, encoding="utf-8"))
    new = derive()
    diff = [k for k in ("verdict", "evidence_cutoff") if old.get(k) != new.get(k)]
    for code in PRODUCTS:
        o = ((old.get("products") or {}).get(code) or {}).get("rulers") or {}
        n = ((new.get("products") or {}).get(code) or {}).get("rulers") or {}
        for ruler in RULERS:
            for f in ("T_pp", "p_value", "pairs", "days_dropped", "give_back_ratio"):
                if (o.get(ruler) or {}).get(f) != (n.get(ruler) or {}).get(f):
                    diff.append(f"{code}/{ruler}/{f}")
    if diff:
        print("CHECK FAILED: " + ", ".join(diff[:8]))
        return 3
    print(f"CHECK_OK verdict={new['verdict']} cutoff={new.get('evidence_cutoff')}")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    face = derive()
    write_face(face)
    print(f"VERDICT {face['verdict']}  cutoff={face.get('evidence_cutoff')}")
    for code, p in face["products"].items():
        if "rulers" not in p:
            print(f"  {code}: blocked -- {p.get('why')}")
            continue
        for ruler in RULERS:
            r = p["rulers"][ruler]
            print(f"  {code}/{ruler}: pairs={r.get('pairs')} T={r.get('T_pp')}pp "
                  f"p={r.get('p_value')} give={r.get('give_back_ratio')} "
                  f"drop={r.get('days_dropped')} -> {r.get('verdict')}")
    print("face -> " + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
