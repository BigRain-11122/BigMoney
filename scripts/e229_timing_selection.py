"""E229 -- WHERE does the paired timing value come from?

E228 gave the paired timing value a standard error for the first time: on the single
sh510300 panel every gated arm reads -524..-704 bp/yr against a bar of 3.09, and on the
equal-weight basket `binary_low` reads +218 bp/yr at t=0.71. It did not ask WHERE that
number comes from. A gated rule differs from the flat constant in two separable ways:

  * the SELECTION channel -- it is in the market a different share of the time, so the
    sessions it sits out contribute (-c) * (r_t - mu_is) each. This is "which days".
  * the SIZING channel -- on the days both arms hold, its weight is not c, so it
    contributes (w_t - c) * (r_t - mu_is). This is "how much".
  * the TOLL channel -- whatever the movement costs, -|dw_t| * side, charged per side.

Under E228's own accounting those three sum to the paired series session by session:

    d_t = (w_t - c) * (r_t - mu_is) - cost_t
        = 1[w_t = 0] * (-c) * (r_t - mu_is)          (selection)
        + 1[w_t > 0] * (w_t - c) * (r_t - mu_is)     (sizing)
        - cost_t                                     (toll)

so the decomposition is arithmetic on an existing series, not a new study. The sizing
channel is further split exactly into a LEVEL term (the gate's in-market average weight
sitting away from c) and a COVARIANCE term (it holding more when the return is above the
drift) -- that split is the difference between "the gate picks days but sizes them wrong"
and "the gate holds the right amount at the wrong time".

Everything below is frozen in this docstring and in the module constants before any
number was read. Nothing here can adopt a rule: E228 already judged the pair, and the
channels are only a labelling of that same series.

Frozen decision vocabulary (per arm, per panel):
  * NO_STRUCTURE      every channel is below 1 bp/yr in absolute value -- the pair is noise.
  * <CH>_DOMINANT     the largest |channel| in bp/yr, where CH is selection / sizing /
                      toll. Reported with the channel's own Newey-West t and whether it
                      clears the channel bar.
  * the channel bar is Bonferroni over arms x panels x 3 channels; the arm-level bar
    from E228 is printed beside it because the two answer different questions.
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
E228_FACE = os.path.join(OUTDIR, "matched_latest.json")

COST_SIDE_BP = e225.COST_SIDE_BP
IS_FRAC = e225.IS_FRAC
MIN_OOS_SESSIONS = e225.MIN_OOS_SESSIONS
NW_LAG = e225.NW_LAG
Z_80 = e225.Z_80
SESSIONS_PER_YEAR = e225.SESSIONS_PER_YEAR
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET
ARMS = e225.ARMS
GATED_ARMS = [a for a in ARMS if a != "always_on"]

CHANNELS = ("selection", "sizing", "toll")
NO_STRUCTURE_BP = 1.0  # frozen: below one bp/yr per year a channel is not a structure


def _ann(sum_bp, n):
    """Annualise a channel's TOTAL contribution over n sessions."""
    if not n:
        return None
    return sum_bp / float(n) * SESSIONS_PER_YEAR


def channel_rows(weights, ret_bp, split, cost_side_bp, const=None):
    """Per-session channel decomposition of the E228 pair.

    Returns (rows, meta) where every row carries the three channel terms and the pair
    term they must sum to. `const` defaults to the gated arm's own OOS average weight,
    which is the exact exposure match E228 publishes as the diagnostic constant.
    """
    base, mu_is = e228.rows_for(weights, ret_bp, split, cost_side_bp)
    cut = split - 1
    oos = [r for r in base if r["i"] >= cut]
    if not oos:
        return None, {"mu_is_bp_per_day": mu_is, "const_weight": None}
    w_vals = [r["w"] for r in oos]
    c = e225._mean(w_vals) if const is None else float(const)
    rows = []
    for r in oos:
        ret = ret_bp[r["i"] + 1]
        assert ret is not None, "rows_for must not emit a session without a return"
        dev = ret - mu_is
        if r["w"] == 0.0:
            sel = (-c) * dev
            siz = 0.0
        else:
            sel = 0.0
            siz = (r["w"] - c) * dev
        toll = -r["cost_bp"]
        rows.append({"i": r["i"], "w": r["w"], "ret_bp": ret, "dev_bp": dev,
                     "selection": sel, "sizing": siz, "toll": toll,
                     "pair": r["excess_bp"] - (c * ret - c * mu_is)})
    return rows, {"mu_is_bp_per_day": mu_is, "const_weight": c}


def _channel_stats(series, ann_bp):
    if not series:
        return {"n": 0, "ann_bp_per_year": None, "t_nw": None}
    se = e225._hac_se(series, NW_LAG) if len(series) >= 3 else None
    m = e225._mean(series)
    return {"n": len(series),
            "mean_bp_per_session": m,
            "ann_bp_per_year": ann_bp,
            "se_nw": se,
            "t_nw": (m / se) if (se and m is not None) else None,
            "n_eff": e225._n_eff(series) if len(series) >= 3 else None}


def decompose(rows, meta, bar_channel):
    """Channel totals, their t's, and the sizing split into level and covariance."""
    n = len(rows)
    out = {"oos_sessions": n, "const_weight": meta["const_weight"],
           "identity_residual_bp": None}
    series = {ch: [r[ch] for r in rows] for ch in CHANNELS}
    pair_series = [r["pair"] for r in rows]
    residual = sum(sum(series[ch]) for ch in CHANNELS) - sum(pair_series)
    out["identity_residual_bp"] = residual
    for ch in CHANNELS:
        out[ch] = _channel_stats(series[ch], _ann(sum(series[ch]), n))

    # sizing split: sum_in (w-c)(r-mu) == n_in*m_w*m_r + sum_in (w-c-m_w)(r-mu-m_r)
    in_rows = [r for r in rows if r["w"] > 0.0]
    out_rows = [r for r in rows if r["w"] == 0.0]
    n_in = len(in_rows)
    out["in_market_sessions"] = n_in
    out["out_of_market_sessions"] = len(out_rows)
    if n_in:
        dw = [r["w"] - meta["const_weight"] for r in in_rows]
        dv = [r["dev_bp"] for r in in_rows]
        m_dw = e225._mean(dw)
        m_dv = e225._mean(dv)
        level = n_in * m_dw * m_dv
        cov = sum((a - m_dw) * (b - m_dv) for a, b in zip(dw, dv))
        out["sizing_level"] = {"ann_bp_per_year": _ann(level, n),
                               "in_market_mean_weight_minus_c": m_dw,
                               "in_market_mean_dev_bp": m_dv,
                               "reading": "the gate's in-market average weight sits away "
                                          "from the flat constant"}
        out["sizing_covariance"] = {"ann_bp_per_year": _ann(cov, n),
                                    "reading": "on shared days the gate holds more when the "
                                               "return is above the drift"}
        out["sizing_split_residual_bp"] = level + cov - sum(series["sizing"])
    else:
        out["sizing_level"] = {"ann_bp_per_year": None}
        out["sizing_covariance"] = {"ann_bp_per_year": None}
        out["sizing_split_residual_bp"] = None

    # what the dodged days actually looked like, in plain terms
    if out_rows:
        devs = [r["dev_bp"] for r in out_rows]
        out["dodged_days"] = {"n": len(devs),
                              "mean_dev_bp_per_session": e225._mean(devs),
                              "ann_bp_per_year_if_held": _ann(sum(devs), n),
                              "reading": "the days the gate sat out, measured against the "
                                         "same in-sample drift the arms are charged"}
    else:
        out["dodged_days"] = {"n": 0}

    # which channel carries the pair
    mags = {ch: abs(out[ch]["ann_bp_per_year"]) for ch in CHANNELS
            if out[ch]["ann_bp_per_year"] is not None}
    out["bar_channel_t"] = bar_channel
    if not mags:
        out["dominant"] = None
        out["verdict"] = "UNRESOLVED"
        out["verdict_reason"] = "no_channels"
        return out
    dom = max(mags, key=lambda ch: mags[ch])
    out["dominant"] = dom
    if mags[dom] < NO_STRUCTURE_BP:
        out["verdict"] = "NO_STRUCTURE"
        out["verdict_reason"] = "largest_channel_%.3fbp_below_%.1f" % (mags[dom],
                                                                       NO_STRUCTURE_BP)
        return out
    t = out[dom]["t_nw"]
    resolvable = (t is not None and abs(t) >= bar_channel)
    out["dominant_t_nw"] = t
    out["dominant_resolvable"] = resolvable
    out["verdict"] = "%s_DOMINANT" % dom.upper()
    out["verdict_reason"] = ("t=%.2f %s bar %.2f" %
                             (t if t is not None else float("nan"),
                              ">=" if resolvable else "<", bar_channel))
    return out


def arm_decomposition(weights, ret_bp, split, cost_side_bp, bar_channel):
    rows, meta = channel_rows(weights, ret_bp, split, cost_side_bp)
    if rows is None:
        return None
    return decompose(rows, meta, bar_channel)


# ---------------------------------------------------------------- reference crosscheck
def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _e228_crosscheck(face):
    ref = _load(E228_FACE)
    if not ref or not face.get("panels"):
        return None
    try:
        ref_rows = {(p["panel"], a["name"]): a for p in ref["panels"] for a in p["arms"]}
    except (KeyError, TypeError):
        return None
    out = []
    drift = 0.0
    for panel in face["panels"]:
        for a in panel["arms"]:
            mine = a["channels"]["pair_ann_bp_per_year"]
            theirs_row = ref_rows.get((panel["panel"], a["name"])) or {}
            theirs = (((theirs_row.get("matched") or {}).get("oos") or {})
                      .get("paired") or {}).get("ann_bp_per_year")
            if mine is None or theirs is None:
                continue
            d = abs(mine - theirs)
            drift = max(drift, d)
            out.append({"panel": panel["panel"], "arm": a["name"],
                        "rebuilt_bp_per_year": mine,
                        "published_bp_per_year": theirs, "abs_diff_bp": d})
    return {"source": os.path.relpath(E228_FACE, ROOT).replace("\\", "/"),
            "study": ref.get("study"), "cells": len(out),
            "max_abs_diff_bp": drift, "rows": out}


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
    n_tests_arm = len(GATED_ARMS) * n_panels
    n_tests_chan = n_tests_arm * len(CHANNELS)
    bar_arm = max(2.0, e222._z_two_sided(0.05 / n_tests_arm))
    bar_channel = max(2.0, e222._z_two_sided(0.05 / n_tests_chan))

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
        split_out = []
        # the reference arm: a constant weight has no channels by construction
        w_null = e225.weights_series(sig, "always_on")
        null_dec = arm_decomposition(w_null, ret_bp, split, COST_SIDE_BP, bar_channel)
        panel["reference_constant_arm"] = ({k: null_dec[k] for k in
                                            ("const_weight", "identity_residual_bp",
                                             "verdict", "verdict_reason")}
                                           if null_dec else None)
        panel["arms"] = []
        for arm in GATED_ARMS:
            target = e225.arm_target(sig, split, arm)
            w = e225.weights_series(sig, arm, target)
            dec = arm_decomposition(w, ret_bp, split, COST_SIDE_BP, bar_channel)
            if dec is None:
                continue
            rows, _meta = channel_rows(w, ret_bp, split, COST_SIDE_BP)
            pair_ann = _ann(sum(r["pair"] for r in rows), len(rows))
            dec = {"name": arm, "target_bp": target, "channels": {
                "pair_ann_bp_per_year": pair_ann,
                "identity_residual_bp": dec["identity_residual_bp"],
                "oos_sessions": dec["oos_sessions"],
                "const_weight": dec["const_weight"],
                "in_market_sessions": dec["in_market_sessions"],
                "out_of_market_sessions": dec["out_of_market_sessions"],
                "selection": dec["selection"], "sizing": dec["sizing"],
                "toll": dec["toll"],
                "sizing_level": dec["sizing_level"],
                "sizing_covariance": dec["sizing_covariance"],
                "sizing_split_residual_bp": dec["sizing_split_residual_bp"],
                "dodged_days": dec["dodged_days"],
            }, "dominant": dec.get("dominant"), "dominant_t_nw": dec.get("dominant_t_nw"),
                   "dominant_resolvable": dec.get("dominant_resolvable"),
                   "verdict": dec["verdict"], "verdict_reason": dec["verdict_reason"],
                   "bar_arm_t": bar_arm}
            if dec["channels"]["oos_sessions"] < MIN_OOS_SESSIONS:
                dec["verdict"] = "UNRESOLVED"
                dec["verdict_reason"] = "oos_sessions_%d_below_%d" % (
                    dec["channels"]["oos_sessions"], MIN_OOS_SESSIONS)
            panel["arms"].append(dec)
            split_out.append(dec)

    face = {
        "study": "E229",
        "title": "where does E228's paired timing value come from? selection (which days) "
                 "vs sizing (how much) vs toll, an exact three-way split of the same series",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "gated_arms": GATED_ARMS,
            "channels": list(CHANNELS),
            "identity": "d_t = 1[w=0]*(-c)*(r-mu_is) + 1[w>0]*(w-c)*(r-mu_is) - cost_t",
            "const_weight": "the gated arm's own OOS average weight (E228's exact match)",
            "sizing_split": "n_in*m_w*m_r (level) + sum_in (w-c-m_w)(r-mu-m_r) (covariance)",
            "cost_side_bp": COST_SIDE_BP,
            "cost_model": "unit turnover |dw| pays one side; w_{-1}=0 so entry pays a side",
            "is_frac": IS_FRAC,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "nw_lag": NW_LAG,
            "z_80pct": Z_80,
            "no_structure_bp_per_year": NO_STRUCTURE_BP,
            "bar_arm_t": bar_arm,
            "bar_channel_t": bar_channel,
            "bar_basis": "two-sided 5%% over %d arm tests and %d channel tests"
                         % (n_tests_arm, n_tests_chan),
            "vocabulary": "NO_STRUCTURE below 1bp/yr; otherwise <CH>_DOMINANT with the "
                          "channel's NW t against bar_channel_t",
            "no_adoption": "E228 already judged the pair; the channels label that series",
        },
        "panels": panels,
    }

    chk = _e228_crosscheck(face)
    if chk:
        face["e228_crosscheck"] = chk

    # ------------------------------------------------ the deliverable: which channel carries it
    rows_out = []
    for panel in panels:
        for a in panel["arms"]:
            ch = a["channels"]
            rows_out.append({"panel": panel["panel"], "arm": a["name"],
                             "pair": ch["pair_ann_bp_per_year"],
                             "selection": ch["selection"]["ann_bp_per_year"],
                             "sizing": ch["sizing"]["ann_bp_per_year"],
                             "toll": ch["toll"]["ann_bp_per_year"],
                             "dominant": a["dominant"], "verdict": a["verdict"]})
    face["channel_summary"] = {
        "reading": "each row is the same paired series split three ways; the three "
                   "channels reconstruct the pair exactly (identity_residual_bp)",
        "rows": rows_out,
        "selection_dominant": sum(1 for r in rows_out if r["dominant"] == "selection"),
        "sizing_dominant": sum(1 for r in rows_out if r["dominant"] == "sizing"),
        "toll_dominant": sum(1 for r in rows_out if r["dominant"] == "toll"),
        "no_structure": sum(1 for r in rows_out if r["verdict"] == "NO_STRUCTURE"),
        "cells": len(rows_out),
    }

    primary = panels[0]["arms"]
    sel_dom = [a for a in primary if a["dominant"] == "selection"]
    siz_dom = [a for a in primary if a["dominant"] == "sizing"]
    toll_dom = [a for a in primary if a["dominant"] == "toll"]
    resolvable = [{"panel": p["panel"], "arm": a["name"], "channel": a["dominant"],
                   "t": a["dominant_t_nw"]}
                  for p in panels for a in p["arms"] if a.get("dominant_resolvable")]
    binary_level = []
    for p in panels:
        for a in p["arms"]:
            ch = a["channels"]
            cov = ch["sizing_covariance"]["ann_bp_per_year"]
            if a["name"].startswith("binary") and cov is not None:
                binary_level.append(abs(cov))
    best = None
    for a in primary:
        ch = a["channels"]
        if ch["pair_ann_bp_per_year"] is None:
            continue
        cand = ch["sizing"]["ann_bp_per_year"]
        if cand is None:
            continue
        if best is None or cand > best[1]:
            best = (a["name"], cand, ch["sizing"]["t_nw"])
    face["answer"] = (
        "on the primary panel the pair splits into %d selection-dominant, %d sizing-dominant "
        "and %d toll-dominant arms (of %d); across both panels %d cell(s) carry a dominant "
        "channel that clears the channel bar %.2f (%s). The best sizing channel on the primary "
        "panel is %s at %s bp/yr (t=%s), and the binary arms' covariance term is identically "
        "zero (max %s bp/yr) -- a 0/1 gate holds one weight whenever it holds at all, so for "
        "those arms 'sizing' can only be a level shift, never timing skill. The three channels "
        "reconstruct the pair exactly: max |identity residual| = %s bp."
        % (len(sel_dom), len(siz_dom), len(toll_dom), len(primary), len(resolvable),
           bar_channel,
           "; ".join("%s/%s t=%.2f" % (r["panel"][:7], r["arm"], r["t"]) for r in resolvable)
           or "none",
           (best[0] if best else "-"),
           ("%.0f" % best[1]) if best else "-",
           ("%.2f" % best[2]) if (best and best[2] is not None) else "-",
           ("%.2e" % max(binary_level)) if binary_level else "-",
           ("%.3e" % max(abs(p["arms"][0]["channels"]["identity_residual_bp"])
                         for p in panels
                         if p["arms"] and
                         p["arms"][0]["channels"]["identity_residual_bp"] is not None))
           if any(p["arms"] for p in panels) else "-"))
    face["resolvable_dominant_channels"] = resolvable

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "TIMINGSEL-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "timingsel_latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "name", "oos_sessions", "const_weight", "in_market_sessions",
                "out_of_market_sessions", "pair_ann_bp_per_year",
                "selection_ann_bp_per_year", "sizing_ann_bp_per_year",
                "toll_ann_bp_per_year", "sizing_level_ann_bp_per_year",
                "sizing_covariance_ann_bp_per_year", "selection_t_nw", "sizing_t_nw",
                "toll_t_nw", "dominant", "dominant_t_nw", "dominant_resolvable",
                "dodged_mean_dev_bp_per_session", "identity_residual_bp", "verdict",
                "verdict_reason"]
        assert len(cols) == 22, "column list length drift"
        csv_path = os.path.join(outdir, "timingsel_by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    ch = a["channels"]
                    w.writerow({
                        "panel": panel["panel"], "name": a["name"],
                        "oos_sessions": ch["oos_sessions"],
                        "const_weight": ch["const_weight"],
                        "in_market_sessions": ch["in_market_sessions"],
                        "out_of_market_sessions": ch["out_of_market_sessions"],
                        "pair_ann_bp_per_year": ch["pair_ann_bp_per_year"],
                        "selection_ann_bp_per_year": ch["selection"]["ann_bp_per_year"],
                        "sizing_ann_bp_per_year": ch["sizing"]["ann_bp_per_year"],
                        "toll_ann_bp_per_year": ch["toll"]["ann_bp_per_year"],
                        "sizing_level_ann_bp_per_year":
                            ch["sizing_level"]["ann_bp_per_year"],
                        "sizing_covariance_ann_bp_per_year":
                            ch["sizing_covariance"]["ann_bp_per_year"],
                        "selection_t_nw": ch["selection"]["t_nw"],
                        "sizing_t_nw": ch["sizing"]["t_nw"],
                        "toll_t_nw": ch["toll"]["t_nw"],
                        "dominant": a["dominant"], "dominant_t_nw": a["dominant_t_nw"],
                        "dominant_resolvable": a["dominant_resolvable"],
                        "dodged_mean_dev_bp_per_session":
                            ch["dodged_days"].get("mean_dev_bp_per_session"),
                        "identity_residual_bp": ch["identity_residual_bp"],
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

    w = e225.weights_series(sig, "binary_low")
    rows, meta = channel_rows(w, ret, split, COST_SIDE_BP)
    dec = decompose(rows, meta, 3.0)

    # L1 the three channels reconstruct the pair session by session
    leg("channels_reconstruct_the_pair", abs(dec["identity_residual_bp"]) < 1e-9,
        "residual %.3e bp over %d sessions" % (dec["identity_residual_bp"],
                                               dec["oos_sessions"]))

    # L2 every session lands in exactly one of selection / sizing
    leg("sessions_partition_into_in_and_out",
        dec["in_market_sessions"] + dec["out_of_market_sessions"] == dec["oos_sessions"]
        and all((r["sizing"] == 0.0) if r["w"] == 0.0 else (r["selection"] == 0.0)
                for r in rows),
        "%d in + %d out = %d" % (dec["in_market_sessions"],
                                 dec["out_of_market_sessions"], dec["oos_sessions"]))

    # L3 the toll channel is exactly minus the charged cost, nothing else
    base, mu_is = e228.rows_for(w, ret, split, COST_SIDE_BP)
    cut = split - 1
    want = -sum(r["cost_bp"] for r in base if r["i"] >= cut)
    leg("toll_channel_is_the_charged_cost",
        abs(sum(r["toll"] for r in rows) - want) < 1e-9,
        "%.6f vs %.6f bp" % (sum(r["toll"] for r in rows), want))

    # L4 a constant weight has no channels at all -- the reference arm
    w_null = e225.weights_series(sig, "always_on")
    ndec = arm_decomposition(w_null, ret, split, COST_SIDE_BP, 3.0)
    leg("constant_arm_has_no_structure",
        ndec["verdict"] == "NO_STRUCTURE"
        and abs(ndec["selection"]["ann_bp_per_year"] or 0.0) < 1e-9
        and abs(ndec["sizing"]["ann_bp_per_year"] or 0.0) < 1e-9,
        "selection %.3e sizing %.3e" % (ndec["selection"]["ann_bp_per_year"] or 0.0,
                                        ndec["sizing"]["ann_bp_per_year"] or 0.0))

    # L5 the selection channel equals -c * sum over sat-out sessions of (r - mu_is)
    c = meta["const_weight"]
    want_sel = -c * sum(r["dev_bp"] for r in rows if r["w"] == 0.0)
    leg("selection_is_the_dodged_drift", abs(sum(r["selection"] for r in rows) - want_sel) < 1e-9,
        "%.6f vs %.6f bp" % (sum(r["selection"] for r in rows), want_sel))

    # L6 the sizing split (level + covariance) is exact
    leg("sizing_splits_into_level_and_covariance",
        dec["sizing_split_residual_bp"] is not None
        and abs(dec["sizing_split_residual_bp"]) < 1e-9,
        "residual %.3e bp" % (dec["sizing_split_residual_bp"] or 0.0))

    # L7 a gate that sat out only the sessions with the LOWEST returns must read a
    # positive selection channel. Alignment matters: the weight set at index i covers
    # the return at i+1, so "sitting out session j" means w[j-1] = 0. Only out-of-sample
    # sessions are dodgeable -- an in-sample dodge would move mu_is as well.
    mu_syn = e225._mean([r for r in ret[1:split] if r is not None])
    oos_ret_idx = [j for j in range(split, len(ret)) if ret[j] is not None]
    worst = set(j for j in sorted(oos_ret_idx, key=lambda j: ret[j] - mu_syn)[:40])
    w_craft = [0.0 if (i + 1) in worst else 0.5 for i in range(len(ret))]
    crows, cmeta = channel_rows(w_craft, ret, split, COST_SIDE_BP)
    cdec = decompose(crows, cmeta, 3.0)
    leg("dodging_low_days_reads_positive_selection",
        (cdec["selection"]["ann_bp_per_year"] or 0.0) > 0.0
        and cdec["dominant"] == "selection",
        "selection %.1f bp/yr, dominant=%s"
        % (cdec["selection"]["ann_bp_per_year"] or 0.0, cdec["dominant"]))

    # L8 a gate that holds MORE on the highest-dev days must read a positive
    # covariance term (it is holding the right amount at the right time)
    best = set(j for j in sorted(oos_ret_idx, key=lambda j: -(ret[j] - mu_syn))[:60])
    w_cov = [0.9 if (i + 1) in best else 0.3 for i in range(len(ret))]
    krows, kmeta = channel_rows(w_cov, ret, split, COST_SIDE_BP)
    kdec = decompose(krows, kmeta, 3.0)
    leg("holding_more_on_up_days_reads_positive_covariance",
        (kdec["sizing_covariance"]["ann_bp_per_year"] or 0.0) > 0.0,
        "covariance %.1f bp/yr" % (kdec["sizing_covariance"]["ann_bp_per_year"] or 0.0))

    # L9 the mirrored construction reads negative -- the sign is the construction's,
    # not the panel's
    worst2 = set(j for j in sorted(oos_ret_idx, key=lambda j: ret[j] - mu_syn)[:60])
    w_bad = [0.9 if (i + 1) in worst2 else 0.3 for i in range(len(ret))]
    brows, bmeta = channel_rows(w_bad, ret, split, COST_SIDE_BP)
    bdec = decompose(brows, bmeta, 3.0)
    leg("mirrored_construction_flips_the_sign",
        (bdec["sizing_covariance"]["ann_bp_per_year"] or 0.0) < 0.0,
        "covariance %.1f bp/yr" % (bdec["sizing_covariance"]["ann_bp_per_year"] or 0.0))

    # L10 an always-in gate has no selection channel by construction
    w_in = [0.4] * len(ret)
    irows, imeta = channel_rows(w_in, ret, split, COST_SIDE_BP)
    idec = decompose(irows, imeta, 3.0)
    leg("always_in_gate_has_empty_selection",
        idec["out_of_market_sessions"] == 0
        and abs(sum(r["selection"] for r in irows)) < 1e-12,
        "%d sat-out sessions" % idec["out_of_market_sessions"])

    # L11 a flat channel series yields no t: the verdict must refuse, not divide
    z = _channel_stats([0.0] * 300, 0.0)
    leg("flat_channel_has_no_t", z["t_nw"] is None, "no t from a zero-variance channel")

    # L12 below one bp/yr nothing is called a structure
    tiny_rows = [{"i": 0, "w": 0.5, "ret_bp": 0.0, "dev_bp": 0.0,
                  "selection": 0.0, "sizing": 1e-4, "toll": 0.0, "pair": 1e-4}]
    tdec = decompose(tiny_rows, {"const_weight": 0.5, "mu_is_bp_per_day": 0.0}, 3.0)
    leg("sub_bp_channel_is_not_a_structure", tdec["verdict"] == "NO_STRUCTURE",
        tdec["verdict_reason"])

    # L13 the channel bar is looser than the arm bar, both derived from their counts
    bar_arm = max(2.0, e222._z_two_sided(0.05 / (len(GATED_ARMS) * 2)))
    bar_chan = max(2.0, e222._z_two_sided(0.05 / (len(GATED_ARMS) * 2 * len(CHANNELS))))
    leg("channel_bar_is_derived_and_looser", bar_chan == 0.0 or bar_chan >= bar_arm,
        "arm %.3f <= channel %.3f" % (bar_arm, bar_chan))

    # L14 missing returns do not desynchronise the channels from the pair
    holed = list(ret)
    for i in range(700, 720):
        holed[i] = None
    hs = e225.vol_signal(holed)
    hw = e225.weights_series(hs, "tilt_linear")
    hrows, hmeta = channel_rows(hw, holed, split, COST_SIDE_BP)
    hdec = decompose(hrows, hmeta, 3.0)
    leg("missing_returns_keep_the_identity",
        abs(hdec["identity_residual_bp"]) < 1e-9
        and hdec["oos_sessions"] == len([r for r in e228.rows_for(hw, holed, split,
                                                                 COST_SIDE_BP)[0]
                                        if r["i"] >= split - 1]),
        "residual %.3e over %d sessions" % (hdec["identity_residual_bp"],
                                            hdec["oos_sessions"]))

    # L15 the dodged-days face reports the sign convention it claims
    if cdec["dodged_days"]["n"]:
        leg("dodged_days_mean_is_negative_by_construction",
            cdec["dodged_days"]["mean_dev_bp_per_session"] < 0.0,
            "mean dev %.3f bp/session over %d sat-out days"
            % (cdec["dodged_days"]["mean_dev_bp_per_session"], cdec["dodged_days"]["n"]))
    else:
        leg("dodged_days_mean_is_negative_by_construction", False, "no sat-out days")

    # L16 the pair reproduced by the channels equals E228's own pair function
    epair = e228.arm_pair(w, ret, split, COST_SIDE_BP, 3.0)
    pub = (((epair.get("matched") or {}).get("oos") or {}).get("paired") or {})
    leg("pair_matches_e228_for_the_same_arm",
        pub.get("ann_bp_per_year") is None or abs(
            sum(r["pair"] for r in rows) / len(rows) * SESSIONS_PER_YEAR
            - pub["ann_bp_per_year"]) < 1e-6,
        "channels %.6f vs e228 %.6f" % (
            sum(r["pair"] for r in rows) / len(rows) * SESSIONS_PER_YEAR,
            pub.get("ann_bp_per_year") or float("nan")))

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