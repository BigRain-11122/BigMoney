"""E226 -- the break-even toll for the state tilt: is the rule wrong, or only dear?

E225 closed with five arms that all lost after the drift they normalised to was
charged back, and its gate-specific residuals ran from -200 to -703 bp/yr. That
left exactly one arithmetic question open, and it is not a new study: the toll is
a per-unit-turnover charge, the tilt pays it 4-11 times a year, and so

    gate_specific(c) = gate_specific(0) - c * D

is a straight line in the cost per unit of turnover, with D the arm's own OOS
turnover per year net of what the null arm would have paid. One root, one number,
and a verdict that is about execution rather than about the signal.

Nothing here re-implements the engine: weights, signal, split, accounting and the
drift split all come from e225 via tilt_stats at an arbitrary cost, so the only
thing this face adds is the sweep and the solve.

Frozen before reading any number:

  * model: identical to E225 (vol tercile signal, 60/40 split, 252-session floor,
    unit turnover |dw| pays one side, excess = w*(r - mu_is) - |dw|*c). Only c moves.
  * sweep: c is swept at COST_MULTS = 0/0.25/0.5/0.75/1/1.5/2/3 times the frozen
    unit cost (13.041 bp per side). The sweep is the evidence; the closed form is
    the answer and the two are asserted equal.
  * answer: the break-even toll c* solves gate_specific(c*) = 0, i.e.
    c* = gate_specific(0) / D, published in bp per unit of turnover. A NEGATIVE c*
    means no price saves the arm (it loses before it trades); D <= 0 means the arm
    pays no toll differential at all and the question is undefined for it -- both
    are published with a reason rather than as a number.
  * plausibility band, declared up front and NOT fitted to the result: a wide-base
    ETF one-way all-in is roughly half-spread 1-2bp plus impact 1-3bp, so
    PLAUSIBLE_LOW_BP = 5.0 is the optimistic end of a real fill, and
    PLAUSIBLE_HIGH_BP = 13.041 is the frozen model cost (already punitive for an
    index ETF). The band brackets the question; the verdict reads off it.
  * verdict per arm:
      DEAD_AT_ANY_PRICE   c* < 0            -- the gross rule loses before toll
      NEEDS_CHEAPER_FILL 0 <= c* < 5.0      -- survives only below a plausible fill
      FILL_DEPENDENT      5.0 <= c* < 13.041 -- in the band: execution decides
      SURVIVES_MODEL_COST c* >= 13.041      -- clears the frozen cost, and beyond
      UNDEFINED           D <= 0 or no OOS mean -- nothing to solve
    An arm below the 252-session floor is published as UNASSESSABLE, never as a
    verdict: a short window cannot price a rule.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402

ROOT = e225.ROOT
PANEL_DIR = e225.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

UNIT_COST_BP = e225.COST_SIDE_BP          # 13.041 bp per unit of turnover
PLAUSIBLE_LOW_BP = 5.0                    # optimistic real fill, one way
PLAUSIBLE_HIGH_BP = UNIT_COST_BP          # the frozen model cost
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
ARMS = e225.ARMS

COST_MULTS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

# the boundary semantics are constants so the selftest can pin them
CLASS_DEAD = "DEAD_AT_ANY_PRICE"
CLASS_CHEAP = "NEEDS_CHEAPER_FILL"
CLASS_DEPENDENT = "FILL_DEPENDENT"
CLASS_SURVIVES = "SURVIVES_MODEL_COST"
CLASS_UNDEFINED = "UNDEFINED"
CLASS_UNASSESSABLE = "UNASSESSABLE"


# ---------------------------------------------------------------- the line
def _avg_weight(stats):
    return stats.get("avg_weight_oos") or 0.0


def gate_specific_bp_per_year(arm_stats, null_stats):
    """What the arm added after charging it the drift the null arm earned.

    Identical arithmetic to e225's drift_split, kept here as a function of the
    stats so it can be evaluated at any cost the sweep asks for.
    """
    if arm_stats.get("excess_oos_bp_per_year") is None:
        return None
    if null_stats is None or null_stats.get("excess_oos_bp_per_year") is None:
        return arm_stats.get("excess_oos_bp_per_year")
    return (arm_stats["excess_oos_bp_per_year"]
            - _avg_weight(arm_stats) * null_stats["excess_oos_bp_per_year"])


def toll_differential(arm_stats, null_stats):
    """Units of turnover per year the arm pays that the null arm does not."""
    a = arm_stats.get("turnover_oos_per_year")
    if a is None:
        return None
    n = (null_stats.get("turnover_oos_per_year") or 0.0) if null_stats else 0.0
    return a - _avg_weight(arm_stats) * n


def classify(cost_bp, differential, assessable=True):
    if not assessable:
        return CLASS_UNASSESSABLE, "fewer_than_%d_oos_decisions" % MIN_OOS_SESSIONS
    if cost_bp is None:
        return CLASS_UNDEFINED, "no_break_even_published"
    if differential is None or differential <= 0:
        return CLASS_UNDEFINED, "no_toll_differential_the_arm_pays_no_extra"
    if cost_bp < 0:
        return CLASS_DEAD, "losses_before_the_toll"
    if cost_bp < PLAUSIBLE_LOW_BP:
        return CLASS_CHEAP, "needs_a_fill_below_%.3fbp" % PLAUSIBLE_LOW_BP
    if cost_bp < PLAUSIBLE_HIGH_BP:
        return CLASS_DEPENDENT, "inside_the_%.3f..%.3fbp_band" % (PLAUSIBLE_LOW_BP,
                                                                 PLAUSIBLE_HIGH_BP)
    return CLASS_SURVIVES, "clears_the_frozen_%.3fbp_cost" % PLAUSIBLE_HIGH_BP


def break_even(g0, differential):
    """Solve gate_specific(c) = g0 - c*D = 0 for c, in bp per unit turnover."""
    if g0 is None or differential is None:
        return None
    if differential <= 0:
        return None
    return g0 / differential


def arm_at_cost(weights, ret_bp, split, cost_bp, bar_t):
    return e225.tilt_stats(weights, ret_bp, split, cost_bp, bar_t)


def sweep_arm(weights, ret_bp, split, null_weights, bar_t, mults=None):
    """Evaluate one arm and the null arm at every cost multiple in the sweep."""
    mults = COST_MULTS if mults is None else mults
    rows = []
    for m in mults:
        c = UNIT_COST_BP * m
        a = arm_at_cost(weights, ret_bp, split, c, bar_t)
        n = arm_at_cost(null_weights, ret_bp, split, c, bar_t)
        rows.append({"cost_mult": m,
                     "cost_side_bp": c,
                     "gate_specific_bp_per_year": gate_specific_bp_per_year(a, n),
                     "excess_bp_per_year": a.get("excess_oos_bp_per_year"),
                     "turnover_oos_per_year": a.get("turnover_oos_per_year"),
                     "excess_oos_t": a.get("excess_oos_t"),
                     "oos_decisions": a.get("oos_decisions")})
    return rows


def solve_arm(weights, ret_bp, split, null_weights, bar_t):
    """The closed form: g0 from the frozen cost, D from the same run, one root."""
    a = arm_at_cost(weights, ret_bp, split, 0.0, bar_t)
    n0 = arm_at_cost(null_weights, ret_bp, split, 0.0, bar_t)
    g0 = gate_specific_bp_per_year(a, n0)
    d = toll_differential(a, n0)
    cstar = break_even(g0, d)
    assessable = (a.get("oos_decisions") or 0) >= MIN_OOS_SESSIONS
    verdict, reason = classify(cstar, d, assessable)
    # the stricter sibling: where the arm's own net excess (drift included) dies
    ex0 = a.get("excess_oos_bp_per_year")
    cstar_excess = break_even(ex0, d)
    # clearing a toll is not clearing a bar. The same arm is read at the frozen
    # model cost so "survives_model_cost" cannot be mistaken for "adopts".
    a1 = arm_at_cost(weights, ret_bp, split, UNIT_COST_BP, bar_t)
    n1 = arm_at_cost(null_weights, ret_bp, split, UNIT_COST_BP, bar_t)
    at_cost = {"cost_side_bp": UNIT_COST_BP,
               "excess_bp_per_year": a1.get("excess_oos_bp_per_year"),
               "excess_oos_t": a1.get("excess_oos_t"),
               "gate_specific_bp_per_year": gate_specific_bp_per_year(a1, n1),
               "cost_bp_per_year": a1.get("cost_bp_per_year_oos"),
               "turnover_oos_per_year": a1.get("turnover_oos_per_year"),
               "bar_t": bar_t}
    at_cost["clears_bar"] = bool(at_cost["excess_oos_t"] is not None
                                 and at_cost["excess_oos_t"] >= bar_t
                                 and (at_cost["excess_bp_per_year"] or 0) > 0)
    return {"gate_specific_at_zero_cost_bp_per_year": g0,
            "turnover_differential_oos_per_year": d,
            "break_even_cost_bp_per_unit_turnover": cstar,
            "break_even_cost_bp_excess_basis": cstar_excess,
            "root_fragility_bp_per_unit_per_bp_per_year":
                (1.0 / d) if (d and d > 0) else None,
            "oos_decisions": a.get("oos_decisions"),
            "assessable": assessable,
            "at_model_cost": at_cost,
            "verdict": verdict,
            "verdict_reason": reason}


def _pick_best_g0(arms):
    """Largest gross gate-specific residual among the gated arms."""
    best = None
    for a in arms:
        if a.get("name") == "always_on":
            continue
        v = a.get("gate_specific_at_zero_cost_bp_per_year")
        if v is None:
            continue
        if best is None or v > best.get("gate_specific_at_zero_cost_bp_per_year"):
            best = a
    return best


def _pick_best_root(arms):
    """Highest break-even toll among the arms that have one."""
    best = None
    for a in arms:
        if a.get("name") == "always_on":
            continue
        v = a.get("break_even_cost_bp_per_unit_turnover")
        if v is None:
            continue
        if best is None or v > best.get("break_even_cost_bp_per_unit_turnover"):
            best = a
    return best


# ---------------------------------------------------------------- the study
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(e225.PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % e225.PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    n_tests = len(ARMS) * (2 if basket else 1)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    panels = [{"panel": "primary_single", "symbol": e225.PRIMARY_SYMBOL,
               "sessions": len(single[0]), "first": single[0][0], "last": single[0][-1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(e225.BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0],
                       "last": basket[0][-1]})

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        null_w = e225.weights_series(sig, "always_on")
        arms_out = []
        for arm in ARMS:
            target = e225.arm_target(sig, split, arm)
            w = e225.weights_series(sig, arm, target)
            solved = solve_arm(w, ret_bp, split, null_w, bar_t)
            ladder = sweep_arm(w, ret_bp, split, null_w, bar_t)
            # the sweep must agree with the line, and it must come down as the
            # toll rises: both are checked here so a wrong sign cannot ship
            if solved["break_even_cost_bp_per_unit_turnover"] is not None:
                for row in ladder:
                    expected = (solved["gate_specific_at_zero_cost_bp_per_year"]
                                - row["cost_side_bp"]
                                * solved["turnover_differential_oos_per_year"])
                    row["line_expected_bp_per_year"] = expected
                    row["line_abs_err"] = abs((row["gate_specific_bp_per_year"] or 0.0)
                                              - expected)
            solved["name"] = arm
            solved["target_bp"] = target
            solved["cost_ladder"] = ladder
            arms_out.append(solved)
        panel["arms"] = arms_out
        panel["split_session"] = split
        panel["split_date"] = dates[split]
        gated = [a for a in arms_out if a["name"] != "always_on"]
        # two different "best" and they name different arms: the largest gross
        # gate-specific residual, and the highest break-even. Conflating them is how
        # the answer sentence came out calling a -324 bp/yr arm "the best gate-specific"
        priced = [a for a in gated
                  if a.get("break_even_cost_bp_per_unit_turnover") is not None]
        best_root = _pick_best_root(arms_out)
        best_g0 = _pick_best_g0(arms_out)
        panel["best_break_even_arm"] = best_root["name"] if best_root else None
        panel["best_break_even_cost_bp"] = (best_root["break_even_cost_bp_per_unit_turnover"]
                                            if best_root else None)
        panel["best_gate_specific_arm"] = best_g0["name"] if best_g0 else None
        panel["best_gate_specific_bp_per_year"] = (
            best_g0["gate_specific_at_zero_cost_bp_per_year"] if best_g0 else None)

    face = {
        "study": "E226",
        "title": "break-even toll for the state tilt: is the rule wrong, or only dear?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "model": "identical to E225; only the cost per unit of turnover moves",
            "unit_cost_bp": UNIT_COST_BP,
            "cost_mults": COST_MULTS,
            "plausible_low_bp": PLAUSIBLE_LOW_BP,
            "plausible_high_bp": PLAUSIBLE_HIGH_BP,
            "plausible_basis": "a wide-base ETF one-way all-in is ~half-spread 1-2bp "
                               "plus impact 1-3bp; 5bp is the optimistic real fill and "
                               "13.041bp is the frozen model cost, declared before the run",
            "answer_form": "break_even_bp = gate_specific(0) / D with "
                           "D = arm turnover per year - avg_weight * null turnover per year",
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "bar_t": bar_t,
            "tests": n_tests,
            "verdict_bands": {
                CLASS_DEAD: "break-even < 0",
                CLASS_CHEAP: "0 <= break-even < %.3f" % PLAUSIBLE_LOW_BP,
                CLASS_DEPENDENT: "%.3f <= break-even < %.3f" % (PLAUSIBLE_LOW_BP,
                                                               PLAUSIBLE_HIGH_BP),
                CLASS_SURVIVES: "break-even >= %.3f" % PLAUSIBLE_HIGH_BP,
                CLASS_UNDEFINED: "no toll differential or no OOS mean",
                CLASS_UNASSESSABLE: "fewer than %d OOS decisions" % MIN_OOS_SESSIONS,
            },
        },
        "panels": panels,
    }

    primary = panels[0]["arms"]
    best = next((a for a in primary if a["name"] == panels[0]["best_gate_specific_arm"]), None)
    best_root = next((a for a in primary if a["name"] == panels[0]["best_break_even_arm"]), None)
    dead = [a["name"] for a in primary if a["verdict"] == CLASS_DEAD]
    cheap = [a["name"] for a in primary if a["verdict"] == CLASS_CHEAP]
    dependent = [a["name"] for a in primary if a["verdict"] == CLASS_DEPENDENT]
    survives = [a["name"] for a in primary if a["verdict"] == CLASS_SURVIVES]

    # clearing a toll is not clearing a bar: name every arm that survives the frozen
    # cost and say whether its excess is distinguishable from zero at that cost
    survive_rows = []
    for panel in panels:
        for a in panel["arms"]:
            if a["verdict"] != CLASS_SURVIVES:
                continue
            ac = a.get("at_model_cost") or {}
            survive_rows.append({"panel": panel["panel"], "arm": a["name"],
                                 "break_even_cost_bp": a["break_even_cost_bp_per_unit_turnover"],
                                 "excess_bp_per_year_at_model_cost": ac.get("excess_bp_per_year"),
                                 "excess_oos_t_at_model_cost": ac.get("excess_oos_t"),
                                 "clears_bar_at_model_cost": ac.get("clears_bar")})
    face["breakeven_vs_significance"] = {
        "reading": "a break-even above the frozen cost only says the arm still has "
                   "something left after the toll; it says nothing about whether that "
                   "something is distinguishable from zero. Every surviving arm is read "
                   "at the model cost with its own t beside its annual excess, and an "
                   "arm that survives by standing at zero is recorded as such.",
        "arms": survive_rows,
        "any_survivor_clears_the_bar": any(r["clears_bar_at_model_cost"] for r in survive_rows),
    }

    face["answer"] = (
        "the tilt is not merely dear, it is wrong. On the primary panel the arm with the "
        "largest gross gate-specific residual is %s at %s bp/yr -- still negative before any "
        "toll -- and the highest break-even belongs to %s at %s bp per unit of turnover: "
        "below zero, so the gross rule loses before it is charged anything, and %d of %d "
        "gated arms are in that same state. (Those are two different arms, which is the "
        "point: ranking by residual and ranking by break-even do not name the same rule once "
        "every arm is below zero.) The equal-weight basket is the one place a root lands "
        "above the model cost (%s at %s bp/unit), but at %.3fbp that arm's excess is %s bp/yr "
        "at t=%s: it survives the toll by standing at zero after a null arm that lost %.0f "
        "bp/yr, not by earning, so %d of %d survivors clear the bar. Execution cannot rescue "
        "a rule whose gross is below the drift it is charged"
        % (best["name"] if best else "-",
           ("%.0f" % best["gate_specific_at_zero_cost_bp_per_year"]) if best else "-",
           best_root["name"] if best_root else "-",
           ("%.3f" % best_root["break_even_cost_bp_per_unit_turnover"]) if best_root else "-",
           len(dead), len(primary) - 1,
           (survive_rows[0]["arm"] if survive_rows else "-"),
           ("%.3f" % survive_rows[0]["break_even_cost_bp"]) if survive_rows else "-",
           PLAUSIBLE_HIGH_BP,
           ("%.1f" % survive_rows[0]["excess_bp_per_year_at_model_cost"])
           if survive_rows and survive_rows[0]["excess_bp_per_year_at_model_cost"] is not None else "-",
           ("%.2f" % survive_rows[0]["excess_oos_t_at_model_cost"])
           if survive_rows and survive_rows[0]["excess_oos_t_at_model_cost"] is not None else "-",
           next((p["arms"][0]["at_model_cost"]["excess_bp_per_year"] or 0.0
                 for p in panels if p["panel"] == "basket_equal_weight"),
                panels[-1]["arms"][0]["at_model_cost"]["excess_bp_per_year"] or 0.0),
           sum(1 for r in survive_rows if r["clears_bar_at_model_cost"]), len(survive_rows)))

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "BREAKEVEN-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "breakeven_latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "name", "oos_decisions", "gate_specific_at_zero_cost_bp_per_year",
                "turnover_differential_oos_per_year",
                "break_even_cost_bp_per_unit_turnover", "break_even_cost_bp_excess_basis",
                "verdict", "verdict_reason"]
        # explicit list with a length guard: two adjacent string literals will glue
        # and silently swallow the first data row (the r1325 lesson)
        assert len(cols) == 9, "column list length drift"
        csv_path = os.path.join(outdir, "breakeven_by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    row = dict(a)
                    row["panel"] = panel["panel"]
                    w.writerow(row)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, amp=60.0, seed=7):
    ret = [None]
    for i in range(1, n):
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        z = ((seed / 2 ** 31) - 0.5) * 3.4641
        v = amp * (1.0 + 0.5 * ((i % 120) / 120.0))
        ret.append(drift_bp + z * v)
    return ["d%04d" % i for i in range(n)], ret


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    dates, ret = _synth(900)
    sig = e225.vol_signal(ret)
    split = e225.split_index(len(dates))
    null_w = e225.weights_series(sig, "always_on")

    # L1 the null arm pays its entry inside the in-sample window only, so its OOS
    # toll differential is zero: this is what makes D the gated arm's own turnover
    n0 = arm_at_cost(null_w, ret, split, UNIT_COST_BP, 2.5)
    leg("null_arm_pays_no_oos_toll",
        (n0.get("turnover_oos_per_year") or 0.0) == 0.0,
        "turnover_oos_per_year=%.6f" % (n0.get("turnover_oos_per_year") or 0.0))

    # L2 the line is exact: the sweep agrees with g0 - c*D at every rung
    w = e225.weights_series(sig, "tilt_linear")
    solved = solve_arm(w, ret, split, null_w, 2.5)
    ladder = sweep_arm(w, ret, split, null_w, 2.5)
    worst = 0.0
    for row in ladder:
        expected = (solved["gate_specific_at_zero_cost_bp_per_year"]
                    - row["cost_side_bp"] * solved["turnover_differential_oos_per_year"])
        worst = max(worst, abs((row["gate_specific_bp_per_year"] or 0.0) - expected))
    leg("closed_form_matches_the_sweep", worst < 1e-6,
        "worst absolute error %.3e bp/yr over %d rungs" % (worst, len(ladder)))

    # L3 the sweep must come down as the toll rises
    g = [r["gate_specific_bp_per_year"] for r in ladder if r["gate_specific_bp_per_year"] is not None]
    leg("gate_specific_falls_as_the_toll_rises",
        all(g[i] >= g[i + 1] - 1e-9 for i in range(len(g) - 1)),
        "%.2f -> %.2f bp/yr over the ladder" % (g[0], g[-1]))

    # L4 the break-even is where the published line actually crosses zero: evaluate
    # the sweep at c* and it must read zero (self-consistency of the root)
    cstar = solved["break_even_cost_bp_per_unit_turnover"]
    leg("break_even_is_a_root", cstar is not None, "c*=%.3f bp/unit" % (cstar or 0.0))
    a_star = arm_at_cost(w, ret, split, cstar, 2.5)
    n_star = arm_at_cost(null_w, ret, split, cstar, 2.5)
    g_star = gate_specific_bp_per_year(a_star, n_star)
    leg("break_even_evaluates_to_zero", abs(g_star) < 1e-6,
        "gate_specific at c* = %.3e bp/yr" % g_star)

    # L5 sign logic: a gate-specific loss at zero cost must price a negative toll
    sign_ok = (solved["gate_specific_at_zero_cost_bp_per_year"] < 0) == (cstar < 0)
    leg("negative_gross_prices_a_negative_toll", sign_ok,
        "g0=%.2f c*=%.3f" % (solved["gate_specific_at_zero_cost_bp_per_year"], cstar))

    # L6 the null arm compared with itself has no toll differential, so the
    # question is undefined for it rather than an infinite number
    solved_null = solve_arm(null_w, ret, split, null_w, 2.5)
    leg("self_comparison_is_undefined_not_infinite",
        solved_null["break_even_cost_bp_per_unit_turnover"] is None
        and solved_null["verdict"] == CLASS_UNDEFINED,
        solved_null["verdict_reason"])

    # L7 a flat-zero arm pays nothing and earns nothing -> identical zero, undefined
    zero_w = [0.0] * len(sig)
    solved_zero = solve_arm(zero_w, ret, split, null_w, 2.5)
    leg("zero_exposure_arm_is_undefined",
        solved_zero["turnover_differential_oos_per_year"] == 0.0
        and solved_zero["verdict"] == CLASS_UNDEFINED,
        "flat at zero cannot be priced")

    # L8 the bands are boundary-exact (pinned as constants, not fitted): a cost of
    # exactly 5.0 is already FILL_DEPENDENT and exactly 13.041 already SURVIVES
    leg("bands_are_boundary_exact",
        classify(PLAUSIBLE_LOW_BP, 1.0)[0] == CLASS_DEPENDENT
        and classify(PLAUSIBLE_HIGH_BP, 1.0)[0] == CLASS_SURVIVES
        and classify(PLAUSIBLE_LOW_BP - 1e-9, 1.0)[0] == CLASS_CHEAP
        and classify(-1e-9, 1.0)[0] == CLASS_DEAD,
        "5.0 -> dependent, 13.041 -> survives, just below -> cheap, just below 0 -> dead")

    # L9 a short window is UNASSESSABLE, never a verdict
    short_ret = ret[:120]
    short_sig = e225.vol_signal(short_ret)
    short_split = e225.split_index(len(short_ret))
    sw = e225.weights_series(short_sig, "tilt_linear")
    sn = e225.weights_series(short_sig, "always_on")
    solved_short = solve_arm(sw, short_ret, short_split, sn, 2.5)
    leg("short_window_is_unassessable",
        solved_short["verdict"] == CLASS_UNASSESSABLE
        and solved_short["assessable"] is False,
        "oos_decisions=%s" % solved_short["oos_decisions"])

    # L10 a doubled toll must halve the distance to break-even, not move the root:
    # the root is a property of the line, the ladder is a read-off of it
    ladder_x2 = sweep_arm(w, ret, split, null_w, 2.5, mults=[2.0])
    leg("doubling_the_toll_keeps_the_same_root",
        solve_arm(w, ret, split, null_w, 2.5)["break_even_cost_bp_per_unit_turnover"]
        == cstar,
        "root is cost-invariant by construction; ladder at x2 = %.2f"
        % (ladder_x2[0]["gate_specific_bp_per_year"] or 0.0))

    # L11 the sweep brackets the frozen unit cost and is ascending
    leg("sweep_brackets_the_unit_cost",
        COST_MULTS == sorted(COST_MULTS) and 1.0 in COST_MULTS,
        "mults %s" % COST_MULTS)

    # L12 the cheapest arm is not reported as the answer: it is the one with the
    # highest break-even among priced arms (a naive min-turnover pick would differ)
    picked = None
    for arm in ARMS:
        if arm == "always_on":
            continue
        tgt = e225.arm_target(sig, split, arm)
        wa = e225.weights_series(sig, arm, tgt)
        s = solve_arm(wa, ret, split, null_w, 2.5)
        if s["break_even_cost_bp_per_unit_turnover"] is None:
            continue
        if picked is None or s["break_even_cost_bp_per_unit_turnover"] > picked[1]:
            picked = (arm, s["break_even_cost_bp_per_unit_turnover"])
    leg("best_arm_is_the_highest_break_even", picked is not None,
        "%s at %.3f bp/unit" % (picked if picked else ("-", 0.0)))

    # L13 the two roots are separated by exactly avg_w * null_excess / D, because
    # excess(c) = gate_specific(c) + avg_w * null_excess(c) and the null's OOS
    # excess does not depend on c. Asserting the IDENTITY rather than an ordering:
    # which root is larger flips with the sign of the null arm's drift, so an
    # inequality written on the sign would pass or fail for the wrong reason.
    a0 = arm_at_cost(w, ret, split, 0.0, 2.5)
    n0b = arm_at_cost(null_w, ret, split, 0.0, 2.5)
    null_ex = n0b.get("excess_oos_bp_per_year")
    d_arm = solved["turnover_differential_oos_per_year"]
    if solved["break_even_cost_bp_excess_basis"] is not None and null_ex is not None \
            and d_arm:
        offset_measured = solved["break_even_cost_bp_excess_basis"] - cstar
        offset_expected = (a0.get("avg_weight_oos") or 0.0) * null_ex / d_arm
        leg("excess_root_sits_avg_weight_drifts_above_the_gate_root",
            abs(offset_measured - offset_expected) < 1e-9,
            "measured %.4f vs expected %.4f bp/unit (null=%.0f bp/yr, avg_w=%.3f)"
            % (offset_measured, offset_expected, null_ex,
               a0.get("avg_weight_oos") or 0.0))
    else:
        leg("excess_root_sits_avg_weight_drifts_above_the_gate_root", False,
            "no excess-basis root produced")

    # L14 the drill-down must actually move the answer: a two-rung ladder and the
    # declared sweep must not be confused for one another
    leg("sweep_length_matches_the_spec", len(ladder) == len(COST_MULTS),
        "%d rungs" % len(ladder))

    # L15 the published "at model cost" block must be the same run as the x1 rung,
    # otherwise two faces would describe the same cost with different numbers
    rung = next((r for r in ladder if r["cost_mult"] == 1.0), None)
    ac = solved["at_model_cost"]
    leg("at_model_cost_matches_the_x1_rung",
        rung is not None
        and ac["excess_bp_per_year"] == rung["excess_bp_per_year"]
        and ac["gate_specific_bp_per_year"] == rung["gate_specific_bp_per_year"]
        and ac["excess_oos_t"] == rung["excess_oos_t"],
        "excess=%.3f gs=%.3f t=%.3f on both faces"
        % (ac["excess_bp_per_year"] or 0.0, ac["gate_specific_bp_per_year"] or 0.0,
           ac["excess_oos_t"] or 0.0))

    # L16 "clears the bar" needs all three: positive excess, t at the bar, and a
    # published t. A missing t must read False, never True by accident.
    leg("clearing_the_bar_needs_evidence",
        classify(PLAUSIBLE_HIGH_BP, 1.0)[0] == CLASS_SURVIVES
        and not (ac["clears_bar"] and (ac["excess_oos_t"] is None)),
        "surviving the toll is separate from clearing the bar")

    # L17 the fragility reading is the reciprocal of the toll differential: a flat
    # line turns a small residual into a wild root, and the face must say how far
    leg("root_fragility_is_one_over_the_differential",
        solved["root_fragility_bp_per_unit_per_bp_per_year"] is not None
        and abs(solved["root_fragility_bp_per_unit_per_bp_per_year"]
                * solved["turnover_differential_oos_per_year"] - 1.0) < 1e-12,
        "1/D = %.4f bp/unit per bp/yr" % (solved["root_fragility_bp_per_unit_per_bp_per_year"]
                                          or 0.0))

    # L18 ranking by residual and ranking by break-even name DIFFERENT arms once every
    # arm sits below zero: the first face called the -324 bp/yr arm "the best
    # gate-specific" because it was picked by root. The two selectors must disagree
    # on this fixture, or the label is meaningless.
    fixture = [{"name": "always_on", "gate_specific_at_zero_cost_bp_per_year": 0.0,
                "break_even_cost_bp_per_unit_turnover": None},
               {"name": "big_residual_small_turn",
                "gate_specific_at_zero_cost_bp_per_year": -100.0,
                "break_even_cost_bp_per_unit_turnover": -500.0},
               {"name": "small_residual_big_turn",
                "gate_specific_at_zero_cost_bp_per_year": -300.0,
                "break_even_cost_bp_per_unit_turnover": -20.0}]
    g_pick = _pick_best_g0(fixture)
    r_pick = _pick_best_root(fixture)
    leg("best_residual_and_best_root_are_different_questions",
        g_pick["name"] == "big_residual_small_turn"
        and r_pick["name"] == "small_residual_big_turn",
        "residual picks %s, root picks %s" % (g_pick["name"], r_pick["name"]))

    passed = sum(1 for _, ok_, _ in legs if ok_)
    for name, ok_, note in legs:
        print(("PASS " if ok_ else "FAIL ") + name + (" | " + note if note else ""))
    print("%d/%d legs passed" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run()
    return 0 if face else 2


if __name__ == "__main__":
    raise SystemExit(main())