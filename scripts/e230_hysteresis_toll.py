"""E230 -- can the toll channel be bought back with a hysteresis deadband?

This module was written by bm-b in r1256 and never committed: six scripts import it
(`e231`..`e237`) and no clean checkout could start a single one of them. The face it
produced, however, WAS committed (`results/state_tilt/HYSTERESIS-2026-10-29.json`,
`hysteresis_latest.json`, `hysteresis_by_rung_2026-10-29.csv`), so the reconstruction is
not free-form: the published face is the acceptance test, and `selftest` leg L14 plus
`reproduce` compare the numbers below against it.

The question the card asked
---------------------------
E229 split each gated arm's paired series into selection / sizing / toll and found the toll
was the only channel clearing its bar. The toll is charged on |dw|, one side per unit of
weight movement, so the one instrument that can buy it back is making the rule move less
often. Does a hysteresis deadband on the volatility state cut the toll faster than it costs
in selection?

The rule
--------
Hold the committed weight until the signal has travelled `band` away from the value it sat
at when that weight was committed:

    if |v_i - v_at_last_commit| >= band:  commit weight_at(sig, i, arm); last_commit = v_i
    else:                                 hold

`band = 0` commits every session and *is* the base arm exactly (L1). The band grid is
`0, 0.10, 0.25, 0.50, 1.00, 2.00` times the **in-sample** standard deviation of the signal,
so the band cannot see the future (L2). Three arms, two panels, x1 and x2 costs.

One design point that is not cosmetic: the three channels are computed against ONE frozen
constant per (panel, arm) -- the base arm's own OOS average weight -- so rungs are
comparable. Re-deriving the constant at every rung would give every rung a different
benchmark (L8).

Nothing here can adopt a band: the base arms are already judged (E228/E229), and this study
only asks whether one of their channels is purchasable.
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
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

BAND_ARMS = ("binary_low", "tilt_step", "tilt_linear")
BAND_FRACS = (0.0, 0.10, 0.25, 0.50, 1.00, 2.00)
# a rung at or below this many weight changes has not slowed the rule, it has replaced it
RULE_COLLAPSE_FLOOR = 5

CHANNELS = ("selection", "sizing", "toll")
RULE = "hold the committed weight until |v_i - v_at_last_commit| >= band"
BAR_BASIS = "two-sided 5% over 60 cells x 2 cost levels"
VOCABULARY = ("BAND_COSTS", "BAND_NOISE", "BAND_PAYS", "BAND_PAYS_TOLL_SHORT",
              "BASELINE", "NO_EFFECT", "UNRESOLVED")


# ---------------------------------------------------------------- the rule
def band_width(sig, split):
    """In-sample standard deviation of the signal, in bp.

    Only sessions strictly before `split` participate: the band scale is a property of the
    past, exactly like the arm's own threshold terciles.
    """
    past = [sig[i] for i in range(1, split) if sig[i] is not None]
    return e225._sd(past)


def band_weights(sig, arm, band):
    """The banded weight series, one weight per decision session.

    `band = 0` reproduces `e225.weights_series(sig, arm)` exactly (L1). A `None` signal
    commits the arm's own answer for that session, so a band can never manufacture a
    position the base rule would not hold.
    """
    out = []
    committed_w = None
    committed_v = None
    for i in range(len(sig)):
        v = sig[i]
        want = e225.weight_at(sig, i, arm)
        if committed_w is None or v is None or committed_v is None:
            committed_w, committed_v = want, v
        elif abs(v - committed_v) >= band:
            committed_w, committed_v = want, v
        out.append(committed_w)
    return out


def change_profile(weights):
    """How much a weight path moves: transitions and total absolute movement."""
    changes = 0
    total = 0.0
    prev = 0.0
    for w in weights:
        d = abs(w - prev)
        total += d
        if d > 0.0:
            changes += 1
        prev = w
    return {"weight_changes": changes, "total_abs_dw": total, "sessions": len(weights)}


# ---------------------------------------------------------------- accounting
def _ann(sum_bp, n):
    if not n:
        return None
    return sum_bp / float(n) * SESSIONS_PER_YEAR


def _stats(vals):
    if not vals:
        return {"n": 0, "ann_bp_per_year": None, "t_nw": None}
    n = len(vals)
    se = e225._hac_se(vals, NW_LAG) if n >= 3 else None
    m = e225._mean(vals)
    return {"n": n,
            "mean_bp_per_session": m,
            "ann_bp_per_year": _ann(sum(vals), n),
            "se_nw": se,
            "t_nw": (m / se) if (se and m is not None) else None,
            "n_eff": e225._n_eff(vals) if n >= 3 else None}


def _totals(rows):
    n = len(rows)
    out = {"oos_sessions": n}
    sums = {ch: sum(r[ch] for r in rows) for ch in CHANNELS}
    for ch in CHANNELS:
        out["%s_ann_bp_per_year" % ch] = _ann(sums[ch], n)
    out["pair_ann_bp_per_year"] = _ann(sum(r["pair"] for r in rows), n)
    out["identity_residual_bp"] = (sums["selection"] + sums["sizing"] + sums["toll"]
                                   - sum(r["pair"] for r in rows))
    return out


def rows_for(weights, ret_bp, split, cost_side_bp, const):
    """E229's per-session decomposition on top of `e228.rows_for`.

    One accounting, not two: the panel comes from E228 (which is where the excess is
    defined and where the charge is levied), and this function only assigns the three
    channels. `const` is required on purpose -- the comparability of the ladder rests on
    every rung being measured against the base arm's own constant.
    """
    base, mu_is = e228.rows_for(weights, ret_bp, split, cost_side_bp)
    cut = split - 1
    out = []
    for r in base:
        if r["i"] < cut:
            continue
        ret = ret_bp[r["i"] + 1]
        dev = ret - mu_is
        if r["w"] == 0.0:
            sel, siz = (-const) * dev, 0.0
        else:
            sel, siz = 0.0, (r["w"] - const) * dev
        out.append({"i": r["i"], "w": r["w"], "selection": sel, "sizing": siz,
                    "toll": -r["cost_bp"], "pair": sel + siz - r["cost_bp"]})
    if not out:
        return None, mu_is
    return out, mu_is


def channel_rows_c(weights, ret_bp, split, cost_side_bp, const):
    """`rows_for` under the name the rest of the family calls it."""
    return rows_for(weights, ret_bp, split, cost_side_bp, float(const))


def paired_delta(base_rows, cur_rows):
    """Session-paired difference of two decompositions, channel by channel."""
    if base_rows is None or cur_rows is None or len(base_rows) != len(cur_rows):
        raise ValueError("paired_delta needs two identical-length decompositions")
    out = {}
    for ch in CHANNELS + ("pair",):
        out[ch] = [c[ch] - b[ch] for b, c in zip(base_rows, cur_rows)]
    out["delta_identity_residual_bp"] = sum(
        out["selection"][i] + out["sizing"][i] + out["toll"][i] - out["pair"][i]
        for i in range(len(out["pair"])))
    return out


def rung_verdict(delta, same_path, bar_t):
    """The frozen vocabulary, applied to one rung's paired x2 delta."""
    d_pair = _stats(delta["pair"])
    d_toll = _stats(delta["toll"])
    d_sel = _stats(delta["selection"])
    out = {"bar_t": bar_t,
           "d_pair_ann_bp_per_year": d_pair["ann_bp_per_year"],
           "d_pair_t_nw": d_pair["t_nw"],
           "d_selection_ann_bp_per_year": d_sel["ann_bp_per_year"],
           "d_sizing_ann_bp_per_year": _stats(delta["sizing"])["ann_bp_per_year"],
           "d_toll_ann_bp_per_year": d_toll["ann_bp_per_year"],
           "delta_identity_residual_bp": delta["delta_identity_residual_bp"]}
    pair = d_pair["ann_bp_per_year"]
    t = d_pair["t_nw"]
    toll = d_toll["ann_bp_per_year"]
    toll_t = d_toll["t_nw"]
    if same_path:
        out["verdict"] = "NO_EFFECT"
        out["verdict_reason"] = "the band never moves a weight: this rung is the base arm"
        return out
    if pair is not None and t is not None and abs(t) >= bar_t and pair > 0.0:
        # a rung only earns BAND_PAYS if the TOLL is what carried it: a pair that clears
        # the bar while its toll channel does not is a fix for some other reason
        if toll_t is not None and abs(toll_t) >= bar_t:
            out["verdict"] = "BAND_PAYS"
            out["verdict_reason"] = ("t=%.2f, toll +%.1f vs selection %.1f bp/yr at x2 costs"
                                     % (t, toll or 0.0, d_sel["ann_bp_per_year"] or 0.0))
            # the claim only means something if the toll bought back more than the
            # selection given up to buy it
            out["toll_saving_exceeds_selection_loss"] = bool(
                toll is not None and d_sel["ann_bp_per_year"] is not None
                and toll > abs(d_sel["ann_bp_per_year"]))
        else:
            out["verdict"] = "BAND_PAYS_TOLL_SHORT"
            out["verdict_reason"] = (
                "t=%.2f clears the bar but the toll channel (t=%.2f) does not"
                % (t, toll_t if toll_t is not None else float("nan")))
        return out
    if pair is not None and pair > 0.0:
        out["verdict"] = "BAND_NOISE"
        out["verdict_reason"] = ("t=%.2f < bar %.2f" % (t if t is not None else float("nan"),
                                                       bar_t))
        return out
    if pair is not None and pair < 0.0:
        out["verdict"] = "BAND_COSTS"
        out["verdict_reason"] = ("pair %.1f bp/yr not better than the base arm"
                                 % abs(pair))
        return out
    out["verdict"] = "UNRESOLVED"
    out["verdict_reason"] = "no pair delta could be measured"
    return out


# ---------------------------------------------------------------- the study
def _z_two_sided(p):
    return e222._z_two_sided(p)


def _truncate(data, upto):
    """Cut a panel back to a published session count (reproduction only)."""
    if not data or not upto:
        return data
    n, last = upto
    dates, ret_bp = data
    if n is None or n > len(dates):
        return data
    if last is not None and dates[n - 1] != last:
        raise ValueError("panel at session %d is %s, not %s"
                         % (n, dates[n - 1], last))
    return dates[:n], ret_bp[:n]


def run(save=True, panel_dir=None, outdir=None, upto=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    upto = upto or {}
    single = _truncate(e225.single_panel(PRIMARY_SYMBOL, panel_dir),
                       upto.get("primary_single"))
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = _truncate(e225.basket_panel(panel_dir), upto.get("basket_equal_weight"))

    n_cells = len(BAND_ARMS) * (2 if basket else 1) * (len(BAND_FRACS) - 1) * 2
    bar_t = max(2.0, _z_two_sided(0.05 / n_cells))

    panels = []
    for name, data in (("primary_single", single), ("basket_equal_weight", basket)):
        if not data:
            continue
        dates, ret_bp = data
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        if len(dates) - split < MIN_OOS_SESSIONS:
            continue
        sd_is = band_width(sig, split)
        panel = {"panel": name,
                 "symbol": PRIMARY_SYMBOL if name == "primary_single"
                 else "+".join(sorted(BASKET)),
                 "sessions": len(dates), "first": dates[0], "last": dates[-1],
                 "is_frac": IS_FRAC, "split_session": split, "split_date": dates[split],
                 "band_grid_fracs": list(BAND_FRACS), "signal_sd_is_bp": sd_is, "arms": []}
        if not sd_is:
            panel["note"] = "signal too short for an in-sample band width"
            panels.append(panel)
            continue
        for arm in BAND_ARMS:
            base_w = e225.weights_series(sig, arm)
            probe, _mu = channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, 0.0)
            const = e225._mean([r["w"] for r in probe]) or 0.0
            base_rows, mu_is = channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, const)
            base_rows_x2, _ = channel_rows_c(base_w, ret_bp, split,
                                             COST_SIDE_BP * COST_X2_MULT, const)
            base_prof = change_profile(base_w)
            arm_out = {"name": arm, "const_weight": const, "mu_is_bp_per_day": mu_is,
                       "base": _totals(base_rows), "base_x2": _totals(base_rows_x2),
                       "rungs": []}
            for frac in BAND_FRACS:
                band = frac * sd_is
                w = base_w if frac == 0.0 else band_weights(sig, arm, band)
                rows, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, const)
                rows_x2, _ = channel_rows_c(w, ret_bp, split,
                                            COST_SIDE_BP * COST_X2_MULT, const)
                prof = change_profile(w)
                rung = {"band_frac": frac, "band_bp": band, "band_width_is_bp": sd_is,
                        "weight_changes": prof["weight_changes"],
                        "total_abs_dw": prof["total_abs_dw"],
                        "rule_collapsed": prof["weight_changes"] <= RULE_COLLAPSE_FLOOR,
                        "totals": _totals(rows), "totals_x2": _totals(rows_x2)}
                if frac == 0.0:
                    rung["verdict"] = "BASELINE"
                    rung["verdict_reason"] = "the base arm itself"
                else:
                    delta = paired_delta(base_rows_x2, rows_x2)
                    v = rung_verdict(delta, w == base_w, bar_t)
                    rung["delta_x1_pair_ann_bp_per_year"] = (
                        rung["totals"]["pair_ann_bp_per_year"]
                        - arm_out["base"]["pair_ann_bp_per_year"])
                    rung["delta_x2"] = v
                    d_toll_x1 = (rung["totals"]["toll_ann_bp_per_year"]
                                 - arm_out["base"]["toll_ann_bp_per_year"])
                    rung["toll_x2_linearity_residual_bp"] = (
                        v["d_toll_ann_bp_per_year"] - COST_X2_MULT * d_toll_x1)
                    rung["weight_changes_saved"] = prof["weight_changes"] - base_prof["weight_changes"]
                arm_out["rungs"].append(rung)
            panel["arms"].append(arm_out)
        panels.append(panel)

    rows = []
    for panel in panels:
        for arm in panel["arms"]:
            for rung in arm["rungs"]:
                if rung["band_frac"] == 0.0:
                    continue
                rows.append({"panel": panel["panel"], "arm": arm["name"],
                             "band_frac": rung["band_frac"], "band_bp": rung["band_bp"],
                             "verdict": rung["delta_x2"]["verdict"],
                             "verdict_reason": rung["delta_x2"]["verdict_reason"],
                             "rule_collapsed": rung["rule_collapsed"],
                             "weight_changes": rung["weight_changes"],
                             "weight_changes_saved": rung["weight_changes_saved"],
                             # levels are the x1 world; only the deltas carry the x2 charge
                             "pair_ann_bp_per_year": rung["totals"]["pair_ann_bp_per_year"],
                             "selection_ann_bp_per_year": rung["totals"]["selection_ann_bp_per_year"],
                             "sizing_ann_bp_per_year": rung["totals"]["sizing_ann_bp_per_year"],
                             "toll_ann_bp_per_year": rung["totals"]["toll_ann_bp_per_year"],
                             "d_pair_ann_bp_per_year": rung["delta_x2"]["d_pair_ann_bp_per_year"],
                             "d_pair_t_nw": rung["delta_x2"]["d_pair_t_nw"],
                             "d_selection_ann_bp_per_year": rung["delta_x2"]["d_selection_ann_bp_per_year"],
                             "d_toll_ann_bp_per_year": rung["delta_x2"]["d_toll_ann_bp_per_year"]})

    counts = {k: sum(1 for r in rows if r["verdict"] == k)
              for k in ("BAND_PAYS", "BAND_COSTS", "BAND_NOISE", "BAND_PAYS_TOLL_SHORT",
                        "NO_EFFECT", "UNRESOLVED")}
    saved = [r["weight_changes_saved"] for r in rows]
    tolls = [r["d_toll_ann_bp_per_year"] for r in rows
             if r["d_toll_ann_bp_per_year"] is not None]
    sels = [r["d_selection_ann_bp_per_year"] for r in rows
            if r["d_selection_ann_bp_per_year"] is not None]
    collapsed = [r for r in rows if r["rule_collapsed"]]
    paying = [r for r in rows if r["verdict"] == "BAND_PAYS"]
    summary = {"cells": len(rows), "band_pays": counts["BAND_PAYS"],
               "band_costs": counts["BAND_COSTS"], "band_noise": counts["BAND_NOISE"],
               "band_pays_toll_short": counts["BAND_PAYS_TOLL_SHORT"],
               "no_effect": counts["NO_EFFECT"], "unresolved": counts["UNRESOLVED"],
               "rule_collapse_floor": RULE_COLLAPSE_FLOOR,
               "rule_collapsed": len(collapsed),
               "ladder_vacuous": bool(rows) and all(r["rule_collapsed"] for r in rows),
               "reading": ("one row per (panel, arm, rung>0); deltas are the banded arm's "
                           "pair minus the base arm's pair at x2 costs, so a positive "
                           "d_toll_ann_bp_per_year is a toll saving"),
               "rows": rows}
    answer = None
    if rows:
        answer = (
            "the ladder moved the rule as intended -- across %d cells the band changed the "
            "number of weight changes by %d..%d (total %d), and the toll channel moved with "
            "it (%.1f..%.1f bp/yr at x2 costs). The selection channel moved %.1f..%.1f "
            "bp/yr against it. %d of %d banded cells are called a fix (BAND_PAYS), %d lose "
            "to the base arm (BAND_COSTS), %d are point-estimate-only (BAND_NOISE), %d save "
            "toll but not enough to cover the selection given up, %d never move a weight, "
            "%d unresolved. Bar: |t| >= %.2f over %d cells. %d of %d banded cells sit at or "
            "below %d weight changes over the whole sample -- there the band has not slowed "
            "the rule, it has replaced it with a buy-and-hold at roughly the base exposure, "
            "so any toll saving in those cells is the null arm's zero-turnover, not a fix. "
            "%s"
            % (len(rows), min(saved), max(saved), sum(saved),
               min(tolls), max(tolls), min(sels), max(sels),
               counts["BAND_PAYS"], len(rows), counts["BAND_COSTS"], counts["BAND_NOISE"],
               counts["BAND_PAYS_TOLL_SHORT"], counts["NO_EFFECT"], counts["UNRESOLVED"],
               bar_t, n_cells,
               len(collapsed), len(rows), RULE_COLLAPSE_FLOOR,
               ("None of the %d cells called a fix is collapsed." % len(paying))
               if paying and not any(r["rule_collapsed"] for r in paying)
               else ("%d of the %d cells called a fix are collapsed."
                     % (sum(1 for r in paying if r["rule_collapsed"]), len(paying))))
            )

    face = {
        "study": "E230",
        "title": ("does a hysteresis deadband on the volatility state buy back the toll "
                  "channel faster than it loses selection?"),
        "evidence_cutoff": (single[0][-1] if single else None),
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": {
            "rule": RULE,
            "band_arms": list(BAND_ARMS),
            "band_grid_fracs": list(BAND_FRACS),
            "band_scale": "in-sample standard deviation of the volatility signal",
            "channels": list(CHANNELS),
            "identity": "pair = selection + sizing + toll, per session and per rung",
            "const_weight": "the base arm's own OOS average weight, frozen across rungs",
            "cost_side_bp": COST_SIDE_BP, "cost_x2_mult": COST_X2_MULT,
            "is_frac": IS_FRAC, "nw_lag": NW_LAG,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "bar_basis": BAR_BASIS, "bar_t": bar_t,
            "rule_collapse_floor": RULE_COLLAPSE_FLOOR,
            "known_mechanical": ("the toll is linear in the cost parameter, so d_toll(x2) == "
                                 "2*d_toll(x1); the x2 limb of the frozen condition cannot "
                                 "fail once x1 passes"),
            "no_adoption": ("the base arms are already judged; this only asks whether one of "
                            "their channels is purchasable"),
            "vocabulary": list(VOCABULARY),
        },
        "answer": answer,
        "ladder_summary": summary,
        "panels": panels,
    }
    if save:
        os.makedirs(outdir, exist_ok=True)
        cutoff = face["evidence_cutoff"]
        latest = os.path.join(outdir, "hysteresis_latest.json")
        dated = os.path.join(outdir, "HYSTERESIS-%s.json" % cutoff)
        for path in (dated, latest):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        with open(os.path.join(outdir, "hysteresis_by_rung_%s.csv" % cutoff), "w",
                  encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["panel", "arm", "band_frac", "band_bp", "band_bp_sd_is",
                        "weight_changes", "weight_changes_saved", "pair_ann_bp_per_year",
                        "d_pair_ann_bp_per_year", "d_pair_t_nw",
                        "d_selection_ann_bp_per_year", "d_toll_ann_bp_per_year",
                        "verdict"])
            for panel in panels:
                for arm in panel["arms"]:
                    for rung in arm["rungs"]:
                        w.writerow([panel["panel"], arm["name"], rung["band_frac"],
                                    rung["band_bp"], rung["band_width_is_bp"],
                                    rung["weight_changes"],
                                    rung.get("weight_changes_saved", ""),
                                    rung["totals_x2"]["pair_ann_bp_per_year"],
                                    (rung.get("delta_x2") or {}).get("d_pair_ann_bp_per_year", ""),
                                    (rung.get("delta_x2") or {}).get("d_pair_t_nw", ""),
                                    (rung.get("delta_x2") or {}).get("d_selection_ann_bp_per_year", ""),
                                    (rung.get("delta_x2") or {}).get("d_toll_ann_bp_per_year", ""),
                                    rung.get("verdict")
                                    or (rung.get("delta_x2") or {}).get("verdict", "")])
        print("wrote %s" % dated)
    print("cells %d | pays %d costs %d noise %d toll_short %d no_effect %d unresolved %d"
          % (summary["cells"], summary["band_pays"], summary["band_costs"],
             summary["band_noise"], summary["band_pays_toll_short"],
             summary["no_effect"], summary["unresolved"]))
    return face


# ---------------------------------------------------------------- reproduction
# The r1256 face is FROZEN as the acceptance test for this reconstruction: it is the only
# surviving copy of the original module's output, and a refreshed `latest` would make the
# test compare the module with itself.
REPRO_FACE = os.path.join(OUTDIR, "HYSTERESIS-2026-10-29.json")


def reproduce(face_path=None, tol=1e-6):
    """Compare a fresh run against a published face, field by field.

    The face is the only surviving copy of the original module's output, so it is the
    acceptance test for this reconstruction. It is never overwritten: `run --save` writes
    the current cutoff's dated face and `latest`, and the r1256 file stays where it is.
    """
    face_path = face_path or REPRO_FACE
    if not os.path.exists(face_path):
        return {"available": False, "reason": "no published face at %s" % face_path}
    published = json.load(open(face_path, encoding="utf-8"))
    # prose is compared separately: it is prose, and the published face's BAND_PAYS reason
    # prints twice the x2 toll delta it publishes beside it
    # the face was priced on the bar it stamps: cut the live panel back to it, so the test
    # is the module's arithmetic rather than today's panel having gained a session
    upto = {p.get("panel"): (p.get("sessions"), p.get("last"))
            for p in (published.get("panels") or []) if p.get("panel")}
    fresh = run(save=False, upto=upto)
    if fresh is None:
        return {"available": False, "reason": "study could not run"}
    diffs = []
    prose = []

    def note(path, a, b):
        if path.endswith("verdict_reason") or path.endswith("answer"):
            prose.append("%s %r vs %r" % (path, a, b))
        else:
            diffs.append("%s %r vs %r" % (path, a, b))

    def walk(path, a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if k in ("generated",):
                    continue
                if k not in a or k not in b:
                    note("%s.%s" % (path, k), a.get(k), b.get(k))
                    continue
                walk("%s.%s" % (path, k), a[k], b[k])
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                diffs.append("%s length %d vs %d" % (path, len(a), len(b)))
                return
            for i, (x, y) in enumerate(zip(a, b)):
                walk("%s[%d]" % (path, i), x, y)
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if abs(a - b) > tol:
                note(path, a, b)
        elif a != b:
            note(path, a, b)

    walk("face", {k: published.get(k) for k in ("panels", "ladder_summary", "answer")},
         {k: fresh.get(k) for k in ("panels", "ladder_summary", "answer")})
    return {"available": True, "path": face_path, "diffs": diffs[:40],
            "n_diffs": len(diffs), "identical": not diffs and not prose,
            "prose_diffs": prose[:10], "n_prose_diffs": len(prose),
            "numeric_identical": not diffs}


# ---------------------------------------------------------------- reference fixtures
def _synth(n=900, drift_bp=1.0, vol_cycle=None, seed=7):
    return e225._synth(n, drift_bp, vol_cycle, seed)


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    _dates, ret_bp = _synth()
    sig = e225.vol_signal(ret_bp)
    split = e225.split_index(len(ret_bp))

    # L1 band 0 is the base arm, on every arm
    ok = all(band_weights(sig, arm, 0.0) == e225.weights_series(sig, arm)
             for arm in BAND_ARMS)
    leg("band_zero_is_the_base_arm", ok, "%d arms" % len(BAND_ARMS))

    # L2 the band scale reads only the past
    past = band_width(sig, split)
    future_loud = list(sig)
    for i in range(split, len(future_loud)):
        if future_loud[i] is not None:
            future_loud[i] *= 25.0
    leg("band_width_ignores_the_future", past == band_width(future_loud, split),
        "%.6f" % (past or 0.0))

    # L3 a wider band never moves more
    prof = [change_profile(band_weights(sig, "tilt_linear", f * past))["weight_changes"]
            for f in BAND_FRACS]
    leg("wider_band_moves_less", all(prof[i] >= prof[i + 1] for i in range(len(prof) - 1)),
        str(prof))

    # L4 a flat path has no changes
    leg("flat_path_has_no_changes", change_profile([0.0] * 120)["weight_changes"] == 0)

    # L5 the profile counts transitions and movement
    p = change_profile([1.0, 1.0, 0.5, 0.0])
    leg("profile_counts_transitions_and_movement",
        p["weight_changes"] == 3 and abs(p["total_abs_dw"] - 2.0) < 1e-12, str(p))

    # L6 identity holds per session and per rung
    w = band_weights(sig, "tilt_step", 0.25 * past)
    rows, mu_is = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, 0.4)
    worst = max(abs(r["selection"] + r["sizing"] + r["toll"] - r["pair"]) for r in rows)
    leg("channel_identity_per_session", worst < 1e-9, "max residual %.3g" % worst)

    # L7 the totals publish the same identity
    tot = _totals(rows)
    leg("channel_identity_in_totals", abs(tot["identity_residual_bp"]) < 1e-9,
        "%.3g" % tot["identity_residual_bp"])

    # L8 the constant is honoured, not silently re-derived
    rows0, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, 0.0)
    mean_w = e225._mean([r["w"] for r in rows0])
    rows_m, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, mean_w)
    leg("const_is_an_argument",
        _totals(rows0)["selection_ann_bp_per_year"] != _totals(rows_m)["selection_ann_bp_per_year"],
        "const 0 vs %.4f" % (mean_w or 0.0))

    # L9 a rung against itself is all zeros
    d = paired_delta(rows, rows)
    leg("paired_delta_of_identical_rows_is_zero",
        all(abs(v) < 1e-15 for ch in CHANNELS + ("pair",) for v in d[ch]))

    # L10 the vocabulary answers each branch
    def fake(mean, toll_mean=None):
        """A delta with a chosen mean and a deterministic alternating wiggle."""
        def series(m):
            # period-7 wiggle: variance without the lag-1 negative autocorrelation that a
            # period-2 pattern would hand the Newey-West estimator
            return [m + (i % 7 - 3) * 1.0 for i in range(60)]
        return {"pair": series(mean), "selection": series(-3.0),
                "sizing": series(0.0),
                "toll": ([1.0] * 60 if toll_mean is None else series(toll_mean)),
                "delta_identity_residual_bp": 0.0}

    bars = {"same": rung_verdict(fake(0.0), True, 3.0)["verdict"],
            "pays": rung_verdict(fake(5.0, 3.0), False, 3.0)["verdict"],
            "noise": rung_verdict(fake(0.2, 3.0), False, 3.0)["verdict"],
            "costs": rung_verdict(fake(-5.0, 3.0), False, 3.0)["verdict"]}
    leg("verdict_branches", bars == {"same": "NO_EFFECT", "pays": "BAND_PAYS",
                                     "noise": "BAND_NOISE", "costs": "BAND_COSTS"}, str(bars))

    # L10b a pair that clears the bar on something other than the toll is not a toll fix
    short = rung_verdict(fake(5.0, None), False, 3.0)
    leg("pair_clearing_on_something_else_is_named",
        short["verdict"] == "BAND_PAYS_TOLL_SHORT", short["verdict_reason"])

    # L11 the annualiser is mean x sessions per year
    s = _stats([1.0] * 40)
    leg("annualiser_is_mean_times_sessions",
        abs(s["ann_bp_per_year"] - SESSIONS_PER_YEAR) < 1e-9, "%.3f" % s["ann_bp_per_year"])

    # L12 the toll is linear in the charge
    r1, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP, 0.4)
    r2, _ = channel_rows_c(w, ret_bp, split, COST_SIDE_BP * 2.0, 0.4)
    lin = (sum(x["toll"] for x in r2) - 2.0 * sum(x["toll"] for x in r1))
    leg("toll_is_linear_in_the_charge", abs(lin) < 1e-9, "%.3g" % lin)

    # L13 too-short samples are refused, not silently measured
    leg("short_sample_refused", band_width([None, None, 1.0], 2) in (None, 0.0))

    # L14 the frozen r1256 face is the acceptance test -- and it must still be here
    leg("frozen_acceptance_face_still_exists", os.path.exists(REPRO_FACE),
        os.path.basename(REPRO_FACE))
    rep = reproduce()
    if rep.get("available"):
        leg("reproduces_the_published_face_numbers", rep["numeric_identical"],
            "%d numeric diffs: %s" % (rep["n_diffs"], "; ".join(rep["diffs"][:2])))
    else:
        leg("reproduces_the_published_face", False, rep.get("reason", "unavailable"))

    passed = sum(1 for x in legs if x["ok"])
    print("E230 selftest %d/%d" % (passed, len(legs)))
    for x in legs:
        print("  [%s] %s%s" % ("PASS" if x["ok"] else "FAIL", x["leg"],
                               (" -- " + x["detail"]) if x["detail"] and not x["ok"] else ""))
    return passed == len(legs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "reproduce", "status"])
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return 0 if selftest() else 1
    if args.cmd == "reproduce":
        rep = reproduce()
        print(json.dumps(rep, indent=1, ensure_ascii=False)[:4000])
        return 0 if rep.get("numeric_identical") else 1
    if args.cmd == "status":
        path = os.path.join(OUTDIR, "hysteresis_latest.json")
        if not os.path.exists(path):
            print("no face")
            return 2
        d = json.load(open(path, encoding="utf-8"))
        print(json.dumps({"evidence_cutoff": d.get("evidence_cutoff"),
                          "generated": d.get("generated"),
                          "cells": d["ladder_summary"]["cells"],
                          "band_pays": d["ladder_summary"]["band_pays"]}, indent=1))
        return 0
    face = run(save=not args.no_save)
    return 0 if face else 2


if __name__ == "__main__":
    raise SystemExit(main())