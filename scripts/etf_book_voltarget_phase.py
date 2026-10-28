"""ETF book -- is the 20-bar vol estimator's +1.6pp a level, or one decision calendar?

r1327 measured the sizing overlay's two lags and priced four trailing windows through the
same engine: `vol_window` 20/40/60/120 gave 11.30/10.28/9.70/7.31%/yr, i.e. the 20-bar arm
printed +1.60pp over the production 60-bar control with drawdown essentially unchanged. That
reading rested on ONE decision calendar -- the exact shape r1325 refuted for the buffer arm
(the shipped book's own CAGR spans 9.12%..10.93% across four phases of one 20-bar cycle, and
an arm that improved four metrics together reversed on 70% of the phase-shifted cells).

So this face applies the r1325 ruler to the sizing question. The same four windows are
re-priced on four decision grids started at four different bars inside one 20-bar cycle
(4 x 4 = 16 engine runs, controls shared). Every comparison is PAIRED: an arm is measured
against the 60-bar control of its OWN phase, so the calendar is held fixed and the only
thing that moves is the estimator.

The ruler is printed, not implied: the control arm's own CAGR across those four phases is
the noise floor the +1.6pp has to clear. Anything inside it is "one calendar", not a knobs'
worth of alpha.

WHY THE CRITERIA SIT ABOVE THE CODE: the verdict rule is frozen as constants before the
first run and echoed into the payload; --check refuses a face whose echoed criteria differ
from the constants, so a later "small adjustment" cannot be mistaken for the rule, and the
verdict is recomputed from the summary rather than taken on trust. The activity precondition
(r1261) is asserted: four phases that collapsed onto one decision grid would reproduce the
same sequence four times and make "the level holds" trivially true. Uniqueness is checked on
the decision DATES, not decision counts (four phases inside one cycle can share a count --
83/83/82/82 -- and still never decide on the same day).

Reuse, not re-implementation: the panel comes from etf_book_production.prep_panel, the arms
are the r1327 engine calls (etf_book_voltarget_lag.run_arm), the phases come from the r1325
implementation (etf_book_buffer_adoption.phase_starts) and the stats from etf_equity_alpha.

Usage:
    python scripts/etf_book_voltarget_phase.py run
    python scripts/etf_book_voltarget_phase.py --check      # gate: criteria echo + verdict
    python scripts/etf_book_voltarget_phase.py --selftest   # offline invariants
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_book_voltarget_lag as V
import etf_equity_alpha as A
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_voltarget_phase.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_VOLTARGET_PHASE.md"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes these and --check refuses a face whose
# echo differs, so the rule cannot be re-tuned after the numbers are known.
WINDOWS = V.WINDOWS              # 20/40/60/120 -- the r1327 arms, unchanged
CONTROL_WINDOW = V.CONTROL_WINDOW  # 60 = production sizing window
W_TEST = 20                      # the arm carrying the claim
N_PHASES = 4                     # phases spread across one rebalance cycle
PHASE_REBAL = 20                 # the cycle the phases are drawn from (production REBAL)

CLAIM_PP = 1.60                  # the r1327 single-calendar reading this face tests
SHARE_UP_MIN = 0.75              # the arm must beat its own-phase control in 3 of 4 phases
MEDIAN_DELTA_FLOOR_PP = 0.0      # ... with a median that is not negative
CONTROL_TOL_PP = 0.50            # r1297: phase 0 must reproduce the published cell

CRITERIA = {
    "windows": list(WINDOWS),
    "control_window": CONTROL_WINDOW,
    "w_test": W_TEST,
    "n_phases": N_PHASES,
    "phase_rebal": PHASE_REBAL,
    "claim_pp": CLAIM_PP,
    "share_up_min": SHARE_UP_MIN,
    "median_delta_floor_pp": MEDIAN_DELTA_FLOOR_PP,
    "control_tolerance_pp": CONTROL_TOL_PP,
    "frozen": ("constants above were written before the first run; the gate refuses a face "
               "that echoes others, so 'level' cannot be produced by tuning the ruler"),
}

UNITS = {
    "cagr": "fraction per year (0.0962 = 9.62%/yr)",
    "delta_cagr_pp": "percentage points of CAGR, arm minus the 60-bar control of the SAME phase",
    "noise_pp": "the control arm's own CAGR spread across the four phases (percentage points)",
    "phase": "decision-grid start bar inside one 20-bar cycle (4 per window)",
}


# ---------------------------------------------------------------- mechanics
def phase_starts(index):
    """Phase starts, delegated to the r1325 implementation (single source)."""
    import etf_book_buffer_adoption as B
    return B.phase_starts(index, rebal=PHASE_REBAL, n=N_PHASES)


def cell_metrics(ser, turn, diag):
    full = A.stats2(ser, "full")
    dates = [str(pd.Timestamp(r["date"]).date()) for r in diag]
    return {
        "cagr": full.get("cagr"), "sharpe": full.get("sharpe"), "maxdd": full.get("maxdd"),
        "vol": full.get("vol"),
        "turnover_per_decision": round(float(turn), 4),
        "decisions": len(diag),
        "first_decision": dates[0] if dates else None,
        "last_decision": dates[-1] if dates else None,
        "_dates": tuple(dates),
    }


def paired(cells):
    """Per-phase deltas of every non-control window against that phase's own control."""
    by = {(c["phase"], c["vol_window"]): c for c in cells}
    rows = []
    for phase in sorted({c["phase"] for c in cells}):
        ctrl = by.get((phase, CONTROL_WINDOW))
        if not ctrl or ctrl.get("cagr") is None:
            continue
        for w in WINDOWS:
            if w == CONTROL_WINDOW:
                continue
            arm = by.get((phase, w))
            if not arm or arm.get("cagr") is None:
                continue
            rows.append({
                "phase": phase, "vol_window": w,
                "ctrl_cagr": ctrl["cagr"], "arm_cagr": arm["cagr"],
                "delta_cagr_pp": round(100 * (arm["cagr"] - ctrl["cagr"]), 4),
                "delta_sharpe": round((arm.get("sharpe") or 0.0) - (ctrl.get("sharpe") or 0.0), 4),
                "delta_maxdd_pp": round(100 * ((arm.get("maxdd") or 0.0)
                                               - (ctrl.get("maxdd") or 0.0)), 4),
            })
    return rows


def summarize(cells, rows, w_test=W_TEST):
    """The frozen summary: how often the tested arm wins, and the noise it must clear."""
    mine = [r for r in rows if r["vol_window"] == w_test]
    ctrl_cagr = [c["cagr"] for c in cells
                 if c["vol_window"] == CONTROL_WINDOW and c.get("cagr") is not None]
    out = {"w_test": w_test, "n_phases": N_PHASES, "n_priced": len(mine)}
    if not mine:
        out.update({"status": "undetermined",
                    "reason": "no phase priced the tested arm against its own control"})
        return out
    deltas = [r["delta_cagr_pp"] for r in mine]
    up = sum(1 for d in deltas if d > 0)
    out.update({
        "status": "priced" if len(mine) == N_PHASES else "partial",
        "up_phases": up,
        "share_up": round(up / len(mine), 4),
        "median_delta_pp": round(statistics.median(deltas), 4),
        "min_delta_pp": round(min(deltas), 4),
        "max_delta_pp": round(max(deltas), 4),
        "spread_delta_pp": round(max(deltas) - min(deltas), 4),
        "median_delta_sharpe": round(statistics.median([r["delta_sharpe"] for r in mine]), 4),
        "median_delta_maxdd_pp": round(statistics.median([r["delta_maxdd_pp"] for r in mine]), 4),
        "sign_test_p_two_sided": _sign_test(up, len(mine)),
    })
    if len(ctrl_cagr) >= 2:
        pts = [100 * c for c in ctrl_cagr]
        spread = max(pts) - min(pts)
        q75, q25 = np.percentile(pts, [75, 25])
        out["noise_pp"] = round(float(spread), 4)
        out["noise_iqr_pp"] = round(float(q75 - q25), 4)
        out["control_cagr_pp"] = {"min": round(min(pts), 3), "max": round(max(pts), 3)}
        out["within_noise"] = bool(abs(out["median_delta_pp"]) <= spread)
    else:
        out["noise_pp"] = None
        out["within_noise"] = None
    out["claim_pp"] = CLAIM_PP
    out["claim_holds_in_share"] = round(
        sum(1 for d in deltas if d >= CLAIM_PP) / len(mine), 4)
    return out


def _sign_test(k, n):
    """Exact two-sided sign-test p-value for k successes in n trials at p=1/2."""
    if n <= 0:
        return None
    import math
    def pmf(i):
        return math.comb(n, i) * 0.5 ** n
    obs = pmf(k)
    total = sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12)
    return round(min(1.0, total), 4)


def verdict_for(summary):
    """Frozen decision rule. Recomputed by --check; never hand-written into the payload."""
    if not summary or summary.get("status") == "undetermined":
        return "undetermined: no phase priced the tested arm against its own control"
    if summary.get("status") == "partial":
        return ("partial: %d of %d phases priced, so this is not a verdict on the window"
                % (summary.get("n_priced"), summary.get("n_phases")))
    share = summary.get("share_up") or 0.0
    med = summary.get("median_delta_pp")
    noise = summary.get("noise_pp")
    if share < SHARE_UP_MIN or med is None or med <= MEDIAN_DELTA_FLOOR_PP:
        return ("sequence: the %d-bar arm beats its own-phase control on only %d/%d phases "
                "(median %+.2fpp vs the %.2fpp single-calendar claim) -- the r1327 reading is "
                "one decision sequence and must not be quoted as an improvement"
                % (summary["w_test"], summary["up_phases"], summary["n_phases"],
                   med if med is not None else float("nan"), summary.get("claim_pp", CLAIM_PP)))
    if noise is not None and abs(med) <= noise:
        return ("within noise: the arm wins on %d/%d phases with a median %+.2fpp, but the "
                "control's own CAGR spans %.2fpp across those same phases -- the direction "
                "holds and the size cannot be told apart from calendar luck; keep the "
                "production window and print the range"
                % (summary["up_phases"], summary["n_phases"], med, noise))
    return ("level: the arm wins on %d/%d phases with a median %+.2fpp, clear of the %.2fpp "
            "phase noise -- a faster estimator is a genuine direction, but it is still a risk "
            "knob: change the config only on a signed decision, not on this face"
            % (summary["up_phases"], summary["n_phases"], med, noise if noise is not None else 0.0))


def build():
    close, openp, amt, score, _cls, n_flip = P.prep_panel()
    starts = phase_starts(close.index)
    print("panel %s flips=%d phases=%s" % (close.shape, n_flip,
                                           [str(pd.Timestamp(d).date()) for d in starts]), flush=True)
    cells = []
    for i, d in enumerate(starts):
        for w in WINDOWS:
            ser, turn, diag = V.run_arm(close, openp, amt, score, w, start=str(pd.Timestamp(d).date()))
            m = cell_metrics(ser, turn, diag)
            m.pop("_dates", None)
            m.update({"phase": i, "start": str(pd.Timestamp(d).date()), "vol_window": w})
            cells.append(m)
        print("[phase %d] %s done" % (i, pd.Timestamp(d).date()), flush=True)

    # activity precondition (r1261): the phases must move the decision CALENDAR
    sigs = {}
    for c in cells:
        if c["vol_window"] == CONTROL_WINDOW:
            sigs[c["phase"]] = (c["first_decision"], c["last_decision"], c["decisions"])
    if len({v[:2] for v in sigs.values()}) != len(sigs):
        raise SystemExit("phases collapsed onto one decision calendar: %r" % (sigs,))
    if any(not v[0] for v in sigs.values()):
        raise SystemExit("a phase produced no decisions -- the mechanism did not move")

    rows = paired(cells)
    summary = summarize(cells, rows)
    published = V.published_control_cagr()
    ctrl_p0 = next((c for c in cells if c["phase"] == 0
                    and c["vol_window"] == CONTROL_WINDOW), None)
    control = {
        "arm": "n12_r20 vol_window=%d @ phase0" % CONTROL_WINDOW,
        "published_cagr": published,
        "recomputed_cagr": (ctrl_p0 or {}).get("cagr"),
        "tolerance_pp": CONTROL_TOL_PP,
        "delta_pp": None, "passes": None,
        "note": "published artifact unavailable -- not asserted",
    }
    if published is not None and control["recomputed_cagr"] is not None:
        control["delta_pp"] = round(100 * (control["recomputed_cagr"] - published), 3)
        control["passes"] = abs(control["delta_pp"]) <= CONTROL_TOL_PP
        control["note"] = "phase 0 is the published calendar, so it must reproduce the published arm"

    payload = {
        "schema": "etf_book_voltarget_phase/v1",
        "script": "scripts/etf_book_voltarget_phase.py",
        "face": "results/etf_book_voltarget_phase.json",
        "question": ("r1327 priced the %d-bar estimator at %+.2fpp over the %d-bar control on "
                     "one decision calendar -- does that survive four phases of that calendar?"
                     % (W_TEST, CLAIM_PP, CONTROL_WINDOW)),
        "window": "full panel (every phase)",
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": dict(CRITERIA),
        "units": dict(UNITS),
        "config": {"windows": list(WINDOWS), "control_window": CONTROL_WINDOW,
                   "n_phases": len(starts),
                   "phases": [str(pd.Timestamp(d).date()) for d in starts],
                   "universe": int(close.shape[1]), "flips_repaired": int(n_flip),
                   "cost_bp": V.H.COST * 1e4, "vol_target": V.TARGET_VOL},
        "control": control,
        "cells": cells,
        "deltas": rows,
        "summary": summary,
        "verdict": verdict_for(summary),
        "verdict_source": "recomputed by the gate from `summary`, never hand-written",
        "reuse": {"panel": "etf_book_production.prep_panel",
                  "arms": "etf_book_voltarget_lag.run_arm",
                  "phases": "etf_book_buffer_adoption.phase_starts",
                  "stats": "etf_equity_alpha.stats2"},
        "caveats": [
            "one panel, one cost model (10bp/side, next-open), survivor-pool caveat unchanged",
            "the arms differ ONLY in vol_window; selection, holdings and the cost model are "
            "shared, so a difference is the estimator's, not the book's",
            "four phases of ONE calendar is a ruler, not a sample: it bounds calendar luck, it "
            "does not test data dependence",
            "a sizing overlay is not an alpha; even a 'level' verdict here is a risk-shape "
            "proposal that needs a signed config decision",
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", OUT_JSON, flush=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print("wrote", OUT_MD, flush=True)
    print(json.dumps({"verdict": payload["verdict"], "summary": summary,
                      "control": control}, ensure_ascii=False), flush=True)
    return 0


def render_md(payload):
    s = payload["summary"]
    cfg = payload["config"]
    c = payload["criteria"]
    lines = [
        "# ETF book -- is the %d-bar vol estimator a level, or one calendar?" % s["w_test"],
        "",
        "Question: %s" % payload["question"],
        "",
        "Window ends %s | %d windows x %d decision phases = %d engine runs | %.0fbp/side | target vol %.0f%%"
        % (payload["evidence_cutoff"], len(cfg["windows"]), cfg["n_phases"],
           len(cfg["windows"]) * cfg["n_phases"], cfg["cost_bp"], 100 * cfg["vol_target"]),
        "",
        "**Verdict**: %s" % payload["verdict"],
        "",
        "## Every cell (arm minus the 60-bar control of its own phase)",
        "",
        "| phase | start | ctrl CAGR | " + " | ".join("w%d dCAGR" % w for w in cfg["windows"]
                                                         if w != cfg["control_window"]) + " |",
        "|---|---|---|" + "---|" * (len(cfg["windows"]) - 1),
    ]
    by = {(d["phase"], d["vol_window"]): d for d in payload["deltas"]}
    for cell in [x for x in payload["cells"] if x["vol_window"] == cfg["control_window"]]:
        cells_row = ["| %s | %s | %s |" % (cell["phase"], cell["start"], _pct(cell["cagr"]))]
        for w in cfg["windows"]:
            if w == cfg["control_window"]:
                continue
            d = by.get((cell["phase"], w)) or {}
            cells_row.append("%+.2f |" % d.get("delta_cagr_pp", float("nan")))
        lines.append(" ".join(cells_row))
    lines += [
        "",
        "## The arm under test",
        "",
        "w%d beats its own-phase control on **%d/%d** phases; median %+.2fpp (min %+.2f, max "
        "%+.2f, spread %.2fpp); median dSharpe %+.3f, median dMaxDD %+.2fpp; sign test p=%s."
        % (s["w_test"], s["up_phases"], s["n_phases"], s["median_delta_pp"],
           s["min_delta_pp"], s["max_delta_pp"], s["spread_delta_pp"],
           s["median_delta_sharpe"], s["median_delta_maxdd_pp"], s["sign_test_p_two_sided"]),
        "",
        "## The ruler it has to clear",
        "",
        "The %d-bar control itself spans %s..%s across these four phases -- **%.2fpp of pure "
        "calendar noise** (IQR %.2fpp). The claim under test is %+.2fpp; it holds at that size "
        "in %.0f%% of phases."
        % (cfg["control_window"], _pp((s.get("control_cagr_pp") or {}).get("min")),
           _pp((s.get("control_cagr_pp") or {}).get("max")),
           s.get("noise_pp") or 0.0, s.get("noise_iqr_pp") or 0.0,
           s.get("claim_pp", c["claim_pp"]), 100 * (s.get("claim_holds_in_share") or 0.0)),
        "",
        "Read the two numbers together: a median effect smaller than the control's own phase "
        "spread cannot be told apart from having picked a lucky start date, which is exactly "
        "the trap r1325 found one layer up.",
        "",
        "## Control",
        "",
        "%s -> published %s, recomputed %s, delta %s pp (tolerance %.2f pp). %s."
        % ((payload.get("control") or {}).get("arm", "-"),
           _pct((payload.get("control") or {}).get("published_cagr")),
           _pct((payload.get("control") or {}).get("recomputed_cagr")),
           _num((payload.get("control") or {}).get("delta_pp"), 2),
           c["control_tolerance_pp"], (payload.get("control") or {}).get("note", "")),
        "",
        "## Caveats",
    ]
    for x in payload.get("caveats") or []:
        lines.append("- %s" % x)
    return "\n".join(lines) + "\n"


def _pct(x):
    return "n/a" if not isinstance(x, (int, float)) else "%.2f%%" % (x * 100)


def _num(x, nd=2):
    return "n/a" if not isinstance(x, (int, float)) else ("%." + str(nd) + "f") % x


def _pp(x):
    """Values the summary already stores in PERCENTAGE POINTS (9.12), not fractions.

    r1292/r1316 family: passing a pp value to the %-formatter printed "912.00%" for a
    9.12pp CAGR in the very line that tells the reader how big the ruler is.
    """
    return "n/a" if not isinstance(x, (int, float)) else "%+.2f" % x


# ---------------------------------------------------------------- gate
def check_payload(payload, criteria=None):
    """Engine-free gate: frozen rule echoed, grid complete, verdict recomputed."""
    want = dict(criteria or CRITERIA)
    got = payload.get("criteria") or {}
    for k, v in want.items():
        if got.get(k) != v:
            raise SystemExit("criteria drift on %r: payload=%r frozen=%r -- the face was built "
                             "under a different rule" % (k, got.get(k), v))
    cells = payload.get("cells") or []
    windows = [c.get("vol_window") for c in cells]
    if sorted(set(windows)) != sorted(want["windows"]):
        raise SystemExit("arms %r != frozen windows %r"
                         % (sorted(set(windows)), sorted(want["windows"])))
    if len(cells) != len(want["windows"]) * want["n_phases"]:
        raise SystemExit("grid has %d cells, rule says %d windows x %d phases"
                         % (len(cells), len(want["windows"]), want["n_phases"]))
    if any(c.get("cagr") is None for c in cells):
        raise SystemExit("an unpriced cell cannot support a verdict")
    sigs = {(c.get("phase"), c.get("start"), c.get("first_decision"))
            for c in cells if c.get("vol_window") == want["control_window"]}
    if len({s[1:] for s in sigs}) != want["n_phases"]:
        raise SystemExit("phases share a start/decision signature -- they would price the same "
                         "sequence twice (r1261): %r" % (sigs,))
    recomputed = verdict_for(payload.get("summary") or {})
    if recomputed != payload.get("verdict"):
        raise SystemExit("verdict does not recompute: payload=%r recomputed=%r"
                         % (payload.get("verdict"), recomputed))
    ctl = payload.get("control") or {}
    if ctl.get("passes") is False:
        raise SystemExit("control arm does not reproduce the published cell: %r" % ctl)
    return {"cells": len(cells), "share_up": (payload.get("summary") or {}).get("share_up"),
            "median_pp": (payload.get("summary") or {}).get("median_delta_pp"),
            "noise_pp": (payload.get("summary") or {}).get("noise_pp")}


def check():
    if not OUT_JSON.exists():
        raise SystemExit("no face at %s -- run it first" % OUT_JSON)
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    read = check_payload(payload)
    print("voltarget_phase --check OK %s -> %s" % (read, payload.get("verdict")))
    return 0


# ---------------------------------------------------------------- selftest
def _cells(deltas, noise=(0.0912, 0.1093), w_test=W_TEST):
    """Synthetic grid: every frozen window priced in every phase, deltas as given for w_test.

    The non-tested arms are pinned to their phase's control, so the grid is COMPLETE (the
    gate refuses an incomplete one) while the numbers under test stay exactly known.
    """
    cells, rows = [], []
    for k, d in enumerate(deltas):
        ctrl = noise[0] + (noise[1] - noise[0]) * (k / max(1, len(deltas) - 1))
        for w in WINDOWS:
            cagr = ctrl if (w == CONTROL_WINDOW or w != w_test or not isinstance(d, (int, float))) \
                else ctrl + d / 100.0
            cells.append({"phase": k, "start": "2020-01-%02d" % (1 + k), "vol_window": w,
                          "cagr": cagr, "sharpe": 1.0, "maxdd": -0.10,
                          "first_decision": "2020-01-%02d" % (1 + k),
                          "last_decision": "2026-01-01"})
        if isinstance(d, (int, float)):
            rows.append({"phase": k, "vol_window": w_test, "ctrl_cagr": ctrl,
                         "arm_cagr": ctrl + d / 100.0, "delta_cagr_pp": d,
                         "delta_sharpe": 0.01, "delta_maxdd_pp": 0.0})
    return cells, rows


def selftest():
    ok = 0

    def eq(name, got, want, tol=1e-9):
        nonlocal ok
        if isinstance(want, float) and isinstance(got, (int, float)):
            if abs(got - want) > tol:
                raise SystemExit("FAIL %s: got %r want %r" % (name, got, want))
        elif got != want:
            raise SystemExit("FAIL %s: got %r want %r" % (name, got, want))
        ok += 1

    # 1) the paired delta keeps its units (fraction CAGR difference -> pp)
    cells, rows = _cells([1.6, 1.5, 1.7, 1.4])
    eq("paired delta units", rows[0]["delta_cagr_pp"], 1.6, 1e-6)
    eq("paired rows = phases", len(rows), 4)

    s = summarize(cells, rows)
    eq("summary status", s["status"], "priced")
    eq("summary share up", s["share_up"], 1.0)
    eq("summary median", s["median_delta_pp"], 1.55, 1e-9)
    eq("summary min", s["min_delta_pp"], 1.4, 1e-9)
    eq("summary max", s["max_delta_pp"], 1.7, 1e-9)
    eq("noise is the control's own spread", s["noise_pp"], 1.81, 1e-6)
    eq("within noise when the effect is under the spread", s["within_noise"], True)
    # the claim is a POINT (+1.60pp), so "holds" means reaches that size: 1.6 and 1.7 do,
    # 1.5 and 1.4 do not -- a face that rounded the claim up to "all phases" would hide this
    eq("claim holds only where the effect reaches it", s["claim_holds_in_share"], 0.5)

    # 2) the three verdict doors
    eq("up but inside the ruler -> within noise",
       verdict_for(s).split(":")[0], "within noise")
    big = summarize(*_cells([3.5, 3.1, 4.0, 2.9]))
    eq("up and clear of the ruler -> level", verdict_for(big).split(":")[0], "level")
    flip = summarize(*_cells([1.6, -0.9, 1.7, -0.4]))
    eq("sign flips -> sequence", verdict_for(flip).split(":")[0], "sequence")
    eq("flip share", flip["share_up"], 0.5)
    tiny = summarize(*_cells([0.2, 0.1, 0.3, 0.05]))
    eq("all positive but median under the floor is not a level",
       verdict_for(tiny).split(":")[0], "within noise")

    # 3) an unpriced phase cannot become a verdict
    partial = summarize(*_cells([1.6, None, 1.7, 1.4]))
    eq("partial status", partial["status"], "partial")
    eq("partial verdict prefix", verdict_for(partial).split(":")[0], "partial")
    eq("undetermined on no cells", verdict_for({"status": "undetermined"}).split(":")[0],
       "undetermined")

    # 4) the sign test is exact for n<=4 and refuses to overclaim
    eq("sign test 4/4", _sign_test(4, 4), 0.125)
    eq("sign test 3/4", _sign_test(3, 4), 0.625)
    eq("sign test 2/4", _sign_test(2, 4), 1.0)

    # 5) the gate recomputes the verdict and refuses a hand-written or re-tuned face
    good = {"criteria": dict(CRITERIA), "cells": cells, "summary": s, "control": {"passes": True}}
    good["verdict"] = verdict_for(s)
    eq("gate accepts an honest face", check_payload(good)["cells"], len(cells))
    try:
        check_payload(dict(good, verdict="level: the faster window wins"))
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted a hand-written verdict")
    try:
        check_payload(dict(good, criteria=dict(CRITERIA, share_up_min=0.25)))
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted a re-tuned share floor")
    dup = [dict(c, start="2020-01-01", first_decision="2020-01-01") for c in cells]
    try:
        check_payload(dict(good, cells=dup))
    except SystemExit:
        ok += 1
    else:
        raise SystemExit("FAIL gate accepted four identical phase calendars")

    # 6) mechanism can move: on a vol-shock fixture the estimator window changes the curve,
    #    and on a stationary one it does not (so "identical" there is correct, not dead)
    close, openp, amt, score = V._fixture()
    s60, _, _ = V.run_arm(close, openp, amt, score, 60)
    s20, _, _ = V.run_arm(close, openp, amt, score, 20)
    eq("stationary vol: the arms agree by construction",
       abs(s20.iloc[-1] - s60.iloc[-1]) < 1e-9, True)
    close2, openp2, amt2, score2 = V._fixture(shock_at=320, shock_mult=3.0)
    t60, _, _ = V.run_arm(close2, openp2, amt2, score2, 60)
    t20, _, _ = V.run_arm(close2, openp2, amt2, score2, 20)
    eq("regime shift: the window moves the curve", abs(t20.iloc[-1] - t60.iloc[-1]) > 1e-6, True)

    # 7) the phases really are four distinct calendars on the fixture index
    starts = phase_starts(pd.bdate_range("2020-01-02", periods=200))
    eq("four phases requested", len(starts), 4)
    eq("phases are distinct bars", len(set(starts)), 4)

    # 8) the rendering prints a fraction as pp, not as a bare fraction (r1292 family)
    eq("pct helper", _pct(0.0962), "9.62%")
    eq("missing renders as n/a", _pct(None), "n/a")
    # ...and a value the summary ALREADY stores in pp is not multiplied again
    eq("pp helper keeps pp as pp", _pp(9.12), "+9.12")
    _ruler = [l for l in render_md({
        "question": "q", "verdict": "v", "criteria": dict(CRITERIA),
        "config": {"windows": list(WINDOWS), "control_window": CONTROL_WINDOW,
                   "n_phases": N_PHASES, "phases": ["2020-01-02"], "universe": 1,
                   "flips_repaired": 0, "cost_bp": 10.0, "vol_target": 0.08},
        "evidence_cutoff": "2026-10-28", "cells": cells, "deltas": rows,
        "summary": s, "control": {"passes": True}, "caveats": []}).splitlines()
        if l.startswith("The 60-bar control")]
    eq("the ruler line does not print 912.00%", "912.00%" in (_ruler[0] if _ruler else "x"), False)
    eq("the ruler line prints a pp claim without the doubled unit suffix",
       "fpp" in (_ruler[0] if _ruler else ""), False)

    print("etf_book_voltarget_phase selftest: %d/%d PASS" % (ok, ok))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return build()


if __name__ == "__main__":
    sys.exit(main())