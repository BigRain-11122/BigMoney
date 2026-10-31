"""E228: does the state tilt survive an exposure-matched null?

E226 read every gated arm against the always-on arm by multiplying the null's
drift by the arm's own average weight:

    gate_specific(arm) = arm.excess_oos - avg_weight(arm) * always_on.excess_oos

On the equal-weight basket that hands binary_low a +340 bp/yr residual next to
+1.8 bp/yr of actual excess at t=0.01, and the same rule reads -324 bp/yr on the
single panel. A share of somebody else's drift is an attribution, not a
benchmark: the arm is charged for a position it never held, at a weight it only
held on average.

This face replaces that benchmark with an exposure-matched one. Every gated arm
is compared to a FLAT arm that holds that arm's own average out-of-sample weight
for the whole sample:

    matched(arm) = arm.excess_oos - flat(avg_weight(arm)).excess_oos

The flat arm opens once at i=0 (in the in-sample leg) and never trades again, so
its out-of-sample turnover is zero and its out-of-sample excess is exactly
w_bar * (mean OOS return - IS mean return). Exposure for exposure: same average
weight, same bar, no attribution.

Frozen before reading any number:

  * model: identical to E225/E226 (vol tercile signal, 60/40 split, 252-session
    floor, daily rebalance, |dw| pays one side at 13.041 bp, excess is
    w*(r - mu_is) - |dw|*c). Nothing about the arms, the split or the accounting
    moves. Only the benchmark does.
  * both benchmarks are read at the frozen model cost AND at zero cost, so a
    change of sign cannot be blamed on the toll. Every arm reports both.
  * a sign flip is declared only when both residuals are defined and their signs
    differ (a zero on either side is published as a boundary case, not as a flip).
  * coverage: an arm with fewer than 252 out-of-sample decisions is published as
    UNASSESSABLE and excluded from the flip count -- a short window cannot price
    a rule and it must not be counted as evidence either way.
  * the two daily series (arm and its matched null) must reproduce their own
    published annual figures before a difference t is printed; that assertion is
    also a selftest leg, so a drift in either formula turns the face red instead
    of printing a plausible number.
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

UNIT_COST_BP = e225.COST_SIDE_BP           # 13.041 bp per unit of turnover
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
ARMS = e225.ARMS
NULL_ARM = "always_on"

# the two cost readings every arm is published at
COST_READINGS = (("at_model_cost", UNIT_COST_BP), ("at_zero_cost", 0.0))

SIGN_POS = "positive"
SIGN_NEG = "negative"
SIGN_ZERO = "zero"
SIGN_UNDEFINED = "undefined"

CLASS_FLIP = "SIGN_FLIP"
CLASS_SAME = "SIGN_SAME"
CLASS_BOUNDARY = "BOUNDARY_ZERO"
CLASS_UNASSESSABLE = "UNASSESSABLE"


# ---------------------------------------------------------------- the nulls
def flat_weights(n_sessions, weight):
    """A null that holds one constant weight for the whole sample.

    It pays its opening trade at i=0 -- inside the in-sample leg -- and nothing
    afterwards, so its out-of-sample turnover is zero by construction and its
    out-of-sample excess is exactly weight * (mean OOS return - IS mean return).
    """
    return [float(weight)] * n_sessions


def drift_split_residual(arm_stats, null_stats):
    """E226's benchmark: the arm's excess minus its share of the null's drift."""
    a = arm_stats.get("excess_oos_bp_per_year")
    if a is None:
        return None
    if null_stats is None or null_stats.get("excess_oos_bp_per_year") is None:
        return a
    w_bar = arm_stats.get("avg_weight_oos") or 0.0
    return a - w_bar * null_stats["excess_oos_bp_per_year"]


def matched_residual(arm_stats, matched_stats):
    """The exposure-matched benchmark: arm minus the flat arm at its own weight."""
    a = arm_stats.get("excess_oos_bp_per_year")
    if a is None:
        return None
    if matched_stats is None or matched_stats.get("excess_oos_bp_per_year") is None:
        return None
    return a - matched_stats["excess_oos_bp_per_year"]


# ---------------------------------------------------------------- statistics
def excess_series(weights, ret_bp, split, cost_bp):
    """Out-of-sample daily excess, written to reproduce e225.tilt_stats exactly."""
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        cost = abs(dw) * cost_bp
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append((i, w * r - cost - w * mu_is))
        prev_w = w
    cut = split - 1
    return [x for (i, x) in rows if i >= cut]


def rows_for(weights, ret_bp, split, cost_side_bp):
    """Every session's gross, charged cost and excess against the in-sample drift.

    Returns (rows, mu_is). This is the panel the whole E229..E237 family decomposes: it
    had gone missing from this module while four of them still called it, so the accounting
    lives here once and `excess_series` is its out-of-sample slice (L0 pins that).
    """
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        abs_dw = abs(w - prev_w)
        cost = abs_dw * cost_side_bp
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append({"i": i, "w": w, "abs_dw": abs_dw, "gross_bp": w * r,
                     "cost_bp": cost, "excess_bp": w * r - cost - w * mu_is})
        prev_w = w
    return rows, mu_is


def series_matches_stats(series, stats, tol=1e-6):
    """The daily series must rebuild the annual figure it is printed beside."""
    if not series or stats is None:
        return False
    if stats.get("excess_oos_bp_per_year") is None:
        return False
    m = sum(series) / len(series)
    return abs(m * SESSIONS_PER_YEAR - stats["excess_oos_bp_per_year"]) < tol


def diff_t(a_series, m_series):
    """Newey-West t of the daily difference between the arm and its null."""
    if not a_series or not m_series or len(a_series) != len(m_series):
        return None
    d = [x - y for x, y in zip(a_series, m_series)]
    if len(d) < 3:
        return None
    m = sum(d) / len(d)
    se = e225._hac_se(d)
    if not se:
        return None
    return m / se


def sign_of(x):
    if x is None:
        return SIGN_UNDEFINED
    if x > 0.0:
        return SIGN_POS
    if x < 0.0:
        return SIGN_NEG
    return SIGN_ZERO


def classify_flip(drift_bp, matched_bp, assessable=True):
    """A flip needs two defined, non-zero residuals that disagree in sign."""
    if not assessable:
        return CLASS_UNASSESSABLE, "fewer_than_%d_oos_decisions" % MIN_OOS_SESSIONS
    if drift_bp is None or matched_bp is None:
        return CLASS_UNASSESSABLE, "a_benchmark_is_undefined"
    sd = sign_of(drift_bp)
    sm = sign_of(matched_bp)
    if sd == SIGN_ZERO or sm == SIGN_ZERO:
        return CLASS_BOUNDARY, "zero_on_one_side_is_not_a_flip"
    if sd != sm:
        return CLASS_FLIP, "drift_split_%s_matched_%s" % (sd, sm)
    return CLASS_SAME, "both_%s" % sd


# ---------------------------------------------------------------- one arm
def evaluate_arm(name, weights, ret_bp, split, null_w, bar_t):
    """Read one arm against both benchmarks at both costs."""
    out = {"name": name, "readings": {}}
    for label, cost_bp in COST_READINGS:
        arm_stats = e225.tilt_stats(weights, ret_bp, split, cost_bp, bar_t)
        null_stats = e225.tilt_stats(null_w, ret_bp, split, cost_bp, bar_t)
        w_bar = arm_stats.get("avg_weight_oos")
        if w_bar is None:
            w_bar = 0.0
        matched_w = flat_weights(len(ret_bp), w_bar)
        matched_stats = e225.tilt_stats(matched_w, ret_bp, split, cost_bp, bar_t)

        drift_bp = drift_split_residual(arm_stats, null_stats)
        matched_bp = matched_residual(arm_stats, matched_stats)
        assessable = (arm_stats.get("oos_decisions") or 0) >= MIN_OOS_SESSIONS

        # the difference t is only printed when both daily series rebuild their
        # own published annual figures -- otherwise it would be a number about
        # nothing and the face says so instead
        a_series = excess_series(weights, ret_bp, split, cost_bp)
        m_series = excess_series(matched_w, ret_bp, split, cost_bp)
        series_ok = (series_matches_stats(a_series, arm_stats)
                     and series_matches_stats(m_series, matched_stats))
        t_diff = diff_t(a_series, m_series) if series_ok else None

        verdict, reason = classify_flip(drift_bp, matched_bp, assessable)
        out["readings"][label] = {
            "cost_side_bp": cost_bp,
            "avg_weight_oos": w_bar,
            "oos_decisions": arm_stats.get("oos_decisions"),
            "assessable": assessable,
            "arm_excess_bp_per_year": arm_stats.get("excess_oos_bp_per_year"),
            "arm_excess_oos_t": arm_stats.get("excess_oos_t"),
            "always_on_excess_bp_per_year": null_stats.get("excess_oos_bp_per_year"),
            "always_on_turnover_oos_per_year": null_stats.get("turnover_oos_per_year"),
            "matched_null_excess_bp_per_year": matched_stats.get("excess_oos_bp_per_year"),
            "matched_null_turnover_oos_per_year": matched_stats.get("turnover_oos_per_year"),
            "drift_split_bp_per_year": drift_bp,
            "matched_exposure_bp_per_year": matched_bp,
            "delta_matched_minus_drift_bp_per_year": (
                (matched_bp - drift_bp) if (matched_bp is not None and drift_bp is not None)
                else None),
            "sign_drift_split": sign_of(drift_bp),
            "sign_matched": sign_of(matched_bp),
            "flip": verdict,
            "flip_reason": reason,
            "diff_t": t_diff,
            "series_rebuilds_stats": series_ok,
        }
        if name == NULL_ARM:
            out["readings"][label]["note"] = (
                "null arm against itself: the matched null is the same constant-1.0 "
                "series, so this reading must be exactly 0.00 -- it is the identity leg")
    return out


def summarise_panel(panel):
    arms = [a for a in panel["arms"] if a["name"] != NULL_ARM]
    for label, _cost in COST_READINGS:
        flips = [a["name"] for a in arms
                 if a["readings"][label]["flip"] == CLASS_FLIP]
        boundaries = [a["name"] for a in arms
                      if a["readings"][label]["flip"] == CLASS_BOUNDARY]
        unassess = [a["name"] for a in arms
                    if a["readings"][label]["flip"] == CLASS_UNASSESSABLE]
        panel["sign_flips_" + label] = flips
        panel["boundary_cases_" + label] = boundaries
        panel["unassessable_" + label] = unassess
        panel["n_arms_compared_" + label] = len(arms) - len(unassess)
        panel["n_sign_flips_" + label] = len(flips)
    return panel


def _worst_flip(panel, label):
    """The largest absolute change of reading, flip or not, for the answer sentence."""
    best = None
    for a in panel["arms"]:
        if a["name"] == NULL_ARM:
            continue
        r = a["readings"][label]
        d = r.get("delta_matched_minus_drift_bp_per_year")
        if d is None:
            continue
        if best is None or abs(d) > abs(best[1]):
            best = (a["name"], d, r)
    return best


# ---------------------------------------------------------------- the face
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
        panels.append({"panel": "basket_equal_weight",
                       "symbol": "+".join(sorted(e225.BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0],
                       "last": basket[0][-1]})

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        null_w = e225.weights_series(sig, NULL_ARM)
        arms_out = []
        for arm in ARMS:
            target = e225.arm_target(sig, split, arm)
            w = e225.weights_series(sig, arm, target)
            row = evaluate_arm(arm, w, ret_bp, split, null_w, bar_t)
            row["target_bp"] = target
            arms_out.append(row)
        panel["arms"] = arms_out
        panel["split_session"] = split
        panel["split_date"] = dates[split]
        summarise_panel(panel)

    face = {
        "study": "E228",
        "title": "does the state tilt survive an exposure-matched null?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "model": "identical to E225/E226; only the benchmark changes",
            "unit_cost_bp": UNIT_COST_BP,
            "cost_readings": {label: c for label, c in COST_READINGS},
            "drift_split": "arm.excess_oos - avg_weight(arm) * always_on.excess_oos",
            "matched_exposure": "arm.excess_oos - flat(avg_weight(arm)).excess_oos, "
                                "where flat opens once inside the IS leg and never trades",
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "bar_t": bar_t,
            "tests": n_tests,
            "flip_rule": "both residuals defined and non-zero and of different signs; "
                         "a zero on either side is BOUNDARY_ZERO, not a flip",
            "t_rule": "the daily difference t is published only when both daily series "
                      "rebuild their own published annual figures (tol 1e-6 bp/yr)",
        },
        "panels": panels,
    }

    primary = panels[0]
    worst = _worst_flip(primary, "at_model_cost")
    flips = primary["sign_flips_at_model_cost"]
    compared = primary["n_arms_compared_at_model_cost"]
    basket_flips = (panels[1]["sign_flips_at_model_cost"] if len(panels) > 1 else [])
    basket_compared = (panels[1]["n_arms_compared_at_model_cost"]
                       if len(panels) > 1 else 0)

    # how far apart the two benchmarks sit on each panel, and why: the identity
    # holds only while the always-on null pays no out-of-sample turnover
    gaps = {}
    for panel in panels:
        ds = [abs(a["readings"]["at_model_cost"]["delta_matched_minus_drift_bp_per_year"])
              for a in panel["arms"]
              if a["readings"]["at_model_cost"].get(
                  "delta_matched_minus_drift_bp_per_year") is not None]
        null_row = next((a for a in panel["arms"] if a["name"] == NULL_ARM), None)
        gaps[panel["panel"]] = {
            "max_abs_gap_bp_per_year": max(ds) if ds else None,
            "always_on_turnover_oos_per_year": (
                null_row["readings"]["at_model_cost"]["always_on_turnover_oos_per_year"]
                if null_row else None),
        }
    face["benchmark_gap"] = gaps
    face["frozen_spec"]["identity_condition"] = (
        "drift_split == matched_exposure exactly when the always-on null pays zero "
        "out-of-sample turnover: its OOS excess is then 1.0 x (mean OOS return - IS "
        "mean) and w_bar times it equals the flat arm at w_bar. The session face "
        "publishes the null's measured OOS turnover so the condition is checked, "
        "not assumed.")

    if not flips and not basket_flips:
        anchored = None
        for a in primary["arms"]:
            if a["name"] == NULL_ARM:
                continue
            r = a["readings"]["at_model_cost"]
            if r.get("arm_excess_bp_per_year") is not None and (
                    anchored is None
                    or abs(r["arm_excess_bp_per_year"])
                    < abs(anchored["arm_excess_bp_per_year"])):
                anchored = r
        gap_p = gaps["primary_single"]["max_abs_gap_bp_per_year"]
        gap_b = gaps.get("basket_equal_weight", {}).get("max_abs_gap_bp_per_year")
        null_ex = (anchored or {}).get("always_on_excess_bp_per_year") or 0.0
        null_verb = "earned" if null_ex > 0 else "lost"
        face["answer"] = (
            "the drift split was already exposure-matched. On both panels a flat arm "
            "held at each gated arm's own average weight reproduces E226's reading to "
            "within %.6f bp/yr (primary) and %s bp/yr (basket), because the always-on "
            "null pays no out-of-sample turnover (%.3f / %s per year) and its excess is "
            "therefore exactly 1.0 x (mean OOS return - IS mean) -- so no arm changes "
            "sign out of %d comparable arms on the primary panel and %d on the basket. "
            "That is the finding, and it cuts against the E226 caveat rather than "
            "confirming it: a large gate-specific residual on the basket is not an "
            "attribution artifact, it is the arithmetic of charging an arm a share of a "
            "benchmark that moves a lot. On the primary panel %s leaves %+.1f bp/yr of "
            "own excess against a null that %s %.0f bp/yr, so the residual is what is "
            "left of the rule after that charge -- the benchmark named the movement, it "
            "did not manufacture the gain."
            % ((gap_p or 0.0),
               ("%.6f" % gap_b) if gap_b is not None else "n/a",
               gaps["primary_single"]["always_on_turnover_oos_per_year"] or 0.0,
               ("%.3f" % (gaps.get("basket_equal_weight", {}).get(
                   "always_on_turnover_oos_per_year") or 0.0)) if gap_b is not None else "n/a",
               compared, basket_compared,
               (next((a["name"] for a in primary["arms"]
                      if a["readings"]["at_model_cost"] is anchored), "-")
                if anchored else "-"),
               (anchored or {}).get("arm_excess_bp_per_year") or 0.0,
               null_verb, abs(null_ex)))
    elif worst:
        name, delta, reading = worst
        face["answer"] = (
            "replacing the drift share with an exposure-matched null moves the primary "
            "panel's readings by up to %+.0f bp/yr (%s: %+.0f -> %+.0f) and changes the "
            "sign of %d of %d comparable arms at the frozen cost%s; at zero cost %d of %d "
            "flip. The basket reads %d of %d at the frozen cost%s. A rule whose verdict "
            "depends on which benchmark you pick was never a rule."
            % (delta, name,
               (reading["drift_split_bp_per_year"] or 0.0),
               (reading["matched_exposure_bp_per_year"] or 0.0),
               len(flips), compared,
               (" (" + ", ".join(flips) + ")") if flips else "",
               len(primary["sign_flips_at_zero_cost"]),
               primary["n_arms_compared_at_zero_cost"],
               len(basket_flips), basket_compared,
               (" (" + ", ".join(basket_flips) + ")") if basket_flips else ""))
    else:
        face["answer"] = ("no arm could be read against both benchmarks; the face is "
                          "empty and says so rather than inventing a sign")

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "MATCHED-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "matched_latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "name", "cost_reading", "cost_side_bp", "avg_weight_oos",
                "oos_decisions", "drift_split_bp_per_year", "matched_exposure_bp_per_year",
                "delta_matched_minus_drift_bp_per_year", "flip", "diff_t"]
        # an explicit list plus a length guard: adjacent literals would glue and
        # silently swallow the first data row (the r1325 lesson)
        assert len(cols) == 11, "column list length drift"
        csv_path = os.path.join(outdir, "matched_by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    for label, _cost in COST_READINGS:
                        r = a["readings"][label]
                        w.writerow({"panel": panel["panel"], "name": a["name"],
                                    "cost_reading": label, **r})
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
        ret.append(drift_bp + v * z)
    return ret


def selftest():
    checks = []
    n = 900
    ret = _synth(n)
    split = e225.split_index(n)
    bar_t = 2.8

    # L0 the restored rows_for is the panel the family decomposes: its out-of-sample slice
    # must equal excess_series, which is the same accounting the published face uses
    sig0 = e225.vol_signal(ret)
    w0 = e225.weights_series(sig0, "tilt_step")
    rows0, mu0 = rows_for(w0, ret, split, UNIT_COST_BP)
    checks.append(("L0 rows_for agrees with excess_series",
                   [r["excess_bp"] for r in rows0 if r["i"] >= split - 1]
                   == excess_series(w0, ret, split, UNIT_COST_BP)))
    checks.append(("L0b rows_for never emits a session without a return",
                   all(ret[r["i"] + 1] is not None for r in rows0)))
    def _dw_ok(rows):
        if not rows:
            return False
        if abs(rows[0]["abs_dw"] - abs(rows[0]["w"])) > 1e-12:
            return False
        return all(abs(b["abs_dw"] - abs(b["w"] - a["w"])) < 1e-12
                   for a, b in zip(rows, rows[1:]))

    checks.append(("L0c rows_for charges |dw| against the weight actually held", _dw_ok(rows0)))

    # L1 a flat null's out-of-sample turnover is zero and its excess is w*(drift)
    w_bar = 0.35
    flat = flat_weights(n, w_bar)
    fs = e225.tilt_stats(flat, ret, split, 0.0, bar_t)
    checks.append(("L1 flat null never trades out of sample",
                   abs(fs["turnover_oos_per_year"] or 0.0) < 1e-12))
    checks.append(("L1b flat null holds exactly its weight",
                   abs((fs["avg_weight_oos"] or 0.0) - w_bar) < 1e-12))

    # L2 the null arm against itself is exactly zero under both benchmarks
    null_w = e225.weights_series(e225.vol_signal(ret), NULL_ARM)
    self_row = evaluate_arm(NULL_ARM, null_w, ret, split, null_w, bar_t)
    for label, _c in COST_READINGS:
        r = self_row["readings"][label]
        checks.append(("L2 %s identity leg is exactly 0" % label,
                       r["drift_split_bp_per_year"] is not None
                       and abs(r["drift_split_bp_per_year"]) < 1e-9
                       and r["matched_exposure_bp_per_year"] is not None
                       and abs(r["matched_exposure_bp_per_year"]) < 1e-9))

    # L3 a constant-weight arm is also exactly zero against its matched null
    const = flat_weights(n, 0.4)
    cs = e225.tilt_stats(const, ret, split, UNIT_COST_BP, bar_t)
    cw = flat_weights(n, cs["avg_weight_oos"])
    ms = e225.tilt_stats(cw, ret, split, UNIT_COST_BP, bar_t)
    checks.append(("L3 constant-weight arm: matched residual is 0",
                   abs(matched_residual(cs, ms)) < 1e-9))

    # L4 the always-on null never trades out of sample, so the two benchmarks agree
    # exactly: w_bar * null == flat(w_bar). This is the face's central finding and
    # it is pinned here, not merely observed downstream.
    dec = [0.8 * (1.0 - i / float(n - 1)) for i in range(n)]
    arm_stats = e225.tilt_stats(dec, ret, split, UNIT_COST_BP, bar_t)
    null_stats = e225.tilt_stats(null_w, ret, split, UNIT_COST_BP, bar_t)
    wb = arm_stats["avg_weight_oos"]
    mt = e225.tilt_stats(flat_weights(n, wb), ret, split, UNIT_COST_BP, bar_t)
    d_split = drift_split_residual(arm_stats, null_stats)
    d_match = matched_residual(arm_stats, mt)
    checks.append(("L4 the always-on null has zero OOS turnover",
                   abs(null_stats["turnover_oos_per_year"] or 0.0) < 1e-12))
    checks.append(("L4b with a zero-turnover null the two benchmarks coincide",
                   d_split is not None and d_match is not None
                   and abs(d_split - d_match) < 1e-9))

    # L4c the identity is a property of the NULL, not of the arithmetic: give it
    # turnover and the two readings separate by exactly that null's extra toll
    chatter = [1.0 if (i % 2 == 0) else 0.5 for i in range(n)]
    cn = e225.tilt_stats(chatter, ret, split, UNIT_COST_BP, bar_t)
    d_split_c = drift_split_residual(arm_stats, cn)
    checks.append(("L4c a trading null separates the two benchmarks",
                   d_split_c is not None and d_match is not None
                   and abs(d_split_c - d_match) > 1e-6))

    # L5 flip classifier: only two defined non-zero opposing signs count
    checks.append(("L5a +100 vs -100 is a flip",
                   classify_flip(100.0, -100.0)[0] == CLASS_FLIP))
    checks.append(("L5b +100 vs +50 is not a flip",
                   classify_flip(100.0, 50.0)[0] == CLASS_SAME))
    checks.append(("L5c +100 vs 0 is a boundary, not a flip",
                   classify_flip(100.0, 0.0)[0] == CLASS_BOUNDARY))
    checks.append(("L5d None vs -100 is unassessable, never a flip",
                   classify_flip(None, -100.0)[0] == CLASS_UNASSESSABLE))
    checks.append(("L5e a short window is unassessable regardless of signs",
                   classify_flip(100.0, -100.0, assessable=False)[0] == CLASS_UNASSESSABLE))

    # L6 the daily series rebuilds its own annual figure (the t is only honest then)
    a_series = excess_series(dec, ret, split, UNIT_COST_BP)
    checks.append(("L6 arm series rebuilds its published annual excess",
                   series_matches_stats(a_series, arm_stats)))
    checks.append(("L6b a corrupted series fails the rebuild assertion",
                   not series_matches_stats([x + 1.0 for x in a_series], arm_stats)))

    # L7 the difference t is finite and moves with a larger wedge
    t_small = diff_t(a_series, excess_series(flat_weights(n, wb), ret, split,
                                             UNIT_COST_BP))
    checks.append(("L7 difference t is computable on the synthetic panel",
                   t_small is not None and abs(t_small) < 1e4))

    # L8 missing out-of-sample mean -> None, never 0
    empty = [None] * 40
    es = e225.tilt_stats(flat_weights(len(empty), 0.5), empty, 20, UNIT_COST_BP, bar_t)
    checks.append(("L8 no OOS mean -> matched residual None, never 0",
                   matched_residual(es, es) is None))

    # L9 a boundary-zero arm is reported and excluded from the flip count
    zero_flat = flat_weights(n, 0.0)
    zs = e225.tilt_stats(zero_flat, ret, split, UNIT_COST_BP, bar_t)
    z_row = evaluate_arm("zero_arm", zero_flat, ret, split, null_w, bar_t)
    checks.append(("L9 zero-weight arm reads BOUNDARY_ZERO not SIGN_FLIP",
                   z_row["readings"]["at_model_cost"]["flip"] in
                   (CLASS_BOUNDARY, CLASS_UNASSESSABLE)))

    # L10 the summary counts only comparable arms
    fake_panel = {"arms": [self_row, {"name": "a", "readings": {
        "at_model_cost": {"flip": CLASS_FLIP}, "at_zero_cost": {"flip": CLASS_SAME}}},
        {"name": "b", "readings": {
            "at_model_cost": {"flip": CLASS_UNASSESSABLE},
            "at_zero_cost": {"flip": CLASS_SAME}}}]}
    summarise_panel(fake_panel)
    checks.append(("L10 flip count excludes the null and unassessable arms",
                   fake_panel["n_arms_compared_at_model_cost"] == 1
                   and fake_panel["n_sign_flips_at_model_cost"] == 1))

    passed = sum(1 for _n, ok in checks if ok)
    for name, ok in checks:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(checks)))
    return passed == len(checks)


def main(argv=None):
    ap = argparse.ArgumentParser(description="E228 exposure-matched null for the tilt")
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return 0 if selftest() else 2
    face = run(save=not args.no_save)
    if face is None:
        return 2
    if not args.no_save:
        print(face["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())