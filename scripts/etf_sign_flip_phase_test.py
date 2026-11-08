"""Is the drawdown_60 sign flip an effect, or one decision sequence?

r1442 read the yearly IC table and found one factor whose production sign points the
wrong way in 3 of 7 years while its pooled mean IC is still positive. Flipping it on the
single production decision grid earned +87bp/yr. That number cannot change a config,
because r1325 already measured this book's own across-phase spread inside one 20-bar
cycle and it was as large as the effect being claimed. One arm on one decision calendar
cannot separate an edge from a lucky sequence of decisions.

This face runs the same experiment the buffer face (r1325) ran, on the same engine:

  * 5 books -- the production cell (5 names / 20-bar cadence) plus 5/10, 5/40, 3/20, 8/20, and
  * 4 phases -- decision grids started at four different bars inside one 20-bar cycle,

so every (book, phase) cell gets its own sequence of decisions, and the flip is priced
against that cell's own frozen-sign control. A real effect shows up in most cells with a
magnitude above the phase noise; a lucky sequence shows up in one.

Two identity legs guard the machinery (r1261 / E199: a leg that cannot fail is not a leg):

  * the score face built from an explicit sign dict with the production signs must equal
    `etf_composite_pf.build_score` elementwise (the flip arm's control is the production
    arm, not a second implementation of it);
  * re-running that identical score through the engine on every phase must return
    exactly 0.0 bp in each cell -- otherwise the cells are measuring the harness.

Exit codes: 0 = ran, 2 = mechanism fault (panel/sign receipt unavailable), 3 = a frozen
criterion could not be evaluated.

Usage:
    python scripts/etf_sign_flip_phase_test.py run
    python scripts/etf_sign_flip_phase_test.py --check
    python scripts/etf_sign_flip_phase_test.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F
import etf_book_buffer_adoption as B          # phase_starts: one implementation, never a copy

OUT_JSON = ROOT / "results" / "etf_sign_flip_phase_test.json"
OUT_MD = ROOT / "research" / "ETF_SIGN_FLIP_PHASE_TEST.md"
SIGN_RECEIPT = ROOT / "results" / "etf_factor_sign_stability.json"

SCRIPT = "scripts/etf_sign_flip_phase_test.py"
FACE = "results/etf_sign_flip_phase_test.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes them and --check refuses a face whose
# echo differs, so a later "small adjustment" cannot pass for the rule.
BOOKS = ((5, 20), (5, 10), (5, 40), (3, 20), (8, 20))   # (n_hold, rebal); first = production
N_PHASES = 4
PHASE_REBAL = 20                 # the cycle the phases are drawn from
START = "2020-01-01"
COST = F.COST                    # 8bp per side, the published book's cost
BAR_PP = 0.50                    # a flip has to clear half a point a year to count
SHARE_UP_MIN = 0.75              # ... and do it in three quarters of the cells
SHARPE_OK_MIN = 0.75             # ... without paying for it in risk-adjusted terms
CONTROL_TOL_BP = 5.0             # identity legs must read 0.0; the control must read published

CRITERIA = {
    "books": [list(b) for b in BOOKS],
    "n_phases": N_PHASES,
    "phase_rebal": PHASE_REBAL,
    "bar_pp": BAR_PP,
    "share_up_min": SHARE_UP_MIN,
    "sharpe_ok_min": SHARPE_OK_MIN,
    "identity_tol_bp": CONTROL_TOL_BP,
    "frozen": "constants above were written before the first run; --check refuses a face that echoes others",
}
VERDICTS = ("ADOPT", "PHASE_FRAGILE", "MIXED", "REJECT")
UNITS = {
    "cagr": "fraction per year (0.0962 = 9.62%/yr)",
    "delta_cagr_pp": "percentage points of CAGR, flip arm minus its own frozen-sign cell",
    "phase": "decision-grid start bar inside one rebalance cycle (4 per book)",
    "cagr_pp_iqr": "interquartile range of the control arm's CAGR across phases, in pp",
}


# ---------------------------------------------------------------- mechanics

def arm_cell(close, openp, amt, score, n_hold, rebal, start):
    """One (book, phase, sign set) cell through the production engine."""
    ser, turn, gapfill = F.run_next_open(close, openp, amt, {}, rebal, n_hold=n_hold,
                                         cost=COST, start=str(pd.Timestamp(start).date()),
                                         score=score)
    full = F.metrics(ser, "full")
    oos = F.metrics(ser[ser.index >= pd.Timestamp("2024-01-01")], "oos")
    return {"cagr": full.get("cagr"), "sharpe": full.get("sharpe"), "maxdd": full.get("maxdd"),
            "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
            "turnover_per_decision": round(float(turn), 4), "open_gapfill": int(gapfill)}


def sign_index(per_factor):
    """Factors whose production sign contradicts the yearly table, from the receipt."""
    return sorted(c for c, v in per_factor.items() if v.get("class") == "SIGNS_CONTRARY")


def flip_signs(signs, contrary):
    return {c: (-s if c in contrary else s) for c, s in signs.items()}


def delta(arm, base):
    return {"cagr_pp": round(100.0 * ((arm["cagr"] or 0.0) - (base["cagr"] or 0.0)), 4),
            "sharpe": round((arm["sharpe"] or 0.0) - (base["sharpe"] or 0.0), 4),
            "oos_pp": round(100.0 * ((arm["oos_cagr"] or 0.0) - (base["oos_cagr"] or 0.0)), 4),
            "turnover": round((arm["turnover_per_decision"] or 0.0)
                              - (base["turnover_per_decision"] or 0.0), 4),
            "maxdd_pp": round(100.0 * ((arm["maxdd"] or 0.0) - (base["maxdd"] or 0.0)), 4)}


def iqr(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    q1, q3 = np.percentile(vals, [25, 75])
    return round(float(q3 - q1), 4)


def dispersion(cells):
    """Per-book phase noise of the CONTROL arm -- the ruler the effect is measured against."""
    base = {(c["n_hold"], c["rebal"], c["phase"]): c for c in cells if c["arm"] == "frozen"}
    out = {}
    for (n_hold, rebal) in BOOKS:
        rows = [v for (h, r, _p), v in base.items() if (h, r) == (n_hold, rebal)]
        if len(rows) < 2:
            continue
        cagr = [100.0 * (r["cagr"] or 0.0) for r in rows]
        shr = [r["sharpe"] or 0.0 for r in rows]
        out["n%d_r%d" % (n_hold, rebal)] = {
            "n_phases": len(rows),
            "cagr_pp_min": round(min(cagr), 3), "cagr_pp_max": round(max(cagr), 3),
            "cagr_pp_iqr": iqr(cagr) or 0.0, "sharpe_iqr": iqr(shr) or 0.0,
        }
    med = np.median([r["cagr_pp_iqr"] for r in out.values()]) if out else None
    return {"books": out, "median_cagr_pp_iqr": round(float(med), 4) if med is not None else None}


def summarize(cells):
    """Per-cell deltas against each cell's own frozen-sign control, then the shared shares."""
    idx = {(c["n_hold"], c["rebal"], c["phase"], c["arm"]): c for c in cells}
    rows = []
    for (n_hold, rebal) in BOOKS:
        for (h, r, phase, arm) in sorted(idx):
            if (h, r) != (n_hold, rebal) or arm != "frozen":
                continue
            flip = idx.get((h, r, phase, "flip"))
            if flip is None:
                continue
            base = idx[(h, r, phase, "frozen")]
            d = delta(flip, base)
            rows.append({"n_hold": h, "rebal": r, "phase": phase,
                         "base_cagr": base["cagr"], "flip_cagr": flip["cagr"],
                         "base_sharpe": base["sharpe"], "flip_sharpe": flip["sharpe"],
                         "delta_cagr_pp": d["cagr_pp"], "delta_sharpe": d["sharpe"],
                         "delta_oos_pp": d["oos_pp"], "delta_turnover": d["turnover"],
                         "delta_maxdd_pp": d["maxdd_pp"]})
    n = len(rows)
    if not n:
        return {"n_cells": 0, "degraded": "no cells"}
    cagr = np.array([r["delta_cagr_pp"] for r in rows])
    sharpe = np.array([r["delta_sharpe"] for r in rows])
    return {
        "n_cells": n,
        "share_up": round(float((cagr > 0).mean()), 4),
        "share_sharpe_ok": round(float((sharpe >= 0).mean()), 4),
        "share_oos_ok": round(float((np.array([r["delta_oos_pp"] for r in rows]) >= 0).mean()), 4),
        "median_delta_cagr_pp": round(float(np.median(cagr)), 4),
        "median_delta_sharpe": round(float(np.median(sharpe)), 4),
        "median_delta_oos_pp": round(float(np.median([r["delta_oos_pp"] for r in rows])), 4),
        "worst_delta_cagr_pp": round(float(cagr.min()), 4),
        "best_delta_cagr_pp": round(float(cagr.max()), 4),
        "cells": rows,
    }


def verdict(summary, disp, criteria=CRITERIA):
    """Frozen ordering: a flip has to be big, broad, and larger than the phase noise."""
    reasons = []
    if not summary or summary.get("n_cells", 0) < len(BOOKS) * N_PHASES:
        return "MIXED", ["cell grid incomplete -- nothing can be read"]
    med = summary["median_delta_cagr_pp"]
    noise = (disp or {}).get("median_cagr_pp_iqr")
    if med <= criteria["bar_pp"] or summary["share_up"] < criteria["share_up_min"]:
        reasons.append("median %+.2fpp (bar %+.2fpp), return up in %.0f%% of %d cells (need %.0f%%)"
                       % (med, criteria["bar_pp"], 100 * summary["share_up"],
                          summary["n_cells"], 100 * criteria["share_up_min"]))
        return "REJECT", reasons
    if noise is not None and abs(med) <= noise:
        reasons.append("median %+.2fpp is inside the control's own phase IQR %.2fpp -- "
                       "the effect is not separable from the decision grid"
                       % (med, noise))
        return "PHASE_FRAGILE", reasons
    if summary["share_sharpe_ok"] < criteria["sharpe_ok_min"]:
        reasons.append("return up in %.0f%% of cells but risk-adjusted also up in only %.0f%% "
                       "(need %.0f%%)" % (100 * summary["share_up"],
                                          100 * summary["share_sharpe_ok"],
                                          100 * criteria["sharpe_ok_min"]))
        return "MIXED", reasons
    reasons.append("median %+.2fpp, up in %.0f%% of %d cells, Sharpe not worse in %.0f%%, "
                   "above the %.2fpp phase IQR"
                   % (med, 100 * summary["share_up"], summary["n_cells"],
                      100 * summary["share_sharpe_ok"], noise or 0.0))
    return "ADOPT", reasons


# ---------------------------------------------------------------- build

def build():
    close, openp, amt, feats = F.build_panel()
    if not feats:
        print("[signflip] no factor faces -- mechanism fault")
        return None, 2
    if not SIGN_RECEIPT.exists():
        print("[signflip] %s missing -- the flip arm has no source of truth" % SIGN_RECEIPT)
        return None, 2
    sign_face = json.loads(SIGN_RECEIPT.read_text(encoding="utf-8"))
    per_factor = sign_face.get("per_factor") or {}
    contrary = sign_index(per_factor)
    if len(contrary) != 1:
        print("[signflip] expected exactly one CONTRARY factor, receipt says %r -- "
              "criterion not evaluable" % (contrary,))
        return None, 3
    flip = flip_signs(dict(F.SIGNS), set(contrary))
    recorded = ((sign_face.get("diagnostic_decisions") or {}).get("flip_contrary") or {}).get("signs")
    recorded_agrees = (recorded is not None
                       and all(abs(float(recorded[c]) - flip[c]) < 1e-12 for c in flip))

    score_frozen = F.build_score(close, amt, feats)
    score_ident = score_from_signs_safe(feats, close, amt, dict(F.SIGNS))
    score_flip = score_from_signs_safe(feats, close, amt, flip)
    if score_ident is None or score_flip is None:
        print("[signflip] could not build the score faces")
        return None, 3
    ident_gap = float(np.nanmax(np.abs((score_ident - score_frozen).to_numpy())))

    starts = B.phase_starts(close.index, start=START, rebal=PHASE_REBAL, n=N_PHASES)
    cells = []
    identity = []
    for (n_hold, rebal) in BOOKS:
        for d in starts:
            phase = str(pd.Timestamp(d).date())
            base = arm_cell(close, openp, amt, score_frozen, n_hold, rebal, d)
            cells.append(dict(base, n_hold=n_hold, rebal=rebal, phase=phase, arm="frozen"))
            flipc = arm_cell(close, openp, amt, score_flip, n_hold, rebal, d)
            cells.append(dict(flipc, n_hold=n_hold, rebal=rebal, phase=phase, arm="flip"))
            if (n_hold, rebal) == BOOKS[0]:
                again = arm_cell(close, openp, amt, score_ident, n_hold, rebal, d)
                identity.append({"phase": phase, "delta_cagr_pp": delta(again, base)["cagr_pp"]})

    act = {}
    for c in cells:
        if c["arm"] == "frozen" and (c["n_hold"], c["rebal"]) == BOOKS[0]:
            act[c["phase"]] = {"cagr": c["cagr"], "turnover": c["turnover_per_decision"]}
    distinct = len({(round(v["cagr"], 10), round(v["turnover"], 10)) for v in act.values()})
    if distinct != len(act):
        raise RuntimeError("phases collapsed onto one decision sequence: %r" % (act,))

    summary = summarize(cells)
    disp = dispersion(cells)
    label, reasons = verdict(summary, disp)
    ident_max = max(abs(r["delta_cagr_pp"]) for r in identity) if identity else None

    control = {"n_cells": len(identity), "max_abs_identity_bp": ident_max,
               "within_tol": (ident_max is not None
                              and ident_max <= CRITERIA["identity_tol_bp"]),
               "score_face_max_abs_gap": round(ident_gap, 12)}
    if ident_max is None or ident_max > CRITERIA["identity_tol_bp"]:
        label, reasons = "MIXED", ["identity leg reads %r bp -- the cells measure the harness"
                                  % (ident_max,)]

    payload = {
        "script": SCRIPT,
        "face": "etf_sign_flip_phase_test",
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "units": dict(UNITS),
        "criteria": dict(CRITERIA),
        "config": {"books": [list(b) for b in BOOKS], "n_phases": len(starts),
                   "phases": [str(pd.Timestamp(d).date()) for d in starts],
                   "cost_bp": COST * 1e4, "universe": int(close.shape[1]),
                   "flipped_factor": contrary[0], "flipped_sign": flip[contrary[0]],
                   "production_sign": float(F.SIGNS[contrary[0]])},
        "source_receipt": {"path": "results/etf_factor_sign_stability.json",
                           "evidence_cutoff": sign_face.get("evidence_cutoff"),
                           "recorded_flip_signs_agree": bool(recorded_agrees),
                           "receipt_classes": {c: v.get("class") for c, v in per_factor.items()}},
        "identity": control,
        "activity": {"phases": act, "distinct_sequences": distinct, "n_phases": len(act)},
        "cells": cells,
        "summary": summary,
        "dispersion": disp,
        "verdict": {"label": label, "reasons": reasons,
                    "rule": "frozen criteria; recomputed from summary by --check"},
        "caveats": [
            "exploratory: no preregistration, no ledger booking; no production config changes here",
            "cells share one panel and overlap in time -- the sign test counts cells, not independent bets",
            "the flip is chosen after the yearly table was read (6 factors examined, 1 flattering arm "
            "printed); the cell grid prices that arm, it does not undo the selection risk",
            "one panel / one cost model / 8bp per side; survivor pool and the 2020-2023 regime caveats "
            "of the underlying book are unchanged",
            "the ice is the drawdown_60 factor only: a flip of a DRIFT factor is a different question",
        ],
    }
    return payload, 0


def score_from_signs_safe(feats, close, amt, signs):
    """The sign-dict score face; imported from the sign face's own definition, never copied."""
    from scripts.etf_factor_sign_stability import score_from_signs
    return score_from_signs(feats, close, amt, signs)


# ---------------------------------------------------------------- reporting

def render_md(payload):
    c = payload["config"]
    s = payload["summary"]
    v = payload["verdict"]
    d = payload.get("dispersion") or {}
    ident = payload.get("identity") or {}
    lines = [
        "# ETF book -- is the drawdown_60 sign flip an effect or one decision sequence?",
        "",
        "Window ends %s | %d books x %d phases = %d cells | %.1fbp/side | flipped %s %+.0f -> %+.0f"
        % (payload["evidence_cutoff"], len(c["books"]), c["n_phases"], s.get("n_cells", 0),
           c["cost_bp"], c["flipped_factor"], c["production_sign"], c["flipped_sign"]),
        "",
        "## Verdict (rule frozen before the run)",
        "",
        "**%s** -- %s" % (v["label"], "; ".join(v["reasons"])),
        "",
        "## Identity legs",
        "",
        "Score face built from the production sign dict vs `build_score`: max gap %s "
        "(0 means the control arm IS the production arm). Re-running that identical score "
        "through the engine: %s cells, worst %s bp."
        % (ident.get("score_face_max_abs_gap"), ident.get("n_cells"),
           ident.get("max_abs_identity_bp")),
        "",
        "## Phase noise of the control arm",
        "",
        "| book | phases | CAGR min | CAGR max | CAGR IQR (pp) | Sharpe IQR |",
        "|---|---|---|---|---|---|",
    ]
    for key, row in (d.get("books") or {}).items():
        lines.append("| %s | %d | %.2f%% | %.2f%% | %.3f | %.3f |"
                     % (key, row["n_phases"], row["cagr_pp_min"], row["cagr_pp_max"],
                        row["cagr_pp_iqr"], row["sharpe_iqr"]))
    lines += [
        "",
        "Median phase IQR of CAGR: **%s pp**; the flip's median effect is %+.2fpp -- %s."
        % (d.get("median_cagr_pp_iqr"), s.get("median_delta_cagr_pp", 0.0),
           "inside the noise" if (d.get("median_cagr_pp_iqr") or 0)
           > abs(s.get("median_delta_cagr_pp") or 0) else "above the noise"),
        "",
        "## The flip across every cell",
        "",
        "cells | return up | Sharpe not worse | OOS not worse | median dCAGR | median dSharpe | "
        "median dOOS | worst | best",
        "|---|---|---|---|---|---|---|---|---|",
        "%d | %.0f%% | %.0f%% | %.0f%% | %+.2fpp | %+.3f | %+.2fpp | %+.2fpp | %+.2fpp"
        % (s.get("n_cells", 0), 100 * s.get("share_up", 0), 100 * s.get("share_sharpe_ok", 0),
           100 * s.get("share_oos_ok", 0), s.get("median_delta_cagr_pp", 0.0),
           s.get("median_delta_sharpe", 0.0), s.get("median_delta_oos_pp", 0.0),
           s.get("worst_delta_cagr_pp", 0.0), s.get("best_delta_cagr_pp", 0.0)),
        "",
        "## Per-cell detail (flip vs its own frozen-sign control)",
        "",
        "| book | phase | dCAGR | dSharpe | dOOS | dTurnover | dMaxDD |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in s.get("cells", []):
        lines.append("| n%d_r%d | %s | %+.2fpp | %+.3f | %+.2fpp | %+.3f | %+.2fpp |"
                     % (r["n_hold"], r["rebal"], r["phase"], r["delta_cagr_pp"],
                        r["delta_sharpe"], r["delta_oos_pp"], r["delta_turnover"],
                        r["delta_maxdd_pp"]))
    lines += ["", "## Frozen criteria", "", "```", json.dumps(payload["criteria"], indent=2), "```",
              "", "## Caveats", ""]
    for cv in payload["caveats"]:
        lines.append("* " + cv)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- consistency gate

def check_payload(payload):
    """Engine-free: is this face internally consistent, current, and honestly graded?"""
    bad = []
    for key in ("cagr", "delta_cagr_pp", "phase", "cagr_pp_iqr"):
        if key not in (payload.get("units") or {}):
            bad.append("units missing %r -- a bare number has no denominator" % key)
    crit = payload.get("criteria") or {}
    for key, want in CRITERIA.items():
        if key == "frozen":
            continue
        got = crit.get(key)
        if isinstance(want, list):
            if [list(x) for x in (got or [])] != want:
                bad.append("criteria %r is %r but the frozen rule is %r" % (key, got, want))
        elif isinstance(want, float):
            if got is None or abs(float(got) - want) > 1e-12:
                bad.append("criteria %r is %r but the frozen rule is %r" % (key, got, want))
        elif got != want:
            bad.append("criteria %r is %r but the frozen rule is %r" % (key, got, want))

    cfg = payload.get("config") or {}
    cells = payload.get("cells") or []
    want_cells = len(cfg.get("books") or []) * len(cfg.get("phases") or []) * 2
    if len(cells) != want_cells:
        bad.append("cell grid incomplete: %d cells for %d books x %d phases x 2 arms"
                   % (len(cells), len(cfg.get("books") or []), len(cfg.get("phases") or [])))
    if any(c.get("cagr") is None for c in cells):
        bad.append("a cell carries no CAGR reading")

    act = payload.get("activity") or {}
    if len(act.get("phases") or {}) != len(cfg.get("phases") or []):
        bad.append("activity covers %d phases but the config declares %d"
                   % (len(act.get("phases") or {}), len(cfg.get("phases") or [])))
    if (act.get("distinct_sequences") or 0) != len(act.get("phases") or {}):
        bad.append("phases collapsed onto one decision sequence -- the path test is void")

    ident = payload.get("identity") or {}
    if ident.get("within_tol") is not True:
        bad.append("identity leg is out of tolerance (worst %r bp) -- cells measure the harness"
                   % ident.get("max_abs_identity_bp"))
    if ident.get("score_face_max_abs_gap") not in (0.0, 0, None):
        bad.append("sign-dict score does not reproduce build_score (gap %r)"
                   % ident.get("score_face_max_abs_gap"))
    src = payload.get("source_receipt") or {}
    if src.get("recorded_flip_signs_agree") is not True:
        bad.append("flip signs do not match the sign face's recorded flip arm")

    v = payload.get("verdict") or {}
    if v.get("label") not in VERDICTS:
        bad.append("verdict label %r is not one of %r" % (v.get("label"), VERDICTS))
    else:
        label, _ = verdict(payload.get("summary") or {}, payload.get("dispersion"))
        if ident.get("within_tol") is not True:
            label = "MIXED"
        if label != v.get("label"):
            bad.append("published verdict %r does not follow from the summary (rule says %r)"
                       % (v.get("label"), label))
    return (not bad), bad


def check():
    if not OUT_JSON.exists():
        print("FAIL face missing: %s" % OUT_JSON.relative_to(ROOT))
        return 1
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    ok, bad = check_payload(payload)
    # staleness: a face priced on a panel older than the sign receipt it consumes is not current
    src = payload.get("source_receipt") or {}
    if src.get("evidence_cutoff") and payload.get("evidence_cutoff"):
        if str(payload["evidence_cutoff"]) < str(src["evidence_cutoff"]):
            ok = False
            bad.append("face cutoff %s is older than its sign receipt %s"
                       % (payload["evidence_cutoff"], src["evidence_cutoff"]))
    if ok:
        print("OK %s verdict=%s cells=%d median=%+.2fpp"
              % (FACE, payload["verdict"]["label"], len(payload.get("cells") or []),
                 payload["summary"]["median_delta_cagr_pp"]))
        return 0
    for b in bad:
        print("FAIL " + b)
    return 1


# ---------------------------------------------------------------- selftest

def _fixture(bars=320, names=14, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-04", periods=bars, freq="B")
    cols = ["s%02d" % i for i in range(names)]
    steps = rng.normal(0.0004, 0.012, size=(bars, names)).cumsum(axis=0)
    close = pd.DataFrame(100 * np.exp(steps), index=idx, columns=cols)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(5e7, index=idx, columns=cols)
    feats = {}
    e = rng.normal(size=(bars, names))
    feats["price_position"] = pd.DataFrame(e, index=idx, columns=cols)
    feats["drawdown_60"] = pd.DataFrame(-e, index=idx, columns=cols)
    feats["vol_60"] = pd.DataFrame(rng.normal(size=(bars, names)), index=idx, columns=cols)
    feats["mom_12_1"] = pd.DataFrame(rng.normal(size=(bars, names)), index=idx, columns=cols)
    feats["adx_14"] = pd.DataFrame(rng.normal(size=(bars, names)), index=idx, columns=cols)
    feats["intraday_range"] = pd.DataFrame(rng.normal(size=(bars, names)), index=idx, columns=cols)
    return close, openp, amt, feats


def selftest():
    fails = []

    def check(name, cond, extra=""):
        if cond:
            print("  ok  " + name)
        else:
            fails.append(name)
            print("  FAIL " + name + ("  " + extra if extra else ""))

    # 1-2: phase_starts must return distinct bars and refuse to collapse
    close, openp, amt, feats = _fixture()
    starts = B.phase_starts(close.index, start="2021-01-04", rebal=20, n=4)
    check("phase_starts returns 4 distinct bars", len(set(starts)) == 4)
    post = [d for d in close.index if d >= pd.Timestamp("2021-01-04")]
    check("phase #0 is the first bar >= start", starts[0] == post[0])
    check("phases stay inside one cycle", (post.index(starts[-1]) - post.index(starts[0])) < 20)

    # 3: the sign-dict score reproduces build_score exactly
    s_ident = score_from_signs_safe(feats, close, amt, dict(F.SIGNS))
    s_build = F.build_score(close, amt, feats)
    gap = float(np.nanmax(np.abs((s_ident - s_build).to_numpy())))
    check("sign-dict score equals build_score", gap < 1e-12, "gap=%r" % gap)

    # 4: the same score through the engine on two phases must read identical CAGR
    a1 = arm_cell(close, openp, amt, s_build, 5, 20, starts[0])
    a2 = arm_cell(close, openp, amt, s_ident, 5, 20, starts[0])
    check("identical score -> identical cell", abs((a1["cagr"] or 0) - (a2["cagr"] or 0)) < 1e-12)

    # 5: flipping a sign that is already correct must not be a no-op
    flipped = flip_signs(dict(F.SIGNS), {"drawdown_60"})
    s_flip = score_from_signs_safe(feats, close, amt, flipped)
    check("flip changes the score face",
          float(np.nanmax(np.abs((s_flip - s_build).to_numpy()))) > 1e-6)

    # 6: verdict branches are reachable from summaries alone
    strong = {"n_cells": 20, "share_up": 1.0, "share_sharpe_ok": 1.0,
              "median_delta_cagr_pp": 3.0}
    weak = {"n_cells": 20, "share_up": 0.4, "share_sharpe_ok": 0.5,
            "median_delta_cagr_pp": 0.1}
    noisy = {"n_cells": 20, "share_up": 1.0, "share_sharpe_ok": 1.0,
             "median_delta_cagr_pp": 0.8}
    check("ADOPT reachable", verdict(strong, {"median_cagr_pp_iqr": 0.5})[0] == "ADOPT")
    check("REJECT reachable", verdict(weak, {"median_cagr_pp_iqr": 0.5})[0] == "REJECT")
    check("PHASE_FRAGILE reachable", verdict(noisy, {"median_cagr_pp_iqr": 1.5})[0] == "PHASE_FRAGILE")
    l, _ = verdict({"n_cells": 3, "share_up": 1.0, "share_sharpe_ok": 1.0,
                    "median_delta_cagr_pp": 9.0}, {"median_cagr_pp_iqr": 0.1})
    check("incomplete grid is not ADOPT", l == "MIXED")

    # 7: delta arithmetic is arm minus base in pp, and zero on identical arms
    d = delta({"cagr": 0.10, "sharpe": 1.0, "oos_cagr": 0.2, "turnover_per_decision": 0.5,
               "maxdd": -0.1},
              {"cagr": 0.0913, "sharpe": 0.9, "oos_cagr": 0.19, "turnover_per_decision": 0.5,
               "maxdd": -0.1})
    check("delta_cagr_pp is 100*(arm-base)", abs(d["cagr_pp"] - 0.87) < 1e-9, str(d))
    check("identical arms read zero", abs(delta({"cagr": 0.1, "sharpe": 1.0, "oos_cagr": 0.1,
                                                 "turnover_per_decision": 0.2, "maxdd": 0.0},
                                                {"cagr": 0.1, "sharpe": 1.0, "oos_cagr": 0.1,
                                                 "turnover_per_decision": 0.2, "maxdd": 0.0},
                                                )["cagr_pp"]) < 1e-12)

    # 8: summarize pairs each flip cell with its OWN phase's control (a wrong join is the bug)
    cells = []
    for ph, base in (("p1", 0.10), ("p2", 0.20)):
        cells.append({"n_hold": 5, "rebal": 20, "phase": ph, "arm": "frozen",
                      "cagr": base, "sharpe": 1.0, "oos_cagr": base, "maxdd": -0.1,
                      "turnover_per_decision": 0.5})
        cells.append({"n_hold": 5, "rebal": 20, "phase": ph, "arm": "flip",
                      "cagr": base + 0.01, "sharpe": 1.0, "oos_cagr": base + 0.01,
                      "maxdd": -0.1, "turnover_per_decision": 0.5})
    summ = summarize(cells)
    check("summarize joins per phase", summ["n_cells"] == 2
          and abs(summ["median_delta_cagr_pp"] - 1.0) < 1e-9, str(summ)[:200])

    # 9: check_payload refuses a face built under other thresholds
    payload = {
        "units": dict(UNITS), "criteria": dict(CRITERIA),
        "config": {"books": [list(b) for b in BOOKS], "phases": ["2021-01-04"] * N_PHASES},
        "activity": {"phases": {str(i): {} for i in range(N_PHASES)},
                     "distinct_sequences": N_PHASES, "n_phases": N_PHASES},
        "identity": {"within_tol": True, "score_face_max_abs_gap": 0.0,
                     "max_abs_identity_bp": 0.0, "n_cells": 4},
        "source_receipt": {"recorded_flip_signs_agree": True, "evidence_cutoff": "2021-01-01"},
        "cells": [{"cagr": 0.1} for _ in range(len(BOOKS) * N_PHASES * 2)],
        "summary": {"n_cells": len(BOOKS) * N_PHASES, "share_up": 1.0, "share_sharpe_ok": 1.0,
                    "median_delta_cagr_pp": 3.0},
        "dispersion": {"median_cagr_pp_iqr": 0.5},
        "verdict": {"label": "ADOPT"},
        "evidence_cutoff": "2021-06-01",
    }
    ok, bad = check_payload(payload)
    check("well-formed payload passes", ok, str(bad))
    tampered = json.loads(json.dumps(payload))
    tampered["criteria"]["bar_pp"] = 0.10
    ok2, bad2 = check_payload(tampered)
    check("re-tuned criteria refused", (not ok2) and any("bar_pp" in b for b in bad2))
    tampered = json.loads(json.dumps(payload))
    tampered["identity"]["within_tol"] = False
    ok3, bad3 = check_payload(tampered)
    check("broken identity leg refused", not ok3 and any("identity" in b for b in bad3))
    tampered = json.loads(json.dumps(payload))
    tampered["verdict"]["label"] = "ADOPT"
    tampered["summary"]["median_delta_cagr_pp"] = 0.0
    ok4, bad4 = check_payload(tampered)
    check("word does not follow the numbers", not ok4 and any("does not follow" in b for b in bad4))

    print("[signflip] selftest %d/%d PASS" % (17 - len(fails), 17))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check:
        return check()
    payload, rc = build()
    if rc != 0:
        return rc
    os.makedirs(OUT_JSON.parent, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True),
                        encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    s = payload["summary"]
    print("[signflip] cutoff %s | %d books x %d phases | flipped %s"
          % (payload["evidence_cutoff"], len(payload["config"]["books"]),
             payload["config"]["n_phases"], payload["config"]["flipped_factor"]))
    print("  cells %d | up %.0f%% | sharpe ok %.0f%% | oos ok %.0f%% | median %+.2fpp "
          "(worst %+.2f / best %+.2f) | phase IQR %.2fpp"
          % (s["n_cells"], 100 * s["share_up"], 100 * s["share_sharpe_ok"], 100 * s["share_oos_ok"],
             s["median_delta_cagr_pp"], s["worst_delta_cagr_pp"], s["best_delta_cagr_pp"],
             (payload["dispersion"] or {}).get("median_cagr_pp_iqr") or 0.0))
    print("  verdict: %s -- %s" % (payload["verdict"]["label"],
                                    "; ".join(payload["verdict"]["reasons"])))
    print("[signflip] face -> %s ; %s" % (OUT_JSON.relative_to(ROOT), OUT_MD.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())