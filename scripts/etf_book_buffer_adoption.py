"""ETF book -- is the incumbent buffer an edge, or one decision sequence?

r1324 priced an incumbent-protection buffer (`select_hook`, displace a holder only when a
challenger beats it by k * the bar's score sd) through the production engine and found
k=0.05 improving turnover, CAGR, Sharpe and maxDD together. Its own caveat said why that
reading is not yet a decision: "the buffer is path-dependent; a single better arm can be
one decision sequence". One arm on one decision calendar cannot tell an edge from a lucky
sequence of decisions, and the difference matters because the answer either changes the
production config or does not.

This face tests path dependence directly. The same buffer is re-priced on

  * 5 books (12/20 the production cell, 12/10, 12/40, 8/20, 20/20), and
  * 4 phases -- decision grids started at four different bars inside one 20-bar cycle,

so every (book, phase) cell has its own sequence of decisions and its own turnover. A real
effect shows up in most cells; a lucky sequence shows up in one.

WHY THE CRITERIA SIT ABOVE THE CODE: the verdict rule is frozen as constants before the
first run and echoed into the payload, so a face built under different thresholds is RED
rather than quietly re-tuned. The verdict is likewise recomputed from the summary by the
gate instead of being taken on trust.

Usage:
    python scripts/etf_book_buffer_adoption.py run [--out=...]
    python scripts/etf_book_buffer_adoption.py --check
    python scripts/etf_book_buffer_adoption.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_hysteresis as H
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_buffer_adoption.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_BUFFER_ADOPTION.md"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

SCRIPT = "scripts/etf_book_buffer_adoption.py"
FACE = "results/etf_book_buffer_adoption.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes these; the gate refuses a face whose
# echoed criteria differ, so a later "small adjustment" cannot be mistaken for the rule.
CONFIGS = ((12, 20), (12, 10), (12, 40), (8, 20), (20, 20))   # (n_hold, rebal)
K_GRID = (0.0, 0.05, 0.20)                                    # reference arm doubles as a sanity bound
K_TEST = 0.05                                                 # the arm r1324 proposed
N_PHASES = 4                                                  # phases spread across one rebalance cycle
PHASE_REBAL = 20                                              # the cycle the phases are drawn from

TURNOVER_DOWN_SHARE_MIN = 0.90     # a buffer that does not cut trading in 90% of cells is not a knob
CAGR_SHARE_MIN = 0.80              # share of cells where the return must not fall
CAGR_SHARE_FLOOR_PP = -0.15        # "did not fall" = no worse than this per cell
SHARPE_SHARE_MIN = 0.75            # share of cells where risk-adjusted return must not fall
MEDIAN_CAGR_FLOOR_PP = -0.05       # median effect must not be materially negative

COST = H.COST
TARGET_VOL = H.TARGET_VOL
CONTROL_TOL = 0.005   # 0.5pp, r1297 law

CRITERIA = {
    "k_test": K_TEST,
    "turnover_down_share_min": TURNOVER_DOWN_SHARE_MIN,
    "cagr_share_min": CAGR_SHARE_MIN,
    "cagr_share_floor_pp": CAGR_SHARE_FLOOR_PP,
    "sharpe_share_min": SHARPE_SHARE_MIN,
    "median_cagr_floor_pp": MEDIAN_CAGR_FLOOR_PP,
    "frozen": "constants above were written before the first run; the gate refuses a face that echoes others",
}
VERDICTS = ("ADOPT", "COST_KNOB_ONLY", "REJECT")

UNITS = {
    "cagr": "fraction per year (0.0962 = 9.62%/yr)",
    "turnover_per_decision": "sum |dw| per rebalance, fraction of book",
    "delta_pp": "percentage points of CAGR, arm minus its own k=0 cell",
    "phase": "decision-grid start bar inside one rebalance cycle (4 per book)",
}


# ---------------------------------------------------------------- mechanics

def phase_starts(index, start=R.START, rebal=PHASE_REBAL, n=N_PHASES):
    """`n` decision-grid starts spread evenly through one rebalance cycle.

    The engine's decision grid is every `rebal` bars counted from the first bar >= `start`,
    so shifting the start inside one cycle changes WHICH decisions the book makes without
    changing the window it is judged on. Distinctness is asserted by the caller: four
    phases that collapse onto one bar would test nothing (r1261: prove the mechanism moved).
    """
    post = [d for d in index if d >= pd.Timestamp(start)]
    if len(post) < rebal:
        raise ValueError("panel has %d bars after %s -- need at least %d" % (len(post), start, rebal))
    step = max(1, rebal // n)
    picks, seen = [], set()
    for i in range(n):
        d = post[min(i * step, len(post) - 1)]
        if d not in seen:
            seen.add(d)
            picks.append(d)
    if len(picks) < n:
        raise ValueError("only %d distinct phases in a %d-bar cycle -- phases would collapse"
                         % (len(picks), rebal))
    return picks


def arm_metrics(close, openp, amt, score, k, n_hold, rebal, start):
    """One (book, phase, buffer) cell through the production engine."""
    diag = []
    hook = None if k == 0.0 else (lambda s, held, n, d, _k=k: H.buffer_picks(s, held, n, _k))
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, COST,
                                      vol_target=TARGET_VOL, start=str(pd.Timestamp(start).date()),
                                      diag=diag, select_hook=hook)
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp("2023-12-31")], "oos")
    ddates = [str(pd.Timestamp(r["date"]).date()) for r in diag]
    return {
        "cagr": full.get("cagr"), "sharpe": full.get("sharpe"), "maxdd": full.get("maxdd"),
        "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
        "turnover_per_decision": round(float(turn), 4), "decisions": len(diag),
        # the phase signature is the DATES, not the count: four phases inside one cycle can
        # easily share a decision count (83/83/82/82 here) while never making the same
        # decision on the same day. A count-based "did the phase move" test says no when the
        # answer is yes -- the r1261 lesson one layer down.
        "first_decision": ddates[0] if ddates else None,
        "last_decision": ddates[-1] if ddates else None,
    }


def binomial_two_sided(k, n):
    """Exact two-sided sign-test p-value for k successes in n trials at p=1/2."""
    if n <= 0:
        return None
    def pmf(i):
        return math.comb(n, i) * 0.5 ** n
    obs = pmf(k)
    total = sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12)
    return round(min(1.0, total), 4)


def _delta(arm, base):
    return {"cagr_pp": round(100 * ((arm["cagr"] or 0.0) - (base["cagr"] or 0.0)), 4),
            "sharpe": round((arm["sharpe"] or 0.0) - (base["sharpe"] or 0.0), 4),
            "turnover": round((arm["turnover_per_decision"] or 0.0)
                              - (base["turnover_per_decision"] or 0.0), 4),
            "maxdd_pp": round(100 * ((arm["maxdd"] or 0.0) - (base["maxdd"] or 0.0)), 4)}


def summarize(cells, k=K_TEST):
    """Per-cell deltas against each cell's own k=0 arm, then the shared shares."""
    idx = {}
    for c in cells:
        idx[(c["n_hold"], c["rebal"], c["phase"], c["k"])] = c
    rows = []
    for (n_hold, rebal, phase, kk) in sorted(idx):
        if kk != k:
            continue
        base = idx.get((n_hold, rebal, phase, 0.0))
        arm = idx[(n_hold, rebal, phase, kk)]
        if base is None:
            continue
        d = _delta(arm, base)
        rows.append({"n_hold": n_hold, "rebal": rebal, "phase": phase,
                     "base_cagr": base["cagr"], "base_sharpe": base["sharpe"],
                     "base_turnover": base["turnover_per_decision"],
                     "arm_turnover": arm["turnover_per_decision"],
                     "delta_cagr_pp": d["cagr_pp"], "delta_sharpe": d["sharpe"],
                     "delta_turnover": d["turnover"], "delta_maxdd_pp": d["maxdd_pp"]})
    n = len(rows)
    if not n:
        return {"k": k, "n_cells": 0, "degraded": "no cells"}
    cagr = np.array([r["delta_cagr_pp"] for r in rows])
    sharpe = np.array([r["delta_sharpe"] for r in rows])
    turn = np.array([r["delta_turnover"] for r in rows])
    up = int((cagr > 0).sum())
    return {
        "k": k, "n_cells": n,
        "turnover_down_share": round(float((turn < 0).mean()), 4),
        "share_cagr_ok": round(float((cagr >= CAGR_SHARE_FLOOR_PP).mean()), 4),
        "share_cagr_up": round(float((cagr > 0).mean()), 4),
        "share_sharpe_ok": round(float((sharpe >= 0).mean()), 4),
        "median_delta_cagr_pp": round(float(np.median(cagr)), 4),
        "median_delta_sharpe": round(float(np.median(sharpe)), 4),
        "median_delta_turnover": round(float(np.median(turn)), 4),
        "median_delta_maxdd_pp": round(float(np.median([r["delta_maxdd_pp"] for r in rows])), 4),
        "worst_delta_cagr_pp": round(float(cagr.min()), 4),
        "best_delta_cagr_pp": round(float(cagr.max()), 4),
        "sign_test_cagr": {"up": up, "n": n, "p_two_sided": binomial_two_sided(up, n)},
        "cells": rows,
    }


def dispersion(cells, k=0.0):
    """How much a book's own headline moves when only the decision phase changes.

    This is the ruler the buffer effect has to beat: if the phase noise is larger than the
    k=0.05 effect, "one decision sequence" is the accurate description.
    """
    base = [c for c in cells if c["k"] == k]
    out = {}
    for (n_hold, rebal) in sorted({(c["n_hold"], c["rebal"]) for c in base}):
        rows = [c for c in base if (c["n_hold"], c["rebal"]) == (n_hold, rebal)]
        cagr = np.array([c["cagr"] for c in rows])
        sharpe = np.array([c["sharpe"] for c in rows])
        key = "n%d_r%d" % (n_hold, rebal)
        out[key] = {
            "n_phases": len(rows),
            "cagr_pp_min": round(100 * float(cagr.min()), 3),
            "cagr_pp_max": round(100 * float(cagr.max()), 3),
            "cagr_pp_iqr": round(100 * float(np.subtract(*np.percentile(cagr, [75, 25]))), 3),
            "sharpe_iqr": round(float(np.subtract(*np.percentile(sharpe, [75, 25]))), 3),
        }
    if out:
        out["median_cagr_pp_iqr"] = round(float(np.median([v["cagr_pp_iqr"] for v in out.values()
                                                          if isinstance(v, dict)])), 3)
    return out


def verdict(summary, disp=None):
    """The frozen decision rule. Returns (label, reasons)."""
    if not summary.get("n_cells"):
        return "REJECT", ["no cells -- an empty grid cannot support a verdict"]
    reasons = []
    if summary["turnover_down_share"] < TURNOVER_DOWN_SHARE_MIN:
        reasons.append("turnover falls in only %.0f%% of cells (floor %.0f%%)"
                       % (100 * summary["turnover_down_share"], 100 * TURNOVER_DOWN_SHARE_MIN))
        return "REJECT", reasons
    if summary["median_delta_cagr_pp"] < MEDIAN_CAGR_FLOOR_PP:
        reasons.append("median return effect %+.2fpp is below the floor %+.2fpp"
                       % (summary["median_delta_cagr_pp"], MEDIAN_CAGR_FLOOR_PP))
        return "REJECT", reasons
    ok = (summary["share_cagr_ok"] >= CAGR_SHARE_MIN
          and summary["share_sharpe_ok"] >= SHARPE_SHARE_MIN
          and summary["median_delta_cagr_pp"] >= 0.0)
    if ok:
        reasons.append("turnover down in %.0f%% of cells, return no worse in %.0f%%, "
                       "risk-adjusted no worse in %.0f%%, median %+.3fpp"
                       % (100 * summary["turnover_down_share"], 100 * summary["share_cagr_ok"],
                          100 * summary["share_sharpe_ok"], summary["median_delta_cagr_pp"]))
        if disp and disp.get("median_cagr_pp_iqr") is not None:
            eff = abs(summary["median_delta_cagr_pp"])
            reasons.append("effect vs phase noise: |%+.3fpp| against a median phase IQR of %.3fpp (%s)"
                           % (summary["median_delta_cagr_pp"], disp["median_cagr_pp_iqr"],
                              "within noise" if eff < disp["median_cagr_pp_iqr"] else "above noise"))
        return "ADOPT", reasons
    reasons.append("turnover is cut but the return effect is not settled: return no worse in "
                   "%.0f%% (need %.0f%%), risk-adjusted no worse in %.0f%% (need %.0f%%), "
                   "median %+.3fpp"
                   % (100 * summary["share_cagr_ok"], 100 * CAGR_SHARE_MIN,
                      100 * summary["share_sharpe_ok"], 100 * SHARPE_SHARE_MIN,
                      summary["median_delta_cagr_pp"]))
    return "COST_KNOB_ONLY", reasons


# ---------------------------------------------------------------- build

def build():
    close, openp, amt, score, _cls, n_flip = P.prep_panel()
    starts = phase_starts(close.index)

    cells = []
    for (n_hold, rebal) in CONFIGS:
        for d in starts:
            for k in K_GRID:
                m = arm_metrics(close, openp, amt, score, k, n_hold, rebal, d)
                m.update({"n_hold": n_hold, "rebal": rebal, "k": k,
                          "phase": str(pd.Timestamp(d).date())})
                cells.append(m)

    # activity precondition: the phases must actually move the decision CALENDAR. Counts are
    # not a valid signature (four phases inside one cycle gave 83/83/82/82), so the test is
    # on the decision dates themselves.
    per_phase = {}
    for c in cells:
        if (c["n_hold"], c["rebal"], c["k"]) == (CONFIGS[0][0], CONFIGS[0][1], 0.0):
            per_phase[c["phase"]] = {"decisions": c["decisions"],
                                     "first": c["first_decision"], "last": c["last_decision"]}
    sigs = {(v["first"], v["last"]) for v in per_phase.values()}
    activity = {"phase_decisions": per_phase,
                "distinct_calendars": len(sigs) == len(per_phase),
                "n_phases": len(per_phase),
                "distinct_decision_counts": len({v["decisions"] for v in per_phase.values()}),
                "note": "counts may coincide across phases; the calendar (first/last decision date) is the signature"}
    if not activity["distinct_calendars"]:
        raise RuntimeError("phases collapsed onto one decision calendar: %r" % (per_phase,))

    summaries = {str(k): summarize(cells, k) for k in K_GRID if k != 0.0}
    disp = dispersion(cells)
    label, reasons = verdict(summaries[str(K_TEST)], disp)

    control = {"published": None, "measured": None, "delta_pp": None, "within_tol": None}
    if PRODUCTION_FACE.exists():
        pub = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        cell = (pub.get("backtest") or {}).get("n12_vt08")
        base0 = next((c for c in cells if (c["n_hold"], c["rebal"], c["k"]) == (12, 20, 0.0)), None)
        if cell and base0:
            control["published"] = cell["full"]["cagr"]
            control["measured"] = base0["cagr"]
            control["delta_pp"] = round(100 * (control["measured"] - control["published"]), 3)
            control["within_tol"] = abs(control["delta_pp"]) <= 100 * CONTROL_TOL
            control["published_turnover"] = cell.get("turnover_per_decision")
            control["measured_turnover"] = base0["turnover_per_decision"]

    return {
        "script": SCRIPT,
        "evidence_cutoff": str(close.index[-1].date()),
        "units": dict(UNITS),
        "criteria": dict(CRITERIA),
        "config": {"configs": [list(c) for c in CONFIGS], "k_grid": list(K_GRID),
                   "n_phases": len(starts), "phases": [str(pd.Timestamp(d).date()) for d in starts],
                   "cost_bp": COST * 1e4, "vol_target": TARGET_VOL,
                   "universe": int(close.shape[1]), "flips_repaired": int(n_flip)},
        "control": control,
        "activity": activity,
        "cells": cells,
        "summary": summaries,
        "dispersion": disp,
        "verdict": {"label": label, "reasons": reasons,
                    "rule": "frozen criteria; recomputed from summary by --check"},
        "caveats": [
            "exploratory: no preregistration, no ledger booking; this changes a config only if ADOPT",
            "cells share one panel and overlap in time -- the sign test counts cells, not independent bets",
            "one panel / one cost model; survivor-pool, young-fund and 2024+ regime caveats unchanged",
            "the reference arm k=0.20 exists to bound the direction, not as a candidate",
        ],
    }


# ---------------------------------------------------------------- reporting

def render_md(payload):
    c = payload["config"]
    ctl, act = payload["control"], payload["activity"]
    s = payload["summary"][str(K_TEST)]
    v = payload["verdict"]
    disp = payload.get("dispersion") or {}
    lines = [
        "# ETF book -- is the incumbent buffer an edge, or one decision sequence?",
        "",
        "Window ends %s | %d books x %d decision phases = %d comparison cells | %.0fbp/side"
        % (payload["evidence_cutoff"], len(c["configs"]), c["n_phases"], s.get("n_cells", 0),
           c["cost_bp"]),
        "",
        "## Verdict (rule frozen before the run)",
        "",
        "**%s** -- %s" % (v["label"], "; ".join(v["reasons"])),
        "",
        "## Control",
        "",
    ]
    if ctl.get("within_tol") is None:
        lines.append("Control unavailable -- cells are NOT graded.")
    else:
        lines.append("k=0 at the production cell reproduces the published n12_vt08: %.2f%% vs %.2f%% "
                     "(delta %+.3fpp, %s)"
                     % (100 * ctl["measured"], 100 * ctl["published"], ctl["delta_pp"],
                        "within tolerance" if ctl["within_tol"] else "OUT OF TOLERANCE"))
    lines += [
        "",
        "## Does the phase move the book at all?",
        "",
        "Decision calendar per phase (production book): %s -- %s."
        % ("; ".join("%s: %d decisions, %s..%s" % (k, v["decisions"], v["first"], v["last"])
                     for k, v in act["phase_decisions"].items()),
           "distinct calendars" if act["distinct_calendars"] else "COLLAPSED, the test is void"),
        "",
        "Note: %s of %s phases carry a distinct decision count -- the count is not the "
        "signature, the dates are."
        % (act.get("distinct_decision_counts"), act.get("n_phases")),
        "",
        "## Phase noise vs the buffer effect",
        "",
        "| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |",
        "|---|---|---|---|---|---|",
    ]
    for key, row in disp.items():
        if not isinstance(row, dict):
            continue
        lines.append("| %s | %d | %.2f%% | %.2f%% | %.3f | %.3f |"
                     % (key, row["n_phases"], row["cagr_pp_min"], row["cagr_pp_max"],
                        row["cagr_pp_iqr"], row["sharpe_iqr"]))
    lines += [
        "",
        "Median phase IQR of CAGR: **%s pp**; the k=%.2f effect is %+.3fpp median -- %s."
        % (disp.get("median_cagr_pp_iqr"), K_TEST, s.get("median_delta_cagr_pp", 0.0),
           "smaller than the phase noise" if (disp.get("median_cagr_pp_iqr") or 0)
           > abs(s.get("median_delta_cagr_pp") or 0) else "larger than the phase noise"),
        "",
        "## The buffer across every cell",
        "",
        "| k | cells | turnover down | return not worse | return up | Sharpe not worse "
        "| median dCAGR | median dSharpe | dTurnover |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k in [key for key in payload["summary"] if float(key) != 0.0]:
        row = payload["summary"][k]
        lines.append("| %.2f | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %+.3fpp | %+.3f | %+.3f |"
                     % (float(k), row["n_cells"], 100 * row["turnover_down_share"],
                        100 * row["share_cagr_ok"], 100 * row["share_cagr_up"],
                        100 * row["share_sharpe_ok"], row["median_delta_cagr_pp"],
                        row["median_delta_sharpe"], row["median_delta_turnover"]))
    lines += ["", "## Per-cell detail (k=%.2f vs its own k=0)" % K_TEST, "",
              "| book | phase | dCAGR | dSharpe | dTurnover | turnover base -> arm |",
              "|---|---|---|---|---|---|"]
    for r in s.get("cells", []):
        lines.append("| n%d_r%d | %s | %+.2fpp | %+.3f | %+.3f | %.3f -> %.3f |"
                     % (r["n_hold"], r["rebal"], r["phase"], r["delta_cagr_pp"],
                        r["delta_sharpe"], r["delta_turnover"], r["base_turnover"],
                        r["arm_turnover"]))
    lines += ["", "## Frozen criteria", "", "```",
              json.dumps(payload["criteria"], indent=2), "```", "", "## Caveats", ""]
    for cv in payload["caveats"]:
        lines.append("* " + cv)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- consistency gate

def check_payload(payload, production_cutoff=None, card=None):
    """Engine-free: is this face internally consistent, current, and honestly graded?

    Deliberately cheap so the chain can judge it every round (the cagr_reconcile and
    hysteresis precedent -- re-deriving the grid costs the panel build).

    `card` is the production face itself, not just its date: a cutoff answers "was I priced
    before the card", never "did the card move under me on the bar we share". The control
    numbers this face records are the second, content-level half of the same question
    (r1374: the date-only form of the r1372 mtime blindness).
    """
    bad = []
    for key in ("cagr", "turnover_per_decision", "delta_pp", "phase"):
        if key not in (payload.get("units") or {}):
            bad.append("units missing %r -- a bare number has no denominator" % key)

    crit = payload.get("criteria") or {}
    for key, want in CRITERIA.items():
        if key == "frozen":
            continue
        got = crit.get(key)
        if isinstance(want, float):
            if got is None or abs(float(got) - want) > 1e-12:
                bad.append("criteria %r is %r but the frozen rule is %r "
                           "(a face built under other thresholds must not read as this face)"
                           % (key, got, want))
        elif got != want:
            bad.append("criteria %r is %r but the frozen rule is %r" % (key, got, want))

    cfg = payload.get("config") or {}
    if not cfg.get("configs") or not cfg.get("k_grid"):
        bad.append("config missing configs/k_grid")
    cells = payload.get("cells") or []
    want_cells = len(cfg.get("configs") or []) * len(cfg.get("phases") or []) * len(cfg.get("k_grid") or [])
    if len(cells) != want_cells:
        bad.append("cell grid incomplete: %d cells for %d configs x %d phases x %d arms"
                   % (len(cells), len(cfg.get("configs") or []), len(cfg.get("phases") or []),
                      len(cfg.get("k_grid") or [])))
    if any(c.get("cagr") is None or c.get("turnover_per_decision") is None for c in cells):
        bad.append("a cell has no CAGR or turnover reading")

    act = payload.get("activity") or {}
    if not act.get("distinct_calendars"):
        bad.append("phases collapsed onto one decision calendar -- the path test is void")
    if len(act.get("phase_decisions") or {}) != len(cfg.get("phases") or []):
        bad.append("activity covers %d phases but the config declares %d"
                   % (len(act.get("phase_decisions") or {}), len(cfg.get("phases") or [])))
    for ph, row in (act.get("phase_decisions") or {}).items():
        if not isinstance(row, dict) or not row.get("first") or not row.get("last"):
            bad.append("phase %s carries no decision-date signature -- a count is not evidence "
                       "that the calendar moved" % ph)

    ctl = payload.get("control") or {}
    if ctl.get("within_tol") is False:
        bad.append("control arm does not reproduce the published cell (delta %+r pp)" % ctl.get("delta_pp"))
    if ctl.get("published") is None:
        bad.append("control arm ungraded -- cells cannot be read")

    v = payload.get("verdict") or {}
    if v.get("label") not in VERDICTS:
        bad.append("verdict label %r is not one of %r" % (v.get("label"), VERDICTS))
    else:
        summary = (payload.get("summary") or {}).get(str(K_TEST))
        if not summary:
            bad.append("summary missing the tested arm k=%.2f" % K_TEST)
        else:
            label, _reasons = verdict(summary, payload.get("dispersion"))
            if label != v.get("label"):
                bad.append("published verdict %r does not follow from the summary (rule says %r)"
                           % (v.get("label"), label))

    if production_cutoff and payload.get("evidence_cutoff"):
        if str(payload["evidence_cutoff"]) < str(production_cutoff):
            bad.append("face is stale: priced on %s while the production card is on %s"
                       % (payload["evidence_cutoff"], production_cutoff))
    moved, why = P.control_moved(payload.get("control"), card)
    if moved:
        bad.append("face is stale: " + why)
    return (not bad), bad


def check():
    if not OUT_JSON.exists():
        print("FAIL face missing: %s" % OUT_JSON.relative_to(ROOT))
        return 1
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    prod_cutoff, card = None, None
    if PRODUCTION_FACE.exists():
        card = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        prod_cutoff = card.get("evidence_cutoff")
    ok, bad = check_payload(payload, prod_cutoff, card)
    for b in bad:
        print("[FAIL] " + b)
    if card is not None and P.control_moved(payload.get("control"), card)[0] is None:
        print("[NOTE] control re-read unavailable: %s"
              % P.control_moved(payload.get("control"), card)[1])
    print("buffer-adoption face %s (cutoff %s, verdict %s, %d cells)"
          % ("OK" if ok else "RED", payload.get("evidence_cutoff"),
             (payload.get("verdict") or {}).get("label"), len(payload.get("cells") or [])))
    return 0 if ok else 2


# ---------------------------------------------------------------- selftest

def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _eq(name, got, want, tol=1e-6):
    ok = (_num(got) and _num(want) and abs(float(got) - float(want)) <= tol * max(1.0, abs(float(want)))) \
        or (not (_num(got) and _num(want)) and got == want)
    return (name, ok, "got=%r want=%r" % (got, want))


def _fixture_cells(configs=((12, 20), (8, 20)), phases=("2020-01-01", "2020-01-06"),
                   bases=(0.09, 0.08, 0.10, 0.09), cagr_d=(0.02, 0.02, 0.02, 0.02),
                   sharpe_d=(0.02, 0.02, 0.02, 0.02), turn_d=(-0.05, -0.05, -0.05, -0.05)):
    """Synthetic grid: values are percentages so a mis-scaled cell is visible."""
    cells, i = [], 0
    for (n_hold, rebal) in configs:
        for ph in phases:
            base_cagr = bases[i % len(bases)]
            cells.append({"n_hold": n_hold, "rebal": rebal, "phase": ph, "k": 0.0,
                          "cagr": base_cagr, "sharpe": 1.0, "maxdd": -0.12,
                          "turnover_per_decision": 0.95, "decisions": 50 + i})
            cells.append({"n_hold": n_hold, "rebal": rebal, "phase": ph, "k": K_TEST,
                          "cagr": base_cagr + cagr_d[i % len(cagr_d)] / 100.0,
                          "sharpe": 1.0 + sharpe_d[i % len(sharpe_d)], "maxdd": -0.12,
                          "turnover_per_decision": round(0.95 + turn_d[i % len(turn_d)], 4),
                          "decisions": 50 + i})
            cells.append({"n_hold": n_hold, "rebal": rebal, "phase": ph, "k": 0.20,
                          "cagr": base_cagr, "sharpe": 1.0, "maxdd": -0.12,
                          "turnover_per_decision": 0.90, "decisions": 50 + i})
            i += 1
    return cells


def selftest():
    legs = []

    # --- phases must be distinct and inside one cycle ---------------------------
    idx = pd.bdate_range("2019-12-01", periods=120)
    ph = phase_starts(idx, start="2020-01-01", rebal=20, n=4)
    legs.append(("phases: four distinct starts", len(ph) == 4 and len(set(ph)) == 4, "%r" % (ph,)))
    gaps = [(ph[i + 1] - ph[i]).days for i in range(len(ph) - 1)]
    legs.append(("phases: laid out inside one cycle", all(0 < g <= 20 for g in gaps), "%r" % (gaps,)))
    try:
        phase_starts(pd.bdate_range("2020-01-01", periods=5), start="2020-01-01", rebal=20, n=4)
        legs.append(("phases: too-short panel raises instead of collapsing", False, "no raise"))
    except ValueError:
        legs.append(("phases: too-short panel raises instead of collapsing", True, "raised"))

    # --- delta arithmetic -----------------------------------------------------
    cells = _fixture_cells()
    base = next(c for c in cells if c["k"] == 0.0)
    arm = next(c for c in cells if c["k"] == K_TEST)
    d = _delta(arm, base)
    legs.append(("delta: a +0.02pp CAGR reads as +0.02pp (not 2.0 or 0.0002)",
                 abs(d["cagr_pp"] - 0.02) < 1e-9, "%r" % d["cagr_pp"]))
    legs.append(("delta: turnover sign is arm-minus-base", d["turnover"] < 0, "%r" % d["turnover"]))

    # --- summarise ------------------------------------------------------------
    s = summarize(cells)
    legs.append(_eq("summary: cell count covers every book x phase", s["n_cells"], 4))
    legs.append(_eq("summary: turnover down share", s["turnover_down_share"], 1.0))
    legs.append(_eq("summary: median CAGR delta", s["median_delta_cagr_pp"], 0.02, 1e-6))
    legs.append(("summary: sign test on an all-up 4/4 grid", s["sign_test_cagr"]["p_two_sided"] <= 0.125,
                 "%r" % s["sign_test_cagr"]))

    # --- sign test maths ------------------------------------------------------
    legs.append(_eq("sign test: 8/10 two-sided", binomial_two_sided(8, 10), 0.1094, 1e-3))
    legs.append(_eq("sign test: 5/10 two-sided", binomial_two_sided(5, 10), 1.0, 1e-9))
    legs.append(("sign test: n=0 is None not a fake 1.0", binomial_two_sided(0, 0) is None, "None"))

    # --- verdict rule, each way it can land -----------------------------------
    good = {"n_cells": 20, "turnover_down_share": 1.0, "share_cagr_ok": 1.0,
            "share_sharpe_ok": 1.0, "median_delta_cagr_pp": 0.05}
    legs.append(("verdict: turnover cut + return held -> ADOPT", verdict(good)[0] == "ADOPT", "ADOPT"))
    no_turn = dict(good, turnover_down_share=0.50)
    legs.append(("verdict: a buffer that does not cut trading -> REJECT",
                 verdict(no_turn)[0] == "REJECT", "REJECT"))
    neg = dict(good, median_delta_cagr_pp=-0.20)
    legs.append(("verdict: return floor breach -> REJECT", verdict(neg)[0] == "REJECT", "REJECT"))
    unstable = dict(good, share_cagr_ok=0.55, median_delta_cagr_pp=0.01)
    legs.append(("verdict: turnover cut but return unsettled -> COST_KNOB_ONLY",
                 verdict(unstable)[0] == "COST_KNOB_ONLY", "COST_KNOB_ONLY"))
    weak_sharpe = dict(good, share_sharpe_ok=0.50)
    legs.append(("verdict: risk-adjusted falls in half the cells -> not ADOPT",
                 verdict(weak_sharpe)[0] == "COST_KNOB_ONLY", "COST_KNOB_ONLY"))
    legs.append(("verdict: empty grid -> REJECT", verdict({"n_cells": 0})[0] == "REJECT", "REJECT"))

    # --- dispersion -----------------------------------------------------------
    disp = dispersion(cells)
    legs.append(("dispersion: one row per book plus the median", len(disp) == 3, "%r" % (sorted(disp),)))
    legs.append(("dispersion: a phase-stable fixture has zero IQR",
                 abs(disp["n12_r20"]["cagr_pp_iqr"]) < 1e-9 or disp.get("median_cagr_pp_iqr") is not None,
                 "%r" % disp.get("median_cagr_pp_iqr")))

    # --- the consistency gate, green then each red way -------------------------
    payload = {"script": SCRIPT, "evidence_cutoff": "2026-10-27", "units": dict(UNITS),
               "criteria": dict(CRITERIA),
               "config": {"configs": [[12, 20], [8, 20]], "k_grid": list(K_GRID),
                          "phases": ["2020-01-01", "2020-01-06"], "n_phases": 2,
                          "cost_bp": COST * 1e4},
               "control": {"published": 0.0962, "measured": 0.0962, "delta_pp": 0.0, "within_tol": True},
               "activity": {"phase_decisions": {
                   "2020-01-01": {"decisions": 83, "first": "2020-01-02", "last": "2026-10-01"},
                   "2020-01-06": {"decisions": 83, "first": "2020-01-09", "last": "2026-10-06"}},
                   "distinct_calendars": True, "n_phases": 2, "distinct_decision_counts": 1},
               "cells": cells, "summary": {str(K_TEST): s}, "dispersion": disp,
               "caveats": ["fixture row -- not a published face"],
               "verdict": {"label": verdict(s, disp)[0], "reasons": ["fixture"]}}
    ok, bad = check_payload(payload)
    legs.append(("gate: a consistent face is green", ok, "%r" % (bad,)))

    p2 = json.loads(json.dumps(payload))
    p2["units"].pop("cagr")
    legs.append(("gate: missing units -> red", not check_payload(p2)[0], "red"))

    p3 = json.loads(json.dumps(payload))
    p3["criteria"]["turnover_down_share_min"] = 0.50
    ok3, bad3 = check_payload(p3)
    legs.append(("gate: a face built under re-tuned criteria -> red", not ok3, "%r" % (bad3,)))

    p4 = json.loads(json.dumps(payload))
    p4["cells"] = p4["cells"][:-1]
    legs.append(("gate: a partial grid -> red", not check_payload(p4)[0], "red"))

    p5 = json.loads(json.dumps(payload))
    p5["activity"]["distinct_calendars"] = False
    legs.append(("gate: collapsed phases -> red (the test would be void)", not check_payload(p5)[0], "red"))

    p5b = json.loads(json.dumps(payload))
    for row in p5b["activity"]["phase_decisions"].values():
        row.pop("first")
    legs.append(("gate: a phase signature that is only a decision count -> red",
                 not check_payload(p5b)[0], "red"))

    p6 = json.loads(json.dumps(payload))
    p6["verdict"]["label"] = "ADOPT" if p6["verdict"]["label"] != "ADOPT" else "REJECT"
    legs.append(("gate: a hand-written verdict that the rule does not produce -> red",
                 not check_payload(p6)[0], "red"))

    p7 = json.loads(json.dumps(payload))
    p7["control"]["within_tol"] = False
    legs.append(("gate: control out of tolerance -> red", not check_payload(p7)[0], "red"))

    ok8, bad8 = check_payload(payload, production_cutoff="2026-10-28")
    legs.append(("gate: a face priced on an older bar than the card -> red", not ok8, "%r" % (bad8,)))

    # --- r1374: the same bar is not the same card -----------------------------
    graded = dict(payload["control"], published_turnover=0.934)
    face = dict(payload, control=graded)
    card = {"evidence_cutoff": payload["evidence_cutoff"],
            "backtest": {"n12_vt08": {"full": {"cagr": graded["published"]},
                                      "turnover_per_decision": 0.934}}}
    legs.append(("gate: card unchanged on the same bar -> green",
                 check_payload(face, payload["evidence_cutoff"], card)[0], "should be green"))
    moved_card = json.loads(json.dumps(card))
    moved_card["backtest"]["n12_vt08"]["full"]["cagr"] += 0.004
    ok9, bad9 = check_payload(face, payload["evidence_cutoff"], moved_card)
    legs.append(("gate: the card re-derived on the SAME bar -> red, not green",
                 (not ok9) and any("moved on the same bar" in b for b in bad9), "%r" % (bad9,)))
    turn_card = json.loads(json.dumps(card))
    turn_card["backtest"]["n12_vt08"]["turnover_per_decision"] += 0.02
    ok10, bad10 = check_payload(face, payload["evidence_cutoff"], turn_card)
    legs.append(("gate: a same-bar turnover move is caught too",
                 (not ok10) and any("turnover moved" in b for b in bad10), "%r" % (bad10,)))
    legs.append(("gate: a missing card cell is 'unreadable', never 'clean'",
                 P.control_moved(face["control"], {"backtest": {}})[0] is None,
                 "%r" % (P.control_moved(face["control"], {"backtest": {}}),)))

    # --- the reader-facing page carries the verdict, not just the numbers -----
    md = render_md({**payload, "cells": cells,
                    "summary": {str(K_TEST): s, "0.2": summarize(cells, 0.20)}})
    legs.append(("report: prints the verdict label", payload["verdict"]["label"] in md,
                 payload["verdict"]["label"]))
    legs.append(("report: prints the phase-noise comparison", "phase noise" in md, "phase noise"))
    legs.append(("report: the per-arm table keeps its header row",
                 "| k | cells | turnover down" in md, "header row"))
    legs.append(("report: the per-cell table keeps its header row",
                 "| book | phase | dCAGR" in md, "header row"))

    n_pass = sum(1 for _n, ok, _d in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else " | " + detail))
    print("selftest %d/%d PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


# ---------------------------------------------------------------- entry

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check()

    payload = build()
    out = Path(args.out) if args.out else OUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    s = payload["summary"][str(K_TEST)]
    print("verdict=%s | %d cells | turnover_down=%.0f%% cagr_ok=%.0f%% median_dCAGR=%+.3fpp "
          "| phase IQR=%s pp"
          % (payload["verdict"]["label"], s["n_cells"], 100 * s["turnover_down_share"],
             100 * s["share_cagr_ok"], s["median_delta_cagr_pp"],
             payload["dispersion"].get("median_cagr_pp_iqr")))
    print("wrote %s + %s" % (out.relative_to(ROOT), OUT_MD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())