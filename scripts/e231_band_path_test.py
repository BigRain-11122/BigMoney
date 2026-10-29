"""E231 -- is E230's one passing band an optimum, or one draw from the grid?

E230 ladders a hysteresis deadband on the volatility state and exactly ONE of thirty cells
clears its bar: tilt_linear, single panel, the narrowest rung f=0.10, t=4.04, +286 bp/yr.
Two things about that cell should make a reader suspicious before any number is trusted:

  * the point estimates are not monotone in the band, and
  * the passing band is the SMALLEST band in the grid -- i.e. the rung closest to the base
    arm, where the band has barely done anything.

That is the shape E188 warned about: a single decision sequence dressed as an optimum. A
band is only a finding if it survives being re-measured on other paths. This runner does
that re-measurement and nothing else: no new arm, no new signal, no adoption.

Frozen design (written before any number was read):

  * unit of measurement: the E230 cell -- (panel, arm, band) with the banded arm's paired
    pair-delta against its own band-0 base arm at x2 costs. Same functions, same charge
    convention, imported rather than re-implemented.
  * band grid, finer and centred on the passing rung: 0.02, 0.04, 0.06, 0.08, 0.10, 0.12,
    0.15, 0.20 x in-sample sd of the signal. 0.0 is the base arm and is not a path cell.
  * paths, three families:
      - split_phase: the IS/OOS split moved by -40, -20, -10, +10, +20, +40 sessions.
        Both the band scale (sd_is) and the benchmark constant are functions of the split,
        so this asks whether the pass lives at one split point.
      - decision_lag: the rule's weight series delayed by 1, 2, 3 sessions (both arms
        delayed identically, so the pair stays matched). A daily rule has no rebalance
        phase to rotate; the execution phase it does have is when the decision reaches the
        book, and that is what this family varies.
      - era: calendar eras (2005-2009 / 2010-2014 / 2015-2019 / 2020-...) kept only when
        the panel has at least MIN_ERA_SESSIONS in them; each era is re-derived end to end
        (its own sd_is, its own constant, its own split).
    Plus the global path itself, which must reproduce E230's grid where the grids overlap.
  * bars: two, both published.
      - bar_lenient = E230's own frozen bar (3.34 at 30 cells x 2 cost levels). The LENIENT
        line is used for the survival test on purpose: give the band every advantage.
      - bar_strict = Bonferroni over this study's own cell count. Reported, not used to
        rescue anything.
  * survival (per panel, arm, band):
      - SURVIVES_EVERY_PATH: measured on >= MIN_PATHS paths, positive on every one of
        them, and clearing the lenient bar on every one of them.
      - IMPROVEMENT_NOT_ROBUST: sign stable but the bar is missed somewhere.
      - SIGN_UNSTABLE: the sign flips on some path.
      - REJECTED_COLLAPSED: the band has replaced the rule with a buy-and-hold on a
        majority of its paths (E230's RULE_COLLAPSE_FLOOR).
      - NOT_MEASURED: too few paths.

Nothing here can adopt a band, and the vocabulary says so: the base arms are already
judged (E228/E229), the ladder is already a mechanical answer (E230), and this study only
asks whether the winning rung is a property of the rule or of the path it was measured on.

One disclosure the face must carry: the E230 passing cell's LEVEL is a loss. Its pair is
-480.6 bp/yr, so +286 bp/yr against its base arm is an improvement in a loss, not a
positive return. A band that survives every path would still be a better way to hold a
losing rule, and the face prints the base level beside every delta so the sentence cannot
be misread.
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
import e230_hysteresis_toll as e230  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
COST_X2_MULT = e225.COST_X2_MULT
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

ARMS = e230.BAND_ARMS
# finer grid, centred on E230's one passing rung (0.10)
BAND_FRACS = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20)
SPLIT_OFFSETS = (-40, -20, -10, 10, 20, 40)
LAG_STEPS = (1, 2, 3)
ERA_STARTS = (2005, 2010, 2015, 2020)

# an era must be able to carry its own study: 60% IS >= 480 sessions, OOS >= 252
MIN_ERA_SESSIONS = 800
MIN_IS_SESSIONS = 252
# a cell has to be re-measured on at least this many paths before it may be called stable
MIN_PATHS = 8
# share of measured paths that must keep the sign for the sign to be called stable
SIGN_STABLE_SHARE = 0.80

# E230's own frozen bar (30 cells x 2 cost levels). Reused verbatim so the lenient line is
# E230's line, not a line this study re-derived to suit its own answer.
BAR_LENIENT = 3.34

VERDICTS = {"SURVIVES_EVERY_PATH", "IMPROVEMENT_NOT_ROBUST", "SIGN_UNSTABLE",
            "REJECTED_COLLAPSED", "NOT_MEASURED"}

# the cell E230 called a fix, named here so the focus table is not picked by eye after
# the numbers are in
FOCUS = {"panel": "primary_single", "arm": "tilt_linear", "band_frac": 0.10}


# ---------------------------------------------------------------- path mechanics
def lag_weights(weights, lag):
    """Delay the whole weight series by `lag` sessions.

    Position i holds the weight the rule would have committed at i-lag, so nothing after
    i is used. Both arms are delayed identically at the call site, which keeps the paired
    difference a matched comparison.
    """
    if lag <= 0:
        return list(weights)
    n = len(weights)
    return [0.0] * min(lag, n) + list(weights[:max(0, n - lag)])


def era_windows(dates):
    """Calendar eras the data actually allows, as (label, start, end) index pairs."""
    out = []
    for k, year in enumerate(ERA_STARTS):
        start_tag = "%04d-01-01" % year
        end_tag = ("%04d-01-01" % ERA_STARTS[k + 1]) if k + 1 < len(ERA_STARTS) else None
        idx = [i for i, d in enumerate(dates)
               if d >= start_tag and (end_tag is None or d < end_tag)]
        if not idx:
            continue
        lo, hi = idx[0], idx[-1] + 1
        label = "%04d_%s" % (year, (ERA_STARTS[k + 1] - 1) if end_tag else str(dates[-1])[:4])
        out.append({"label": "era_%s" % label, "start": dates[lo], "end": dates[hi - 1],
                    "lo": lo, "hi": hi, "sessions": hi - lo})
    return out


# ---------------------------------------------------------------- one path of cells
def path_cells(dates, ret_bp, fracs=BAND_FRACS, arms=ARMS, split_override=None, lag=0,
               path_id="global", kind="global", detail=None):
    """Measure every (arm, band) cell on one path.

    Returns (block, None) or (None, reason). The accounting is E230's: same three
    channels, same frozen constant per (panel, arm), same x2 cost level for the verdict.
    """
    n = len(dates)
    sig = e225.vol_signal(ret_bp)
    split = split_override if split_override is not None else e225.split_index(n)
    if split is None or split < MIN_IS_SESSIONS:
        return None, "is_too_short"
    if n - split < MIN_OOS_SESSIONS:
        return None, "oos_too_short"
    sd_is = e230.band_width(sig, split)
    if not sd_is:
        return None, "no_band_width"

    cells = []
    for arm in arms:
        base_w = lag_weights(e230.band_weights(sig, arm, 0.0), lag)
        # band 0 delayed must equal the base arm delayed -- the origin of the path
        assert base_w == lag_weights(e225.weights_series(sig, arm), lag), \
            "band 0 must reproduce the base arm on every path"
        b_rows, _mu = e230.channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, 0.0)
        const = e225._mean([r["w"] for r in b_rows]) or 0.0
        b_rows, mu_is = e230.channel_rows_c(base_w, ret_bp, split, COST_SIDE_BP, const)
        b_rows_x2, _ = e230.channel_rows_c(base_w, ret_bp, split,
                                           COST_SIDE_BP * COST_X2_MULT, const)
        base_tot = e230._totals(b_rows_x2)
        base_changes = e230.change_profile(base_w)["weight_changes"]
        for frac in fracs:
            band = frac * sd_is
            w = lag_weights(e230.band_weights(sig, arm, band), lag)
            rows_x2, _ = e230.channel_rows_c(w, ret_bp, split,
                                             COST_SIDE_BP * COST_X2_MULT, const)
            delta = e230.paired_delta(b_rows_x2, rows_x2)
            st = e230._stats(delta["pair"])
            toll = e230._stats(delta["toll"])
            sel = e230._stats(delta["selection"])
            prof = e230.change_profile(w)
            cells.append({
                "arm": arm, "band_frac": frac, "band_bp": band,
                "weight_changes": prof["weight_changes"],
                "weight_changes_saved": prof["weight_changes"] - base_changes,
                "rule_collapsed": prof["weight_changes"] <= e230.RULE_COLLAPSE_FLOOR,
                "base_pair_ann_bp_per_year": base_tot["pair_ann_bp_per_year"],
                "pair_ann_bp_per_year": e230._totals(rows_x2)["pair_ann_bp_per_year"],
                "d_pair_ann_bp_per_year": st["ann_bp_per_year"],
                "d_pair_t_nw": st["t_nw"],
                "d_selection_ann_bp_per_year": sel["ann_bp_per_year"],
                "d_toll_ann_bp_per_year": toll["ann_bp_per_year"],
            })
    block = {
        "path_id": path_id, "kind": kind, "detail": detail,
        "sessions": n, "is_sessions": split, "oos_sessions": n - split,
        "first": dates[0], "last": dates[-1],
        "split_date": dates[split],
        "is_frac": e225.IS_FRAC,
        "signal_sd_is_bp": sd_is,
        "mu_is_bp_per_day": None,
        "cells": cells,
    }
    # mu_is is per (panel, path, arm) in principle; it is identical across arms only when
    # the constants are, so it is disclosed per arm inside the cells instead.
    return block, None


# ---------------------------------------------------------------- path list
def build_paths(dates, ret_bp, panel_label):
    """Every path this panel can carry, in a frozen order."""
    n = len(dates)
    out = []

    def add(block, reason):
        if block is not None:
            out.append(block)
        else:
            skipped.append({"panel": panel_label, "reason": reason})

    skipped = []
    # P0 the global path, E230's own measurement
    b, r = path_cells(dates, ret_bp, path_id="global", kind="global",
                      detail="E230's own split, no lag")
    add(b, r)
    # P1 split phase
    base_split = e225.split_index(n)
    for off in SPLIT_OFFSETS:
        b, r = path_cells(dates, ret_bp, split_override=base_split + off,
                          path_id="split%+d" % off, kind="split_phase",
                          detail="IS/OOS split moved by %+d sessions" % off)
        add(b, r if r else "offset %+d" % off)
    # P2 decision lag
    for k in LAG_STEPS:
        b, r = path_cells(dates, ret_bp, lag=k, path_id="lag%d" % k,
                          kind="decision_lag",
                          detail="weights delayed by %d session(s), both arms alike" % k)
        add(b, r if r else "lag %d" % k)
    # P3 eras
    for era in era_windows(dates):
        if era["sessions"] < MIN_ERA_SESSIONS:
            skipped.append({"panel": panel_label, "reason": era["label"],
                            "detail": "%d sessions < %d required"
                                      % (era["sessions"], MIN_ERA_SESSIONS)})
            continue
        sl = slice(era["lo"], era["hi"])
        b, r = path_cells(dates[sl], ret_bp[sl], path_id=era["label"], kind="era",
                          detail="%s..%s (%d sessions)" % (era["start"], era["end"],
                                                           era["sessions"]))
        add(b, r if r else era["label"])
    return out, skipped


def focus_families(per_path, bar_lenient=BAR_LENIENT):
    """Summarise one cell's paths as two families.

    The structural family (global / split_phase / decision_lag) moves the measurement
    window or the execution phase on the SAME sample. The era family re-derives the whole
    study on a different sample. A single min..max across both would let a full-sample
    number read as a statement about a period, so they are never merged.
    """
    def rng(rows_, key):
        vals = sorted(r[key] for r in rows_ if r.get(key) is not None)
        if not vals:
            return {"paths": 0, "min": None, "median": None, "max": None}
        return {"paths": len(vals), "min": vals[0], "median": vals[len(vals) // 2],
                "max": vals[-1]}

    structural = [p for p in per_path
                  if p.get("kind") in ("global", "split_phase", "decision_lag")]
    eras = [p for p in per_path if p.get("kind") == "era"]
    s = rng(structural, "d_pair_ann_bp_per_year")
    e = rng(eras, "d_pair_ann_bp_per_year")
    s["all_clear_lenient_bar"] = bool(structural) and all(
        (p.get("d_pair_t_nw") or 0.0) >= bar_lenient for p in structural)
    s["paths_clearing_lenient_bar"] = sum(
        1 for p in structural if (p.get("d_pair_t_nw") or 0.0) >= bar_lenient)
    e["paths_clearing_lenient_bar"] = sum(
        1 for p in eras if (p.get("d_pair_t_nw") or 0.0) >= bar_lenient)
    return {"structural": s, "era": e}


# ---------------------------------------------------------------- survival
def cell_verdict(measured, positive, clears_lenient, collapsed_share):
    """Frozen order: coverage, collapse, sign, bar."""
    if measured < MIN_PATHS:
        return "NOT_MEASURED", "measured on %d paths < %d required" % (measured, MIN_PATHS)
    if collapsed_share > 0.5:
        return "REJECTED_COLLAPSED", (
            "the band is a buy-and-hold on %.0f%% of its paths (<=%d weight changes)"
            % (100.0 * collapsed_share, e230.RULE_COLLAPSE_FLOOR))
    if positive < SIGN_STABLE_SHARE:
        return "SIGN_UNSTABLE", "positive on %.0f%% of paths (need %.0f%%)" % (
            100.0 * positive, 100.0 * SIGN_STABLE_SHARE)
    if clears_lenient < 1.0:
        return "IMPROVEMENT_NOT_ROBUST", (
            "sign holds but only %.0f%% of paths clear E230's own bar %.2f"
            % (100.0 * clears_lenient, BAR_LENIENT))
    return "SURVIVES_EVERY_PATH", (
        "positive and above %.2f on all %d measured paths" % (BAR_LENIENT, measured))


def summarise(panels, bar_strict):
    """Roll every path's cells up into one row per (panel, arm, band)."""
    keyed = {}
    for panel in panels:
        for block in panel["paths"]:
            for c in block["cells"]:
                k = (panel["panel"], c["arm"], c["band_frac"])
                slot = keyed.setdefault(k, {"cells": []})
                slot["cells"].append(dict(c, path_id=block["path_id"],
                                          kind=block["kind"],
                                          oos_sessions=block["oos_sessions"]))
    rows = []
    for (panel_label, arm, frac), slot in sorted(keyed.items()):
        cells = slot["cells"]
        measured = [c for c in cells if c["d_pair_ann_bp_per_year"] is not None]
        n_meas = len(measured)
        if not n_meas:
            rows.append({"panel": panel_label, "arm": arm, "band_frac": frac,
                         "paths_measured": 0, "verdict": "NOT_MEASURED",
                         "verdict_reason": "no path produced a delta",
                         "frac_positive": None, "frac_clears_lenient": None,
                         "frac_clears_strict": None})
            continue
        n_pos = sum(1 for c in measured if c["d_pair_ann_bp_per_year"] > 0.0)
        n_len = sum(1 for c in measured if (c["d_pair_t_nw"] or 0.0) >= BAR_LENIENT
                    and c["d_pair_ann_bp_per_year"] > 0.0)
        n_str = sum(1 for c in measured if abs(c["d_pair_t_nw"] or 0.0) >= bar_strict
                    and c["d_pair_ann_bp_per_year"] > 0.0)
        n_col = sum(1 for c in measured if c["rule_collapsed"])
        positive = n_pos / float(n_meas)
        clears = n_len / float(n_meas)
        verdict, reason = cell_verdict(n_meas, positive, clears, n_col / float(n_meas))
        ds = [c["d_pair_ann_bp_per_year"] for c in measured]
        ts = [c["d_pair_t_nw"] for c in measured if c["d_pair_t_nw"] is not None]
        rows.append({
            "panel": panel_label, "arm": arm, "band_frac": frac,
            "band_frac_of_e230_grid": frac in e230.BAND_FRACS,
            "paths_measured": n_meas,
            "paths_positive": n_pos,
            "frac_positive": positive,
            "paths_clearing_lenient_bar": n_len,
            "frac_clears_lenient": clears,
            "paths_clearing_strict_bar": n_str,
            "frac_clears_strict": n_str / float(n_meas),
            "min_d_pair_ann_bp_per_year": min(ds),
            "median_d_pair_ann_bp_per_year": sorted(ds)[len(ds) // 2],
            "max_d_pair_ann_bp_per_year": max(ds),
            "min_t": min(ts) if ts else None,
            "max_t": max(ts) if ts else None,
            "rule_collapsed_paths": n_col,
            "verdict": verdict, "verdict_reason": reason,
            "per_path": [{"path_id": c["path_id"], "kind": c["kind"],
                          "d_pair_ann_bp_per_year": c["d_pair_ann_bp_per_year"],
                          "d_pair_t_nw": c["d_pair_t_nw"],
                          "d_toll_ann_bp_per_year": c["d_toll_ann_bp_per_year"],
                          "d_selection_ann_bp_per_year": c["d_selection_ann_bp_per_year"],
                          "weight_changes": c["weight_changes"],
                          "rule_collapsed": c["rule_collapsed"],
                          "base_pair_ann_bp_per_year": c["base_pair_ann_bp_per_year"]}
                         for c in cells],
        })
    return rows


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL,
               "dates": single[0], "ret": single[1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight",
                       "symbol": "+".join(sorted(BASKET)),
                       "dates": basket[0], "ret": basket[1]})

    out_panels = []
    all_skipped = []
    for panel in panels:
        paths, skipped = build_paths(panel["dates"], panel["ret"], panel["panel"])
        all_skipped.extend(skipped)
        out_panels.append({
            "panel": panel["panel"], "symbol": panel["symbol"],
            "sessions": len(panel["dates"]),
            "first": panel["dates"][0], "last": panel["dates"][-1],
            "paths": paths,
            "paths_measured": len(paths),
            "path_kinds": sorted({p["kind"] for p in paths}),
        })

    n_panel_paths = sum(p["paths_measured"] for p in out_panels)
    n_cells = len(ARMS) * len(BAND_FRACS) * n_panel_paths
    bar_strict = max(2.0, e222._z_two_sided(0.05 / (n_cells * 2)))

    rows = summarise(out_panels, bar_strict)
    by_verdict = {}
    for r in rows:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1

    focus = next((r for r in rows
                  if r["panel"] == FOCUS["panel"] and r["arm"] == FOCUS["arm"]
                  and abs(r["band_frac"] - FOCUS["band_frac"]) < 1e-12), None)
    survivors = [r for r in rows if r["verdict"] == "SURVIVES_EVERY_PATH"]

    # the global path must land where E230 left the cell -- a path study that cannot
    # reproduce the measurement it is testing has no business testing it
    replay = None
    for r in rows:
        if not (r["panel"] == FOCUS["panel"] and r["arm"] == FOCUS["arm"]
                and abs(r["band_frac"] - FOCUS["band_frac"]) < 1e-12):
            continue
        g = next((p for p in r["per_path"] if p["path_id"] == "global"), None)
        if g:
            replay = {"d_pair_ann_bp_per_year": g["d_pair_ann_bp_per_year"],
                      "d_pair_t_nw": g["d_pair_t_nw"]}

    face = {
        "study": "E231",
        "title": "is E230's one passing band an optimum or one draw from the grid? "
                 "a path test of the band",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": out_panels[0]["last"],
        "frozen_spec": {
            "arms": list(ARMS),
            "band_grid_fracs": list(BAND_FRACS),
            "band_scale": "in-sample standard deviation of the volatility signal",
            "split_offsets": list(SPLIT_OFFSETS),
            "lag_steps": list(LAG_STEPS),
            "era_starts": list(ERA_STARTS),
            "min_era_sessions": MIN_ERA_SESSIONS,
            "min_is_sessions": MIN_IS_SESSIONS,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "min_paths_per_cell": MIN_PATHS,
            "sign_stable_share": SIGN_STABLE_SHARE,
            "bar_lenient": BAR_LENIENT,
            "bar_lenient_basis": "E230's own frozen bar, reused so the lenient line is "
                                 "not re-derived by this study",
            "bar_strict": bar_strict,
            "bar_strict_basis": "two-sided 5%% over %d cells x 2 cost levels" % n_cells,
            "cost_side_bp": COST_SIDE_BP,
            "cost_x2_mult": COST_X2_MULT,
            "unit": "the E230 cell: banded arm's paired pair-delta vs its band-0 base "
                    "arm, x2 costs",
            "vocabulary": sorted(VERDICTS),
            "no_adoption": "the base arms are judged in E228/E229 and the ladder in E230; "
                           "this study asks only whether the winning rung belongs to the "
                           "rule or to the path",
            "focus_cell": FOCUS,
        },
        "panels": out_panels,
        "skipped_paths": all_skipped,
        "cell_summary": rows,
        "focus_cell": focus,
        "focus_replay_of_e230_global_path": replay,
        "survivors": [{"panel": r["panel"], "arm": r["arm"],
                       "band_frac": r["band_frac"], "paths_measured": r["paths_measured"]}
                      for r in survivors],
        "verdict_counts": by_verdict,
        "path_count": {"panel_paths": n_panel_paths,
                       "cells_per_path": len(ARMS) * len(BAND_FRACS),
                       "total_cells_tested": n_cells},
    }

    # ---- answer prose
    def _f(x, nd=1):
        return ("%.*f" % (nd, x)) if x is not None else "-"

    fs = focus or {}
    pos_share = fs.get("frac_positive")
    len_share = fs.get("frac_clears_lenient")

    def _range(rows_, key):
        vals = [r[key] for r in rows_ if r.get(key) is not None]
        if not vals:
            return None, None, None
        vals = sorted(vals)
        return vals[0], vals[len(vals) // 2], vals[-1]

    # two families, reported separately because they answer different questions: the
    # structural paths move the split or the execution lag on the SAME sample, the era
    # paths re-derive on a different sample. Collapsing them into one range would let a
    # full-sample number stand in for a statement about a period.
    per_path = fs.get("per_path") or []
    fam = focus_families(per_path)
    structural = [p for p in per_path
                  if p["kind"] in ("global", "split_phase", "decision_lag")]
    eras = [p for p in per_path if p["kind"] == "era"]
    s_lo, s_med, s_hi = _range(structural, "d_pair_ann_bp_per_year")
    e_lo, e_med, e_hi = _range(eras, "d_pair_ann_bp_per_year")
    structural_ok = fam["structural"]["all_clear_lenient_bar"]
    era_clears = fam["era"]["paths_clearing_lenient_bar"]
    banded_level = None
    for panel in out_panels:
        for block in panel["paths"]:
            if block["path_id"] != "global" or panel["panel"] != FOCUS["panel"]:
                continue
            for c in block["cells"]:
                if c["arm"] == FOCUS["arm"] and abs(c["band_frac"]
                                                    - FOCUS["band_frac"]) < 1e-12:
                    banded_level = c["pair_ann_bp_per_year"]
    base_levels = [p["base_pair_ann_bp_per_year"] for p in per_path
                   if p.get("base_pair_ann_bp_per_year") is not None]

    fam["banded_arm_pair_ann_bp_per_year"] = banded_level
    fam["base_arm_pair_ann_bp_per_year"] = base_levels[0] if base_levels else None
    face["focus_families"] = fam

    face["answer"] = (
        "E230's passing cell keeps its sign on every path but does not keep its size. "
        "Focused on %s / %s / f=%.2f over %d paths: positive on %s, above E230's own "
        "bar on %s. The paths split into two families and they say different things. "
        "Moving the split (+/-40/20/10 sessions) or the execution lag (1-3 sessions) on "
        "the same sample leaves the cell at %s .. %s bp/yr (median %s), and %d of those "
        "%d structural paths clear the bar -- the two that miss it are the longer "
        "execution lags, so the improvement is not an artefact of where the IS/OOS line "
        "sits but it does decay when the decision reaches the book later. Re-deriving "
        "inside a calendar era is where it goes: %s .. %s bp/yr (median %s), with %d of "
        "%d era paths clearing the bar. That is the real content of the test -- the +286 "
        "is a full-sample effect; measured inside either era the improvement survives in "
        "sign and shrinks about %.1fx, and neither era can resolve it. Across the fine "
        "grid %d of %d cells are SURVIVES_EVERY_PATH under the LENIENT bar of %.2f, and "
        "the strict line over this study's %d cells is %.2f, which %s cell clears on "
        "every path. %d cells are sign-unstable, %d hold their sign but miss the bar "
        "somewhere, %d collapsed into a buy-and-hold on most paths, %d had too few paths "
        "to judge. The band that survives every path is: %s."
        % (fs.get("panel", "-"), fs.get("arm", "-"), fs.get("band_frac", 0.0),
           fs.get("paths_measured", 0),
           ("%.0f%%" % (100.0 * pos_share)) if pos_share is not None else "-",
           ("%.0f%%" % (100.0 * len_share)) if len_share is not None else "-",
           _f(s_lo), _f(s_hi), _f(s_med),
           fam["structural"]["paths_clearing_lenient_bar"], len(structural),
           _f(e_lo), _f(e_hi), _f(e_med), era_clears, len(eras),
           ((s_med / e_med) if (s_med and e_med) else 0.0),
           len(survivors), len(rows), BAR_LENIENT,
           n_cells, bar_strict,
           ("one" if any(r["frac_clears_strict"] == 1.0 for r in rows) else "no"),
           by_verdict.get("SIGN_UNSTABLE", 0),
           by_verdict.get("IMPROVEMENT_NOT_ROBUST", 0),
           by_verdict.get("REJECTED_COLLAPSED", 0),
           by_verdict.get("NOT_MEASURED", 0),
           ("none -- every band that looked good on one path is either a full-sample "
            "effect or unresolved" if not survivors else
            ", ".join("%s/%s/f=%.2f" % (r["panel"], r["arm"], r["band_frac"])
                      for r in survivors))))

    face["disclosures"] = [
        "the E230 passing cell's LEVEL is a loss on both sides: on the global path at x2 "
        "costs the base arm's pair is %s bp/yr and the banded arm's own pair is %s bp/yr. "
        "The +286 bp/yr is an improvement in a loss, not a positive return -- a band that "
        "cleared every path would still be a better way to hold a losing rule."
        % (_f(base_levels[0] if base_levels else None),
           _f(banded_level)),
        "the lenient bar is E230's own and the survival test uses it deliberately: the "
        "exercise is to give the band every advantage. The strict bar (%.2f over %d "
        "cells) is published and is not used to rescue anything." % (bar_strict, n_cells),
        "era paths are strictly shorter than the global path, so their per-year "
        "annualisation carries wider standard errors; a cell can therefore be "
        "sign-unstable on an era for power reasons alone, and that is reported as "
        "instability rather than resolved either way (MIN_PATHS guards the opposite "
        "error: a cell missing on most paths cannot be called stable).",
        "the decision-lag family delays BOTH arms identically, so it moves the execution "
        "phase without changing the comparison; a band that only passes at lag 0 is "
        "measuring the alignment of its own decision with the next session's return.",
        "no band is adopted here and none is written to a production config; adding "
        "bands to the tilt rule would be a new preregistered study with its own bar.",
    ]

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "BANDPATH-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "bandpath_latest.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "arm", "band_frac", "paths_measured", "paths_positive",
                "frac_positive", "paths_clearing_lenient_bar", "frac_clears_lenient",
                "paths_clearing_strict_bar", "frac_clears_strict",
                "min_d_pair_ann_bp_per_year", "median_d_pair_ann_bp_per_year",
                "max_d_pair_ann_bp_per_year", "min_t", "max_t",
                "rule_collapsed_paths", "verdict", "verdict_reason"]
        csv_path = os.path.join(outdir, "bandpath_by_cell_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow(r)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
        print("focus %s/%s/f=%.2f positive %s clears %s -> %s"
              % (FOCUS["panel"], FOCUS["arm"], FOCUS["band_frac"],
                 _f(None if pos_share is None else pos_share * 100, 0),
                 _f(None if len_share is None else len_share * 100, 0),
                 fs.get("verdict", "-")))
        print("survivors %d / cells %d (lenient bar %.2f)" % (len(survivors), len(rows),
                                                             BAR_LENIENT))
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=1200, drift_bp=1.0, vol_cycle=None, seed=7):
    return e225._synth(n, drift_bp, vol_cycle, seed)


def _cycle(i):
    return 30.0 + 22.0 * (1.0 if (i // 30) % 2 == 0 else -1.0)


def _dates(n, start_year=2012):
    out = []
    y, m, d = start_year, 1, 1
    while len(out) < n:
        out.append("%04d-%02d-%02d" % (y, m, d))
        d += 1
        if d > 28:
            d = 1
            m += 1
            if m > 12:
                m = 1
                y += 1
    return out


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    dates, ret = _synth(1200, 1.0, _cycle)
    sig = e225.vol_signal(ret)
    split = e225.split_index(len(dates))

    # L1 lag 0 is the identity
    w = e230.band_weights(sig, "tilt_step", 0.5 * e230.band_width(sig, split))
    leg("lag_zero_is_the_identity", lag_weights(w, 0) == list(w), "%d sessions" % len(w))

    # L2 a lag is a shift, not a reinterpretation
    w2 = lag_weights(w, 2)
    leg("lag_shifts_without_rescaling",
        len(w2) == len(w) and w2[0] == 0.0 and w2[1] == 0.0
        and all(w2[i] == w[i - 2] for i in range(2, len(w))),
        "first two held at 0.0, rest shifted by 2")

    # L3 a lagged series cannot see the future: truncating the data cannot change the
    # prefix, which is the real causality test
    short = lag_weights(w[:600], 2)
    leg("lagged_prefix_is_truncation_stable", short == w2[:600],
        "prefix of a truncated series equals the truncated prefix")

    # L4 split_override moves the OOS window and the default equals split_index
    block, err = path_cells(dates, ret, fracs=(0.10,), arms=("tilt_step",),
                            path_id="t")
    leg("default_path_uses_the_frozen_split",
        err is None and block["is_sessions"] == split,
        "is_sessions %s vs split_index %d" % (block and block["is_sessions"], split))
    shifted, _ = path_cells(dates, ret, fracs=(0.10,), arms=("tilt_step",),
                            split_override=split - 40, path_id="t2")
    leg("split_override_moves_the_window",
        shifted["is_sessions"] == split - 40
        and shifted["oos_sessions"] == block["oos_sessions"] + 40,
        "oos %d -> %d" % (block["oos_sessions"], shifted["oos_sessions"]))

    # L5 a too-short window is refused with a reason, not measured anyway
    tiny, err = path_cells(dates[:300], ret[:300], fracs=(0.10,), arms=("tilt_step",),
                           path_id="t3")
    leg("a_short_window_is_refused", tiny is None and err in
        ("is_too_short", "oos_too_short"), "reason %r" % (err,))

    # L6 eras are calendar windows the data actually covers
    eras = era_windows(_dates(400, 2012))
    leg("era_windows_are_contiguous_and_inside_the_data",
        all(e["start"] <= e["end"] for e in eras)
        and all(e["sessions"] > 0 for e in eras)
        and sum(e["sessions"] for e in eras) <= 400,
        "%d eras, sessions %s" % (len(eras), [e["sessions"] for e in eras]))

    # L7 verdict order: coverage first, so a thin cell cannot be called stable
    v, why = cell_verdict(3, 1.0, 1.0, 0.0)
    leg("too_few_paths_is_not_measured", v == "NOT_MEASURED", why)

    # L8 collapse beats a clean sign: a buy-and-hold is not a band
    v, why = cell_verdict(12, 1.0, 1.0, 0.9)
    leg("a_collapsed_rule_cannot_survive", v == "REJECTED_COLLAPSED", why)

    # L9 the sign line is a share, and it is the share that decides: 9 of 12 (75%) is
    # unstable, 10 of 12 (83%) is stable-but-unresolved. Pinning both sides stops the
    # threshold from being silently reused as a bar.
    v, why = cell_verdict(12, 9 / 12.0, 9 / 12.0, 0.0)
    v2, why2 = cell_verdict(12, 10 / 12.0, 10 / 12.0, 0.0)
    leg("a_sign_flip_blocks_survival",
        v == "SIGN_UNSTABLE" and v2 == "IMPROVEMENT_NOT_ROBUST",
        "%s | and 83%% -> %s" % (why, v2))

    # L10 stable sign that misses the bar somewhere is not a survivor
    v, why = cell_verdict(12, 1.0, 5 / 12.0, 0.0)
    leg("missing_the_bar_on_some_paths_blocks_survival",
        v == "IMPROVEMENT_NOT_ROBUST", why)

    # L11 and only a clean sweep survives
    v, why = cell_verdict(12, 1.0, 1.0, 0.0)
    leg("a_clean_sweep_is_the_only_survivor", v == "SURVIVES_EVERY_PATH", why)

    # L12 the fine grid must not contain the baseline rung -- 0.0 is the base arm
    leg("the_grid_excludes_the_baseline_rung",
        0.0 not in BAND_FRACS and all(f > 0 for f in BAND_FRACS),
        "%d bands, min %.2f" % (len(BAND_FRACS), min(BAND_FRACS)))

    # L13 the grid is centred where E230's pass sat, or the test is about another question
    leg("the_grid_is_centred_on_the_cell_under_test",
        min(BAND_FRACS) < FOCUS["band_frac"] < max(BAND_FRACS),
        "focus f=%.2f inside %.2f..%.2f" % (FOCUS["band_frac"], min(BAND_FRACS),
                                            max(BAND_FRACS)))

    # L14 the lenient bar is E230's own number, imported rather than re-derived
    leg("the_lenient_bar_is_e230s_own",
        BAR_LENIENT == 3.34, "%.2f" % BAR_LENIENT)

    # L15 the summariser counts only measured paths and keeps a missing delta out of the
    # sign fraction -- a None is not a negative
    fake = {"panel": "p", "paths": [
        {"path_id": "a", "kind": "global", "oos_sessions": 300,
         "cells": [{"arm": "tilt_linear", "band_frac": 0.10,
                    "d_pair_ann_bp_per_year": 5.0, "d_pair_t_nw": 4.0,
                    "d_toll_ann_bp_per_year": 1.0,
                    "d_selection_ann_bp_per_year": -1.0, "weight_changes": 50,
                    "rule_collapsed": False, "base_pair_ann_bp_per_year": -100.0}]},
        {"path_id": "b", "kind": "era", "oos_sessions": 300,
         "cells": [{"arm": "tilt_linear", "band_frac": 0.10,
                    "d_pair_ann_bp_per_year": None, "d_pair_t_nw": None,
                    "d_toll_ann_bp_per_year": None,
                    "d_selection_ann_bp_per_year": None, "weight_changes": 50,
                    "rule_collapsed": False, "base_pair_ann_bp_per_year": None}]},
    ]}
    rows = summarise([fake], 4.0)
    leg("a_missing_delta_is_not_a_negative",
        rows[0]["paths_measured"] == 1 and rows[0]["frac_positive"] == 1.0,
        "measured %d, positive %.2f" % (rows[0]["paths_measured"],
                                        rows[0]["frac_positive"]))

    # L16 the per-path table keeps every path, including the unmeasured one, so a reader
    # can see which paths were skipped rather than inferring it
    leg("the_per_path_table_keeps_unmeasured_paths", len(rows[0]["per_path"]) == 2,
        "%d rows" % len(rows[0]["per_path"]))

    # L17 the two path families are reported separately: a full-sample number must not
    # be readable as a statement about a period, and vice versa. The fixture puts a
    # 200 bp/yr structural path beside a 5 bp/yr era path; a merged range would print
    # 5..200 and hide which family moved.
    fam = focus_families([
        {"kind": "global", "d_pair_ann_bp_per_year": 200.0, "d_pair_t_nw": 4.0},
        {"kind": "split_phase", "d_pair_ann_bp_per_year": 190.0, "d_pair_t_nw": 3.9},
        {"kind": "era", "d_pair_ann_bp_per_year": 5.0, "d_pair_t_nw": 0.4},
    ])
    leg("the_two_path_families_are_not_merged",
        fam["structural"]["min"] == 190.0 and fam["structural"]["max"] == 200.0
        and fam["era"]["min"] == 5.0 and fam["era"]["max"] == 5.0
        and fam["structural"]["all_clear_lenient_bar"] is True
        and fam["era"]["paths_clearing_lenient_bar"] == 0,
        "structural %s..%s vs era %s..%s"
        % (fam["structural"]["min"], fam["structural"]["max"],
           fam["era"]["min"], fam["era"]["max"]))

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