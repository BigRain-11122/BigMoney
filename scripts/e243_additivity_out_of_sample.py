#!/usr/bin/env python3
"""E243 -- does "the rest channel adds up" survive outside the window that produced it?

E240 published the identified additivity test on the five-member common grid (2020-11-17 onwards,
1328 sessions): one counterparty 0.183 vs the sum of the other three 0.175, difference
+0.008 [-0.012, +0.022] -> rest_channel_is_additive. That verdict came from ONE window, and the
family's own two laws apply to it:

  * a single-arm result is not a rule until its neighbourhood is tested (E188 / E231 path test);
  * a difference that exists in one era only is not a mechanism (E213 bucket reread).

So this face re-runs the SAME design on a grid of cells and publishes the difference interval in
every one of them:

  all_five            the E240 window itself, replayed to a tolerance (this is the control cell)
  pre2020_four        the four members that exist before 2020-11-16, on their own common grid
  era_2020_2022       five members, first era
  era_2023_2024       five members, second era
  era_2025_now        five members, newest era
  loo_drop_<member>   leave-one-member-out, five cells (the neighbourhood test)
  early_three         the three oldest members 2013-03..2016-11 -- a k=3 design, where the "sum
                      of the other three" degenerates to the single remaining member and the
                      difference is therefore not an aggregation reading. Published, labelled
                      degenerate, and excluded from the stability verdict.

A second, independent product came out of building the grid, and it is the more important one:
E240's POOLED aggregator (`pooled.diff = -4.1e-15`) is not agreement, it is an artifact. The
pooled stack replicates one member's response vector across its k-1 counterfactual "one
counterparty" blocks, which annihilates exactly the direction that separates b_one from
b_rest3; the solver then returns the symmetric split. The face proves this mechanically on every
run: `pooled_split_is_an_artifact` fits the pooled design on a fixture whose TRUTH differs 45x
between the one and the rest channel and shows the pooled difference collapses to < 1e-12 while
the per-pair aggregator reads the gap. A design that cannot see a regressor must publish
identifies: false, never a number (E239 family).

NO BILL, NO ADOPTION. This face re-prices nothing and adopts no arm.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402
import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
MIN_SESSIONS = e240.MIN_SESSIONS
REJECT_MIN_PAIRS = 2     # frozen: additivity survives one 95% false positive across 20 pairs
RESOLUTION_MAX = 0.10    # frozen: an interval wider than +/-0.10 log points cannot support
                         # "the two channels pay the same" -- it merely fails to reject it
STUDY = "E243"

# The era cut points. 2020-11-16 is the first session of sh588000, so it is also the date the
# five-member grid begins; the pre-2020 cells are the four members that exist before it.
ERA5_START = "2020-11-16"
ERAS = (("era_2020_2022", "2020-11-16", "2022-12-31"),
        ("era_2023_2024", "2023-01-01", "2024-12-31"),
        ("era_2025_now", "2025-01-01", "9999-12-31"))
PRE2020_END_BEFORE = "2020-11-16"
EARLY_THREE = ("sh510050", "sh510300", "sh510500")
EARLY_THREE_FROM = "2013-03-15"     # first session on which all three print
EARLY_THREE_TO = "2016-11-03"       # last session before the fourth member exists

VERDICTS = ("rest_channel_is_additive",
            "additivity_only_in_the_mean",
            "additivity_era_dependent",
            "additivity_rejected_out_of_sample",
            "additivity_not_resolved_out_of_sample",
            "unresolved_heterogeneous_pairs",
            "unresolved_interval_too_wide",
            "unresolved_insufficient_rows")


# ---------------------------------------------------------------- panel windows
def subset_per(per, syms, lo=None, hi=None):
    """Restrict each member's date->(y,l) map to [lo, hi], keeping ONE base session before lo.

    An increment needs a prior session, so a window that starts at `lo` must be measured from the
    last session the book printed BEFORE it -- otherwise the first row of every cell silently
    drops and the cell measures a different thing than its label claims.
    """
    out = {}
    for s in syms:
        dates = sorted(per[s])
        keep = [d for d in dates if (lo is None or d >= lo) and (hi is None or d <= hi)]
        if lo is not None:
            before = [d for d in dates if d < lo]
            if before:
                base = before[-1]
                if base not in keep:
                    keep = [base] + keep
        if hi is not None:
            keep = [d for d in keep if d <= hi]
        out[s] = {d: per[s][d] for d in keep}
    return out


def _cell(per, syms, lo=None, hi=None, label="", kind="window", note=None, lag=NW_LAG):
    """Run the identified additivity design on one cell."""
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    cell = {"label": label, "kind": kind, "members": list(syms),
            "window_inclusive": [lo, hi], "note": note}
    if len(syms) < 3:
        cell.update({"decided": False,
                     "reason": "fewer than three members have a panel in this window"})
        return cell
    win = subset_per(per, syms, lo, hi)
    rows, panel = e240.common_increments(win, syms)
    dates = panel.get("dates") or []
    cell["sessions"] = len(dates)
    cell["first"] = dates[0] if dates else None
    cell["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        cell.update({"decided": False,
                     "reason": "common grid has %d sessions (floor %d)"
                               % (len(dates), MIN_SESSIONS)})
        return cell
    pv = e240.pair_one_vs_rest(panel, syms, lag)
    if pv.get("reason"):
        cell.update({"decided": False, "reason": pv["reason"],
                     "cases": pv.get("cases")})
        return cell

    pairs = [c for c in pv["cases"] if "diff" in c]
    # aggregator 1 (E240 convention): spread of the per-pair differences
    ci_spread = pv.get("diff_ci")
    # aggregator 2 (conservative): average per-pair HAC half-width, i.e. each pair's own error bar
    halves = [(c["diff_ci"][1] - c["diff_ci"][0]) / (2.0 * Z95)
              for c in pairs if c.get("diff_ci")]
    se_pair = sum(halves) / len(halves) if halves else None
    ci_pair = ([pv["mean_diff"] - Z95 * se_pair, pv["mean_diff"] + Z95 * se_pair]
               if se_pair else None)
    cons = _wider(ci_spread, ci_pair)

    # The additive claim is "the difference is zero" for EVERY counterparty, so a mean that
    # averages one real channel into nineteen nulls is not the test (E239 family: a mean over
    # heterogeneous cells reads as a number that no cell reports). Count the pairs whose own
    # interval excludes zero, and require unanimity for the additive reading.
    decisive = [c for c in pairs
                if c.get("diff_ci") and not (c["diff_ci"][0] <= 0.0 <= c["diff_ci"][1])]
    signs = set(1 if c["diff"] > 0 else -1 for c in decisive)
    frac = (len(decisive) / float(len(pairs))) if pairs else 0.0
    pair_verdict = _pair_verdict(decisive, signs, len(pairs))
    mean_verdict = _verdict(cons)
    half = (cons[1] - cons[0]) / 2.0 if cons else None
    hetero_limit = max(REJECT_MIN_PAIRS, int(0.25 * len(pairs)))
    if pair_verdict in ("rest_channel_exceeds_one_counterparty",
                        "rest_channel_below_one_counterparty"):
        # a coherent pair signal is evidence even when the mean interval is wide
        verdict = pair_verdict
    elif len(decisive) > hetero_limit:
        verdict = "unresolved_heterogeneous_pairs"
    elif half is not None and half > RESOLUTION_MAX:
        verdict = "unresolved_interval_too_wide"
    elif pair_verdict == "rest_channel_is_additive" \
            and mean_verdict == "rest_channel_is_additive":
        verdict = "rest_channel_is_additive"
    else:
        verdict = "unresolved_heterogeneous_pairs"

    cell.update({
        "decided": True,
        "pairs": pv["n_pairs"],
        "mean_b_one": pv["mean_b_one"],
        "mean_b_rest": pv["mean_b_rest3"],
        "mean_diff": pv["mean_diff"],
        "diff_ci_pairspread": ci_spread,
        "diff_ci_pairhac": ci_pair,
        "diff_ci_used": cons,
        "diff_ci_halfwidth": half,
        "resolution_max": RESOLUTION_MAX,
        "verdict": verdict,
        "verdict_by_pair_unanimity": pair_verdict,
        "verdict_by_mean_interval": mean_verdict,
        "pairs_excluding_zero": len(decisive),
        "pairs_excluding_zero_frac": frac,
        "pairs_excluding_zero_signs": sorted(signs),
        "aggregators_disagree": pair_verdict != mean_verdict,
        "uncertainty_methods_agree": _verdict(ci_spread) == _verdict(ci_pair),
        # the pooled aggregator is published but NOT used: see pooled_split_is_an_artifact
        "pooled_diff_not_evidence": (pv.get("pooled") or {}).get("diff"),
        "per_pair_diffs": [{"own_of": c["own_of"], "one_of": c["one_of"],
                            "diff": c["diff"], "ci": c["diff_ci"]} for c in pairs],
    })
    return cell


def _wider(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if (a[1] - a[0]) >= (b[1] - b[0]) else b


def _verdict(ci):
    """Three-way reading of a difference interval. 0 inside the interval = additive."""
    if not ci:
        return "unresolved_insufficient_rows"
    lo, hi = ci
    if lo <= 0.0 <= hi:
        return "rest_channel_is_additive"
    return "rest_channel_exceeds_one_counterparty" if lo > 0.0 \
        else "rest_channel_below_one_counterparty"


def _pair_verdict(decisive, signs, n_pairs):
    """Additivity is "every pair's difference is zero", so the pair set votes first.

    At a 95% interval over 20 pairs, one or two exclusions are the expected false positives, so
    only a COHERENT (same-signed) set of at least REJECT_MIN_PAIRS exclusions refutes equality.
    Mixed signs are noise and defer to the mean interval; the count is always published.
    """
    if not decisive:
        return "rest_channel_is_additive"
    if len(decisive) >= REJECT_MIN_PAIRS and len(signs) == 1:
        return ("rest_channel_exceeds_one_counterparty" if signs == {1}
                else "rest_channel_below_one_counterparty")
    if len(decisive) > max(REJECT_MIN_PAIRS, int(0.25 * n_pairs)):
        return "unresolved_heterogeneous_pairs"
    return "rest_channel_is_additive"


# ---------------------------------------------------------------- the pooled artifact
def _dates(n, start="2019-01-01"):
    """Real ISO session labels, so the era windows of the face apply to fixtures too."""
    d0 = datetime.strptime(start, "%Y-%m-%d")
    return [(d0.replace(year=d0.year) + _days(k)).strftime("%Y-%m-%d") for k in range(n)]


def _days(k):
    from datetime import timedelta
    return timedelta(days=k)


def synth(n=400, own=0.5, one=0.9, rest=0.02, members=5, seed=7, start="2019-01-01"):
    """A book with an EXPLICITLY asymmetric one-vs-rest channel.

    y_m = own*dl_m + one*dl_star + rest*sum_{o != m, star} dl_o

    With one=0.9 and rest=0.02 the truth differs by 0.88 between the two channels, so any
    aggregator that reads the difference must see ~0.88 on the pair whose counterparty is the
    star, and ~0 on the others.
    """
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(members)]
    star = syms[0]
    labels = _dates(n, start)
    lo = {s: 18.0 for s in syms}
    rows = {s: [] for s in syms}
    for t in range(n):
        dl = {s: rnd.gauss(0.0, 1.0) for s in syms}
        for s in syms:
            lo[s] += dl[s]
        for s in syms:
            others = [o for o in syms if o != s]
            y = own * dl[s] + one * dl[star] + rest * sum(dl[o] for o in others if o != star)
            rows[s].append((labels[t], y, lo[s]))
    return {s: {r[0]: (r[1], r[2]) for r in rows[s]} for s in syms}


def synth_switch(n=1200, own=0.5, one=0.2, rest_before=0.2, rest_after=0.02, members=5, seed=9,
                 switch_at=0.5, start="2019-01-01"):
    """Same book, but the rest channel pays differently before and after `switch_at`."""
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(members)]
    star = syms[0]
    cut = int(n * switch_at)
    labels = _dates(n, start)
    lo = {s: 18.0 for s in syms}
    rows = {s: [] for s in syms}
    for t in range(n):
        dl = {s: rnd.gauss(0.0, 1.0) for s in syms}
        for s in syms:
            lo[s] += dl[s]
        rest = rest_before if t < cut else rest_after
        for s in syms:
            others = [o for o in syms if o != s]
            y = own * dl[s] + one * dl[star] + rest * sum(dl[o] for o in others if o != star)
            rows[s].append((labels[t], y, lo[s]))
    return {s: {r[0]: (r[1], r[2]) for r in rows[s]} for s in syms}


def pooled_split_is_an_artifact(save_face=None):
    """Mechanical proof, re-run every time the face is built.

    The pooled stack replicates one member's response vector across its k-1 counterfactual
    "one counterparty" blocks.  The direction that separates b_one from b_rest3 is annihilated by
    that replication, so the solver returns the symmetric split and reports a difference of zero
    on ANY dataset -- including one whose truth differs by 0.88.  The per-pair aggregator, which
    does not replicate y, reads the gap.
    """
    out = {"scheme": "pooled replicates y_m across the k-1 one-counterparty blocks",
           "reason": "the b_one - b_rest3 direction is annihilated by the replication, so the "
                     "solver returns the symmetric split; a zero here is not agreement",
           "fixtures": []}
    for seed, (one, rest) in ((7, (0.9, 0.02)), (11, (0.05, 0.6)), (13, (0.3, 0.3))):
        per = synth(one=one, rest=rest, seed=seed)
        syms = list(per)
        _, panel = e240.common_increments(per, syms)
        pv = e240.pair_one_vs_rest(panel, syms)
        pooled = pv.get("pooled") or {}
        out["fixtures"].append({
            "seed": seed, "truth_one": one, "truth_rest": rest,
            "truth_gap": one - rest,
            "per_pair_diff": pv.get("mean_diff"),
            "per_pair_ci": pv.get("diff_ci"),
            "pooled_diff": pooled.get("diff"),
            "pooled_identifies": bool(pooled.get("diff") is not None
                                      and abs(pooled["diff"]) > 1e-9),
        })
    lows = [abs(f["pooled_diff"]) for f in out["fixtures"] if f["pooled_diff"] is not None]
    out["pooled_max_abs_diff_across_fixtures"] = max(lows) if lows else None
    out["pooled_identifies"] = bool(lows and max(lows) > 1e-9)
    out["per_pair_reads_the_gap"] = bool(
        any(f["per_pair_diff"] is not None and abs(f["per_pair_diff"]) > 1e-3
            for f in out["fixtures"]))
    out["conclusion"] = ("pooled aggregator identifies:false -- its zero difference is the "
                         "symmetric split of an annihilated direction, so it cannot vote on "
                         "additivity"
                         if not out["pooled_identifies"]
                         else "pooled aggregator separates the channels on these fixtures")
    if save_face is not None:
        save_face["pooled_split_is_an_artifact"] = out
    return out


# ---------------------------------------------------------------- verdict roll-up
def rollup(cells):
    counted = [c for c in cells if c.get("decided") and c.get("kind") != "degenerate"]
    verdicts = {c["label"]: c["verdict"] for c in counted}
    distinct = set(verdicts.values())
    additive = [lab for lab, v in verdicts.items() if v == "rest_channel_is_additive"]
    hetero = [lab for lab, v in verdicts.items() if v == "unresolved_heterogeneous_pairs"]
    too_wide = [lab for lab, v in verdicts.items() if v == "unresolved_interval_too_wide"]
    if not counted:
        overall = "unresolved_insufficient_rows"
    elif distinct == {"rest_channel_is_additive"}:
        overall = "rest_channel_is_additive"
    elif not additive and not hetero and len(too_wide) == len(counted):
        overall = "additivity_not_resolved_out_of_sample"
    elif not additive and not hetero:
        overall = "additivity_rejected_out_of_sample"
    elif len(hetero) >= max(1, len(counted) // 2) and len(additive) <= len(counted) // 4:
        # the mean interval covers zero somewhere, but the pair set disagrees in most cells:
        # the equality exists in the average, not between counterparties
        overall = "additivity_only_in_the_mean"
    elif not additive:
        overall = "additivity_rejected_out_of_sample"
    else:
        overall = "additivity_era_dependent"
    unstable_methods = [c["label"] for c in counted
                        if not c.get("uncertainty_methods_agree", True)]
    return {"cells_counted": len(counted),
            "cells_excluded_degenerate": len([c for c in cells
                                              if c.get("kind") == "degenerate"]),
            "verdicts_by_cell": verdicts,
            "additive_cells": additive,
            "heterogeneous_cells": hetero,
            "interval_too_wide_cells": too_wide,
            "non_additive_cells": [lab for lab, v in verdicts.items()
                                   if v != "rest_channel_is_additive"],
            "verdict": overall,
            "verdict_stable_across_cells": len(distinct) == 1,
            "verdict_unstable_under_uncertainty_method": unstable_methods,
            "additivity_is_era_dependent": overall == "additivity_era_dependent",
            "additivity_only_in_the_mean": overall == "additivity_only_in_the_mean",
            "headline_cell": "all_five",
            "headline_verdict": verdicts.get("all_five"),
            "headline_reproduced": bool(
                verdicts.get("all_five") is not None)}


def run(save=True, per=None, outdir=None, lag=NW_LAG, e240_ref=None, basket=None):
    outdir = outdir or OUTDIR
    per = per if per is not None else e239.panels(None)
    basket = BASKET if basket is None else basket
    allsyms = [s for s in basket if per.get(s)]
    if len(allsyms) < 4:
        return {"study": STUDY, "error": "fewer than four members have a panel"}

    pre2020 = [s for s in allsyms if min(per[s]) < PRE2020_END_BEFORE]
    cells = []
    cells.append(_cell(per, allsyms, None, None, label="all_five", kind="headline",
                       note="the E240 window; replay control"))
    cells.append(_cell(per, pre2020, None, PRE2020_END_BEFORE, label="pre2020_four",
                       kind="window",
                       note="the members that exist before sh588000 prints"))
    for label, lo, hi in ERAS:
        cells.append(_cell(per, allsyms, lo, hi, label=label, kind="era",
                           note="five-member era split"))
    for drop in allsyms:
        kept = [s for s in allsyms if s != drop]
        cells.append(_cell(per, kept, None, None, label="loo_drop_" + drop, kind="neighbour",
                           note="leave-one-member-out: the neighbourhood test"))
    cells.append(_cell(per, [s for s in EARLY_THREE if per.get(s)],
                       EARLY_THREE_FROM, EARLY_THREE_TO, label="early_three",
                       kind="degenerate",
                       note="k=3: 'the sum of the other three' degenerates to the one remaining "
                            "member, so the difference is not an aggregation reading -- "
                            "published, excluded from the stability verdict"))

    art = pooled_split_is_an_artifact()
    roll = rollup(cells)
    ref = e240_ref if e240_ref is not None else _e240_ref(outdir)
    replay = _replay(ref, cells)

    face = {
        "study": STUDY,
        "title": "does 'the rest channel adds up' survive outside the window that produced it?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": max((c.get("last") or "") for c in cells) or None,
        "frozen_spec": {
            "question": "E240's rest_channel_is_additive came from one window (1328 sessions "
                        "from 2020-11-17). Is it a mechanism or a property of that window?",
            "design": "y_m on (d log own_m, d log one counterparty, d log SUM of the other "
                      "k-2) -- one and the sum are in the same units and the additive world "
                      "predicts equality; no kappa and no 4x",
            "cells": "headline replay + pre-2020 four-member window + three five-member eras "
                     "+ five leave-one-member-out + one labelled k=3 degenerate cell",
            "uncertainty": "two aggregators per cell -- pair-spread (E240 convention) and the "
                           "average per-pair HAC half-width; the WIDER interval is used for the "
                           "verdict, and any disagreement is published",
            "pooled_aggregator": "published, not used: see pooled_split_is_an_artifact",
            "verdict_vocabulary": list(VERDICTS),
            "no_adoption": "this face re-prices nothing and adopts no arm",
        },
        "members": allsyms,
        "cells": cells,
        "rollup": roll,
        "pooled_split_is_an_artifact": art,
        "e240_reference": ref,
        "e240_replay": replay,
        "no_bill": {"permitted": False,
                    "reason": "the face tests a verdict's portability; any charge or "
                              "configuration change is a separate pre-registered act"},
    }
    face["summary"] = _summary(face)
    if save:
        _write(face, outdir)
    return face


def _e240_ref(outdir):
    p = os.path.join(outdir, "aggatt_latest.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
    except (ValueError, OSError):
        return None
    pv = (d.get("designs") or {}).get("pair_one_vs_rest") or {}
    return {"source": "results/state_tilt/aggatt_latest.json",
            "mean_b_one": pv.get("mean_b_one"),
            "mean_b_rest": pv.get("mean_b_rest3"),
            "mean_diff": pv.get("mean_diff"),
            "diff_ci": pv.get("diff_ci"),
            "pooled_diff": (pv.get("pooled") or {}).get("diff")}


def _replay(ref, cells):
    """The headline cell must be the E240 cell, not merely similar to it."""
    head = next((c for c in cells if c["label"] == "all_five"), None)
    out = {"cell": "all_five", "tolerance": 1e-9}
    if ref is None or (ref.get("mean_diff") is None and ref.get("mean_b_one") is None):
        out.update({"status": "no_reference", "reproduced": None})
        return out
    if not head or not head.get("decided"):
        out.update({"status": "headline_cell_not_decided", "reproduced": False})
        return out
    gaps = {}
    for key, mine in (("mean_b_one", head.get("mean_b_one")),
                      ("mean_diff", head.get("mean_diff"))):
        want = ref.get(key)
        gaps[key] = None if (want is None or mine is None) else abs(mine - want)
    out["gaps"] = gaps
    out["status"] = ("reproduced" if all(g is not None and g <= out["tolerance"]
                                        for g in gaps.values())
                     else "MISMATCH")
    out["reproduced"] = out["status"] == "reproduced"
    return out


def _summary(face):
    roll = face["rollup"]
    hl = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    return {"verdict": roll["verdict"],
            "headline_diff": hl.get("mean_diff"),
            "headline_ci": hl.get("diff_ci_used"),
            "headline_verdict": roll.get("headline_verdict"),
            "headline_reproduced": face["e240_replay"].get("reproduced"),
            "cells_counted": roll["cells_counted"],
            "additive_cells": roll["additive_cells"],
            "non_additive_cells": roll["non_additive_cells"],
            "verdict_stable_across_cells": roll["verdict_stable_across_cells"],
            "pooled_aggregator_identifies": face["pooled_split_is_an_artifact"].get(
                "pooled_identifies"),
            "one_line": _answer(face)}


def _answer(face):
    roll = face["rollup"]
    v = roll["verdict"]
    n = roll["cells_counted"]
    if v == "rest_channel_is_additive":
        return ("additive in every one of the %d counted cells -- the verdict is not a property "
                "of the 2020-11 window" % n)
    if v == "additivity_only_in_the_mean":
        return ("the difference averages to zero but %d of %d cells have counterparties whose "
                "own intervals disagree -- the equality lives in the mean, not between "
                "counterparties (E240's +/-0.017 was the spread of 20 heterogeneous pairs, not "
                "the precision of one difference)" % (len(roll["heterogeneous_cells"]), n))
    if v == "additivity_not_resolved_out_of_sample":
        return ("no cell resolves the difference: every interval is wider than +/-%.2f, so "
                "additivity is neither supported nor refuted outside E240's window"
                % RESOLUTION_MAX)
    if v == "additivity_era_dependent":
        return ("additive in %d of %d cells and not in %s -- the verdict is era dependent and "
                "must be published as such"
                % (len(roll["additive_cells"]), n,
                   ", ".join(roll["non_additive_cells"][:4])))
    if v == "additivity_rejected_out_of_sample":
        return ("the difference is non-zero in every one of the %d counted cells -- the E240 "
                "verdict does not survive its own neighbourhood" % n)
    return "no cell had enough rows to decide"


def _fmt(v, spec="%.4f"):
    return "n/a" if v is None else (spec % v)


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    cutoff = face.get("evidence_cutoff") or "unknown"
    name = "ADDOS-" + str(cutoff) + ".json"
    for fn in (name, "addos_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return name


# ---------------------------------------------------------------- selftest
def _run(per, lag=NW_LAG):
    """Fixtures carry their own member names, so the basket follows the panel."""
    return run(save=False, per=per, lag=lag, basket=sorted(per))


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def additive_face():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        face = _run(per)
        roll = face["rollup"]
        if roll["cells_counted"] < 3:
            raise AssertionError("only %d cells decided" % roll["cells_counted"])
        if roll["verdict"] != "rest_channel_is_additive":
            raise AssertionError("additive fixture read as %s" % roll["verdict"])

    def asymmetric_face_is_not_additive():
        per = synth(n=900, own=0.5, one=0.9, rest=0.02, seed=7)
        face = _run(per)
        hl = next(c for c in face["cells"] if c["label"] == "all_five")
        if hl["verdict"] == "rest_channel_is_additive":
            raise AssertionError("a 0.88 truth gap read as additive")
        if face["rollup"]["verdict"] == "rest_channel_is_additive":
            raise AssertionError("rollup washed out a real gap")

    def pooled_never_sees_the_gap():
        """Pinned: the pooled aggregator reports ~0 on every fixture, so it is not evidence."""
        art = pooled_split_is_an_artifact()
        worst = art["pooled_max_abs_diff_across_fixtures"]
        if worst is None:
            raise AssertionError("no pooled reading was produced")
        if worst > 1e-9:
            raise AssertionError("pooled diff moved (%.3g) -- the artifact gate would now be "
                                 "wrong" % worst)
        if art["pooled_identifies"]:
            raise AssertionError("pooled claimed identification it cannot have")
        if not art["per_pair_reads_the_gap"]:
            raise AssertionError("the pair aggregator missed a 0.88 gap too -- fixtures are wrong")

    def era_switch_is_caught():
        """A channel weight that changes on a date must surface as unstable, not as one verdict."""
        per = synth_switch(n=1400, own=0.5, one=0.2, rest_before=0.2, rest_after=0.02, seed=9,
                           switch_at=0.5)
        face = _run(per)
        if face["rollup"]["cells_counted"] < 3:
            raise AssertionError("era fixtures produced too few cells")
        if face["rollup"]["verdict_stable_across_cells"]:
            raise AssertionError("a channel weight that moves on a date was reported as a "
                                 "single stable verdict (%s)" % face["rollup"]["verdict"])
        if face["rollup"]["verdict"] == "rest_channel_is_additive":
            raise AssertionError("the rollup washed out a channel weight change")

    def split_cells_keep_the_era_label():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        face = _run(per)
        eras = [c for c in face["cells"] if c["kind"] == "era" and c.get("decided")]
        if not eras:
            raise AssertionError("no era cell decided")
        for c in eras:
            lo, hi = c["window_inclusive"]
            if c["first"] is None or not (lo <= c["first"] <= hi):
                # the kept base session may sit one row before lo; the row dates are increments
                raise AssertionError("cell %s first row %s outside %s..%s"
                                     % (c["label"], c["first"], lo, hi))

    def leave_one_out_shape():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        face = _run(per)
        loos = [c for c in face["cells"] if c["kind"] == "neighbour"]
        if len(loos) != len(face["members"]):
            raise AssertionError("%d leave-one-out cells for %d members"
                                 % (len(loos), len(face["members"])))
        for c in loos:
            if c.get("decided"):
                k = len(c["members"])
                if c["pairs"] != k * (k - 1):
                    raise AssertionError("cell %s has %d pairs for %d members (expected %d)"
                                         % (c["label"], c["pairs"], k, k * (k - 1)))
            if len(c["members"]) != len(face["members"]) - 1:
                raise AssertionError("cell %s dropped the wrong number of members" % c["label"])

    def insufficient_rows_is_not_additive():
        per = synth(n=120, own=0.5, one=0.2, rest=0.2, seed=5)
        face = _run(per)
        if face["rollup"]["verdict"] != "unresolved_insufficient_rows":
            raise AssertionError("a 119-session grid decided '%s'"
                                 % face["rollup"]["verdict"])
        for c in face["cells"]:
            if c.get("decided"):
                raise AssertionError("cell %s decided on a short grid" % c["label"])

    def conservative_interval_wins():
        per = synth(n=900, own=0.5, one=0.9, rest=0.02, seed=7)
        face = _run(per)
        for c in face["cells"]:
            if not c.get("decided"):
                continue
            a, b, used = c["diff_ci_pairspread"], c["diff_ci_pairhac"], c["diff_ci_used"]
            if used is None:
                raise AssertionError("cell %s has no interval" % c["label"])
            widths = [w for w in ((a[1] - a[0]) if a else None, (b[1] - b[0]) if b else None)
                      if w is not None]
            if abs((used[1] - used[0]) - max(widths)) > 1e-12:
                raise AssertionError("cell %s used the narrower interval" % c["label"])

    def degenerate_cell_is_excluded():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        face = _run(per)
        deg = [c for c in face["cells"] if c["kind"] == "degenerate"]
        if not deg:
            raise AssertionError("no degenerate cell was published")
        if face["rollup"]["cells_counted"] != len([c for c in face["cells"]
                                                   if c.get("decided")
                                                   and c["kind"] != "degenerate"]):
            raise AssertionError("rollup counted a non-decided or degenerate cell")

    def missing_reference_does_not_crash():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        face = run(save=False, per=per, e240_ref={}, basket=sorted(per))
        rep = face["e240_replay"]
        if rep.get("status") != "no_reference" or rep.get("reproduced") is not None:
            raise AssertionError("an empty reference face was not reported as no_reference")

    def subset_keeps_one_base_session():
        per = {"a": {"d1": (1.0, 10.0), "d2": (1.1, 10.1), "d3": (1.2, 10.3)},
               "b": {"d1": (1.0, 10.0), "d2": (1.3, 10.2), "d3": (1.1, 10.4)},
               "c": {"d1": (1.0, 10.0), "d2": (0.9, 9.9), "d3": (1.4, 10.5)}}
        win = subset_per(per, list(per), "d2", "d3")
        for s in win:
            if "d1" not in win[s]:
                raise AssertionError("the base session before the window was dropped for %s" % s)
        if len(win["a"]) != 3:
            raise AssertionError("window kept %d rows" % len(win["a"]))

    def replay_gate_rejects_a_different_face():
        per = synth(n=900, own=0.5, one=0.2, rest=0.2, seed=5)
        wrong = {"mean_b_one": 99.0, "mean_diff": 99.0}
        face = run(save=False, per=per, e240_ref=wrong, basket=sorted(per))
        if face["e240_replay"]["reproduced"]:
            raise AssertionError("the replay gate accepted a face it did not reproduce")

    def wide_interval_is_not_assessed():
        """A cell whose interval is wider than the resolution line must NOT read as additive."""
        per = synth(n=260, own=0.5, one=0.2, rest=0.2, seed=5, start="2020-01-01")
        face = _run(per)
        decided = [c for c in face["cells"] if c.get("decided")]
        if not decided:
            raise AssertionError("no cell decided on a 259-session grid")
        wide = [c for c in decided if c["diff_ci_halfwidth"] > RESOLUTION_MAX]
        if not wide:
            raise AssertionError("no wide-interval cell was produced; the gate would be untested")
        for c in wide:
            if c["verdict"] == "rest_channel_is_additive":
                raise AssertionError("cell %s has half-width %.3f and still read as additive"
                                     % (c["label"], c["diff_ci_halfwidth"]))

    def rollup_names_the_mean_only_case():
        counts = {"a": "unresolved_heterogeneous_pairs",
                  "b": "unresolved_heterogeneous_pairs",
                  "c": "unresolved_interval_too_wide",
                  "d": "rest_channel_is_additive"}
        cells = [{"label": k, "verdict": v, "decided": True, "kind": "window"}
                 for k, v in counts.items()]
        r = rollup(cells)
        if r["verdict"] != "additivity_only_in_the_mean":
            raise AssertionError("rollup labelled the mean-only case '%s'" % r["verdict"])
        cells2 = [{"label": k, "verdict": "unresolved_interval_too_wide", "decided": True,
                   "kind": "window"} for k in "ab"]
        if rollup(cells2)["verdict"] != "additivity_not_resolved_out_of_sample":
            raise AssertionError("all-wide cells were not reported as not-resolved")

    for name, fn in (("additive fixture -> additive everywhere", additive_face),
                     ("asymmetric fixture -> not additive", asymmetric_face_is_not_additive),
                     ("pooled aggregator cannot see the gap", pooled_never_sees_the_gap),
                     ("era switch is caught", era_switch_is_caught),
                     ("era cells keep their window", split_cells_keep_the_era_label),
                     ("leave-one-out shape", leave_one_out_shape),
                     ("short grid is unresolved, not additive", insufficient_rows_is_not_additive),
                     ("conservative interval wins", conservative_interval_wins),
                     ("degenerate cell excluded from rollup", degenerate_cell_is_excluded),
                     ("missing E240 face does not crash", missing_reference_does_not_crash),
                     ("window keeps one base session", subset_keeps_one_base_session),
                     ("replay gate rejects a foreign face", replay_gate_rejects_a_different_face),
                     ("wide interval is NOT-ASSESSED", wide_interval_is_not_assessed),
                     ("rollup names the mean-only case", rollup_names_the_mean_only_case)):
        leg(name, fn)

    passed = sum(1 for _, ok, _ in legs if ok)
    print("E243 additivity-out-of-sample selftest")
    for name, ok, why in legs:
        print("  %-46s %s%s" % (name, "PASS" if ok else "FAIL",
                                "" if ok else "  <- " + why))
    print("Summary: %d/%d" % (passed, len(legs)))
    return passed == len(legs)


def main(argv=None):
    ap = argparse.ArgumentParser(description="E243 additivity out of sample")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest", "artifact"))
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return 0 if selftest() else 1
    if args.cmd == "artifact":
        print(json.dumps(pooled_split_is_an_artifact(), ensure_ascii=False, indent=1))
        return 0
    face = run(outdir=args.outdir)
    if not face or face.get("error"):
        print(face)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
