"""E228 -- does the state tilt survive an EXPOSURE-MATCHED null?

E225 published a drift split: a gated arm inherits the null arm's out-of-sample drift
in proportion to its average exposure, and `gate_specific = excess - avg_weight * null_ann`
was read as what the gate itself earned or lost. E226 then showed that split can hand a
rule that earned nothing a positive residual -- on the equal-weight basket `binary_low`
carried +340 bp/yr of gate-specific residual beside +1.8 bp/yr of actual excess.

The reason is structural, not arithmetic: an attributed share of the null's drift is not
a benchmark. A benchmark has to be a TRADED ARM, charged the same toll, so that the
difference between the two is the timing itself and nothing else. This face builds it:

  * matched null (per gated arm, per panel): a flat arm held at the gated arm's own
    average weight, under exactly E225's accounting (weight decided at the close of t,
    applied to t+1, unit turnover pays one side, w_{-1} = 0 so entry pays a side).
    Two constants are published because they answer two different questions:
      - `is`   the in-sample average weight, frozen at the split. This is the only
               causally legitimate benchmark: it uses nothing after the split.
      - `oos`  the average weight actually held out of sample. This is an EXACT
               exposure match but it looks at the answer, so it is a diagnostic
               bound, not a tradable arm.
  * the measurement is the PAIRED daily difference d_t = excess_gated(t) - excess_matched(t).
    The drift term cancels inside the pair (both arms are charged the same mu_is), so the
    series is the timing value plus the extra toll the gate paid. That is why the paired
    series has a usable standard error while the published residual had none at all.
  * t is Newey-West with lag 20 on the paired series; the i.i.d. t and the effective
    sample size are printed beside it. The bar is Bonferroni over gated arms x panels.
  * decision rule: TIMING_SURVIVES iff the paired OOS excess per year > 0 AND its NW t
    clears the bar AND it stays positive at x2 costs. TIMING_DEAD if the pair is negative
    or the t misses. UNRESOLVED below 252 OOS sessions.
  * the face also publishes, per arm, how far the E225 attribution sat from this benchmark
    (`attribution_minus_paired_bp`) and how many arms change SIGN between the two ways of
    asking the question -- that count is the actual deliverable of the card.

Everything above is frozen in this docstring and in the module constants before any
number was read.
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
import e224_vol_gate as e224  # noqa: E402
import e225_state_tilt as e225  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
E225_FACE = os.path.join(OUTDIR, "latest.json")
E226_FACE = os.path.join(OUTDIR, "latest.json")

COST_SIDE_BP = e225.COST_SIDE_BP
COST_X2_MULT = e225.COST_X2_MULT
IS_FRAC = e225.IS_FRAC
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
NW_LAG = e225.NW_LAG
Z_80 = e225.Z_80
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

ARMS = e225.ARMS
GATED_ARMS = [a for a in ARMS if a != "always_on"]


# ---------------------------------------------------------------- accounting rows
def rows_for(weights, ret_bp, split, cost_side_bp):
    """E225's per-decision rows, returned verbatim so two arms share one index set.

    Kept deliberately identical to e225.tilt_stats: cost is charged on |dw| with
    w_{-1} = 0 and a None return skips the row while still carrying the weight
    forward. The selftest pins that the annualised excess built from these rows
    equals what e225.tilt_stats publishes for the same weights.
    """
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        cost = abs(dw) * cost_side_bp
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append({"i": i, "w": w, "abs_dw": abs(dw), "gross_bp": w * r,
                     "cost_bp": cost, "excess_bp": w * r - cost - w * mu_is})
        prev_w = w
    return rows, mu_is


def _ann(mean_bp):
    return None if mean_bp is None else mean_bp * SESSIONS_PER_YEAR


def _pair_stats(delta, rows, mu_is, cost_side_bp):
    """Summary of the paired daily difference series over the out-of-sample window."""
    if not delta:
        return {"n": 0, "mean_bp": None, "ann_bp_per_year": None, "t_nw": None}
    m = e225._mean(delta)
    sd = e225._sd(delta)
    se_iid = (sd / (len(delta) ** 0.5)) if (sd is not None and delta) else None
    se_nw = e225._hac_se(delta, NW_LAG) if len(delta) >= 3 else None
    return {
        "n": len(delta),
        "mean_bp": m,
        "ann_bp_per_year": _ann(m),
        "sd_bp": sd,
        "se_iid": se_iid,
        "se_nw": se_nw,
        "t_nw": (m / se_nw) if (se_nw and m is not None) else None,
        "t_iid": (m / se_iid) if (se_iid and m is not None) else None,
        "n_eff": e225._n_eff(delta) if len(delta) >= 3 else None,
        "mde_ann_bp_per_year": (Z_80 * se_nw * SESSIONS_PER_YEAR) if se_nw else None,
    }


def _avg_weight(rows, split, which):
    cut = split - 1
    if which == "oos":
        sel = [r["w"] for r in rows if r["i"] >= cut]
    elif which == "is":
        sel = [r["w"] for r in rows if r["i"] < cut]
    elif which == "full":
        sel = [r["w"] for r in rows]
    else:
        raise ValueError("unknown window: %r" % (which,))
    return e225._mean(sel) if sel else None


def _sign(x, eps=0.0):
    if x is None:
        return None
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0


def arm_pair(weights, ret_bp, split, cost_side_bp, bar_t):
    """One gated arm against its own exposure-matched null, at one cost level."""
    gated_rows, mu_is = rows_for(weights, ret_bp, split, cost_side_bp)
    cut = split - 1
    out = {"mu_is_bp_per_day": mu_is, "matched": {}}

    for which in ("is", "oos", "full"):
        c = _avg_weight(gated_rows, split, which)
        if c is None:
            out["matched"][which] = None
            continue
        m_rows, m_mu = rows_for([c] * len(ret_bp), ret_bp, split, cost_side_bp)
        assert m_mu == mu_is, "matched null must share the in-sample drift"
        g_oos = [r for r in gated_rows if r["i"] >= cut]
        m_oos = [r for r in m_rows if r["i"] >= cut]
        gi = [r["i"] for r in g_oos]
        mi = [r["i"] for r in m_oos]
        assert gi == mi, "gated and matched rows must cover the same decision sessions"
        delta = [g["excess_bp"] - m["excess_bp"] for g, m in zip(g_oos, m_oos)]
        stats = _pair_stats(delta, g_oos, mu_is, cost_side_bp)
        out["matched"][which] = {
            "const_weight": c,
            "turnover_total": sum(r["abs_dw"] for r in m_rows),
            # The entry side is charged on the first decision session that HAS a
            # return. On the basket panel the first session's return is missing, so
            # the flat arm's entry lands on a skipped row and its whole-run turnover
            # is 0.0 -- the same thing happens to the gated arm there, so the pair
            # stays comparable, but the difference must be published rather than
            # left for a reader to trip over.
            "entry_charged": abs(sum(r["abs_dw"] for r in m_rows) - c) < 1e-12,
            "cost_bp_per_year_oos": (_ann(e225._mean([r["cost_bp"] for r in m_oos]))
                                     if m_oos else None),
            "excess_oos_bp_per_year": (_ann(e225._mean([r["excess_bp"] for r in m_oos]))
                                       if m_oos else None),
            "paired": stats,
        }

    g_oos = [r for r in gated_rows if r["i"] >= cut]
    out["gated"] = {
        "oos_decisions": len(g_oos),
        "avg_weight_oos": _avg_weight(gated_rows, split, "oos"),
        "turnover_total": sum(r["abs_dw"] for r in gated_rows),
        "turnover_per_year": (sum(r["abs_dw"] for r in gated_rows)
                              / (len(ret_bp) / float(SESSIONS_PER_YEAR))),
        "cost_bp_per_year_oos": (_ann(e225._mean([r["cost_bp"] for r in g_oos]))
                                 if g_oos else None),
        "gross_bp_per_year_oos": (_ann(e225._mean([r["gross_bp"] for r in g_oos]))
                                  if g_oos else None),
        "excess_oos_bp_per_year": (_ann(e225._mean([r["excess_bp"] for r in g_oos]))
                                   if g_oos else None),
    }
    out["bar_t"] = bar_t
    return out


def pair_verdict(arm_out, bar_t, x2=None, min_oos=MIN_OOS_SESSIONS):
    """Judge the PAIR (gated minus matched), never the raw gated level."""
    ref = (arm_out.get("matched") or {}).get("oos") or {}
    p = ref.get("paired") or {}
    if (arm_out["gated"].get("oos_decisions") or 0) < min_oos:
        return "UNRESOLVED", "oos_sessions_%d_below_%d" % (
            arm_out["gated"].get("oos_decisions") or 0, min_oos)
    if p.get("ann_bp_per_year") is None or p.get("t_nw") is None:
        return "UNRESOLVED", "paired_series_unusable"
    if p["ann_bp_per_year"] <= 0:
        return "TIMING_DEAD", "paired_ann_not_positive"
    if p["t_nw"] < bar_t:
        return "TIMING_DEAD", "paired_t_%.2f_below_bar_%.2f" % (p["t_nw"], bar_t)
    if x2 is not None:
        p2 = ((x2.get("matched") or {}).get("oos") or {}).get("paired") or {}
        if p2.get("ann_bp_per_year") is None or p2["ann_bp_per_year"] <= 0:
            return "TIMING_DEAD", "dies_at_x2_costs"
    return "TIMING_SURVIVES", "clears_rule"


def attribution(gated_ann, avg_weight_oos, null_ann):
    """E225's drift split, reproduced here so the two benchmarks can be compared."""
    if gated_ann is None or null_ann is None or avg_weight_oos is None:
        return None, None
    comp = avg_weight_oos * null_ann
    return comp, gated_ann - comp


# ---------------------------------------------------------------- reference faces
def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _e225_crosscheck(face):
    ref = _load(E225_FACE)
    if not ref or not face.get("panels"):
        return None
    try:
        ref_panels = {p["panel"]: {a["name"]: a for a in p["arms"]}
                      for p in ref["panels"]}
    except (KeyError, TypeError):
        return None
    rows = []
    drift = 0.0
    for panel in face["panels"]:
        ours = {a["name"]: a for a in panel["arms"]}
        for name, a in ours.items():
            theirs = (ref_panels.get(panel["panel"]) or {}).get(name)
            if not theirs:
                continue
            g = a["gated"]["excess_oos_bp_per_year"]
            t = theirs.get("excess_oos_bp_per_year")
            if g is None or t is None:
                continue
            d = abs(g - t)
            drift = max(drift, d)
            rows.append({"panel": panel["panel"], "arm": name,
                         "rebuilt_bp_per_year": g, "published_bp_per_year": t,
                         "abs_diff_bp": d})
    return {"source": os.path.relpath(E225_FACE, ROOT).replace("\\", "/"),
            "study": ref.get("study"),
            "cells": len(rows),
            "max_abs_diff_bp": drift,
            "rows": rows}


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    n_tests = len(GATED_ARMS) * (2 if basket else 1)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

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
        panel["split_session"] = split
        panel["split_date"] = dates[split]
        panel["is_frac"] = IS_FRAC

        arms_out = []
        null_w = e225.weights_series(sig, "always_on")
        null_rows, null_mu = rows_for(null_w, ret_bp, split, COST_SIDE_BP)
        cut = split - 1
        null_oos = [r for r in null_rows if r["i"] >= cut]
        null_ann = _ann(e225._mean([r["excess_bp"] for r in null_oos])) if null_oos else None
        panel["null_arm_oos_excess_bp_per_year"] = null_ann

        for arm in GATED_ARMS:
            target = e225.arm_target(sig, split, arm)
            w = e225.weights_series(sig, arm, target)
            a = arm_pair(w, ret_bp, split, COST_SIDE_BP, bar_t)
            a_x2 = arm_pair(w, ret_bp, split, COST_SIDE_BP * COST_X2_MULT, bar_t)
            a["name"] = arm
            a["target_bp"] = target
            oos_pair = ((a["matched"] or {}).get("oos") or {}).get("paired") or {}
            x2_pair = (((a_x2.get("matched") or {}).get("oos") or {}).get("paired")) or {}
            a["paired_ann_bp_per_year_x2"] = x2_pair.get("ann_bp_per_year")
            a["verdict"], a["verdict_reason"] = pair_verdict(a, bar_t, x2=a_x2)

            comp, gate_specific = attribution(a["gated"]["excess_oos_bp_per_year"],
                                              a["gated"]["avg_weight_oos"], null_ann)
            a["e225_attribution"] = {
                "market_drift_component_bp_per_year": comp,
                "gate_specific_bp_per_year": gate_specific,
            }
            pair_ann = oos_pair.get("ann_bp_per_year")
            a["benchmark_comparison"] = {
                "attribution_bp_per_year": gate_specific,
                "paired_vs_matched_oos_bp_per_year": pair_ann,
                "attribution_minus_paired_bp": (gate_specific - pair_ann
                                                if (gate_specific is not None and pair_ann is not None)
                                                else None),
                "attribution_sign": _sign(gate_specific, 1.0),
                "paired_sign": _sign(pair_ann, 1.0),
                "sign_changed": (gate_specific is not None and pair_ann is not None
                                 and _sign(gate_specific, 1.0) != _sign(pair_ann, 1.0)),
                "paired_is_behind_matched_is_bp_per_year":
                    (((a["matched"] or {}).get("is") or {}).get("paired") or {}).get("ann_bp_per_year"),
            }
            arms_out.append(a)
        panel["arms"] = arms_out

    face = {
        "study": "E228",
        "title": "does the state tilt survive an exposure-matched null? a traded flat arm "
                 "at the gated arm's own average weight, judged on the paired daily series",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "gated_arms": GATED_ARMS,
            "matched_null": "flat arm at the gated arm's average weight, same toll, same mu_is",
            "matched_constants": ["is (primary, causal)", "oos (exact match, diagnostic)",
                                  "full"],
            "cost_side_bp": COST_SIDE_BP,
            "cost_model": "unit turnover |dw| pays one side; w_{-1}=0 so entry pays a side",
            "is_frac": IS_FRAC,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "nw_lag": NW_LAG,
            "z_80pct": Z_80,
            "bar_t": bar_t,
            "tests": n_tests,
            "bar_basis": "two-sided 5%% over %d tests (%d gated arms x %d panels)"
                         % (n_tests, len(GATED_ARMS), len(panels)),
            "measurement": "paired daily difference excess_gated - excess_matched",
            "decision_rule": "TIMING_SURVIVES iff paired OOS ann > 0 and paired NW t >= bar "
                             "and still positive at x2 costs",
        },
        "panels": panels,
    }

    chk = _e225_crosscheck(face)
    if chk:
        face["e225_crosscheck"] = chk

    # ------------------------------------------------ the deliverable: benchmark agreement
    flip_rows = []
    gaps = []
    for panel in panels:
        for a in panel["arms"]:
            bc = a["benchmark_comparison"]
            if bc["attribution_minus_paired_bp"] is not None:
                gaps.append(abs(bc["attribution_minus_paired_bp"]))
            flip_rows.append({"panel": panel["panel"], "arm": a["name"],
                              "attribution_bp_per_year": bc["attribution_bp_per_year"],
                              "paired_bp_per_year": bc["paired_vs_matched_oos_bp_per_year"],
                              "sign_changed": bc["sign_changed"],
                              "paired_t": (((a["matched"] or {}).get("oos") or {})
                                           .get("paired") or {}).get("t_nw")})
    survived = [{"panel": p["panel"], "arm": a["name"]}
                for p in panels for a in p["arms"] if a["verdict"] == "TIMING_SURVIVES"]
    face["benchmark_agreement"] = {
        "reading": "the E225 drift split is an attribution, not a benchmark; here both are "
                   "priced on the same toll and the same drift, so the difference is what "
                   "the attribution left out -- the matched arm's own toll",
        "arms": flip_rows,
        "sign_changes": sum(1 for r in flip_rows if r["sign_changed"]),
        "cells": len(flip_rows),
        "max_abs_gap_bp_per_year": (max(gaps) if gaps else None),
        "median_abs_gap_bp_per_year": (e225._median(gaps) if gaps else None),
        "identity": "attribution - pair == -(matched arm's own OOS toll); a constant weight "
                    "trades only at entry, so that toll is exactly zero and the two "
                    "benchmarks are one number. The split was never biased -- it was "
                    "undetermined, and the pair supplies its standard error.",
    }

    primary = panels[0]["arms"]
    best = None
    for a in primary:
        p = ((a["matched"] or {}).get("oos") or {}).get("paired") or {}
        if p.get("ann_bp_per_year") is None:
            continue
        if best is None or p["ann_bp_per_year"] > best[1]["ann_bp_per_year"]:
            best = (a["name"], p)
    pair_t_best = best[1]["t_nw"] if best else None
    face["answer"] = (
        "exposure for exposure the tilt is %s bp/yr at t=%s, against a bar of %.2f: %d of %d "
        "gated cells survive. The E225 drift split and this traded benchmark agree to within "
        "%s bp/yr on %d of %d cells (%d sign changes), so the attribution was not biased -- "
        "what it lacked was a standard error, and the paired series supplies one. The reason "
        "the split could still hand a losing rule a positive residual is visible in the "
        "constants: the matched arm sits at the gate's own average weight, so it inherits the "
        "same drift the gate was charged for, and only the TIMING term separates them."
        % (("%.0f" % best[1]["ann_bp_per_year"]) if best else "-",
           ("%.2f" % pair_t_best) if pair_t_best is not None else "-",
           bar_t, len(survived), sum(len(p["arms"]) for p in panels),
           ("%.0f" % face["benchmark_agreement"]["max_abs_gap_bp_per_year"])
           if face["benchmark_agreement"]["max_abs_gap_bp_per_year"] is not None else "-",
           sum(1 for r in flip_rows if not r["sign_changed"]),
           face["benchmark_agreement"]["cells"],
           face["benchmark_agreement"]["sign_changes"]))

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "MATCHED-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "matched_latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "name", "oos_decisions", "avg_weight_oos", "turnover_per_year",
                "gated_excess_oos_bp_per_year", "matched_is_ann_bp_per_year",
                "matched_oos_ann_bp_per_year", "paired_ann_bp_per_year",
                "paired_ann_bp_per_year_x2", "paired_t_nw", "paired_t_iid", "paired_n_eff",
                "paired_mde_ann_bp_per_year", "attribution_bp_per_year",
                "attribution_minus_paired_bp", "sign_changed", "verdict",
                "verdict_reason"]
        assert len(cols) == 19, "column list length drift"
        csv_path = os.path.join(outdir, "matched_by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    mo = (a["matched"] or {}).get("oos") or {}
                    mi = (a["matched"] or {}).get("is") or {}
                    p = mo.get("paired") or {}
                    bc = a["benchmark_comparison"]
                    w.writerow({
                        "panel": panel["panel"], "name": a["name"],
                        "oos_decisions": a["gated"]["oos_decisions"],
                        "avg_weight_oos": a["gated"]["avg_weight_oos"],
                        "turnover_per_year": a["gated"]["turnover_per_year"],
                        "gated_excess_oos_bp_per_year": a["gated"]["excess_oos_bp_per_year"],
                        "matched_is_ann_bp_per_year": mi.get("excess_oos_bp_per_year"),
                        "matched_oos_ann_bp_per_year": mo.get("excess_oos_bp_per_year"),
                        "paired_ann_bp_per_year": p.get("ann_bp_per_year"),
                        "paired_ann_bp_per_year_x2": a["paired_ann_bp_per_year_x2"],
                        "paired_t_nw": p.get("t_nw"),
                        "paired_t_iid": p.get("t_iid"),
                        "paired_n_eff": p.get("n_eff"),
                        "paired_mde_ann_bp_per_year": p.get("mde_ann_bp_per_year"),
                        "attribution_bp_per_year": bc["attribution_bp_per_year"],
                        "attribution_minus_paired_bp": bc["attribution_minus_paired_bp"],
                        "sign_changed": bc["sign_changed"],
                        "verdict": a["verdict"], "verdict_reason": a["verdict_reason"],
                    })
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, vol_cycle=None, seed=7):
    return e225._synth(n, drift_bp, vol_cycle, seed)


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    dates, ret = _synth(900)
    sig = e225.vol_signal(ret)
    split = e225.split_index(len(dates))

    # L1 the rebuilt rows reproduce the published annualised excess exactly
    w = e225.weights_series(sig, "binary_low")
    st = e225.tilt_stats(w, ret, split, COST_SIDE_BP, 2.5)
    rows, mu_is = rows_for(w, ret, split, COST_SIDE_BP)
    cut = split - 1
    oos = [r for r in rows if r["i"] >= cut]
    rebuilt = e225._mean([r["excess_bp"] for r in oos]) * SESSIONS_PER_YEAR
    leg("rows_reproduce_e225_excess", st["excess_oos_bp_per_year"] is not None
        and abs(rebuilt - st["excess_oos_bp_per_year"]) < 1e-9,
        "rebuilt %.9f vs published %.9f" % (rebuilt, st["excess_oos_bp_per_year"]))

    # L2 the matched arm's turnover can only be its own constant (one entry side) or
    # zero when that entry lands on a session with no return -- never more
    pair = arm_pair(w, ret, split, COST_SIDE_BP, 2.5)
    mo = pair["matched"]["oos"]
    leg("matched_arm_pays_entry_only",
        mo["turnover_total"] <= mo["const_weight"] + 1e-12
        and mo["cost_bp_per_year_oos"] == 0.0,
        "turnover %.6f <= const weight %.6f, OOS toll exactly 0"
        % (mo["turnover_total"], mo["const_weight"]))

    # L2b an entry that lands on a session with no return is never charged -- it is
    # not a free trade, it is an unmeasured one, so the face publishes entry_charged
    _, ret_gap = _synth(400)
    ret_gap[1] = None
    sg = e225.vol_signal(ret_gap)
    p_gap = arm_pair(e225.weights_series(sg, "binary_low"), ret_gap, 250, COST_SIDE_BP, 2.5)
    mgap = p_gap["matched"]["oos"]
    leg("gap_session_entry_is_disclosed_not_charged",
        mgap["turnover_total"] == 0.0 and mgap["entry_charged"] is False,
        "turnover 0.0 with entry_charged False, const %.4f" % mgap["const_weight"])

    # L3 a constant-weight gate has no timing: the pair is exactly zero
    c = 0.4
    flat_pair = arm_pair([c] * len(ret), ret, split, COST_SIDE_BP, 2.5)
    p0 = flat_pair["matched"]["oos"]["paired"]
    leg("constant_gate_has_zero_timing", p0["ann_bp_per_year"] is not None
        and abs(p0["ann_bp_per_year"]) < 1e-9,
        "paired ann %.3e" % (p0["ann_bp_per_year"] or 0.0))

    # L4 a uniform shift of every return cancels in BOTH arms, because each is
    # measured against the same in-sample drift: the excess series is not a
    # function of the return level
    k = 5.0
    ret_k = [None if r is None else r + k for r in ret]
    pair_k = arm_pair(w, ret_k, split, COST_SIDE_BP, 2.5)
    a0 = mo["paired"]["ann_bp_per_year"]
    a1 = pair_k["matched"]["oos"]["paired"]["ann_bp_per_year"]
    leg("uniform_drift_shift_cancels_in_both_arms",
        a0 is not None and a1 is not None and abs(a0 - a1) < 1e-9
        and abs(pair_k["gated"]["excess_oos_bp_per_year"]
                - pair["gated"]["excess_oos_bp_per_year"]) < 1e-9,
        "pair %.9f vs %.9f, level unchanged under +%.1fbp/day" % (a0 or 0.0, a1 or 0.0, k))

    # L5 the exposure match is what makes the pair blind to out-of-sample drift: a
    # shift applied ONLY after the split leaves the oos-matched pair untouched
    # (mean(w_t - c_oos) == 0 by construction) while both levels move by their own
    # exposure
    k2 = 5.0
    ret_oos = list(ret)
    for i in range(split, len(ret_oos)):
        if ret_oos[i] is not None:
            ret_oos[i] = ret_oos[i] + k2
    pair_o = arm_pair(w, ret_oos, split, COST_SIDE_BP, 2.5)
    po = pair_o["matched"]["oos"]["paired"]["ann_bp_per_year"]
    leg("oos_drift_shift_cancels_in_the_matched_pair",
        po is not None and abs(po - a0) < 1e-9,
        "%.9f vs %.9f under +%.1fbp/day after the split" % (po or 0.0, a0 or 0.0, k2))

    # L6 ... and the IS-frozen constant leaves exactly the residue the exposure
    # mismatch predicts, which is why the two constants answer different questions
    pi = pair_o["matched"]["is"]["paired"]["ann_bp_per_year"]
    pi0 = pair["matched"]["is"]["paired"]["ann_bp_per_year"]
    want = k2 * (pair["gated"]["avg_weight_oos"]
                 - pair["matched"]["is"]["const_weight"]) * SESSIONS_PER_YEAR
    leg("is_constant_leaves_the_predicted_drift_residue",
        pi is not None and pi0 is not None and abs((pi - pi0) - want) < 1e-6,
        "residue %.6f vs predicted %.6f" % ((pi - pi0) if pi is not None else 0.0, want))

    # L7 the levels themselves DO move under that shift, so the invariance belongs
    # to the pair and not to the arms
    leg("arm_levels_move_under_oos_drift",
        abs(pair_o["gated"]["excess_oos_bp_per_year"]
            - pair["gated"]["excess_oos_bp_per_year"]) > 1.0
        and abs(pair_o["matched"]["oos"]["excess_oos_bp_per_year"]
                - mo["excess_oos_bp_per_year"]) > 1.0,
        "gated +%.1f and matched +%.1f bp/yr"
        % (pair_o["gated"]["excess_oos_bp_per_year"]
           - pair["gated"]["excess_oos_bp_per_year"],
           pair_o["matched"]["oos"]["excess_oos_bp_per_year"] - mo["excess_oos_bp_per_year"]))

    # L6 the matched arm shares the in-sample drift estimate (asserted inside
    # arm_pair as well; this leg pins the published number)
    leg("matched_arm_shares_mu_is", abs(pair["mu_is_bp_per_day"] - mu_is) < 1e-12,
        "mu_is %.6f" % pair["mu_is_bp_per_day"])

    # L7 the three matched constants differ when the weight varies, and the OOS one
    # reproduces the gated arm's own average exposure
    ci = pair["matched"]["is"]["const_weight"]
    co = pair["matched"]["oos"]["const_weight"]
    cf = pair["matched"]["full"]["const_weight"]
    leg("matched_constants_are_the_three_averages",
        abs(co - pair["gated"]["avg_weight_oos"]) < 1e-12 and len({round(ci, 6), round(co, 6),
                                                                  round(cf, 6)}) >= 2,
        "is %.4f oos %.4f full %.4f" % (ci, co, cf))

    # L8 doubling the toll moves the pair by exactly the difference in charged costs
    pair_x2 = arm_pair(w, ret, split, COST_SIDE_BP * COST_X2_MULT, 2.5)
    want = (0.0 - (pair["gated"]["cost_bp_per_year_oos"]
                   - mo["cost_bp_per_year_oos"]))
    got = (pair_x2["matched"]["oos"]["paired"]["ann_bp_per_year"]
           - mo["paired"]["ann_bp_per_year"])
    leg("x2_toll_moves_the_pair_by_the_cost_difference", abs(got - want) < 1e-9,
        "asked %.9f, got %.9f" % (want, got))

    # L9 the MDE is exactly z times the paired standard error, annualised
    p = mo["paired"]
    leg("paired_mde_is_z_times_nw_se",
        p["se_nw"] is not None
        and abs(p["mde_ann_bp_per_year"] - Z_80 * p["se_nw"] * SESSIONS_PER_YEAR) < 1e-9,
        "derived from its own dispersion")

    # L10 a constant paired series yields no standard error and therefore no t --
    # the verdict must refuse, not divide
    z = _pair_stats([3.0] * 300, [], 0.0, COST_SIDE_BP)
    leg("zero_variance_pair_has_no_t", z["t_nw"] is None and z["mean_bp"] == 3.0,
        "no t from a flat series")

    # L11 sign is tri-state around the tolerance, so a rounding-scale gap is not a flip
    leg("sign_is_tristate_with_tolerance",
        _sign(0.4, 1.0) == 0 and _sign(1.4, 1.0) == 1 and _sign(-1.4, 1.0) == -1,
        "0.4 -> 0, 1.4 -> 1, -1.4 -> -1")

    # L12 the verdict refuses a short window
    short = {"gated": {"oos_decisions": 100},
             "matched": {"oos": {"paired": {"ann_bp_per_year": 500.0, "t_nw": 9.0}}}}
    v, why = pair_verdict(short, 3.0)
    leg("short_window_unresolved", v == "UNRESOLVED" and "below" in why, why)

    # L13 the verdict applies the bar to the PAIRED t, not to any level
    fake = {"gated": {"oos_decisions": 400},
            "matched": {"oos": {"paired": {"ann_bp_per_year": 100.0, "t_nw": 3.1}}}}
    ok_v, _ = pair_verdict(fake, 3.0)
    low = {"gated": {"oos_decisions": 400},
           "matched": {"oos": {"paired": {"ann_bp_per_year": 100.0, "t_nw": 2.9}}}}
    low_v, _ = pair_verdict(low, 3.0)
    leg("verdict_applies_the_bar", ok_v == "TIMING_SURVIVES" and low_v == "TIMING_DEAD",
        "same pair flips at the bar")

    # L14 a pair that dies at double costs cannot survive
    dead = {"gated": {"oos_decisions": 400},
            "matched": {"oos": {"paired": {"ann_bp_per_year": 100.0, "t_nw": 5.0}}}}
    x2 = {"matched": {"oos": {"paired": {"ann_bp_per_year": -1.0}}}}
    v2, why2 = pair_verdict(dead, 3.0, x2=x2)
    leg("x2_costs_can_veto", v2 == "TIMING_DEAD" and why2 == "dies_at_x2_costs", why2)

    # L15 the attribution reproduces E225's algebra exactly: comp + gate_specific == level
    comp, gs = attribution(120.0, 0.4, -300.0)
    leg("attribution_identity", abs(comp - (-120.0)) < 1e-12
        and abs(comp + gs - 120.0) < 1e-12,
        "comp %.4f gate_specific %.4f" % (comp, gs))

    # L16 a matched arm at zero weight is the identity arm: excess exactly zero
    zero_rows, _ = rows_for([0.0] * len(ret), ret, split, COST_SIDE_BP)
    zex = [r["excess_bp"] for r in zero_rows if r["i"] >= cut]
    leg("zero_weight_matched_arm_is_exactly_flat", all(abs(x) < 1e-12 for x in zex),
        "all %d OOS rows exactly zero" % len(zex))

    # L17 gated and matched rows cover the same decision sessions even when a
    # return is missing (the None skip must not desynchronise the two arms)
    holed = list(ret)
    for i in range(700, 720):
        holed[i] = None
    hp = arm_pair(e225.weights_series(e225.vol_signal(holed), "tilt_linear"), holed,
                  split, COST_SIDE_BP, 2.5)
    leg("pair_survives_missing_returns",
        hp["matched"]["oos"]["paired"]["n"] == hp["gated"]["oos_decisions"],
        "%d paired rows for %d gated decisions"
        % (hp["matched"]["oos"]["paired"]["n"], hp["gated"]["oos_decisions"]))

    # L18 the bar is built from the arm x panel count, not from a literal
    leg("bar_from_test_count",
        abs(max(2.0, e222._z_two_sided(0.05 / 8)) - 2.7344) < 1e-3,
        "4 gated arms x 2 panels -> z=%.4f" % max(2.0, e222._z_two_sided(0.05 / 8)))

    # L19 the attribution and the matched benchmark differ by EXACTLY the matched
    # arm's own out-of-sample toll. A constant weight stops trading after its entry
    # side, so that toll is zero and the two "different" benchmarks are one number --
    # this is the structural reason the split was safe, and the reason it will stop
    # being safe for any benchmark that rebalances.
    null_rows, _ = rows_for([1.0] * len(ret), ret, split, COST_SIDE_BP)
    null_oos = [r for r in null_rows if r["i"] >= cut]
    null_ann = e225._mean([r["excess_bp"] for r in null_oos]) * SESSIONS_PER_YEAR
    gated_ann = e225._mean([r["excess_bp"] for r in oos]) * SESSIONS_PER_YEAR
    _comp, attr_bp = attribution(gated_ann, pair["gated"]["avg_weight_oos"], null_ann)
    pair_bp = mo["paired"]["ann_bp_per_year"]
    leg("attribution_minus_pair_is_the_matched_toll",
        abs((attr_bp - pair_bp) + mo["cost_bp_per_year_oos"]) < 1e-9,
        "gap %.9f vs -matched_toll %.9f (both zero here: a flat arm stops trading)"
        % (attr_bp - pair_bp, mo["cost_bp_per_year_oos"]))

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