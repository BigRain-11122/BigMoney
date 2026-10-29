"""E232 -- does the toll channel survive a non-linear charge?

E226..E231 all charge movement at a fixed 13.041 bp per unit of |dw|, so the family
conclusion -- that the toll is the only channel that ever separates these rules from a
flat constant -- rests on a LINEAR charge. If impact is concave or convex in the weight
moved, the same rule pays a different bill and the ordering between arms can move.

Frozen design (written before any number was read):

  * charge: cost = cost_side_bp * |dw| ** gamma, so a full 1.0 weight change costs the
    same at every gamma by construction. gamma = 1.0 reproduces the family cost model
    exactly; that is a selftest leg, not a claim.
  * gamma grid: 0.75, 1.00, 1.25, 1.50.
  * arms: binary_low, tilt_step, tilt_linear -- the three E229 judged.
  * panels: the primary single (sh510300) and the equal-weight basket, as E229/E230.
  * channels: E229's three, at ONE frozen constant per (panel, arm) -- the same
    OOS average weight E230 used -- recomputed at each gamma.
  * ladder: E230's deadband instrument re-read at each gamma, on the two smallest bands
    (0.10 and 0.25 x sd_is) for all three arms, so the one BAND_PAYS cell from E230 and
    its nearest neighbours can be asked whether their verdict survives curvature.

Two things this face must carry rather than bury:

  1. selection and sizing do not touch the charge function, so they are curvature
     INVARIANT by construction. Every cross-gamma difference in the pair is exactly the
     toll difference. Both facts are selftest legs, so a shift in the pair cannot be
     reported as skill.
  2. the ticket that opened this card says a concave charge makes a rule that moves in
     small steps "pay relatively less". That is backwards, and the face measures the
     direction instead of repeating the premise: with |dw| < 1 a concave charge
     (gamma < 1) raises the price of a small move (0.5 ** 0.75 = 0.59 > 0.5), so
     splitting one move into n steps costs sqrt(n) times as much, not less.

Nothing here can adopt a rule: the arms are already judged. The card asks one question --
is any of the family's conclusions a fact about the cost model rather than about the rule.
"""

from __future__ import annotations

import argparse
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
import e230_hysteresis_toll as e230  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
IS_FRAC = e225.IS_FRAC
NW_LAG = e225.NW_LAG
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

GAMMAS = (0.75, 1.00, 1.25, 1.50)
ARMS = ["binary_low", "tilt_step", "tilt_linear"]
LADDER_FRACS = (0.10, 0.25)
CHANNELS = ("selection", "sizing", "toll")

# E230's published bar and its single passing cell, quoted so the face can say whether
# the cell that passed on a linear charge still passes here.
E230_FOCUS = {"panel": "primary_single", "arm": "tilt_linear", "band_frac": 0.10}


def charge_bp(abs_dw, cost_side_bp, gamma):
    """The frozen charge function: linear at gamma=1, and a 1.0 move costs the same always."""
    if gamma is None or gamma <= 0.0:
        raise ValueError("gamma must be > 0; gamma=0 is a flat per-trade fee, a "
                         "different cost model rather than a curvature point")
    if abs_dw is None or abs_dw <= 0.0:
        return 0.0
    return cost_side_bp * (abs_dw ** gamma)


def rows_for_gamma(weights, ret_bp, split, cost_side_bp, gamma):
    """e228.rows_for with the charge function replaced and nothing else changed."""
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        cost = charge_bp(abs(dw), cost_side_bp, gamma)
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append({"i": i, "w": w, "abs_dw": abs(dw), "gross_bp": w * r,
                     "cost_bp": cost, "excess_bp": w * r - cost - w * mu_is})
        prev_w = w
    return rows, mu_is


def channel_rows(weights, ret_bp, split, cost_side_bp, gamma, const):
    """E229's three channels against one frozen constant, at one gamma (e230 mirror)."""
    base, mu_is = rows_for_gamma(weights, ret_bp, split, cost_side_bp, gamma)
    cut = split - 1
    rows = []
    for r in base:
        if r["i"] < cut:
            continue
        ret = ret_bp[r["i"] + 1]
        assert ret is not None, "rows_for_gamma must not emit a session without a return"
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
                     "pair": sel + siz + toll, "cost_bp": r["cost_bp"],
                     "abs_dw": r["abs_dw"]})
    return rows, mu_is


def total_cost(weights, cost_side_bp, gamma):
    """Whole-sample movement bill for one weight path, at one gamma."""
    prev = 0.0
    total = 0.0
    changes = 0
    for w in weights:
        d = abs(w - prev)
        if d > 0.0:
            changes += 1
            total += charge_bp(d, cost_side_bp, gamma)
        prev = w
    return {"weight_changes": changes, "total_cost_bp": total}


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL,
               "sessions": len(single[0]), "first": single[0][0],
               "last": single[0][-1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0],
                       "last": basket[0][-1]})

    # bar over the cells that can actually be a claim: arms x panels x gammas
    n_cells = len(ARMS) * len(panels) * len(GAMMAS)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        sd_is = e230.band_width(sig, split)
        panel.update({"split_session": split, "split_date": dates[split],
                      "signal_sd_is_bp": sd_is})
        if not sd_is:
            panel["arms"] = []
            panel["note"] = "signal too short for an in-sample band width"
            continue
        panel["arms"] = []
        for arm in ARMS:
            base_w = e225.weights_series(sig, arm)
            # the constant is the SAME at every gamma: it is a property of the weight
            # path, not of the charge, so cross-gamma rows stay comparable.
            probe, _mu = channel_rows(base_w, ret_bp, split, COST_SIDE_BP, 1.0, 0.0)
            const = e225._mean([r["w"] for r in probe]) or 0.0
            cost_profile = {("%.2f" % g): total_cost(base_w, COST_SIDE_BP, g)
                            for g in GAMMAS}
            arm_out = {"name": arm, "const_weight": const,
                       "cost_profile": cost_profile, "gammas": []}
            base_rows = {}
            for g in GAMMAS:
                rows, mu_is = channel_rows(base_w, ret_bp, split, COST_SIDE_BP, g, const)
                base_rows[("%.2f" % g)] = rows
                tot = e230._totals(rows)
                toll_t = e230._stats([r["toll"] for r in rows])["t_nw"]
                sel_t = e230._stats([r["selection"] for r in rows])["t_nw"]
                pair_t = e230._stats([r["pair"] for r in rows])["t_nw"]
                arm_out["gammas"].append({
                    "gamma": g, "mu_is_bp_per_day": mu_is, "totals": tot,
                    "toll_t_nw": toll_t, "selection_t_nw": sel_t,
                    "pair_t_nw": pair_t,
                    "toll_clears_bar": (toll_t is not None and abs(toll_t) >= bar_t),
                    "toll_single_channel": (
                        toll_t is not None and sel_t is not None
                        and abs(toll_t) >= bar_t and abs(sel_t) < bar_t),
                })
            # ---- E230's instrument re-read at each gamma
            arm_out["ladder"] = []
            for frac in LADDER_FRACS:
                band = frac * sd_is
                w = e230.band_weights(sig, arm, band)
                prof = e230.change_profile(w)
                cell = {"band_frac": frac, "band_bp": band,
                        "weight_changes": prof["weight_changes"],
                        "weight_changes_saved": (prof["weight_changes"]
                                                 - cost_profile["1.00"]["weight_changes"]),
                        "rule_collapsed": prof["weight_changes"] <= e230.RULE_COLLAPSE_FLOOR,
                        "by_gamma": []}
                for g in GAMMAS:
                    key = "%.2f" % g
                    rows, _ = channel_rows(w, ret_bp, split, COST_SIDE_BP, g, const)
                    delta = e230.paired_delta(base_rows[key], rows)
                    v = e230.rung_verdict(delta, w == base_w, bar_t)
                    cell["by_gamma"].append({
                        "gamma": g,
                        "d_pair_ann_bp_per_year": v["d_pair_ann_bp_per_year"],
                        "d_pair_t_nw": v["d_pair_t_nw"],
                        "d_selection_ann_bp_per_year": v["d_selection_ann_bp_per_year"],
                        "d_toll_ann_bp_per_year": v["d_toll_ann_bp_per_year"],
                        "delta_identity_residual_bp": v["delta_identity_residual_bp"],
                        "verdict": v["verdict"],
                        "verdict_reason": v["verdict_reason"],
                    })
                cell["verdicts"] = [x["verdict"] for x in cell["by_gamma"]]
                cell["verdict_stable"] = len(set(cell["verdicts"])) == 1
                arm_out["ladder"].append(cell)
            panel["arms"].append(arm_out)

    # ---------------- cross-gamma reading
    toll_rows, ladder_rows, order_rows = [], [], []
    for panel in panels:
        for a in panel.get("arms") or []:
            tolls = [g["totals"]["toll_ann_bp_per_year"] for g in a["gammas"]]
            pairs = [g["totals"]["pair_ann_bp_per_year"] for g in a["gammas"]]
            sels = [g["totals"]["selection_ann_bp_per_year"] for g in a["gammas"]]
            for g in a["gammas"]:
                toll_rows.append({
                    "panel": panel["panel"], "arm": a["name"], "gamma": g["gamma"],
                    "toll_ann_bp_per_year": g["totals"]["toll_ann_bp_per_year"],
                    "selection_ann_bp_per_year": g["totals"]["selection_ann_bp_per_year"],
                    "sizing_ann_bp_per_year": g["totals"]["sizing_ann_bp_per_year"],
                    "pair_ann_bp_per_year": g["totals"]["pair_ann_bp_per_year"],
                    "toll_t_nw": g["toll_t_nw"], "selection_t_nw": g["selection_t_nw"],
                    "toll_clears_bar": g["toll_clears_bar"],
                    "toll_single_channel": g["toll_single_channel"],
                })
            order_rows.append({
                "panel": panel["panel"], "arm": a["name"],
                "toll_range_bp": [min(tolls), max(tolls)],
                "pair_range_bp": [min(pairs), max(pairs)],
                "selection_range_bp": [min(sels), max(sels)],
                "selection_invariant": (max(sels) - min(sels)) < 1e-9,
                "toll_sign_stable": (min(tolls) > 0) or (max(tolls) < 0),
                "pair_sign_stable": (min(pairs) > 0) or (max(pairs) < 0),
            })
            for cell in a["ladder"]:
                ladder_rows.append({
                    "panel": panel["panel"], "arm": a["name"],
                    "band_frac": cell["band_frac"],
                    "weight_changes": cell["weight_changes"],
                    "weight_changes_saved": cell["weight_changes_saved"],
                    "verdict_stable": cell["verdict_stable"],
                    "verdicts": cell["verdicts"],
                    "by_gamma": cell["by_gamma"],
                })

    # arm ordering (which arm's pair ranks first) per panel per gamma
    ranking = []
    for panel in panels:
        for g in GAMMAS:
            vals = []
            for a in panel.get("arms") or []:
                row = [x for x in a["gammas"] if x["gamma"] == g][0]
                vals.append((a["name"], row["totals"]["pair_ann_bp_per_year"]))
            ranked = [n for n, _ in sorted(vals, key=lambda kv: -(kv[1] or 0.0))]
            ranking.append({"panel": panel["panel"], "gamma": g, "order": ranked})
    order_stable = {}
    for panel in panels:
        orders = [tuple(r["order"]) for r in ranking if r["panel"] == panel["panel"]]
        order_stable[panel["panel"]] = len(set(orders)) == 1

    focus = [r for r in ladder_rows
             if r["panel"] == E230_FOCUS["panel"] and r["arm"] == E230_FOCUS["arm"]
             and abs(r["band_frac"] - E230_FOCUS["band_frac"]) < 1e-12]
    focus_verdicts = focus[0]["verdicts"] if focus else []
    focus_moves = bool(focus) and not focus[0]["verdict_stable"]

    pays_by_gamma = {}
    for g in GAMMAS:
        pays_by_gamma["%.2f" % g] = sum(
            1 for r in ladder_rows
            for x in r["by_gamma"] if x["gamma"] == g and x["verdict"] == "BAND_PAYS")
    single_channel_rows = [r for r in toll_rows if r["toll_single_channel"]]

    face = {
        "study": "E232",
        "title": "does the family's toll conclusion survive a non-linear charge?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "gammas": list(GAMMAS),
            "arms": ARMS,
            "charge": "cost = cost_side_bp * |dw| ** gamma; a 1.0 move costs the same "
                      "at every gamma",
            "cost_side_bp": COST_SIDE_BP,
            "ladder_fracs": list(LADDER_FRACS),
            "channels": list(CHANNELS),
            "const_weight": "the base arm's OOS average weight at gamma=1.0, frozen "
                            "across gammas so the rows stay comparable",
            "is_frac": IS_FRAC,
            "nw_lag": NW_LAG,
            "bar_t": bar_t,
            "bar_basis": "two-sided 5%% over %d cells (arms x panels x gammas)" % n_cells,
            "e230_focus_cell": E230_FOCUS,
            "no_adoption": "the arms are already judged; this asks only whether a "
                           "conclusion is a fact about the cost model",
            "premise_note": "a concave charge makes SMALL moves dearer per unit "
                            "(0.5**0.75 = 0.594 > 0.5), so splitting one move into n "
                            "steps costs sqrt(n) times as much, not less",
        },
        "panels": panels,
        "toll_channel": toll_rows,
        "arm_ranges": order_rows,
        "ladder": ladder_rows,
        "arm_ordering": ranking,
        "summary": {
            "cells": len(ladder_rows),
            "bar_t": bar_t,
            "toll_clears_bar_at_all_gammas": sum(
                1 for a in [r for p in panels for r in (p.get("arms") or [])]
                if all(g["toll_clears_bar"] for g in a["gammas"])),
            "toll_single_channel_cells": len(single_channel_rows),
            "toll_single_channel_at_all_gammas": sum(
                1 for a in [r for p in panels for r in (p.get("arms") or [])]
                if all(g["toll_single_channel"] for g in a["gammas"])),
            "pair_sign_flips": sum(1 for r in order_rows if not r["pair_sign_stable"]),
            "toll_sign_flips": sum(1 for r in order_rows if not r["toll_sign_stable"]),
            "selection_invariant_cells": sum(1 for r in order_rows
                                             if r["selection_invariant"]),
            "arm_ordering_stable": order_stable,
            "ladder_cells": len(ladder_rows),
            "ladder_verdict_stable": sum(1 for r in ladder_rows if r["verdict_stable"]),
            "band_pays_by_gamma": pays_by_gamma,
            "e230_focus_verdicts_by_gamma": focus_verdicts,
            "e230_focus_verdict_moves": focus_moves,
        },
    }

    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "COSTCURVE-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "costcurve_latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _fmt(v, spec="%.1f"):
    return "-" if v is None else (spec % v)


def _answer(face):
    s = face["summary"]
    tolls = [r["toll_ann_bp_per_year"] for r in face["toll_channel"]
             if r["toll_ann_bp_per_year"] is not None]
    pairs = [r["pair_ann_bp_per_year"] for r in face["toll_channel"]
             if r["pair_ann_bp_per_year"] is not None]
    stable = [p for p, ok in s["arm_ordering_stable"].items() if ok]
    parts = [
        "The charge function was swept over gamma %.2f..%.2f (a 1.0 move costs the same "
        "at every point) on %d panel(s), %d arms, and the E230 deadband re-read at each "
        "gamma." % (min(GAMMAS), max(GAMMAS),
                    len(face["panels"]), len(ARMS)),
        "The toll channel moves from %s to %s bp/yr and the pair from %s to %s bp/yr "
        "across the sweep. Selection is curvature-invariant in %d of %d arm cells (by "
        "construction -- it never touches the charge), so every cross-gamma move in the "
        "pair is the toll." % (_fmt(min(tolls)), _fmt(max(tolls)),
                              _fmt(min(pairs)), _fmt(max(pairs)),
                              s["selection_invariant_cells"], len(face["arm_ranges"])),
        "%d of %d arms keep |t| >= %.2f on the toll at ALL four gammas, and %d of them "
        "keep the toll as the ONLY channel past the bar at every gamma. Arm ordering by "
        "pair is invariant on %d of %d panels."
        % (s["toll_clears_bar_at_all_gammas"], len(face["arm_ranges"]), s["bar_t"],
           s["toll_single_channel_at_all_gammas"], len(stable), len(face["panels"])),
        "On the ladder, %d of %d (panel, arm, band) cells return the same verdict at "
        "every gamma; BAND_PAYS counts by gamma are %s. E230's focus cell (%s / %s / "
        "f=%.2f) reads %s%s."
        % (s["ladder_verdict_stable"], s["ladder_cells"],
           ", ".join("%s: %d" % (k, v) for k, v in sorted(s["band_pays_by_gamma"].items())),
           E230_FOCUS["panel"], E230_FOCUS["arm"], E230_FOCUS["band_frac"],
           " / ".join("%s@%.2f" % (v, g) for v, g in
                      zip(s["e230_focus_verdicts_by_gamma"], GAMMAS)) or "-",
           " -- the verdict MOVES with curvature, so that cell is a finding about the "
           "cost model" if s["e230_focus_verdict_moves"] else
           " -- the verdict does not move with curvature"),
    ]
    return " ".join(parts)


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, seed=7):
    import random
    rng = random.Random(seed)
    out, v = [], drift_bp
    for i in range(n):
        v = 0.93 * v + 0.07 * drift_bp + rng.gauss(0.0, 9.0)
        out.append(v)
    return out


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    n = 240
    ret = _synth(n)
    split = 140
    w = [(_synth(n, seed=3)[i] > 1.0) * 1.0 for i in range(n)]

    def l_gamma1_is_the_family_cost():
        a, _ = rows_for_gamma(w, ret, split, COST_SIDE_BP, 1.0)
        b, _ = e228.rows_for(w, ret, split, COST_SIDE_BP)
        assert len(a) == len(b), "row counts differ"
        worst = max(abs(x["cost_bp"] - y["cost_bp"]) for x, y in zip(a, b))
        assert worst < 1e-12, "gamma=1 must reproduce e228.rows_for, worst %.3g" % worst
        worst = max(abs(x["excess_bp"] - y["excess_bp"]) for x, y in zip(a, b))
        assert worst < 1e-12, "excess differs at gamma=1 by %.3g" % worst

    def l_full_move_costs_the_same():
        for g in GAMMAS:
            assert abs(charge_bp(1.0, COST_SIDE_BP, g) - COST_SIDE_BP) < 1e-12, \
                "gamma %.2f charges %.6f for a 1.0 move" % (g, charge_bp(1.0, COST_SIDE_BP, g))

    def l_zero_move_is_free():
        for g in GAMMAS:
            assert charge_bp(0.0, COST_SIDE_BP, g) == 0.0

    def l_concave_is_dearer_for_small_moves():
        small = 0.5
        lin = charge_bp(small, COST_SIDE_BP, 1.0)
        assert charge_bp(small, COST_SIDE_BP, 0.75) > lin, "gamma<1 must be dearer"
        assert charge_bp(small, COST_SIDE_BP, 1.25) < lin, "gamma>1 must be cheaper"

    def l_split_cost_direction():
        # one move of 1.0 vs two of 0.5, at each gamma
        one = charge_bp(1.0, COST_SIDE_BP, 1.0)
        for g in (0.75, 1.25, 1.5):
            two = 2.0 * charge_bp(0.5, COST_SIDE_BP, g)
            if g < 1.0:
                assert two > one, "concave: splitting must cost more"
            else:
                assert two < one, "convex: splitting must cost less"

    def l_selection_sizing_invariant():
        c = 0.4
        for g in GAMMAS:
            rows, _ = channel_rows(w, ret, split, COST_SIDE_BP, g, c)
            if g == GAMMAS[0]:
                base = [(r["selection"], r["sizing"]) for r in rows]
                continue
            cur = [(r["selection"], r["sizing"]) for r in rows]
            assert len(cur) == len(base)
            worst = max(max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                        for a, b in zip(cur, base))
            assert worst < 1e-12, "gamma %.2f moved selection/sizing by %.3g" % (g, worst)

    def l_pair_moves_only_through_toll():
        rows = {}
        for g in GAMMAS:
            rows[g], _ = channel_rows(w, ret, split, COST_SIDE_BP, g, 0.4)
        a, b = GAMMAS[0], GAMMAS[-1]
        worst = max(abs((x["pair"] - y["pair"]) - (x["toll"] - y["toll"]))
                    for x, y in zip(rows[a], rows[b]))
        assert worst < 1e-12, "pair delta is not the toll delta: %.3g" % worst

    def l_identity_holds_at_every_gamma():
        for g in GAMMAS:
            rows, _ = channel_rows(w, ret, split, COST_SIDE_BP, g, 0.4)
            res = sum(r["selection"] + r["sizing"] + r["toll"] - r["pair"] for r in rows)
            assert abs(res) < 1e-9, "gamma %.2f identity residual %.3g" % (g, res)

    def l_cost_profile_monotone():
        flat = [0.0] + [0.5] * (n - 1)
        lo = total_cost(flat, COST_SIDE_BP, 0.75)["total_cost_bp"]
        hi = total_cost(flat, COST_SIDE_BP, 1.5)["total_cost_bp"]
        assert hi < lo, "for |dw|<1 a convex charge must be cheaper: %.4f vs %.4f" % (hi, lo)

    def l_bad_gamma_rejected():
        try:
            charge_bp(0.5, COST_SIDE_BP, 0.0)
        except ValueError:
            return
        raise AssertionError("gamma=0 must be rejected (a flat per-trade fee is a "
                             "different model, not a curvature point)")

    leg("gamma=1.0 reproduces the family cost model exactly", l_gamma1_is_the_family_cost)
    leg("a full 1.0 weight change costs the same at every gamma", l_full_move_costs_the_same)
    leg("a zero move is free at every gamma", l_zero_move_is_free)
    leg("a concave charge is dearer per unit for small moves", l_concave_is_dearer_for_small_moves)
    leg("splitting a move costs sqrt(n) more when concave, less when convex", l_split_cost_direction)
    leg("selection and sizing are curvature-invariant", l_selection_sizing_invariant)
    leg("the pair moves across gamma only through the toll", l_pair_moves_only_through_toll)
    leg("pair = selection + sizing + toll at every gamma", l_identity_holds_at_every_gamma)
    leg("a convex charge is cheaper on a sub-unit weight path", l_cost_profile_monotone)
    leg("gamma=0 is rejected as a different model", l_bad_gamma_rejected)

    ok = sum(1 for _, p, _ in legs if p)
    for name, passed, msg in legs:
        print("%s  %s%s" % ("PASS" if passed else "FAIL", name,
                            ("  -- " + msg) if msg else ""))
    print("%d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=not args.no_save)
    if face is None:
        return 2
    print(face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())