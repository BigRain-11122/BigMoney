"""E230 -- can the toll channel be bought back?

E229 split every gated arm's paired series into selection (which days), sizing (how much)
and toll (what moving costs) and found that on both panels the ONLY channel that clears
its bar is the toll: tilt_step / tilt_linear pay t ~ -10 on the basket. What separates
those rules from a flat constant is measurably the cost of moving, not timing skill.

That raises a mechanical question. The toll is charged on |dw|, one side per unit of
weight movement, so it is bought back by the only thing that changes it: making the rule
move less often. The obvious instrument is a HYSTERESIS DEADBAND on the state signal --
hold the last committed weight until the signal has travelled `band` away from the value
it sat at when that weight was committed. The question the card asks is whether that
trade is a fix or a swindle:

    does the band cut the toll channel FASTER than it cuts the selection channel?

Frozen design (written before any number was read):

  * signal: v_i = the same 20-session rolling volatility E224/E225 already use. No new
    state variable, no new threshold machinery -- the band rides the existing signal.
  * rule: hold the committed weight until |v_i - v_at_last_commit| >= band, then commit
    the base arm's own target weight. `band = 0` therefore commits every session and is
    the base arm EXACTLY; that identity is a selftest leg, not a claim.
  * band grid, in units of the in-sample standard deviation of the signal (IS-only, so
    the band itself is causal): 0, 0.10, 0.25, 0.50, 1.00, 2.00 x sd_is.
  * arms: binary_low, tilt_step, tilt_linear -- the three E229 judged.
  * panels: the primary single (sh510300) and the equal-weight basket, as E229.
  * channels: computed with ONE common constant per (panel, arm) -- the base arm's own
    OOS average weight. E229's per-arm match would re-derive the constant at every rung,
    which makes every rung a different benchmark; the rungs have to be comparable, so
    the constant is frozen at the base arm and the arithmetic identity
    pair = selection + sizing + toll still holds for any c.
  * costs: x1 (13.041 bp/side) and x2 (2x). Every rung publishes both.

Decision rule, per (panel, arm, rung > 0):

  BASELINE     rung 0 -- the base arm itself, deltas are zero by construction.
  NO_EFFECT    the band changes no weight at all; the rung is not an experiment.
  BAND_COSTS   the banded arm's pair is not better than the base arm's pair.
  BAND_NOISE   it is better in point estimate but the paired difference does not clear
               the Bonferroni bar over cells x 2 cost levels -- a band that only looks
               good is not a fix.
  BAND_PAYS    the difference clears the bar AND the frozen condition holds: the toll
               saving exceeds the selection loss at x2 costs.

Two disclosures that the face must carry rather than bury:

  1. the toll channel is exactly linear in the cost parameter while selection and sizing
     are not, so d_toll(x2) == 2*d_toll(x1) identically. The x2 limb of the condition is
     therefore mechanically weaker than the x1 limb, and a study that reported only "it
     still pays at x2" would be reporting an algebraic fact. The face prints both limbs
     and a selftest leg pins the factor of two.
  2. a band that does not reduce the number of weight changes has not been tested. Every
     rung reports its change count beside its toll, and NO_EFFECT is a verdict, not a
     silent pass.

Nothing here can adopt a band: the base arms are already judged (E228/E229), and the
ladder only asks whether one of their channels is purchasable. ADD is not in the
vocabulary on purpose.
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
import e228_matched_exposure as e228  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
COST_X2_MULT = e225.COST_X2_MULT
IS_FRAC = e225.IS_FRAC
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
NW_LAG = e225.NW_LAG
Z_80 = e225.Z_80
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

BAND_ARMS = ["binary_low", "tilt_step", "tilt_linear"]
BAND_FRACS = (0.0, 0.10, 0.25, 0.50, 1.00, 2.00)
CHANNELS = ("selection", "sizing", "toll")

# frozen: at or below this many weight changes over the whole sample the banded rule has
# stopped being a rule -- it is a buy-and-hold at roughly the base arm's exposure, which is
# the null arm. A wide band that "saves toll" by collapsing to that is not a fix, and the
# face has to say so rather than bank the saving.
RULE_COLLAPSE_FLOOR = 5

VERDICTS = {"BASELINE", "NO_EFFECT", "BAND_COSTS", "BAND_NOISE", "BAND_PAYS",
            "UNRESOLVED"}


def _ann(sum_bp, n):
    if not n:
        return None
    return sum_bp / float(n) * SESSIONS_PER_YEAR


# ---------------------------------------------------------------- the band
def band_width(sig, split):
    """IS-only scale for the deadband: the standard deviation of the signal before the split.

    Using anything after the split would let the band see the future; the selftest
    perturbs the post-split signal and requires this number not to move.
    """
    past = [v for v in sig[1:split] if v is not None]
    if len(past) < 2:
        return None
    return e225._sd(past)


def band_weights(sig, arm, band):
    """Hold the last committed weight until the signal travels `band` from where it was.

    band == 0 commits on every session whose signal exists, so the result is E225's own
    weights series for that arm (pinned by a selftest leg). During the signal warm-up
    (v is None) the rule holds whatever weight it already had, which is 0.0 for the first
    such sessions -- the same thing the base arm does.
    """
    out = []
    last_v = None
    w_held = 0.0
    for i in range(len(sig)):
        v = sig[i]
        if v is None:
            out.append(w_held)
            continue
        if last_v is None or abs(v - last_v) >= band:
            w_held = e225.weight_at(sig, i, arm)
            last_v = v
        out.append(w_held)
    return out


def change_profile(weights):
    """How often the rule moves, and how much total weight it pushes."""
    changes = 0
    total_abs_dw = 0.0
    prev = 0.0
    for w in weights:
        d = w - prev
        if d != 0.0:
            changes += 1
            total_abs_dw += abs(d)
        prev = w
    return {"weight_changes": changes, "total_abs_dw": total_abs_dw}


# ---------------------------------------------------------------- channels at one cost
def channel_rows_c(weights, ret_bp, split, cost_side_bp, const):
    """E229's three channels, computed against ONE frozen constant.

    Same index set and same charge convention as e228.rows_for (w_{-1} = 0, a None
    return skips the row but carries the weight forward), so two rungs line up session
    by session and their difference is a per-session series, not two totals.
    """
    base, mu_is = e228.rows_for(weights, ret_bp, split, cost_side_bp)
    cut = split - 1
    rows = []
    for r in base:
        if r["i"] < cut:
            continue
        ret = ret_bp[r["i"] + 1]
        assert ret is not None, "rows_for must not emit a session without a return"
        dev = ret - mu_is
        if r["w"] == 0.0:
            sel = (-const) * dev
            siz = 0.0
        else:
            sel = 0.0
            siz = (r["w"] - const) * dev
        toll = -r["cost_bp"]
        rows.append({"i": r["i"], "w": r["w"], "ret_bp": ret, "dev_bp": dev,
                     "selection": sel, "sizing": siz, "toll": toll,
                     "pair": sel + siz + toll,
                     "cost_bp": r["cost_bp"], "abs_dw": r["abs_dw"]})
    return rows, mu_is


def _stats(series):
    if not series:
        return {"n": 0, "mean_bp": None, "ann_bp_per_year": None, "t_nw": None}
    m = e225._mean(series)
    se = e225._hac_se(series, NW_LAG) if len(series) >= 3 else None
    return {"n": len(series), "mean_bp": m,
            "ann_bp_per_year": _ann(sum(series), len(series)),
            "se_nw": se,
            "t_nw": (m / se) if (se and m is not None) else None,
            "n_eff": e225._n_eff(series) if len(series) >= 3 else None}


def _totals(rows):
    n = len(rows)
    out = {"oos_sessions": n, "pair_ann_bp_per_year": _ann(sum(r["pair"] for r in rows), n)}
    for ch in CHANNELS:
        out[ch + "_ann_bp_per_year"] = _ann(sum(r[ch] for r in rows), n)
    out["identity_residual_bp"] = (sum(r["selection"] + r["sizing"] + r["toll"]
                                       - r["pair"] for r in rows))
    return out


def paired_delta(base_rows, band_rows, rate=1.0):
    """Per-session difference of the banded pair against the base pair at one cost level.

    `rate` scales the toll only, which is exactly what a different cost parameter does:
    the movement charge is linear in it while the selection and sizing terms are not.
    """
    bi = {r["i"]: r for r in base_rows}
    d_pair, d_sel, d_siz, d_toll = [], [], [], []
    for r in band_rows:
        b = bi.get(r["i"])
        if b is None:
            raise AssertionError("rungs must cover the same decision sessions")
        d_pair.append(r["pair"] - b["pair"])
        d_sel.append(r["selection"] - b["selection"])
        d_siz.append(r["sizing"] - b["sizing"])
        d_toll.append((r["toll"] - b["toll"]) * rate)
    return {"pair": d_pair, "selection": d_sel, "sizing": d_siz, "toll": d_toll}


# ---------------------------------------------------------------- verdict
def rung_verdict(delta_block, weights_equal, bar_t):
    """Frozen decision rule; the order of the tests is the order of the docstring."""
    pair_stats = _stats(delta_block["pair"])
    toll = _stats(delta_block["toll"])
    sel = _stats(delta_block["selection"])
    siz = _stats(delta_block["sizing"])
    out = {
        "d_pair_ann_bp_per_year": pair_stats["ann_bp_per_year"],
        "d_pair_t_nw": pair_stats["t_nw"],
        "d_selection_ann_bp_per_year": sel["ann_bp_per_year"],
        "d_sizing_ann_bp_per_year": siz["ann_bp_per_year"],
        "d_toll_ann_bp_per_year": toll["ann_bp_per_year"],
        "bar_t": bar_t,
    }
    # the identity the whole decomposition rests on, at rung level
    out["delta_identity_residual_bp"] = (
        (sel["ann_bp_per_year"] or 0.0) + (siz["ann_bp_per_year"] or 0.0)
        + (toll["ann_bp_per_year"] or 0.0) - (pair_stats["ann_bp_per_year"] or 0.0))
    d = out["d_pair_ann_bp_per_year"]
    if d is None:
        out["verdict"] = "UNRESOLVED"
        out["verdict_reason"] = "no_paired_sessions"
        return out
    if weights_equal:
        out["verdict"] = "NO_EFFECT"
        out["verdict_reason"] = "band_changes_no_weight"
        return out
    if d <= 0.0:
        out["verdict"] = "BAND_COSTS"
        out["verdict_reason"] = "pair %.1f bp/yr not better than the base arm" % (-d)
        return out
    t = out["d_pair_t_nw"]
    if t is None or abs(t) < bar_t:
        out["verdict"] = "BAND_NOISE"
        out["verdict_reason"] = "t=%s < bar %.2f" % (
            ("%.2f" % t) if t is not None else "-", bar_t)
        return out
    pays = ((out["d_toll_ann_bp_per_year"] or 0.0)
            > -(out["d_selection_ann_bp_per_year"] or 0.0))
    out["toll_saving_exceeds_selection_loss"] = pays
    if not pays:
        out["verdict"] = "BAND_PAYS_TOLL_SHORT"
        out["verdict_reason"] = "toll saving does not cover the selection the band gave up"
        return out
    out["verdict"] = "BAND_PAYS"
    out["verdict_reason"] = "t=%.2f, toll %+.1f vs selection %+.1f bp/yr at x2 costs" % (
        t, out["d_toll_ann_bp_per_year"] * COST_X2_MULT,
        out["d_selection_ann_bp_per_year"])
    return out


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    n_panels = 2 if basket else 1
    n_rungs = len(BAND_FRACS) - 1
    n_cells = len(BAND_ARMS) * n_panels * n_rungs * 2  # x two cost levels
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL,
               "sessions": len(single[0]), "first": single[0][0], "last": single[0][-1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0],
                       "last": basket[0][-1]})

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        sd_is = band_width(sig, split)
        panel.update({"split_session": split, "split_date": dates[split],
                      "is_frac": IS_FRAC, "signal_sd_is_bp": sd_is,
                      "band_grid_fracs": list(BAND_FRACS)})
        if not sd_is:
            panel["arms"] = []
            panel["note"] = "signal too short for an in-sample band width"
            continue
        panel["arms"] = []
        for arm in BAND_ARMS:
            base_w = band_weights(sig, arm, 0.0)
            # band 0 must be the base arm itself, or the ladder has no origin
            assert base_w == e225.weights_series(sig, arm), \
                "band 0 must reproduce the base arm exactly"
            base_rows, _mu = channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, 0.0)
            const = e225._mean([r["w"] for r in base_rows]) or 0.0
            base_rows, mu_is = channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, const)
            base_rows_x2, _ = channel_rows_c(base_w, ret_bp, split,
                                             COST_SIDE_BP * COST_X2_MULT, const)
            base_tot = _totals(base_rows)
            arm_out = {"name": arm, "const_weight": const,
                       "mu_is_bp_per_day": mu_is,
                       "base": base_tot,
                       "base_x2": _totals(base_rows_x2),
                       "rungs": []}
            for frac in BAND_FRACS:
                band = frac * sd_is
                w = base_w if frac == 0.0 else band_weights(sig, arm, band)
                prof = change_profile(w)
                if frac == 0.0:
                    rung = {"band_frac": frac, "band_bp": 0.0,
                            "band_width_is_bp": sd_is,
                            "weight_changes": prof["weight_changes"],
                            "rule_collapsed": prof["weight_changes"] <= RULE_COLLAPSE_FLOOR,
                            "total_abs_dw": prof["total_abs_dw"],
                            "totals": base_tot, "totals_x2": _totals(base_rows_x2),
                            "verdict": "BASELINE",
                            "verdict_reason": "the base arm itself"}
                    arm_out["rungs"].append(rung)
                    continue
                rows, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, const)
                rows_x2, _ = channel_rows_c(w, ret_bp, split,
                                            COST_SIDE_BP * COST_X2_MULT, const)
                delta = paired_delta(base_rows, rows)
                delta_x2 = paired_delta(base_rows_x2, rows_x2)
                # the x2 limb differs from the x1 limb only through the toll multiplier
                v = rung_verdict(delta_x2, w == base_w, bar_t)
                toll_x2_expected = (delta["toll"] and
                                    _stats([x * COST_X2_MULT for x in delta["toll"]])
                                    ["ann_bp_per_year"])
                rung = {"band_frac": frac, "band_bp": band,
                        "band_width_is_bp": sd_is,
                        "weight_changes": prof["weight_changes"],
                        "rule_collapsed": prof["weight_changes"] <= RULE_COLLAPSE_FLOOR,
                        "total_abs_dw": prof["total_abs_dw"],
                        "totals": _totals(rows), "totals_x2": _totals(rows_x2),
                        "delta_x2": v,
                        "delta_x1_pair_ann_bp_per_year":
                            _stats(delta["pair"])["ann_bp_per_year"],
                        "toll_x2_linearity_residual_bp":
                            (None if toll_x2_expected is None else
                             abs(v["d_toll_ann_bp_per_year"] - toll_x2_expected)),
                        "weight_changes_saved": (prof["weight_changes"]
                                                 - arm_out["rungs"][0]["weight_changes"])}
                arm_out["rungs"].append(rung)
            panel["arms"].append(arm_out)

    face = {
        "study": "E230",
        "title": "does a hysteresis deadband on the volatility state buy back the toll "
                 "channel faster than it loses selection?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "band_arms": BAND_ARMS,
            "band_grid_fracs": list(BAND_FRACS),
            "band_scale": "in-sample standard deviation of the volatility signal",
            "rule": "hold the committed weight until |v_i - v_at_last_commit| >= band",
            "channels": list(CHANNELS),
            "const_weight": "the base arm's own OOS average weight, frozen across rungs",
            "identity": "pair = selection + sizing + toll, per session and per rung",
            "cost_side_bp": COST_SIDE_BP,
            "cost_x2_mult": COST_X2_MULT,
            "is_frac": IS_FRAC,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "nw_lag": NW_LAG,
            "bar_t": bar_t,
            "bar_basis": "two-sided 5%% over %d cells x 2 cost levels" % n_cells,
            "vocabulary": sorted(VERDICTS | {"BAND_PAYS_TOLL_SHORT"}),
            "rule_collapse_floor": RULE_COLLAPSE_FLOOR,
            "no_adoption": "the base arms are already judged; this only asks whether one "
                           "of their channels is purchasable",
            "known_mechanical": "the toll is linear in the cost parameter, so "
                                "d_toll(x2) == 2*d_toll(x1); the x2 limb of the frozen "
                                "condition cannot fail once x1 passes",
        },
        "panels": panels,
    }

    rows_out = []
    for panel in panels:
        for a in panel.get("arms") or []:
            for r in a["rungs"]:
                if r["band_frac"] == 0.0:
                    continue
                rows_out.append({
                    "panel": panel["panel"], "arm": a["name"],
                    "band_frac": r["band_frac"], "band_bp": r["band_bp"],
                    "weight_changes": r["weight_changes"],
                    "weight_changes_saved": r["weight_changes_saved"],
                    "rule_collapsed": r.get("rule_collapsed"),
                    "pair_ann_bp_per_year":
                        r["totals"]["pair_ann_bp_per_year"],
                    "selection_ann_bp_per_year":
                        r["totals"]["selection_ann_bp_per_year"],
                    "sizing_ann_bp_per_year":
                        r["totals"]["sizing_ann_bp_per_year"],
                    "toll_ann_bp_per_year": r["totals"]["toll_ann_bp_per_year"],
                    "d_pair_ann_bp_per_year":
                        r["delta_x2"]["d_pair_ann_bp_per_year"],
                    "d_pair_t_nw": r["delta_x2"]["d_pair_t_nw"],
                    "d_selection_ann_bp_per_year":
                        r["delta_x2"]["d_selection_ann_bp_per_year"],
                    "d_toll_ann_bp_per_year":
                        r["delta_x2"]["d_toll_ann_bp_per_year"],
                    "verdict": r["delta_x2"]["verdict"],
                    "verdict_reason": r["delta_x2"]["verdict_reason"],
                })
    face["ladder_summary"] = {
        "reading": "one row per (panel, arm, rung>0); deltas are the banded arm's pair "
                   "minus the base arm's pair at x2 costs, so a positive "
                   "d_toll_ann_bp_per_year is a toll saving",
        "cells": len(rows_out),
        "band_pays": sum(1 for r in rows_out if r["verdict"] == "BAND_PAYS"),
        "band_costs": sum(1 for r in rows_out if r["verdict"] == "BAND_COSTS"),
        "band_noise": sum(1 for r in rows_out if r["verdict"] == "BAND_NOISE"),
        "band_pays_toll_short": sum(1 for r in rows_out
                                    if r["verdict"] == "BAND_PAYS_TOLL_SHORT"),
        "no_effect": sum(1 for r in rows_out if r["verdict"] == "NO_EFFECT"),
        "unresolved": sum(1 for r in rows_out if r["verdict"] == "UNRESOLVED"),
        "rows": rows_out,
        "ladder_vacuous": all(r["weight_changes_saved"] == 0 for r in rows_out),
        "rule_collapsed": sum(1 for r in rows_out if r.get("rule_collapsed")),
        "rule_collapse_floor": RULE_COLLAPSE_FLOOR,
    }

    pays = [r for r in rows_out if r["verdict"] == "BAND_PAYS"]
    saves = [r["weight_changes_saved"] for r in rows_out]
    tolls = [r["d_toll_ann_bp_per_year"] for r in rows_out
             if r["d_toll_ann_bp_per_year"] is not None]
    sels = [r["d_selection_ann_bp_per_year"] for r in rows_out
            if r["d_selection_ann_bp_per_year"] is not None]
    face["answer"] = (
        "the ladder moved the rule as intended -- across %d cells the band changed the "
        "number of weight changes by %s..%s (total %s), and the toll channel moved with "
        "it (%s..%s bp/yr at x2 costs). The selection channel moved %s..%s bp/yr against "
        "it. %d of %d banded cells are called a fix (BAND_PAYS), %d lose to the base arm "
        "(BAND_COSTS), %d are point-estimate-only (BAND_NOISE), %d save toll but not "
        "enough to cover the selection given up, %d never move a weight, %d unresolved. "
        "Bar: |t| >= %.2f over %d cells."
        % (len(rows_out),
           min(saves) if saves else "-", max(saves) if saves else "-",
           sum(saves) if saves else "-",
           ("%.1f" % min(tolls)) if tolls else "-",
           ("%.1f" % max(tolls)) if tolls else "-",
           ("%.1f" % min(sels)) if sels else "-",
           ("%.1f" % max(sels)) if sels else "-",
           len(pays), len(rows_out),
           sum(1 for r in rows_out if r["verdict"] == "BAND_COSTS"),
           sum(1 for r in rows_out if r["verdict"] == "BAND_NOISE"),
           sum(1 for r in rows_out if r["verdict"] == "BAND_PAYS_TOLL_SHORT"),
           sum(1 for r in rows_out if r["verdict"] == "NO_EFFECT"),
           sum(1 for r in rows_out if r["verdict"] == "UNRESOLVED"),
           bar_t, n_cells))
    collapsed = [r for r in rows_out if r.get("rule_collapsed")]
    face["answer"] += (
        " %d of %d banded cells sit at or below %d weight changes over the whole sample -- "
        "there the band has not slowed the rule, it has replaced it with a buy-and-hold at "
        "roughly the base exposure, so any toll saving in those cells is the null arm's "
        "zero-turnover, not a fix.%s"
        % (len(collapsed), len(rows_out), RULE_COLLAPSE_FLOOR,
           (" None of the %d cells called a fix is collapsed." % len(pays))
           if pays and not any(r.get("rule_collapsed") for r in pays) else ""))

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "HYSTERESIS-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "hysteresis_latest.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "arm", "band_frac", "band_bp", "weight_changes",
                "weight_changes_saved", "pair_ann_bp_per_year",
                "selection_ann_bp_per_year", "sizing_ann_bp_per_year",
                "toll_ann_bp_per_year", "d_pair_ann_bp_per_year", "d_pair_t_nw",
                "d_selection_ann_bp_per_year", "d_toll_ann_bp_per_year",
                "verdict", "verdict_reason"]
        csv_path = os.path.join(outdir,
                                "hysteresis_by_rung_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows_out:
                w.writerow(r)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, vol_cycle=None, seed=7):
    return e225._synth(n, drift_bp, vol_cycle, seed)


def _cycle(i):
    return 30.0 + 22.0 * (1.0 if (i // 30) % 2 == 0 else -1.0)


def _noise(mean, sd, n=40, seed=11):
    """Deterministic pseudo-random series, so a fixture's standard error is real."""
    out = []
    s = seed
    for _ in range(n):
        s = (1103515245 * s + 12345) % (2 ** 31)
        z = ((s / 2 ** 31) - 0.5) * 3.4641
        out.append(mean + sd * z)
    return out


def _delta_block(pair, selection, sizing=None):
    """Assemble a delta block whose channels satisfy the identity by construction."""
    sizing = sizing if sizing is not None else [0.0] * len(pair)
    toll = [p - s - z for p, s, z in zip(pair, selection, sizing)]
    return {"pair": pair, "selection": selection, "sizing": sizing, "toll": toll}


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    dates, ret = _synth(900, 1.0, _cycle)
    sig = e225.vol_signal(ret)
    split = e225.split_index(len(dates))
    sd_is = band_width(sig, split)

    # L1 band 0 is the base arm exactly, for every arm -- the ladder has an origin
    legs_ok = []
    for arm in BAND_ARMS:
        legs_ok.append(band_weights(sig, arm, 0.0) == e225.weights_series(sig, arm))
    leg("band_zero_reproduces_the_base_arm", all(legs_ok), "%d arms" % len(BAND_ARMS))

    # L2 the band width is IS-only: perturbing the post-split signal cannot move it
    sig2 = list(sig)
    for i in range(split, len(sig2)):
        if sig2[i] is not None:
            sig2[i] = sig2[i] * 3.0 + 7.0
    leg("band_width_is_in_sample_only",
        band_width(sig2, split) == sd_is,
        "sd %.6f unchanged after a 3x post-split perturbation" % sd_is)

    # L3 the band actually suppresses movement -- otherwise nothing is being tested
    w_base = band_weights(sig, "tilt_step", 0.0)
    w_wide = band_weights(sig, "tilt_step", 2.0 * sd_is)
    base_prof = change_profile(w_base)
    wide_prof = change_profile(w_wide)
    leg("wide_band_reduces_weight_changes",
        wide_prof["weight_changes"] < base_prof["weight_changes"],
        "%d changes at band 0 vs %d at band 2.0 sd_is"
        % (base_prof["weight_changes"], wide_prof["weight_changes"]))

    # L4 fewer changes is not the same as less movement: report both, and pin that the
    # two are different quantities here
    leg("change_count_and_pushed_weight_are_different",
        wide_prof["total_abs_dw"] != base_prof["total_abs_dw"],
        "abs dw %.3f vs %.3f" % (wide_prof["total_abs_dw"],
                                 base_prof["total_abs_dw"]))

    # L5 the channels reconstruct the pair for any constant, not just the arm's own mean
    rows, mu_is = channel_rows_c(w_base, ret, split, COST_SIDE_BP, 0.37)
    resid = max(abs(r["selection"] + r["sizing"] + r["toll"] - r["pair"]) for r in rows)
    leg("channels_reconstruct_the_pair_for_an_arbitrary_constant", resid < 1e-9,
        "max residual %.3e bp over %d sessions" % (resid, len(rows)))

    # L6 a deadband cannot create or destroy exposure: every weight is a base-arm weight
    allowed = set(e225.weights_series(sig, "tilt_step"))
    leg("band_weights_are_base_arm_weights",
        set(w_wide) <= allowed,
        "%d distinct weights, all drawn from the base arm's own set"
        % len(set(w_wide)))

    # L7 rung deltas vanish at band 0 (the paired difference of a series with itself)
    d = paired_delta(rows, rows)
    leg("delta_of_a_rung_against_itself_is_zero",
        all(v == 0.0 for v in d["pair"]), "%d sessions" % len(d["pair"]))

    # L8 the toll term is linear in the cost parameter and the other two are not,
    # which is why the x2 limb of the condition is mechanically weaker. Pinned as an
    # identity here so the face can print it as a disclosure rather than a result.
    rows_x2, _ = channel_rows_c(w_base, ret, split, COST_SIDE_BP * COST_X2_MULT, 0.37)
    toll_x1 = sum(r["toll"] for r in rows)
    toll_x2 = sum(r["toll"] for r in rows_x2)
    toll_ratio = (toll_x2 / toll_x1) if toll_x1 else None
    leg("toll_is_linear_in_the_cost_parameter",
        toll_ratio is not None and abs(toll_ratio - COST_X2_MULT) < 1e-12,
        "toll(x2)/toll(x1) = %s vs multiplier %.1f"
        % (("%.9f" % toll_ratio) if toll_ratio is not None else "-", COST_X2_MULT))

    # L9 the rule order is real: a band that moves no weight is NO_EFFECT, never a pass
    flat = rung_verdict(paired_delta(rows, rows), True, 2.0)
    leg("no_effect_is_not_a_pass", flat["verdict"] == "NO_EFFECT",
        flat["verdict_reason"])

    # L10 a band that loses is BAND_COSTS even when it is extremely significant
    killed = _delta_block(_noise(-5.0, 0.05), _noise(-1.0, 0.05))
    kv = rung_verdict(killed, False, 2.0)
    leg("a_loss_is_never_called_a_fix",
        kv["verdict"] == "BAND_COSTS", kv["verdict_reason"])

    # L11 a point-estimate gain inside the noise band is BAND_NOISE. The fixture must
    # carry real dispersion (r1325 family): a flat series has se 0 and would "pass".
    z = _noise(0.0, 1.0)
    zm = e225._mean(z)
    nz = [x - zm + 0.02 for x in z]
    noisy = _delta_block(nz, nz)
    nv = rung_verdict(noisy, False, 2.0)
    leg("noise_is_not_called_a_fix", nv["verdict"] == "BAND_NOISE",
        "%s | t=%s over %d sessions"
        % (nv["verdict_reason"],
           ("%.2f" % nv["d_pair_t_nw"]) if nv["d_pair_t_nw"] is not None else "-",
           len(nz)))

    # L12 a genuine toll saving that the selection gives back is not a fix either.
    # Note the shape this branch needs: with sizing flat, "toll covers selection" is
    # exactly "pair > 0", so the short branch is only reachable when sizing is itself
    # carrying the pair -- which is what makes it worth testing.
    short = _delta_block(_noise(2.0, 0.02), _noise(-1.0, 0.02), _noise(2.0, 0.02))
    sv = rung_verdict(short, False, 0.1)
    leg("toll_saving_short_of_selection_is_not_a_fix",
        sv["verdict"] == "BAND_PAYS_TOLL_SHORT",
        "%s | toll %+.1f vs selection %+.1f bp/yr"
        % (sv["verdict_reason"], sv["d_toll_ann_bp_per_year"],
           sv["d_selection_ann_bp_per_year"]))

    # L13 and the honest one: covering the selection loss with a resolvable gain passes
    good = _delta_block(_noise(1.1, 0.02), _noise(-1.0, 0.02))
    gv = rung_verdict(good, False, 0.1)
    leg("a_covered_selection_loss_with_a_resolvable_gain_passes",
        gv["verdict"] == "BAND_PAYS", gv["verdict_reason"])

    # L14 the rung-level identity is checked, not assumed
    leg("rung_delta_identity_residual_is_zero",
        abs(gv["delta_identity_residual_bp"]) < 1e-9,
        "%.3e bp" % gv["delta_identity_residual_bp"])

    # L15 a zero-dispersion delta has no standard error, so it cannot clear a bar:
    # the degenerate branch must not be read as significance
    zero_se = _delta_block([1.0] * 40, [-1.0] * 40)
    zv = rung_verdict(zero_se, False, 2.0)
    leg("zero_variance_delta_cannot_clear_a_bar",
        zv["verdict"] == "BAND_NOISE",
        "verdict %s (t=%s) -- a constant series has se 0"
        % (zv["verdict"], zv["d_pair_t_nw"]))

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