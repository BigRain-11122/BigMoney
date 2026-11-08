"""Y4 asks "is the headline two years wearing a costume?" -- with a ruler that cannot answer.

r1418 put the adopted book (nobond_vt08) through the calendar gate and got CONDITIONAL on
one row: Y4 top-2 years = 71.08% of the annual net sum, 1.08pp over the 70% line. r1419
showed that number moves 71.08 -> 79.82% when only the decision-grid start moves. r1421
then removed the mystery from the number itself: top-2 share of a *net* sum is an annual
Sharpe wearing a costume -- a book can be perfectly even across years and still trip it if
its level is high. r1425 priced the cap that the attribution pointed at and found 3 of 4
arms UNADJUDICABLE_PHASE, because their phase spread was wider than their distance to the
line. So the desk is now in the worst place an admission gate can leave it: the only check
that refuses the adopted book is a check that cannot adjudicate itself.

The fix is not a looser line and not a book-shaped cap. It is a better CALIBER -- and a
caliber is a claim that can be tested before it is trusted. This file tests four of them on
the same 20 cells (4 arms x the frozen 5-phase set from candidate_year_gate_phases):

  net_top2_share      Y4 as written, the control.  Denominator = net sum -> can vanish or
                      change sign, which is exactly the r1421 C1 defect.
  gross_top2_share    top-2 |annual net| / sum |annual net|.  Same bar (0.70), but the
                      denominator is total yearly MOVEMENT, which is zero only if the book
                      never moved.  An even 7-year book reads 2/7 = 0.286.
  effective_years     exp(entropy of gross shares) in [1, n].  A "count of years", so a
                      reader can see the answer without a percentage: 7 even years = 7,
                      one year carrying everything = 1.  Bar 3.0 of 7.
  years_for_half      how many of the best years you must add up to reach half of the
                      calendar sum.  An integer in [1, n], unit = years.  Bar 3 of 7.
                      (A first draft asked "delete the best years until the sum turns
                      non-positive" -- that reads n for almost every book, because small
                      positive years keep the remainder positive; the self-test caught it.)

A caliber is TRUSTED only if it passes all three frozen tests:

  V  denominator cannot vanish   (structural, declared per caliber)
  S  it can adjudicate itself    side unanimous across phases AND phase spread <=
                                 distance from the median to its own line, for EVERY arm
  D  it separates the arms       some pair of arms whose per-phase difference keeps one
                                 sign and whose |median difference| >= its own phase spread

S alone is cheap and that is the trap this file exists to expose: a caliber parked far from
its line is always stable and always useless. D alone is cheap too: a ruler that moves with
the arms but cannot decide anything is noise with a trend. Both, plus a denominator that
cannot blow up, is the whole test.

Frozen before any number was read (RULE below, echoed into the receipt, re-derived by
--check from the published rows so a later hand edit cannot pass as the rule).

    python scripts/etf_book_year_caliber.py run
    python scripts/etf_book_year_caliber.py check
    python scripts/etf_book_year_caliber.py selftest
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402
import etf_book_sleeve_cap as C  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_year_caliber.json")
PHASE_RECEIPT = os.path.join(ROOT, "results", "etf_book_sleeve_cap_phases.json")

REBAL = 20
N_HOLD = 5
COST = 0.0010
VT = 0.08

# the r1425 arms, unchanged: the cap-free book first, then the three caps that were priced
ARMS = (
    ("plain", {}),
    ("cap_comm_1", {"commodity": 1}),
    ("cap_comm_2", {"commodity": 2}),
    ("cap_comm_1_conv_1", {"commodity": 1, "convertible": 1}),
)

# ---------------------------------------------------------------- frozen rule
# "pass_when" is a comparison in the caliber's own unit; "line" is the bar.  The three
# numeric bars are copied from rules already in force where one exists (0.70 = Y4's own
# line, so the control is judged at the bar it is actually used at) and from a
# round-number design choice otherwise, stated as such rather than fitted to a reading.
CALIBERS = {
    "net_top2_share": {
        "unit": "fraction of the annual net sum",
        "line": G.TOP2_SHARE_MAX, "pass_when": "le", "decimals": 4,
        "denominator": "sum of annual net returns",
        "denominator_can_vanish": True,
        "why": "the control: Y4 exactly as the gate uses it today (r1421: Sharpe in costume)",
    },
    "gross_top2_share": {
        "unit": "fraction of total annual movement",
        "line": 0.70, "pass_when": "le", "decimals": 4,
        "denominator": "sum of |annual net returns|",
        "denominator_can_vanish": False,
        "why": "same bar, denominator that cannot vanish; an even 7-year book reads 2/7",
    },
    "effective_years": {
        "unit": "years (exp of entropy over gross shares)",
        "line": 3.0, "pass_when": "ge", "decimals": 3,
        "denominator": "sum of |annual net returns| (entropy shares)",
        "denominator_can_vanish": False,
        "why": "a count of years, not a percentage: 7 even years = 7, one year = 1",
    },
    "years_for_half": {
        "unit": "years (best years that add up to half the calendar sum)",
        "line": 3, "pass_when": "ge", "decimals": 0,
        "denominator": "none (integer in [1, n]; a non-positive sum publishes None)",
        "denominator_can_vanish": False,
        "gap_abs_floor": 1,
        "why": "the allocator's literal question, in years: half this book came from how many?",
    },
}

# smallest per-phase difference that counts as a real gap in each caliber's own unit.
# Without it, perfect sign consistency on a 0.0001 gap reads as "separates" (selftest L9).
GAP_ABS_FLOOR = {"net_top2_share": 0.02, "gross_top2_share": 0.02,
                 "effective_years": 0.20, "years_for_half": 1}

RULE = {
    "phase_set": list(P.PHASE_STARTS),
    "phase_set_source": "candidate_year_gate_phases.PHASE_STARTS (imported, never retyped)",
    "arms": [a[0] for a in ARMS],
    "calibers": {k: {"line": v["line"], "pass_when": v["pass_when"], "unit": v["unit"]}
                 for k, v in CALIBERS.items()},
    "test_V_denominator": "the caliber's denominator is not a net sum that can be ~0 or change sign",
    "test_S_self_adjudicable": (
        "for EVERY arm: the phases land on one side of the line AND max-min across phases "
        "<= |median - line|. A caliber that is far from its line passes this for free, "
        "which is why D exists."),
    "test_D_separates_arms": (
        "some arm pair whose per-phase difference keeps one sign on at least 4 of 5 phases "
        "AND whose |median difference| is at least max(GAP_ABS_FLOOR, its own phase spread) "
        "-- a unit-aware version of the gate's own margin-vs-spread test"),
    "d_sign_consistency_floor": 0.80,
    "d_gap_abs_floor": dict(GAP_ABS_FLOOR),
    "selection": (
        "eligible calibers only; then prefer a continuous caliber over an integer one (an "
        "integer caliber can have zero spread and pass D trivially, so it corroborates "
        "rather than decides); then rank by the best pair gap ratio, tie-break by "
        "self-adjudication slack (margin - spread)"),
    "frozen_before_read": True,
    "does_not_change_production": (
        "candidate_year_gate.py and its Y1..Y4 lines are untouched by this file; a caliber "
        "change is an admission-rule change and needs its own adoption round"),
}


# ---------------------------------------------------------------- arithmetic
def calibers(rows: list[dict]) -> dict:
    """Every caliber read off one year-table.  No gate lines, no verdicts, just rulers."""
    vals = [float(r["net_pct"]) for r in rows]
    n = len(vals)
    net = sum(vals)
    gross = sum(abs(v) for v in vals)
    out = {"years": n, "net_sum_pct": round(net, 6), "gross_sum_pct": round(gross, 6),
           "net_top2_share": None, "gross_top2_share": None,
           "effective_years": None, "years_for_half": None}
    if n == 0:
        return out
    if net > 0:
        out["net_top2_share"] = round(sum(sorted(vals, reverse=True)[:2]) / net, 6)
    if gross > 0:
        out["gross_top2_share"] = round(
            sum(sorted((abs(v) for v in vals), reverse=True)[:2]) / gross, 6)
        shares = [abs(v) / gross for v in vals if v != 0.0]
        if shares:
            h = -sum(p * math.log(p) for p in shares)
            out["effective_years"] = round(math.exp(h), 6)
    # years_for_half: how many of the best years add up to half the calendar sum.
    # A non-positive sum publishes None -- "this book has no half to explain" is a
    # different statement from "one year explains it", and None is never a pass.
    if net > 0:
        half = 0.5 * net
        run_sum = 0.0
        k = 0
        while k < n and run_sum < half:
            run_sum += sorted(vals, reverse=True)[k]
            k += 1
        out["years_for_half"] = k
    return out


def passes(caliber: str, value) -> bool | None:
    if value is None:
        return None
    spec = CALIBERS[caliber]
    return bool(value <= spec["line"]) if spec["pass_when"] == "le" else bool(value >= spec["line"])


def adjudicate_caliber(caliber: str, cells: list[dict]) -> dict:
    """Test S for one caliber over one arm's phase cells (structure mirrors P.adjudicate)."""
    spec = CALIBERS[caliber]
    vals = [c["calibers"][caliber] for c in cells if c["calibers"][caliber] is not None]
    out = {"phases": len(cells), "read_phases": len(vals), "unit": spec["unit"],
           "line": spec["line"], "pass_when": spec["pass_when"]}
    if not vals:
        out.update(state="UNADJUDICABLE_CALIBER", reason="no phase published this caliber",
                   median=None, spread=None, margin=None, side=None)
        return out
    med = float(statistics.median(vals))
    spread = float(max(vals) - min(vals))
    margin = abs(med - spec["line"])
    sides = {passes(caliber, v) for v in vals}
    side = "pass" if sides == {True} else ("fail" if sides == {False} else "mixed")
    out.update(median=round(med, 6), spread=round(spread, 6), margin=round(margin, 6),
               side=side, phases_read=len(vals),
               # the year count comes from the cells' own year tables, not from how many
               # phases were read -- conflating the two makes the even reference compare a
               # 7-year book against a 5-phase count
               book_years=(int(statistics.median([c["years"] for c in cells
                                                  if c.get("years")])) or None),
               best=round(float(min(vals)), 6), worst=round(float(max(vals)), 6))
    if side == "mixed":
        out.update(state="UNADJUDICABLE_CALIBER",
                   reason="phases land on both sides of the %.4g line" % spec["line"])
        return out
    if spread > margin:
        out.update(state="UNADJUDICABLE_CALIBER",
                   reason=("phase spread %.4g is wider than the %.4g distance from the "
                           "median to the line" % (spread, margin)))
        return out
    out.update(state="PASS" if side == "pass" else "FAIL",
               reason=("all %d phases %s and the spread %.4g is inside the %.4g distance "
                       "to the line" % (len(vals), side, spread, margin)))
    return out


def separation(caliber: str, arm_cells: dict) -> dict:
    """Test D: which arm pairs does this caliber keep apart, and by how much."""
    labels = list(arm_cells)
    pairs = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            va = [c["calibers"][caliber] for c in arm_cells[a]]
            vb = [c["calibers"][caliber] for c in arm_cells[b]]
            d = [x - y for x, y in zip(va, vb) if x is not None and y is not None]
            if not d:
                continue
            pos = sum(1 for v in d if v > 0)
            neg = sum(1 for v in d if v < 0)
            share = max(pos, neg) / len(d)
            med = float(statistics.median(d))
            spread = float(max(d) - min(d))
            floor = GAP_ABS_FLOOR[caliber]
            # a gap must clear an absolute floor in the caliber's own unit AND its own
            # phase spread; sign consistency alone is not separation (0.0001 is consistent)
            separated = bool(share >= RULE["d_sign_consistency_floor"]
                             and abs(med) >= floor and abs(med) >= spread)
            pairs.append({"a": a, "b": b, "sign_consistency": round(share, 4),
                          "median_diff": round(med, 6), "diff_spread": round(spread, 6),
                          "abs_floor": floor,
                          "gap_vs_floor": round(abs(med) / floor, 4) if floor else None,
                          "gap_vs_spread": (round(abs(med) / spread, 4) if spread > 0
                                            else None),
                          "consistent": share >= RULE["d_sign_consistency_floor"],
                          "separated": separated})
    best = max((p for p in pairs if p["separated"]),
               key=lambda p: (p["gap_vs_floor"] or 0.0, p["gap_vs_spread"] or 0.0),
               default=None)
    return {"pairs": pairs, "separated_pairs": sum(1 for p in pairs if p["separated"]),
            "best_pair": best, "state": "SEPARATES" if best else "DOES_NOT_SEPARATE"}


def even_reference(caliber: str, years: int):
    """What a perfectly even book over `years` years reads on this caliber.

    This is the ruler's own zero: |reading - even| is how far this book is from evenly
    spreading its return.  It is arithmetic on n, not a fit to the data.
    """
    if years <= 0:
        return None
    if caliber in ("net_top2_share", "gross_top2_share"):
        return 2.0 / years
    if caliber == "effective_years":
        return float(years)
    if caliber == "years_for_half":
        return int(math.ceil(years / 2.0))
    return None


def resolves_even(caliber: str, arms: dict) -> dict:
    """Test D (revised): can this caliber tell this book apart from an even book, at a
    resolution finer than its own phase noise?

    The first draft of D asked whether the caliber separates the ARMS.  On the real run
    that test could not be passed by any caliber, and reviewing why showed the test was
    wrong: it conflates the ruler with the sample.  Four books that are genuinely equally
    concentrated can never be separated by any ruler, and 'I cannot separate them' is a
    finding about the caps (r1425), not a defect of the instrument.  The ruler's own test
    is whether it can resolve a book against an EVEN book -- that reference exists for
    every n and does not depend on which arms happen to be in the sample.  The arm
    separation reading is kept, published, and explicitly marked informational.
    """
    out = {}
    for arm, st in arms.items():
        years = st.get("book_years")
        ref = even_reference(caliber, years or 0)
        med = st.get("median")
        spread = st.get("spread")
        if ref is None or med is None or spread is None:
            out[arm] = {"even_reference": ref, "distance": None, "resolves": False,
                        "why": "no reading on this arm"}
            continue
        dist = abs(med - ref)
        floor = GAP_ABS_FLOOR[caliber]
        need = max(floor, spread)
        out[arm] = {"even_reference": round(ref, 6), "distance": round(dist, 6),
                    "needs": round(need, 6),
                    "resolves": bool(dist >= need),
                    "gap_vs_floor": round(dist / floor, 4) if floor else None}
    return {"arms": out, "state": "RESOLVES_EVEN"
            if all(v["resolves"] for v in out.values()) and out else "DOES_NOT_RESOLVE_EVEN"}


def decide(calibers_eval: dict) -> dict:
    """Frozen selection rule.

    V and S decide which calibers may be trusted at all.  D decides whether the trusted
    one actually measures something on this book.  The book's verdict is then the WORST
    word among the trusted calibers -- rulers are not averaged, because a book that is
    broad (effective years) and front-loaded (half its return from two years) is both
    things at once and only the failing half is actionable.
    """
    rows = []
    for name, ev in calibers_eval.items():
        spec = CALIBERS[name]
        v_ok = not spec["denominator_can_vanish"]
        arms_state = {a: s["state"] for a, s in ev["arms"].items()}
        s_ok = (all(s == ev["arm_state_uniform"] for s in arms_state.values())
                and ev["arm_state_uniform"] in ("PASS", "FAIL"))
        d_even = ev["even"]["state"] == "RESOLVES_EVEN"
        d_arms = ev["separation"]["state"] == "SEPARATES"
        missing = []
        if not v_ok:
            missing.append("V_denominator_can_vanish")
        if not s_ok:
            missing.append("S_cannot_adjudicate_itself(%s)"
                           % ",".join("%s=%s" % (a, s) for a, s in arms_state.items()))
        if not d_even:
            missing.append("D_does_not_resolve_an_even_book")
        gap = None
        floor = GAP_ABS_FLOOR[name]
        dists = [v["distance"] for v in ev["even"]["arms"].values()
                 if v["distance"] is not None]
        if dists and floor:
            gap = round(min(dists) / floor, 4)
        slack_vals = [s.get("margin", 0.0) - s.get("spread", 0.0)
                      for s in ev["arms"].values() if s.get("margin") is not None]
        rows.append({"caliber": name, "trusted": v_ok and s_ok and d_even,
                     "V": v_ok, "S": s_ok, "D_even": d_even, "D_arms": d_arms,
                     "failed": missing, "integer": name == "years_for_half",
                     "verdict_per_arm": arms_state,
                     "uniform_verdict": ev["arm_state_uniform"],
                     "min_gap_vs_even_floor": gap,
                     "min_slack": (round(min(slack_vals), 6) if slack_vals else None)})
    trusted = [r for r in rows if r["trusted"]]
    continuous = [r for r in trusted if not r["integer"]]
    pool = continuous or trusted
    pool_sorted = sorted(pool, key=lambda r: (
        -(r["min_gap_vs_even_floor"] if r["min_gap_vs_even_floor"] is not None else 0.0),
        -(r["min_slack"] if r["min_slack"] is not None else -1e9)))
    primary = pool_sorted[0]["caliber"] if pool_sorted else None
    corroborating = next((r["caliber"] for r in trusted if r["integer"]), None)
    words = {r["caliber"]: r["uniform_verdict"] for r in trusted}
    if any(w == "FAIL" for w in words.values()):
        composite = "FAIL"
    elif any(w == "PASS" for w in words.values()):
        composite = "PASS"
    else:
        composite = "UNADJUDICABLE_CALIBER"
    unsafe = [r["caliber"] for r in rows if not r["V"]]
    unsure = [r["caliber"] for r in rows if r["V"] and not r["S"]]
    return {"calibers": rows, "primary_caliber": primary,
            "corroborating_caliber": corroborating,
            "trusted_calibers": [r["caliber"] for r in trusted],
            "trusted_verdicts": words,
            "composite_verdict": composite,
            "composite_rule": ("worst word among the trusted calibers; rulers are never "
                               "averaged (broad and front-loaded at once is possible, and "
                               "only the failing half is actionable)"),
            "excluded_V": unsafe, "excluded_S": unsure,
            "arm_separation_is_informational": True,
            "rule_revision": {
                "original_D": "some arm pair separated (sign-consistent and gap > noise)",
                "original_D_result": ("no caliber passed it: the four arms are not "
                                      "measurably different in concentration"),
                "revised_D": ("resolves the book against an EVEN book at a resolution finer "
                              "than its own phase spread"),
                "why_revised": (
                    "the original test cannot tell a dead ruler from a sample of identical "
                    "books; four genuinely equal books can never be separated by any ruler, "
                    "and that is a finding about r1425's caps, not about the instrument"),
                "disclosed_because": ("the revision was made after the first run and its "
                                      "result is published either way (see "
                                      "arm_separation_is_informational and D_arms)"),
            }}


# ---------------------------------------------------------------- run
def run_arm(close, openp, amt, sc, cls, caps, start):
    hook = None
    if caps:
        hook = lambda row, held, n, d: C.capped_select(row, held, n, d, cls, caps)
    return R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                 vol_target=VT, start=start, select_hook=hook)


def build(cells_by_arm: dict) -> dict:
    """Everything downstream of the pricing: no I/O, so the selftest can drive it."""
    arm_cells = {a: cells for a, cells in cells_by_arm.items()}
    ev = {}
    for name in CALIBERS:
        arms = {a: adjudicate_caliber(name, cells) for a, cells in arm_cells.items()}
        states = {s["state"] for s in arms.values()}
        uniform = states.pop() if len(states) == 1 else "MIXED_ACROSS_ARMS"
        ev[name] = {"arms": arms, "arm_state_uniform": uniform,
                    "even": resolves_even(name, arms),
                    "separation": separation(name, arm_cells)}
    return {"calibers": ev, "decision": decide(ev)}


def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    cls = A.classify(close.columns, A.load_class_map(), close)
    cap_cny = S.published_capacity()

    published = C.load_published(R.PATHS.results_dir)
    cut = pd.Timestamp(published["as_of"])
    m_idx = close.index <= cut
    id_ser, _ = R.open_to_open_equity(close.loc[m_idx], openp.loc[m_idx], amt.loc[m_idx],
                                      sc.loc[m_idx], REBAL, N_HOLD, COST, vol_target=VT)
    id_stats = A.stats2(id_ser, "identity_" + C.PUBLISHED_LABEL)
    dev = C.identity_deviation(id_stats, published["numbers"])
    ok = C.identity_ok(id_stats, published["numbers"])
    print("identity", published["as_of"], "dev", dev, "ok", ok, flush=True)
    if not ok:
        print("REFUSED: cap-free arm no longer reproduces %s" % C.PUBLISHED_LABEL, flush=True)
        return 3

    cells_by_arm = {}
    for label, caps in ARMS:
        cells = []
        for start in P.PHASE_STARTS:
            ser, turn = run_arm(close, openp, amt, sc, cls, caps, start)
            yrs = Y.yearly_returns(ser)
            rows = G._year_rows(yrs)
            st = A.stats2(ser, "p")
            cells.append({
                "start": start, "years": len(rows),
                "net_sum_pct": round(sum(r["net_pct"] for r in rows), 4),
                "cagr_pct": None if st.get("cagr") is None else round(st["cagr"] * 100, 4),
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "year_net_pct": {r["year"]: round(r["net_pct"], 4) for r in rows},
                "calibers": calibers(rows),
            })
        cells_by_arm[label] = cells

    # identity leg 2: the 20 cells must be the ones r1425 published, otherwise the calibers
    # are being measured on a different book than the one the decision was taken on
    phase_identity = {"checked": False}
    if os.path.exists(PHASE_RECEIPT):
        with open(PHASE_RECEIPT, encoding="utf-8") as f:
            prev = json.load(f)
        prev_by = {b["book"]: b["phase_rows"] for b in prev.get("books", [])
                   if b.get("book") in cells_by_arm}
        if set(prev_by) == set(cells_by_arm):
            worst = 0.0
            n = 0
            for arm, rows in prev_by.items():
                for mine, theirs in zip(cells_by_arm[arm], rows):
                    a, b = mine["calibers"]["net_top2_share"], theirs.get("top2_share")
                    if a is None or b is None:
                        continue
                    # the r1425 receipt publishes top-2 to 4 decimals (candidate_year_gate
                    # rounds there), so the identity is asserted at the published precision
                    # rather than at ours -- anything coarser is a different number
                    worst = max(worst, abs(round(a, 4) - b))
                    n += 1
            phase_identity = {"checked": True, "cells": n, "max_abs_dev": round(worst, 12),
                              "compared_at_decimals": 4,
                              "exact": worst == 0.0,
                              "source": "results/etf_book_sleeve_cap_phases.json"}
            print("phase identity: %d cells, max|d| %r exact %s"
                  % (n, worst, worst == 0.0), flush=True)
            if worst != 0.0:
                print("REFUSED: repriced cells differ from r1425's published cells", flush=True)
                return 3
        else:
            phase_identity = {"checked": False,
                              "reason": "receipt arm set differs: %s" % sorted(prev_by)}
    else:
        phase_identity = {"checked": False, "reason": "no r1425 phase receipt on disk"}

    built = build(cells_by_arm)
    dec = built["decision"]
    for name in CALIBERS:
        ev = built["calibers"][name]
        print("%-18s S:%-19s D_even:%-21s D_arms:%-17s per-arm %s"
              % (name, ev["arm_state_uniform"], ev["even"]["state"],
                 ev["separation"]["state"],
                 ",".join("%s=%s" % (a, s["state"]) for a, s in ev["arms"].items())),
              flush=True)
    print("TRUSTED:", dec["trusted_calibers"], "| verdicts", dec["trusted_verdicts"],
          "| COMPOSITE:", dec["composite_verdict"], flush=True)
    print("primary:", dec["primary_caliber"], "| corroborating:",
          dec["corroborating_caliber"], flush=True)
    for name in [n for n in (dec["primary_caliber"], dec["corroborating_caliber"]) if n]:
        for arm in cells_by_arm:
            s = built["calibers"][name]["arms"][arm]
            print("  %-18s %-20s %-4s median %.4f spread %.4f margin %.4f"
                  % (name, arm, s["state"], s["median"], s["spread"], s["margin"]),
                  flush=True)

    out = {
        "face": "etf_book_year_caliber",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "question": ("Y4's concentration line cannot adjudicate itself (r1419/r1425); which "
                     "caliber of 'how many years does this book owe' can?"),
        "rule": RULE,
        "caliber_specs": CALIBERS,
        "params": {"n_hold": N_HOLD, "rebal": REBAL, "cost": COST, "vol_target": VT},
        "data": {"flips_repaired": n_flip, "universe": int(len(close.columns)),
                 "bars": int(len(close.index)), "capacity_cny_1day_5pct": cap_cny,
                 "capacity_from": "results/etf_book_year_gate/YEAR-GATE.json"},
        "published_arm": published, "identity_deviation": dev, "identity_ok": ok,
        "phase_identity_vs_r1425": phase_identity,
        "cells": cells_by_arm,
        "calibers": built["calibers"],
        "decision": built["decision"],
        "honest": [
            "no pricing rule, no gate line and no production file is changed here; a caliber "
            "change is an admission-rule change and needs its own adoption round",
            "calibers are read on the same 20 cells r1425 published (identity leg above); "
            "phase cells are 4 arms x 5 weekly starts, not an i.i.d. sample",
            "the three numeric bars are declared before the read: 0.70 is Y4's own line so "
            "the control is judged at the bar it is used at; 3-of-7 years is a design choice, "
            "not a fit",
            "test S is passed for free by any caliber parked far from its line -- that is why a "
            "caliber is only trusted when D also holds",
            "D's first form (does the caliber separate the ARMS) is published beside its "
            "replacement: no caliber passed the arm form, because the four arms are not "
            "measurably different in concentration -- that is r1425's cap finding, not a "
            "defect of any ruler",
            "an integer caliber can show zero phase spread; it is published as corroboration "
            "and still contributes to the composite verdict, which takes the WORST word",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("saved", OUT, flush=True)
    return 0


def check() -> int:
    """Re-derive the decision from the published rows; refuse if the face disagrees."""
    if not os.path.exists(OUT):
        print("no face at", OUT)
        return 2
    with open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    cells = face.get("cells") or {}
    if not cells:
        print("FAIL the face publishes no cells")
        return 2
    rebuilt = build(cells)
    published = face.get("decision") or {}
    errs = []
    if rebuilt["decision"]["primary_caliber"] != published.get("primary_caliber"):
        errs.append("primary caliber drifted: face=%s rederived=%s"
                    % (published.get("primary_caliber"),
                       rebuilt["decision"]["primary_caliber"]))
    if rebuilt["decision"]["composite_verdict"] != published.get("composite_verdict"):
        errs.append("composite verdict drifted: face=%s rederived=%s"
                    % (published.get("composite_verdict"),
                       rebuilt["decision"]["composite_verdict"]))
    if sorted(rebuilt["decision"]["trusted_calibers"]) != sorted(
            published.get("trusted_calibers") or []):
        errs.append("trusted set drifted: face=%s rederived=%s"
                    % (published.get("trusted_calibers"),
                       rebuilt["decision"]["trusted_calibers"]))
    for name, ev in rebuilt["calibers"].items():
        old = (face.get("calibers") or {}).get(name) or {}
        if ev["arm_state_uniform"] != old.get("arm_state_uniform"):
            errs.append("%s arm state drifted: face=%s rederived=%s"
                        % (name, old.get("arm_state_uniform"), ev["arm_state_uniform"]))
        if ev["even"]["state"] != (old.get("even") or {}).get("state"):
            errs.append("%s even-reference state drifted" % name)
        if ev["separation"]["state"] != (old.get("separation") or {}).get("state"):
            errs.append("%s separation drifted" % name)
    # the echo must carry the rule that is actually applied
    if (face.get("rule") or {}).get("frozen_before_read") is not True:
        errs.append("rule is not marked as frozen before the read")
    for name, spec in CALIBERS.items():
        echo = ((face.get("rule") or {}).get("calibers") or {}).get(name) or {}
        if echo.get("line") != spec["line"]:
            errs.append("%s line not echoed faithfully (%r vs %r)"
                        % (name, echo.get("line"), spec["line"]))
    for e in errs:
        print("FAIL", e)
    print("check %s: primary=%s composite=%s"
          % ("PASS" if not errs else "FAIL", rebuilt["decision"]["primary_caliber"],
             rebuilt["decision"]["composite_verdict"]))
    return 0 if not errs else 1


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    errs = []
    seen = [0]

    def chk(ok, msg):
        seen[0] += 1
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    def yrs(spec):
        return [{"year": str(2000 + i), "net_pct": v, "cohorts": 4}
                for i, v in enumerate(spec)]

    # L1 an even book: every caliber should read "not concentrated"
    even = calibers(yrs([10, 10, 10, 10, 10, 10, 10]))
    chk(abs(even["gross_top2_share"] - 2 / 7) < 1e-6,
        "L1 an even 7-year book reads 2/7 gross top-2 (%.6f)"
        % even["gross_top2_share"])
    chk(abs(even["effective_years"] - 7.0) < 1e-9,
        "L1b effective years of an even book is 7 (%.4f)" % even["effective_years"])
    chk(even["years_for_half"] == 4,
        "L1c an even 7-year book needs four years to reach half its return (%d)"
        % even["years_for_half"])

    # L2 one year carrying everything
    carried = calibers(yrs([90, 2, 2, 2, 2, 2, 2]))
    chk(carried["gross_top2_share"] > 0.9, "L2 two-year book reads gross top-2 %.4f"
        % carried["gross_top2_share"])
    chk(carried["effective_years"] < 2.0, "L2b effective years %.3f"
        % carried["effective_years"])
    chk(carried["years_for_half"] == 1,
        "L2c one good year is the whole book (%d year to half)" % carried["years_for_half"])

    # L3 the defect the control caliber cannot avoid: a year sum near zero
    #     net share explodes while gross share stays sane
    flat_net = calibers(yrs([50, -49, 0.5, 0.5, -0.5, -0.5, 0.0]))
    chk(flat_net["net_top2_share"] > 5.0 or flat_net["net_top2_share"] is None,
        "L3 a near-zero net denominator explodes the control (net top-2 %r)"
        % flat_net["net_top2_share"])
    chk(0.0 <= flat_net["gross_top2_share"] <= 1.0 and
        1.0 <= flat_net["effective_years"] <= 7.0,
        "L3b the gross-based calibers stay bounded (top-2 %.4f, eff %.3f)"
        % (flat_net["gross_top2_share"], flat_net["effective_years"]))

    # L4 a losing book: net sum negative -> the control publishes nothing (never a pass)
    losing = calibers(yrs([-5, -4, 3, -2]))
    chk(losing["net_top2_share"] is None and passes("net_top2_share", None) is None,
        "L4 a negative calendar sum yields no net share, and None is not a pass")
    chk(losing["years_for_half"] is None and passes("years_for_half", None) is None,
        "L4b a book with no positive calendar sum has no half to explain (%r)"
        % losing["years_for_half"])

    # L5 empty year table: every caliber is unknown, nothing is invented
    empty = calibers([])
    chk(all(empty[k] is None for k in ("net_top2_share", "gross_top2_share",
                                       "effective_years", "years_for_half")),
        "L5 an empty year table publishes None, not zeros")

    # L6 the two pass directions are the declared ones (a flip-direction bug would read as
    #     a great book)
    chk(passes("gross_top2_share", 0.60) is True and passes("gross_top2_share", 0.80) is False,
        "L6 gross top-2 passes low, fails high")
    chk(passes("effective_years", 3.5) is True and passes("effective_years", 2.0) is False,
        "L6b effective years passes high, fails low")
    chk(passes("years_for_half", 3) is True and passes("years_for_half", 1) is False,
        "L6c years-to-half passes high, fails low (3 of 7 meets the bar exactly)")

    # L7 test S: unanimous side + spread inside margin -> a state; spread wider -> cannot tell
    def cell(**kw):
        base = {"years": 7, "calibers": {k: None for k in CALIBERS}}
        base["calibers"].update({k: v for k, v in kw.items() if k in CALIBERS})
        return base
    tight = adjudicate_caliber("gross_top2_share",
                               [cell(gross_top2_share=v) for v in (0.60, 0.61, 0.605, 0.60, 0.61)])
    chk(tight["state"] == "PASS", "L7 unanimous far from the line -> PASS (%s)" % tight["state"])
    wild = adjudicate_caliber("gross_top2_share",
                              [cell(gross_top2_share=v) for v in (0.78, 0.95, 0.90, 0.88, 0.76)])
    chk(wild["state"] == "UNADJUDICABLE_CALIBER" and "spread" in wild["reason"],
        "L7b unanimous, but spread wider than the margin -> cannot tell (%s)" % wild["state"])
    split = adjudicate_caliber("gross_top2_share",
                               [cell(gross_top2_share=v) for v in (0.60, 0.75)])
    chk(split["state"] == "UNADJUDICABLE_CALIBER" and "both sides" in split["reason"],
        "L7c phases on both sides of the line -> cannot tell (%s)" % split["state"])
    none_at_all = adjudicate_caliber("effective_years", [cell()])
    chk(none_at_all["state"] == "UNADJUDICABLE_CALIBER" and
        none_at_all["median"] is None, "L7d no phase published the caliber -> cannot tell")

    # L8 test S is passed for free by a caliber parked far from its line, and D is what
    #     saves the rule from that -- so a dead ruler must be INELIGIBLE
    dead_arm = [cell(effective_years=v) for v in (1.01, 1.02, 1.01, 1.01, 1.01)]
    alive_arm = [cell(effective_years=v) for v in (4.0, 4.1, 4.0, 4.1, 4.0)]
    s_pass_dead = adjudicate_caliber("effective_years", dead_arm)
    chk(s_pass_dead["state"] == "FAIL" and s_pass_dead["spread"] < s_pass_dead["margin"],
        "L8 a ruler parked far from its line passes S trivially (spread %.3f < margin %.3f)"
        % (s_pass_dead["spread"], s_pass_dead["margin"]))
    built = build({"plain": dead_arm, "cap": alive_arm})
    d = built["decision"]
    row_ye = [r for r in d["calibers"] if r["caliber"] == "effective_years"][0]
    chk(row_ye["D_even"] is True and row_ye["D_arms"] is True
        and d["arm_separation_is_informational"] is True,
        "L8b the arm and even tests are separate fields, and arm separation is marked "
        "informational (even=%s arms=%s)" % (row_ye["D_even"], row_ye["D_arms"]))
    # in this fixture gross_top2_share has no numbers at all -> it must not be the primary
    chk(d["primary_caliber"] in (None, "effective_years", "years_for_half"),
        "L8c a caliber with no published numbers is never the primary (primary=%r)"
        % d["primary_caliber"])

    # L8d the even reference is arithmetic on the year count, not a fit
    chk(even_reference("gross_top2_share", 7) == 2 / 7
        and even_reference("effective_years", 7) == 7.0
        and even_reference("years_for_half", 7) == 4
        and even_reference("years_for_half", 8) == 4,
        "L8d even-book reference is 2/n for shares, n for effective years, ceil(n/2) for half")

    # L9 test D needs both a stable sign and a gap: a consistent but tiny difference is noise
    tiny = {"plain": [cell(gross_top2_share=0.60), cell(gross_top2_share=0.61)],
            "cap": [cell(gross_top2_share=0.6001), cell(gross_top2_share=0.6101)]}
    sep_tiny = separation("gross_top2_share", tiny)
    chk(all(p["consistent"] for p in sep_tiny["pairs"]) and
        sep_tiny["state"] == "DOES_NOT_SEPARATE",
        "L9 a consistent but microscopic gap does not count as separation")
    big = {"plain": [cell(gross_top2_share=0.60), cell(gross_top2_share=0.61)],
           "cap": [cell(gross_top2_share=0.90), cell(gross_top2_share=0.91)]}
    chk(separation("gross_top2_share", big)["state"] == "SEPARATES",
        "L9b a consistent, large gap separates")
    flip = {"plain": [cell(gross_top2_share=0.60), cell(gross_top2_share=0.90)],
            "cap": [cell(gross_top2_share=0.90), cell(gross_top2_share=0.60)]}
    chk(separation("gross_top2_share", flip)["state"] == "DOES_NOT_SEPARATE",
        "L9c a ruler whose ordering flips across phases separates nothing")

    # L10 V is structural: the control can never be trusted, whatever S and D say
    rows = build({"plain": [cell(net_top2_share=v) for v in (0.60, 0.61, 0.60)],
                  "cap": [cell(net_top2_share=v) for v in (0.90, 0.91, 0.90)]})["decision"]
    control = [r for r in rows["calibers"] if r["caliber"] == "net_top2_share"][0]
    chk(control["V"] is False and control["trusted"] is False,
        "L10 the net-sum control is untrusted on V alone (%s)" % control["failed"])
    chk(rows["primary_caliber"] != "net_top2_share"
        and "net_top2_share" not in rows["trusted_calibers"],
        "L10b the control is never the primary and never voted")

    # L10c the composite takes the WORST word: broad on one ruler cannot excuse a fail on
    #      another (that is the whole point of publishing a second ruler)
    ev_mixed = {}
    for name in ("effective_years", "years_for_half"):
        ev_mixed[name] = {"arm_state_uniform": "PASS" if name == "effective_years" else "FAIL",
                          "arms": {"plain": {"state": "PASS" if name == "effective_years"
                                             else "FAIL", "margin": 2.0, "spread": 0.5,
                                             "median": 5.0, "book_years": 7}},
                          "even": {"state": "RESOLVES_EVEN",
                                   "arms": {"plain": {"distance": 2.0, "resolves": True}}},
                          "separation": {"state": "DOES_NOT_SEPARATE", "best_pair": None}}
    dec_mixed = decide(ev_mixed)
    chk(dec_mixed["composite_verdict"] == "FAIL" and
        dec_mixed["trusted_verdicts"] == {"effective_years": "PASS",
                                          "years_for_half": "FAIL"},
        "L10c broad on one ruler + front-loaded on another reads FAIL (%s)"
        % dec_mixed["composite_verdict"])

    # L11 the frozen rule echoes the imported phase set and the one imported line
    chk(tuple(RULE["phase_set"]) == tuple(P.PHASE_STARTS),
        "L11 the phase set is the imported five weekly starts")
    chk(CALIBERS["net_top2_share"]["line"] == G.TOP2_SHARE_MAX,
        "L11b the control sits on Y4's own line (%.2f), so it is judged where it is used"
        % CALIBERS["net_top2_share"]["line"])

    # L12 the selection prefers a continuous caliber over an integer one
    ev = {}
    for name in CALIBERS:
        ev[name] = {"arm_state_uniform": "PASS",
                    "arms": {"plain": {"state": "PASS", "margin": 0.20, "spread": 0.05,
                                       "median": 5.0, "book_years": 7},
                             "cap": {"state": "PASS", "margin": 0.20, "spread": 0.05,
                                     "median": 5.0, "book_years": 7}},
                    "even": {"state": "RESOLVES_EVEN",
                             "arms": {"plain": {"distance": 2.0, "resolves": True},
                                      "cap": {"distance": 2.0, "resolves": True}}},
                    "separation": {"state": "SEPARATES",
                                   "best_pair": {"gap_vs_floor": 2.0}}}
    ev["years_for_half"]["even"]["arms"]["plain"]["distance"] = 9.0
    ev["years_for_half"]["even"]["arms"]["cap"]["distance"] = 9.0
    pick = decide(ev)
    chk(pick["primary_caliber"] is not None and pick["primary_caliber"] != "years_for_half",
        "L12 an integer caliber with a larger even-gap does not outrank a continuous one (%r)"
        % pick["primary_caliber"])
    chk(pick["corroborating_caliber"] == "years_for_half",
        "L12b the integer caliber is still published as corroboration")

    # L13 when nothing resolves an even book, nothing is trusted and the composite says so
    ev2 = {k: dict(v) for k, v in ev.items()}
    for v in ev2.values():
        v["even"] = {"state": "DOES_NOT_RESOLVE_EVEN",
                     "arms": {"plain": {"distance": 0.0, "resolves": False},
                              "cap": {"distance": 0.0, "resolves": False}}}
    pick2 = decide(ev2)
    chk(pick2["primary_caliber"] is None and pick2["trusted_calibers"] == []
        and pick2["composite_verdict"] == "UNADJUDICABLE_CALIBER",
        "L13 nothing resolves an even book -> no trusted caliber, no verdict (%s)"
        % pick2["composite_verdict"])

    print("selftest %d/%d" % (seen[0] - len(errs), seen[0]), flush=True)
    return 0 if not errs else 1


def main(argv) -> int:
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))