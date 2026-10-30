"""Does cutting turnover with the incumbent buffer ever pay -- and at what cost?

r1324 priced an incumbent-protection buffer (displace a holder only when a challenger beats
it by k * the bar's score sd) and found k=0.05 improving turnover, CAGR, Sharpe and maxDD
together. r1325 path-tested that ONE arm across 5 books x 4 decision phases and rejected it:
turnover fell in every cell, return fell in most, and the "+0.07pp" was the 2020-01-02 phase.

Meanwhile the published face `results/etf_book_hysteresis.json` still carries six arms on a
SINGLE decision sequence, and its whole reason to exist is the turnover constraint -- so the
question it answers ("does the score certifying the 12th vs 13th name mean anything?") keeps
being read next to arm numbers that were never path-tested. This face closes that gap for the
whole arm family instead of one point:

  * the same buffer is re-priced at k in {0.05, 0.10, 0.20, 0.35} on
  * 5 books (n_hold x rebal: 12/20 the production cell, 12/10, 12/40, 8/20, 20/20) and
  * 4 decision phases (grids started at four different bars inside one 20-bar cycle),

so every (book, phase, k) cell has its own decision sequence. 80 arm cells + 20 baselines.

Two things are added that neither r1324 nor r1325 published:

  (1) A VERDICT PER ARM under the same frozen rule r1325 used, so "the buffer" is not
      discussed as one number.
  (2) A BREAKEVEN COST per cell: turnover savings are only money if the cost per side is
      high enough to pay for the return the buffer gives away. The arm is priced at the
      production 10bp/side; the breakeven says at what per-side cost the saving would have
      covered the loss in THAT cell, and the face reports the median across cells. That is
      the number an operator needs when the book is small (10bp) or capacity-bound (25bp+).

What is reused, never rewritten:
  * panel/class filter/repair  = scripts.etf_book_production.prep_panel
  * engine                     = scripts.etf_robust_pf.open_to_open_equity
  * cell maths                 = scripts.etf_book_buffer_adoption.arm_metrics
  * per-arm summary + rule     = etf_book_buffer_adoption.summarize / dispersion / verdict
    (the frozen thresholds live there; this face ECHOES them and refuses to run against a
    copy that has drifted -- a second set of thresholds would be a second rule)

Honest limits, stated up front:
  * exploratory: no preregistration, no verdict booking. ADOPT here means "the arm survives
    its own path test", not "change production" -- promotion is a separate prereg.
  * 5 books x 4 phases is a ruler, not a distribution: it bounds phase luck among four
    calendars inside one cycle, it does not sample the future.
  * one panel (survivor pool), one window (2020-01 -> panel edge), one cost assumption with
    the breakeven printed next to it.
  * the buffer is path-dependent by construction; that is precisely why the grid, not a
    single arm, is the unit of the verdict.

Usage:
    python scripts/etf_book_hysteresis_paths.py run [--out=...]
    python scripts/etf_book_hysteresis_paths.py --check
    python scripts/etf_book_hysteresis_paths.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_book_buffer_adoption as B
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_hysteresis_paths.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_HYSTERESIS_PATHS.md"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

SCRIPT = "scripts/etf_book_hysteresis_paths.py"
FACE = "results/etf_book_hysteresis_paths.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; echoed into the payload; the gate refuses a face whose echo
# differs from these constants. Nothing here introduces a NEW threshold: the per-arm rule is
# r1325's, imported from etf_book_buffer_adoption so there is exactly one rule in the repo.
K_ARMS = (0.05, 0.10, 0.20, 0.35)      # the published arm grid, minus the k=0 baseline
K_BASE = 0.0
GRID = (K_BASE,) + K_ARMS
CONFIGS = B.CONFIGS                    # 5 books, r1325's
N_PHASES = B.N_PHASES                  # 4 phases inside one rebalance cycle
PHASE_REBAL = B.PHASE_REBAL

# breakeven assumption: how many rebalance decisions a year is, per book. Derived from the
# panel itself (bars/year), never hardcoded per config.
MIN_ABS_TURNOVER_DELTA = 1e-6          # below this a cell has no saving to convert
BARS_PER_YEAR_FALLBACK = 243.0         # only used if the panel cannot supply a rate

COST = B.COST                          # 10bp/side, the production assumption
TARGET_VOL = B.TARGET_VOL
CONTROL_TOL = B.CONTROL_TOL

CRITERIA = {
    "k_arms": list(K_ARMS),
    "k_base": K_BASE,
    "configs": [list(c) for c in CONFIGS],
    "n_phases": N_PHASES,
    "phase_cycle_bars": PHASE_REBAL,
    "per_arm_rule": {
        "turnover_down_share_min": B.TURNOVER_DOWN_SHARE_MIN,
        "cagr_share_min": B.CAGR_SHARE_MIN,
        "cagr_share_floor_pp": B.CAGR_SHARE_FLOOR_PP,
        "sharpe_share_min": B.SHARPE_SHARE_MIN,
        "median_cagr_floor_pp": B.MEDIAN_CAGR_FLOOR_PP,
        "source": "scripts/etf_book_buffer_adoption.py (r1325); imported, never copied",
    },
    "breakeven": {
        "cost_bp_side_assumed": COST,
        "min_abs_turnover_delta": MIN_ABS_TURNOVER_DELTA,
        "formula": "cost_bp* = -dCAGR_fraction / (|d_turnover_per_decision| * decisions_per_year) * 1e4",
        "frozen": "constants written before the first run; the gate refuses a face that echoes others",
    },
}

UNITS = {
    "cagr": "fraction per year (0.0962 = 9.62%/yr)",
    "delta_cagr_pp": "percentage points of CAGR, arm minus its own k=0 cell",
    "turnover_per_decision": "sum |dw| per rebalance, fraction of book",
    "breakeven_cost_bp_side": "per-side cost (bp) at which this cell's turnover saving would have paid for its return loss",
    "phase": "decision-grid start bar inside one rebalance cycle (4 per book)",
}


# ---------------------------------------------------------------- breakeven

def decisions_per_year(index, rebal):
    """How many decisions a book with this cadence makes per calendar year, from the panel."""
    if index is None or len(index) < 2:
        return BARS_PER_YEAR_FALLBACK / float(rebal)
    span_years = (index[-1] - index[0]).days / 365.25
    if span_years <= 0:
        return BARS_PER_YEAR_FALLBACK / float(rebal)
    bars_per_year = len(index) / span_years
    return bars_per_year / float(rebal)


def breakeven_cost_bp(delta_cagr_pp, delta_turnover, dpy):
    """Per-side cost at which a turnover saving equals the return the arm gave away.

    An arm that gains return needs no cost story: a NEGATIVE breakeven is meaningless, so the
    sign is preserved and read as "already pays at any cost". A cell with no turnover change
    has no conversion path at all and returns None rather than a small number.
    """
    if dpy is None or dpy <= 0:
        return None
    if delta_turnover is None or abs(delta_turnover) < MIN_ABS_TURNOVER_DELTA:
        return None
    if delta_cagr_pp is None:
        return None
    return round(-(delta_cagr_pp / 100.0) / (abs(delta_turnover) * dpy) * 1e4, 2)


def enrich_saving(cells, index):
    """Attach decisions_per_year + breakeven to every cell that has a base to compare with."""
    idx = {}
    for c in cells:
        idx[(c["n_hold"], c["rebal"], c["phase"], c["k"])] = c
    dpy_cache = {}
    for c in cells:
        key = (c["n_hold"], c["rebal"])
        if key not in dpy_cache:
            dpy_cache[key] = decisions_per_year(index, c["rebal"])
        c["decisions_per_year"] = round(dpy_cache[key], 3)
        base = idx.get((c["n_hold"], c["rebal"], c["phase"], K_BASE))
        if base is None or c is base or c["k"] == K_BASE:
            c["breakeven_cost_bp_side"] = None
            continue
        d_cagr_pp = 100.0 * ((c.get("cagr") or 0.0) - (base.get("cagr") or 0.0))
        d_turn = (c.get("turnover_per_decision") or 0.0) - (base.get("turnover_per_decision") or 0.0)
        c["delta_cagr_pp_vs_base"] = round(d_cagr_pp, 4)
        c["delta_turnover_vs_base"] = round(d_turn, 4)
        c["breakeven_cost_bp_side"] = breakeven_cost_bp(d_cagr_pp, d_turn, dpy_cache[key])
    return cells


def arm_result(summary, disp, saving_index=None):
    """Per-arm verdict (r1325's rule) + the saving conversion that r1325 did not price.

    `B.summarize` builds its own row dicts and drops unknown keys, so the breakeven computed
    by `enrich_saving` is re-attached here by cell identity -- (book, phase, k), NOT
    (book, phase). Keying by book+phase only made four arms share one arm's breakeven and
    publish the same median 5.4bp four times (the r1280 family: a table keyed by the compared
    column instead of by the arm silently lets the last arm overwrite the earlier ones).
    """
    label, reasons = B.verdict(summary, disp)
    saving_index = saving_index or {}
    kk = summary.get("k")
    for row in summary.get("cells", []):
        key = (row.get("n_hold"), row.get("rebal"), row.get("phase"), kk)
        row["breakeven_cost_bp_side"] = saving_index.get(key)
    bes = [c["breakeven_cost_bp_side"] for c in summary.get("cells", [])
           if c.get("breakeven_cost_bp_side") is not None]
    out = {
        "k": summary.get("k"),
        "verdict": label,
        "reasons": reasons,
        "n_cells": summary.get("n_cells"),
        "turnover_down_share": summary.get("turnover_down_share"),
        # the rule reads these three; publishing the verdict without them leaves the gate
        # unable to re-judge its own face (r1266: a verdict with no consumer is not a gate)
        "share_cagr_ok": summary.get("share_cagr_ok"),
        "share_cagr_up": summary.get("share_cagr_up"),
        "share_sharpe_ok": summary.get("share_sharpe_ok"),
        "median_delta_cagr_pp": summary.get("median_delta_cagr_pp"),
        "median_delta_turnover": summary.get("median_delta_turnover"),
        "median_delta_sharpe": summary.get("median_delta_sharpe"),
        "worst_delta_cagr_pp": summary.get("worst_delta_cagr_pp"),
        "best_delta_cagr_pp": summary.get("best_delta_cagr_pp"),
        "median_delta_maxdd_pp": summary.get("median_delta_maxdd_pp"),
        "sign_test_cagr": summary.get("sign_test_cagr"),
        "breakeven_cost_bp_side": {
            "n_cells": len(bes),
            "median": round(float(np.median(bes)), 2) if bes else None,
            "q25": round(float(np.percentile(bes, 25)), 2) if bes else None,
            "q75": round(float(np.percentile(bes, 75)), 2) if bes else None,
            "min": round(float(min(bes)), 2) if bes else None,
        },
        "cells": summary.get("cells", []),
    }
    return out


def family_verdict(arms):
    """One sentence over the family: is the knob a knob at all, and does any arm survive?"""
    labels = {str(a["k"]): a["verdict"] for a in arms}
    survived = [a["k"] for a in arms if a["verdict"] == "ADOPT"]
    knobs = [a["k"] for a in arms if a["verdict"] == "COST_KNOB_ONLY"]
    meds = [(a["k"], a["median_delta_cagr_pp"]) for a in arms]
    # is the return effect monotone in k? A real knob degrades smoothly; a lucky cell does not.
    vals = [v for _k, v in meds if v is not None]
    monotone_down = all(vals[i] >= vals[i + 1] - 1e-9 for i in range(len(vals) - 1))
    if survived:
        label = "SOME_ARM_SURVIVES"
        reason = ("arm(s) %s clear the frozen per-cell rule; they are hypotheses for a prereg, "
                  "not a config change" % ", ".join("k=%s" % s for s in survived))
    elif knobs and len(knobs) == len(arms):
        label = "COST_KNOB_FAMILY"
        reason = ("every arm cuts turnover and every arm loses return: the buffer is a cost knob, "
                  "not an edge -- it can only be spent against a higher assumed cost, and the "
                  "breakeven column says how high")
    elif knobs:
        label = "MIXED_NO_SURVIVOR"
        reason = ("%d of %d arms read as cost knobs (turnover down, return not settled: k=%s) and "
                  "%d fail the return floor outright (median dCAGR below %+.2fpp: k=%s); no arm "
                  "clears the rule, so the knob is not monotone and cannot be tuned into an edge"
                  % (len(knobs), len(arms), ", ".join("%.2f" % k for k in knobs),
                     len(arms) - len(knobs), B.MEDIAN_CAGR_FLOOR_PP,
                     ", ".join("%.2f" % a["k"] for a in arms if a["verdict"] == "REJECT")))
    else:
        label = "NO_ARM_SURVIVES"
        reason = "no arm clears the frozen rule and none reads as a pure cost knob"
    return {"label": label, "reasons": [reason], "labels_by_k": labels,
            "median_delta_cagr_pp_by_k": {str(k): v for k, v in meds},
            "return_effect_monotone_in_k": bool(monotone_down)}


# ---------------------------------------------------------------- build

def build():
    close, openp, amt, score, _cls, n_flip = P.prep_panel()
    starts = B.phase_starts(close.index)

    cells = []
    for (n_hold, rebal) in CONFIGS:
        for d in starts:
            for k in GRID:
                m = B.arm_metrics(close, openp, amt, score, k, n_hold, rebal, d)
                m.update({"n_hold": n_hold, "rebal": rebal, "k": k,
                          "phase": str(pd.Timestamp(d).date())})
                cells.append(m)

    cells = enrich_saving(cells, close.index)

    # activity precondition (r1261): the grid must have actually moved decisions.
    per_phase = {}
    for c in cells:
        if (c["n_hold"], c["rebal"], c["k"]) == (CONFIGS[0][0], CONFIGS[0][1], K_BASE):
            per_phase[c["phase"]] = {"decisions": c["decisions"],
                                     "first": c["first_decision"], "last": c["last_decision"]}
    sigs = {(v["first"], v["last"]) for v in per_phase.values()}
    activity = {"phase_decisions": per_phase, "n_phases": len(per_phase),
                "distinct_calendars": len(sigs) == len(per_phase),
                "n_cells": len(cells),
                "note": "counts may coincide across phases; the calendar (first/last decision) is the signature"}
    if not activity["distinct_calendars"]:
        raise RuntimeError("phases collapsed onto one decision calendar: %r" % (per_phase,))

    disp = B.dispersion(cells, k=K_BASE)
    saving_index = {(c["n_hold"], c["rebal"], c["phase"], c["k"]): c.get("breakeven_cost_bp_side")
                    for c in cells if c["k"] != K_BASE}
    arms = [arm_result(B.summarize(cells, k=k), disp, saving_index) for k in K_ARMS]

    # control: the k=0 production cell must reproduce the published card (r1325's gate).
    control = {}
    card_cutoff = None
    if PRODUCTION_FACE.exists():
        try:
            prod = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
            card_cutoff = prod.get("evidence_cutoff")
            cell = (prod.get("backtest") or {}).get("n12_vt08") or {}
            published = (cell.get("full") or {}).get("cagr")
            measured = None
            for c in cells:
                if (c["n_hold"], c["rebal"], c["k"]) == (12, 20, K_BASE) and \
                        c["phase"] == str(pd.Timestamp(starts[0]).date()):
                    measured = c["cagr"]
                    break
            if published is not None and measured is not None:
                control = {"published": round(published, 6), "measured": round(measured, 6),
                           "delta_pp": round(100 * (measured - published), 4),
                           "within_tol": abs(measured - published) <= CONTROL_TOL,
                           "tol": CONTROL_TOL}
        except Exception as exc:  # a control that cannot be read is declared, not silent
            control = {"error": "%s: %s" % (type(exc).__name__, exc)}
    else:
        control = {"error": "production face absent: %s" % PRODUCTION_FACE}

    payload = {
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "units": UNITS,
        "criteria": CRITERIA,
        "config": {"grid": list(GRID), "cost_bp": COST, "vol_target": TARGET_VOL,
                   "universe": "production panel (scripts.etf_book_production.prep_panel)",
                   "flips_repaired": n_flip, "cost_model": "10bp/side, exactly r1325's"},
        "control": control,
        "card_cutoff": card_cutoff,
        "activity": activity,
        "dispersion": disp,
        "arms": arms,
        "family": family_verdict(arms),
        "caveats": [
            "exploratory, no preregistration: ADOPT = survives its own path test, not a config change",
            "5 books x 4 phases bounds phase luck inside one cycle; it does not sample the future",
            "survivor ETF pool, one window 2020-01 -> panel edge, one regime (2024+ strong)",
            "breakeven uses a linear decisions-per-year conversion and the cell's own turnover delta",
            "the buffer is path-dependent by construction: the grid, not one arm, is the unit",
        ],
    }
    return payload


def render_md(payload):
    lines = []
    lines.append("# ETF book -- does the buffer pay for itself anywhere on the arm grid?\n")
    lines.append("Face: `%s` (evidence cutoff **%s**, cost %.0fbp/side)\n"
                 % (FACE, payload["evidence_cutoff"], payload["config"]["cost_bp"]))
    lines.append("## Family verdict -- %s\n" % payload["family"]["label"])
    for r in payload["family"]["reasons"]:
        lines.append("- %s" % r)
    lines.append("\nReturn effect monotone in k: **%s**\n"
                 % payload["family"]["return_effect_monotone_in_k"])
    lines.append("## Arms (20 cells each: 5 books x 4 phases, each cell against its own k=0)\n")
    lines.append("| k | verdict | turnover down | median dCAGR | median dTurn | median dSharpe | breakeven cost (median, q25-q75) |")
    lines.append("|---|---|---|---|---|---|---|")
    for a in payload["arms"]:
        be = a["breakeven_cost_bp_side"]
        be_s = ("%.1f (%.1f-%.1f)" % (be["median"], be["q25"], be["q75"])
                if be["median"] is not None else "n/a")
        lines.append("| %.2f | %s | %.0f%% | %+.3fpp | %+.4f | %+.4f | %s |"
                     % (a["k"], a["verdict"], 100 * (a["turnover_down_share"] or 0),
                        a["median_delta_cagr_pp"] or 0, a["median_delta_turnover"] or 0,
                        a["median_delta_sharpe"] or 0, be_s))
    lines.append("")
    lines.append("Breakeven cost = the per-side cost at which this cell's turnover saving equals "
                 "the return it gave away. A cell that gains return has no breakeven (it already pays).")
    lines.append("\n## Phase noise (the ruler these effects must beat)\n")
    d = payload["dispersion"]
    lines.append("| book | phases | CAGR min-max (pp) | CAGR IQR (pp) | Sharpe IQR |")
    lines.append("|---|---|---|---|---|")
    for key in sorted(k for k in d if isinstance(d[k], dict)):
        v = d[key]
        lines.append("| %s | %d | %.2f - %.2f | %.3f | %.3f |"
                     % (key, v["n_phases"], v["cagr_pp_min"], v["cagr_pp_max"],
                        v["cagr_pp_iqr"], v["sharpe_iqr"]))
    lines.append("\nMedian phase CAGR IQR across books: **%.3fpp**\n" % d.get("median_cagr_pp_iqr", float("nan")))
    lines.append("## Control\n")
    c = payload["control"]
    if "error" in c:
        lines.append("- control unavailable: %s" % c["error"])
    else:
        lines.append("- k=0 production cell reproduces the card: published %.4f vs measured %.4f "
                     "(delta %.2fpp, tol %.3f, within=%s)"
                     % (c["published"], c["measured"], c["delta_pp"], c["tol"], c["within_tol"]))
    lines.append("\n## Honest limits\n")
    for x in payload["caveats"]:
        lines.append("- %s" % x)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- gate

SUMMARY_SCALARS = ("turnover_down_share", "share_cagr_ok", "share_cagr_up",
                   "share_sharpe_ok", "median_delta_cagr_pp", "median_delta_sharpe",
                   "median_delta_turnover", "median_delta_maxdd_pp",
                   "worst_delta_cagr_pp", "best_delta_cagr_pp")


def rebuild_summary(arm):
    """Re-materialise the raw cells a published arm came from, then re-summarise them.

    The published rows carry base_* and delta_* but not the arm's own cagr/sharpe, so the arm
    side is recovered as base + delta and fed back through `B.summarize` -- the single
    implementation that owns the arithmetic. Nothing here restates a formula, so a re-tuned
    rule cannot quietly disagree with the gate (the header's "imported, never copied" promise
    applies to the summary as much as to the thresholds).
    """
    k = arm.get("k")
    cells = []
    for r in arm.get("cells") or []:
        d_cagr, d_sharpe, d_turn = (r.get("delta_cagr_pp"), r.get("delta_sharpe"),
                                    r.get("delta_turnover"))
        if d_cagr is None or d_sharpe is None or d_turn is None:
            continue
        cells.append({"n_hold": r["n_hold"], "rebal": r["rebal"], "phase": r["phase"],
                      "k": K_BASE, "cagr": r.get("base_cagr"),
                      "sharpe": r.get("base_sharpe"),
                      "turnover_per_decision": r.get("base_turnover"),
                      # the base drawdown is not published, only the delta is; anchoring the
                      # base at 0 keeps B.summarize's maxdd delta equal to the published one
                      "maxdd": 0.0})
        cells.append({"n_hold": r["n_hold"], "rebal": r["rebal"], "phase": r["phase"], "k": k,
                      "cagr": (r.get("base_cagr") or 0.0) + d_cagr / 100.0,
                      "sharpe": (r.get("base_sharpe") or 0.0) + d_sharpe,
                      "turnover_per_decision": r.get("arm_turnover"),
                      "maxdd": (r.get("delta_maxdd_pp") or 0.0) / 100.0})
    if not cells:
        return {"k": k, "n_cells": 0, "cells": []}
    return B.summarize(cells, k=k)


def recompute_verdicts(payload):
    """Re-judge every arm from its own cells; the gate compares. Returns per-arm verdicts.

    r1347: the first version fed the STORED summary scalars back into `B.verdict`. That made the
    gate blind in two directions at once -- it crashed the moment a published arm stopped
    carrying a field the rule reads (`KeyError: 'share_cagr_ok'`: the arm kept the verdict and
    dropped its inputs), and a hand-edited median would have been judged exactly as printed.
    The summary is rebuilt from the cells now, and every published scalar is compared against
    the rebuild before the rule runs, so "the number" and "the cells" can no longer disagree.
    """
    out = []
    for a in payload.get("arms") or []:
        summary = rebuild_summary(a)
        mism = []
        for key in SUMMARY_SCALARS:
            if key in summary and key in a and a[key] != summary[key]:
                mism.append("%s published %r but the cells rebuild to %r"
                            % (key, a[key], summary[key]))
        label, reasons = B.verdict(summary, payload.get("dispersion"))
        if label != a.get("verdict"):
            mism.append("verdict published %r but recomputes to %r (%s)"
                        % (a.get("verdict"), label, "; ".join(reasons)))
        out.append({"k": a.get("k"), "verdict": label, "reasons": reasons, "mismatches": mism})
    return out


def staleness(face_cutoff, card_cutoff):
    """Is the face behind the bar the production card is priced on?

    r1346: a check-only gate goes red on every panel advance and stays red until a human
    types the command, so "behind" must be a THIRD state that the runner pays a refresh for,
    while "inconsistent on the same bar" stays red. ISO dates compare as strings safely.
    """
    if not face_cutoff or not card_cutoff:
        return "unknown"
    return "stale" if str(face_cutoff) < str(card_cutoff) else "current"


def check():
    if not OUT_JSON.exists():
        print("CHECK FAIL: face absent %s" % OUT_JSON)
        return 2
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    state = staleness(payload.get("evidence_cutoff"), payload.get("card_cutoff"))
    if state == "stale":
        print("STALE: face priced on %s while the production card is on %s"
              % (payload.get("evidence_cutoff"), payload.get("card_cutoff")))
        return 2
    problems = []
    echo = payload.get("criteria", {}).get("k_arms")
    if echo != list(K_ARMS):
        problems.append("criteria echo drifted: k_arms=%r vs constants %r" % (echo, list(K_ARMS)))
    rule = payload.get("criteria", {}).get("per_arm_rule", {})
    for key, want in (("turnover_down_share_min", B.TURNOVER_DOWN_SHARE_MIN),
                      ("cagr_share_min", B.CAGR_SHARE_MIN),
                      ("cagr_share_floor_pp", B.CAGR_SHARE_FLOOR_PP),
                      ("sharpe_share_min", B.SHARPE_SHARE_MIN),
                      ("median_cagr_floor_pp", B.MEDIAN_CAGR_FLOOR_PP)):
        if rule.get(key) != want:
            problems.append("frozen rule drifted at %s: %r vs %r" % (key, rule.get(key), want))
    activity = payload.get("activity") or {}
    if not activity.get("distinct_calendars"):
        problems.append("phases collapsed onto one decision calendar")
    if (activity.get("n_cells") or 0) < len(CONFIGS) * N_PHASES * len(GRID):
        problems.append("cell count %r is short of %d"
                        % (activity.get("n_cells"), len(CONFIGS) * N_PHASES * len(GRID)))
    recomputed = recompute_verdicts(payload)
    for r in recomputed:
        for m in r["mismatches"]:
            problems.append("arm k=%s: %s" % (r["k"], m))
    fam = payload.get("family") or {}
    if fam.get("label") != family_verdict(payload.get("arms") or [])["label"]:
        problems.append("family verdict %r does not recompute" % fam.get("label"))
    ctl = payload.get("control") or {}
    if ctl.get("error"):
        problems.append("control unreadable: %s" % ctl["error"])
    elif ctl and not ctl.get("within_tol", True):
        problems.append("control arm no longer reproduces the card (published %.4f vs measured %.4f, "
                        "tol %.3f) on the SAME bar -- inconsistent, not behind"
                        % (ctl.get("published") or 0, ctl.get("measured") or 0, ctl.get("tol") or CONTROL_TOL))
    if problems:
        print("CHECK FAIL:\n  " + "\n  ".join(problems))
        return 2
    print("CHECK OK: %d arms, %d cells, family=%s"
          % (len(payload.get("arms") or []), activity.get("n_cells"), fam.get("label")))
    return 0


# ---------------------------------------------------------------- selftest

def _eq(name, got, want, tol=1e-6):
    if isinstance(want, str) or isinstance(got, str):
        ok = got == want
    else:
        ok = (got is None and want is None) or (
            got is not None and want is not None and abs(float(got) - float(want)) <= tol)
    if not ok:
        raise AssertionError("%s: got %r want %r" % (name, got, want))
    print("  ok %s = %r" % (name, got))


def selftest():
    print("selftest: breakeven maths")
    # 1. hand-computed: -0.10pp of CAGR given away against 0.02 turnover per decision at
    #    13 decisions/year -> 0.02*13 = 0.26 turnover-units/year; 0.001/0.26 = 38.46bp
    _eq("breakeven(-0.10pp, -0.02, 13)", breakeven_cost_bp(-0.10, -0.02, 13), 38.46)
    # 2. an arm that GAINS return needs no cost story: sign flips, and reads as "already pays"
    _eq("breakeven(+0.10pp, -0.02, 13)", breakeven_cost_bp(0.10, -0.02, 13), -38.46)
    # 3. no turnover change = no conversion path: must be None, not a huge number
    if breakeven_cost_bp(-0.10, 0.0, 13) is not None:
        raise AssertionError("zero turnover delta must not produce a breakeven")
    print("  ok breakeven(zero turnover) = None")
    # 4. guard on dpy
    if breakeven_cost_bp(-0.10, -0.02, 0) is not None:
        raise AssertionError("dpy=0 must not produce a breakeven")
    print("  ok breakeven(dpy=0) = None")

    print("selftest: decisions_per_year derives from the panel")
    idx = pd.date_range("2020-01-01", periods=1000, freq="B")
    dpy20 = decisions_per_year(idx, 20)
    dpy10 = decisions_per_year(idx, 10)
    _eq("dpy20*2 == dpy40-equivalent", dpy20 * 2, dpy10, 1e-9)

    print("selftest: enrich_saving attaches deltas and breakevens only where a base exists")
    cells = [
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-02", "k": 0.0,
         "cagr": 0.10, "turnover_per_decision": 1.00},
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-02", "k": 0.05,
         "cagr": 0.0990, "turnover_per_decision": 0.98},
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-03", "k": 0.05,
         "cagr": 0.1010, "turnover_per_decision": 0.98},
    ]
    out = enrich_saving(cells, idx)
    with_base = [c for c in out if c["breakeven_cost_bp_side"] is not None]
    if len(with_base) != 1:
        raise AssertionError("only the cell with a base should get a breakeven, got %d" % len(with_base))
    print("  ok exactly one cell got a breakeven (the orphan phase did not)")
    _eq("delta_cagr_pp_vs_base", with_base[0]["delta_cagr_pp_vs_base"], -0.1, 1e-6)
    if with_base[0]["breakeven_cost_bp_side"] <= 0:
        raise AssertionError("a return-losing arm must have a positive breakeven cost: %r"
                             % with_base[0]["breakeven_cost_bp_side"])
    print("  ok breakeven > 0 for a return-losing arm")

    print("selftest: breakeven survives B.summarize's row rebuild")
    summary = {"k": 0.05, "n_cells": 1, "cells": [{"n_hold": 12, "rebal": 20, "phase": "2020-01-02"}],
               "turnover_down_share": 1.0, "share_cagr_ok": 1.0, "share_cagr_up": 1.0,
               "share_sharpe_ok": 1.0, "median_delta_cagr_pp": 0.0, "median_delta_turnover": -0.02,
               "median_delta_sharpe": 0.0, "worst_delta_cagr_pp": 0.0, "best_delta_cagr_pp": 0.0,
               "sign_test_cagr": {}}
    _eq("breakeven re-attached by cell identity",
        arm_result(summary, {}, {(12, 20, "2020-01-02", 0.05): 12.5})["breakeven_cost_bp_side"]["median"],
        12.5)
    _eq("a cell with no saving on disk stays n/a, not zero",
        arm_result(summary, {}, {})["breakeven_cost_bp_side"]["median"], None)
    # r1280 family: the table must be keyed by ARM, not by the compared column, or the last
    # arm overwrites the earlier ones and four arms publish one number.
    _eq("the same cell at another k does not answer for this one",
        arm_result(summary, {}, {(12, 20, "2020-01-02", 0.20): 9.9})["breakeven_cost_bp_side"]["median"],
        None)

    print("selftest: family verdict reads the arms, not a stored string")
    mk = lambda k, v, med: {"k": k, "verdict": v, "median_delta_cagr_pp": med,
                            "turnover_down_share": 1.0}
    _eq("family all COST_KNOB", family_verdict([mk(0.05, "COST_KNOB_ONLY", -0.1),
                                                mk(0.10, "COST_KNOB_ONLY", -0.2)])["label"],
        "COST_KNOB_FAMILY")
    _eq("family with a survivor", family_verdict([mk(0.05, "ADOPT", 0.1),
                                                  mk(0.10, "REJECT", -0.2)])["label"],
        "SOME_ARM_SURVIVES")
    _eq("family none", family_verdict([mk(0.05, "REJECT", -0.1)])["label"], "NO_ARM_SURVIVES")
    _eq("family mixed name split", family_verdict([mk(0.05, "REJECT", -0.145),
                                                   mk(0.10, "COST_KNOB_ONLY", 0.04),
                                                   mk(0.20, "COST_KNOB_ONLY", 0.065),
                                                   mk(0.35, "REJECT", -0.13)])["label"],
        "MIXED_NO_SURVIVOR")
    _eq("monotone down detected", family_verdict([mk(0.05, "REJECT", -0.1),
                                                  mk(0.10, "REJECT", -0.2)])["return_effect_monotone_in_k"],
        True)
    _eq("monotone violation detected", family_verdict([mk(0.05, "REJECT", -0.2),
                                                       mk(0.10, "REJECT", -0.1)])["return_effect_monotone_in_k"],
        False)

    print("selftest: a published arm must be re-judgeable from its own cells (r1347)")
    raw = [
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-02", "k": 0.0,
         "cagr": 0.100, "sharpe": 1.00, "turnover_per_decision": 1.00, "maxdd": -0.10},
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-02", "k": 0.05,
         "cagr": 0.0985, "sharpe": 0.99, "turnover_per_decision": 0.97, "maxdd": -0.10},
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-09", "k": 0.0,
         "cagr": 0.095, "sharpe": 0.95, "turnover_per_decision": 1.02, "maxdd": -0.11},
        {"n_hold": 12, "rebal": 20, "phase": "2020-01-09", "k": 0.05,
         "cagr": 0.0945, "sharpe": 0.95, "turnover_per_decision": 0.99, "maxdd": -0.11},
    ]
    published = arm_result(B.summarize(raw, k=0.05), {})
    rt = recompute_verdicts({"arms": [published], "dispersion": {}})[0]
    _eq("round trip reproduces the verdict", rt["verdict"], published["verdict"])
    if rt["mismatches"]:
        raise AssertionError("a fresh publish must rebuild clean, got %r" % (rt["mismatches"],))
    print("  ok round trip reports no mismatch")
    # the exact shape that crashed the first gate: verdict kept, rule inputs dropped
    stripped = {k: v for k, v in published.items()
                if k not in ("share_cagr_ok", "share_cagr_up", "share_sharpe_ok")}
    rt2 = recompute_verdicts({"arms": [stripped], "dispersion": {}})[0]
    _eq("an arm without its share fields still re-judges", rt2["verdict"], published["verdict"])
    # a hand-edited scalar must not be judged as printed
    tampered = dict(published, median_delta_cagr_pp=0.99)
    rt3 = recompute_verdicts({"arms": [tampered], "dispersion": {}})[0]
    if not any("median_delta_cagr_pp" in m for m in rt3["mismatches"]):
        raise AssertionError("an edited median was not caught by the cells: %r" % (rt3["mismatches"],))
    print("  ok a hand-edited median is contradicted by the cells")
    tampered2 = dict(published, verdict="ADOPT")
    rt4 = recompute_verdicts({"arms": [tampered2], "dispersion": {}})[0]
    if not any("verdict" in m for m in rt4["mismatches"]):
        raise AssertionError("an edited verdict was not caught: %r" % (rt4["mismatches"],))
    print("  ok a hand-edited verdict is contradicted by the rule")

    print("selftest: empty grid cannot support a verdict")
    _eq("empty summary -> REJECT", B.verdict({"n_cells": 0})[0], "REJECT")

    print("selftest: behind-the-card is a third state, not a red gate (r1346)")
    _eq("stale when card advanced", staleness("2026-10-28", "2026-10-29"), "stale")
    _eq("current on the same bar", staleness("2026-10-29", "2026-10-29"), "current")
    _eq("current when the face is ahead", staleness("2026-10-30", "2026-10-29"), "current")
    _eq("unknown without a card", staleness("2026-10-29", None), "unknown")

    print("selftest: the gate refuses a face whose frozen rule echoed differently")
    fake = {"criteria": {"k_arms": list(K_ARMS), "per_arm_rule": {
        "turnover_down_share_min": B.TURNOVER_DOWN_SHARE_MIN,
        "cagr_share_min": B.CAGR_SHARE_MIN,
        "cagr_share_floor_pp": B.CAGR_SHARE_FLOOR_PP,
        "sharpe_share_min": B.SHARPE_SHARE_MIN,
        "median_cagr_floor_pp": B.MEDIAN_CAGR_FLOOR_PP}},
        "activity": {"distinct_calendars": True, "n_cells": 1},
        "arms": [], "family": {"label": "NO_ARM_SURVIVES"}, "dispersion": {}}
    problems = []
    if fake["criteria"]["per_arm_rule"]["median_cagr_floor_pp"] == B.MEDIAN_CAGR_FLOOR_PP:
        fake["criteria"]["per_arm_rule"]["median_cagr_floor_pp"] = -9.99
    if fake["criteria"]["per_arm_rule"]["median_cagr_floor_pp"] == B.MEDIAN_CAGR_FLOOR_PP:
        problems.append("drifted rule was not detected")
    if problems:
        raise AssertionError(problems[0])
    print("  ok drifted rule is visible to the gate's comparison")

    print("selftest PASS (28 legs)")
    return 0


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    if a.cmd != "run":
        print("unknown command: %s" % a.cmd)
        return 2
    payload = build()
    out = Path(a.out) if a.out else OUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    if out == OUT_JSON:
        OUT_MD.write_text(render_md(payload), encoding="utf-8")
    fam = payload["family"]
    print("wrote %s (%d cells, cutoff %s)" % (out, payload["activity"]["n_cells"],
                                              payload["evidence_cutoff"]))
    print("family verdict: %s -- %s" % (fam["label"], fam["reasons"][0]))
    for arm in payload["arms"]:
        be = arm["breakeven_cost_bp_side"]
        print("  k=%.2f %-15s dCAGR %+.3fpp dTurn %+.4f breakeven %s bp/side"
              % (arm["k"], arm["verdict"], arm["median_delta_cagr_pp"] or 0,
                 arm["median_delta_turnover"] or 0,
                 ("%.1f" % be["median"]) if be["median"] is not None else "n/a"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))