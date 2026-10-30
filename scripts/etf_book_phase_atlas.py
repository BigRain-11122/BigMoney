"""ETF book -- is a (names, cadence) cell a property of the market or of one decision calendar?

Every headline this book has published is computed on ONE decision calendar: the engine
decides every `rebal` bars counted from the first bar >= 2020-01-03. Shift that origin by a
week and the same book makes different decisions on different days -- r1325 measured that
once, for one arm (the incumbent buffer), on five books and four phases, and found its own
phase IQR (0.53pp) larger than the effect it was measuring.

This face asks the general question the production config depends on: for the whole
(n_hold, rebal) grid, how much of the spread between cells is a property of the cell and how
much is which day of the cycle the book happens to start on? A grid whose between-cell spread
is inside its own phase band cannot support "N5/R20 is the best cell" -- that sentence is then
a claim about one calendar.

Design (frozen before the first run):

  * cells   = n_hold in (3,5,8,12) x rebal in (10,20,40)  -> 12 cells
  * phases  = EVERY bar offset inside one rebalance cycle (10/20/40 per cell), so a cell's
              band is measured on a complete cycle of decision calendars, not four samples
  * aligned = offsets 0..9 are present for every cell, so the GRID can also be ranked per
              slot (the longer cycles contribute a subsample there -- disclosed, and the full
              cycle is still what the per-cell bands use)
  * cost / vol target / buffer k are the engine's (H.COST / H.TARGET_VOL / 0.0) and are
              overridable on the CLI so the same runner supplies the pool rows

Why the noise question has teeth: the production card and the executable ticket quote two
different widths off the same panel (r1285/E126 measured -1.52pp for 12 names vs 5). Those
differences are only decisions if they exceed the band this face measures.

Usage:
    python scripts/etf_book_phase_atlas.py run [--workers=8] [--k=0.0] [--cost=0.0010]
    python scripts/etf_book_phase_atlas.py --check
    python scripts/etf_book_phase_atlas.py --selftest
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
from parallel_runner import run_cells_parallel, worker_cap
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_phase_atlas.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_PHASE_ATLAS.md"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

SCRIPT = "scripts/etf_book_phase_atlas.py"
FACE = "results/etf_book_phase_atlas.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the payload echoes them and --check refuses a face whose
# echo differs, so a later "small adjustment" cannot be smuggled in as a re-run.
CELLS = ((3, 10), (3, 20), (3, 40), (5, 10), (5, 20), (5, 40),
         (8, 10), (8, 20), (8, 40), (12, 10), (12, 20), (12, 40))   # (n_hold, rebal)
MIN_PHASES = 10          # a cell judged on fewer phases is refused, not silently kept
ALIGNED_SLOTS = 10       # offsets 0..9 exist for every cell -> the grid can be ranked per slot
GATE_TOL = 1e-9

UNITS = {
    "cagr_pp": "percentage points per year (9.13 = 9.13%/yr)",
    "band_pp": "p95-p05 of a cell's CAGR across its own rebalance cycle, percentage points",
    "phase_offset": "bars after the engine's grid origin (0 = the production calendar)",
    "slope": "Spearman rank correlation between two slots' 12-cell rankings",
}


# ---------------------------------------------------------------- mechanics

def cell_phases(index, rebal, start=None):
    """Every bar offset inside one rebalance cycle -- the complete set of decision origins.

    The engine counts decisions every `rebal` bars from the first bar >= `start`, so an offset
    `o` in [0, rebal) is one distinct calendar and the `rebal` offsets cover the cycle exactly
    once. Distinctness is asserted by the caller (r1261: prove the mechanism moved).
    """
    start = R.START if start is None else start
    post = [d for d in index if d >= pd.Timestamp(start)]
    if len(post) < rebal:
        raise ValueError("panel has %d bars after %s -- need at least %d" % (len(post), start, rebal))
    return post[:rebal]


def _rank(xs):
    """Average ranks (1-based) -- ties handled, so Spearman is not order-sensitive."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    rx, ry = _rank(xs), _rank(ys)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return 0.0 if den == 0 else round(num / den, 4)


def _pct(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


# ---------------------------------------------------------------- worker plumbing
# The panel is loaded once per worker (ProcessPool initializer), never per job: 280 cells all
# read the same close/open/amount/score faces.

_P = {}


def _init_worker():
    close, openp, amt, score, _cls, _nf = P.prep_panel()
    _P.update(close=close, openp=openp, amt=amt, score=score)


def _run_cell(n_hold, rebal, offset, phase_date, cost, k):
    """One (cell, phase) run through the production engine (args arrive expanded)."""
    close, openp, amt, score = _P["close"], _P["openp"], _P["amt"], _P["score"]
    diag = []
    hook = None if not k else (lambda s, held, n, d, _k=k: H.buffer_picks(s, held, n, _k))
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      vol_target=H.TARGET_VOL, start=str(pd.Timestamp(phase_date).date()),
                                      diag=diag, select_hook=hook)
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp("2023-12-31")], "oos")
    ddates = [str(pd.Timestamp(r["date"]).date()) for r in diag]
    return {
        "n_hold": n_hold, "rebal": rebal, "phase_offset": offset,
        "phase": str(pd.Timestamp(phase_date).date()),
        "cagr": full.get("cagr"), "sharpe": full.get("sharpe"), "maxdd": full.get("maxdd"),
        "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
        "turnover_per_decision": round(float(turn), 4),
        "decisions": len(diag),
        # the phase signature is the DATES, not the count (r1325: four phases shared counts
        # 83/83/82/82 while never deciding on the same day)
        "first_decision": ddates[0] if ddates else None,
        "last_decision": ddates[-1] if ddates else None,
    }


# ---------------------------------------------------------------- summary (gate reuses it)

def summarize(cells):
    """Per-cell band across its own cycle + the grid-level noise question.

    Pure function of the raw rows: --check rebuilds every scalar through this and compares.
    """
    if not cells:
        raise ValueError("no cells")
    by = {}
    for c in cells:
        by.setdefault((c["n_hold"], c["rebal"]), []).append(c)
    per_cell = []
    for (n_hold, rebal), rows in sorted(by.items()):
        cagrs = [100.0 * r["cagr"] for r in rows if isinstance(r["cagr"], (int, float))]
        ordered = sorted(rows, key=lambda r: r["phase_offset"])
        per_cell.append({
            "n_hold": n_hold, "rebal": rebal,
            "phases": len(rows), "judged": len(cagrs) >= MIN_PHASES,
            "median_cagr_pp": round(_pct(cagrs, 0.5), 4) if cagrs else None,
            "min_cagr_pp": round(min(cagrs), 4) if cagrs else None,
            "max_cagr_pp": round(max(cagrs), 4) if cagrs else None,
            "p05_cagr_pp": round(_pct(cagrs, 0.05), 4) if cagrs else None,
            "p95_cagr_pp": round(_pct(cagrs, 0.95), 4) if cagrs else None,
            "share_positive": round(sum(1 for x in cagrs if x > 0) / len(cagrs), 4) if cagrs else None,
            "median_sharpe": round(_pct([r["sharpe"] for r in rows if isinstance(r["sharpe"], (int, float))], 0.5), 4),
            "median_maxdd": round(_pct([r["maxdd"] for r in rows if isinstance(r["maxdd"], (int, float))], 0.5), 4),
            "median_oos_cagr_pp": round(_pct([100.0 * r["oos_cagr"] for r in rows if isinstance(r["oos_cagr"], (int, float))], 0.5), 4),
            "phase_calendars_distinct": len({(r["first_decision"], r["last_decision"]) for r in ordered}) == len(ordered),
        })
    judged = [c for c in per_cell if c["judged"]]
    bands = [(c["p95_cagr_pp"] - c["p05_cagr_pp"]) for c in judged]
    medians = [c["median_cagr_pp"] for c in judged]
    noise_pp = round(_pct(bands, 0.5), 4) if bands else None
    signal_pp = round(max(medians) - min(medians), 4) if medians else None

    if noise_pp is None or signal_pp is None:
        verdict, reasons = "NOT_JUDGED", ["no cell carries %d phases" % MIN_PHASES]
    elif noise_pp <= GATE_TOL:
        verdict, reasons = "PHASE_INVARIANT", ["every judged cell returns the same CAGR on every calendar"]
    elif signal_pp >= noise_pp:
        verdict, reasons = "CONFIG_ORDER_EXCEEDS_PHASE_NOISE", [
            "between-cell spread %.2fpp >= median cell band %.2fpp" % (signal_pp, noise_pp)]
    else:
        verdict, reasons = "CONFIG_ORDER_WITHIN_PHASE_NOISE", [
            "between-cell spread %.2fpp < median cell band %.2fpp: the grid's ordering is not "
            "separated from which day of the cycle the book starts on" % (signal_pp, noise_pp)]

    # Authoritative cells: read the two live faces, never a constant (r1285: a width that is
    # written down twice drifts; the card and the ticket each name their own).
    prod, prod_rebal, ticket, ticket_rebal = None, None, None, None
    if PRODUCTION_FACE.exists():
        cfg = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8")).get("config") or {}
        prod = cfg.get("n_hold") if isinstance(cfg.get("n_hold"), int) else None
        prod_rebal = cfg.get("rebal") if isinstance(cfg.get("rebal"), int) else None
    tickets = sorted((ROOT / "results" / "etf_book_order").glob("TICKET-*.json"))
    if tickets:
        tk = json.loads(tickets[-1].read_text(encoding="utf-8"))
        ticket = tk.get("n_hold") if isinstance(tk.get("n_hold"), int) else None
        ticket_rebal = tk.get("rebal") if isinstance(tk.get("rebal"), int) else None
    def _cell_at(nh, rb):
        c = next((x for x in per_cell if (x["n_hold"], x["rebal"]) == (nh, rb)), None)
        return None if c is None else {
            "n_hold": nh, "rebal": rb, "judged": c["judged"],
            "median_cagr_pp": c["median_cagr_pp"],
            "band_pp": round(c["p95_cagr_pp"] - c["p05_cagr_pp"], 4),
            "min_cagr_pp": c["min_cagr_pp"], "max_cagr_pp": c["max_cagr_pp"],
            "phases": c["phases"]}

    # per-slot ranking stability across the aligned slots (every cell has offsets 0..9)
    slots = {}
    for c in cells:
        if c["phase_offset"] < ALIGNED_SLOTS:
            slots.setdefault(c["phase_offset"], {})[(c["n_hold"], c["rebal"])] = 100.0 * c["cagr"]
    keys = sorted({k for s in slots.values() for k in s})
    complete = [o for o, s in slots.items() if len(s) == len(keys)]
    ranks = {}
    winners = []
    for o in sorted(complete):
        vals = [slots[o][k] for k in keys]
        r = _rank(vals)
        ranks[o] = dict(zip(keys, r))
        winners.append(keys[max(range(len(vals)), key=lambda i: vals[i])])
    base = sorted(complete)[0] if complete else None
    slopes = [{"slot": o, "spearman_vs_slot%d" % base: spearman([ranks[base][k] for k in keys],
                                                                [ranks[o][k] for k in keys])}
              for o in sorted(complete) if o != base] if base is not None else []
    grid = {
        "cells": len(per_cell), "judged_cells": len(judged),
        "phases_total": len(cells),
        "between_cell_spread_pp": signal_pp,
        "median_cell_band_pp": noise_pp,
        "aligned_slots": len(complete),
        "distinct_winners_across_slots": [list(w) for w in sorted({tuple(w) for w in winners})],
        "n_distinct_winners": len({w for w in winners}),
        "slot_rank_stability": slopes,
        "note": ("between_cell_spread_pp = max-min of the cells' median CAGR; a cell's band is "
                 "its own p95-p05 across one complete rebalance cycle"),
    }
    return {
        "criteria": {"cells": [list(c) for c in CELLS], "min_phases": MIN_PHASES,
                     "aligned_slots": ALIGNED_SLOTS, "gate_tol": GATE_TOL},
        "per_cell": per_cell, "grid": grid,
        "verdict": verdict, "verdict_reasons": reasons,
        "authoritative_cells": {
            "production_card": _cell_at(prod, prod_rebal) if prod and prod_rebal else None,
            "executable_ticket": _cell_at(ticket, ticket_rebal) if ticket and ticket_rebal else None,
        },
    }


# ---------------------------------------------------------------- run / check / selftest

def run(workers=None, k=0.0, cost=None, out=None):
    global OUT_JSON
    cost = H.COST if cost is None else cost
    # r1360 unit guard: cost is a FRACTION per side, so 10bp is 0.0010 and a
    # caller who writes --cost=20 (2000%/side) must be told so here rather than
    # discovering it as `TypeError: float() argument must be ... not 'complex'`
    # 280 cells later -- the equity level crosses zero, growth becomes negative
    # and `growth ** (1/yrs)` returns a complex number inside stats2 (live case:
    # pool row E272-ATLAS-COST20, stocked 2026-10-30 with --cost=20).
    if not (0.0 <= float(cost) <= 0.05):
        raise SystemExit(
            "etf_book_phase_atlas: --cost=%r is not a fraction per side "
            "(0 <= cost <= 0.05 = 500bp). 10bp is 0.0010, not 10; 20bp is "
            "0.0020, not 20. Refusing to price a book at %.1f%% per side."
            % (cost, float(cost) * 100.0))
    close, _o, _a, _s, _c, _nf = P.prep_panel()   # index only; workers load their own copy
    jobs = []
    for (n_hold, rebal) in CELLS:
        for offset, d in enumerate(cell_phases(close.index, rebal)):
            key = "%d/%d/%d" % (n_hold, rebal, offset)
            jobs.append((key, _run_cell, (n_hold, rebal, offset, d, cost, k)))
    n = workers or worker_cap()
    res = run_cells_parallel(jobs, workers=n, desc="cells", initializer=_init_worker)
    used = int(res.pop("__workers__", n))
    cells = [res[key] for key, _f, _a in jobs]

    # activity precondition: the offsets must move the decision CALENDAR (r1261)
    sig = {}
    for c in cells:
        if (c["n_hold"], c["rebal"]) == CELLS[0]:
            sig[c["phase_offset"]] = (c["first_decision"], c["last_decision"])
    if len(set(sig.values())) != len(sig):
        raise RuntimeError("phase offsets collapsed onto one decision calendar: %r" % (sig,))

    payload = summarize(cells)
    payload["audit"] = {
        "workers": used, "jobs": len(cells), "cost": cost, "buffer_k": k,
        "target_vol": H.TARGET_VOL, "start": str(R.START),
        "parallelism": "ProcessPoolExecutor via scripts/parallel_runner.run_cells_parallel",
    }
    payload["rows"] = sorted(cells, key=lambda c: (c["n_hold"], c["rebal"], c["phase_offset"]))
    payload["script"] = SCRIPT
    payload["face"] = FACE
    payload["units"] = UNITS
    cutoff = str(max(close.index).date())
    payload["evidence_cutoff"] = cutoff
    # r1179: an arm face states WHICH world it measured on. The arms audit (E256/E259) reads
    # faces produced hours apart and compares their bands; without a stamp a reading from one
    # panel can sit beside a reading from another and read as a rule effect (E293 class).
    payload["panel"] = dict(P.PANEL_DIGEST or {})
    if out is not None:
        OUT_JSON = Path(out)
        # --out is documented as a repo-relative path; without this a relative
        # argument survives the whole 280-cell run and then dies in relative_to()
        if not OUT_JSON.is_absolute():
            OUT_JSON = ROOT / OUT_JSON
    payload["face"] = str(OUT_JSON.relative_to(ROOT)).replace("\\", "/")
    OUT_JSON.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if out is None:
        md = OUT_MD
    else:
        tag = OUT_JSON.stem.split("atlas")[-1].strip("_").upper() or "VARIANT"
        md = ROOT / "research" / ("ETF_BOOK_PHASE_ATLAS_" + tag + ".md")
    md.write_text(render_md(payload), encoding="utf-8")
    print("audit: workers=%d jobs=%d cost=%.4f k=%.2f" % (used, len(cells), cost, k))
    g = payload["grid"]
    print("grid: %d cells (%d judged) | spread %.2fpp vs median band %.2fpp -> %s"
          % (g["cells"], g["judged_cells"], g["between_cell_spread_pp"] or 0,
             g["median_cell_band_pp"] or 0, payload["verdict"]))
    for c in payload["per_cell"]:
        print("  N%-2d R%-2d median %6.2fpp band %6.2fpp sharpe %.3f  (+%s..%s over %d phases)"
              % (c["n_hold"], c["rebal"], c["median_cagr_pp"], c["p95_cagr_pp"] - c["p05_cagr_pp"],
                 c["median_sharpe"], c["min_cagr_pp"], c["max_cagr_pp"], c["phases"]))
    print("wrote", OUT_JSON)
    return 0


def check(path=None):
    path = OUT_JSON if path is None else path
    if not path.exists():
        print("FAIL: no face at %s" % path)
        return 2
    pay = json.loads(path.read_text(encoding="utf-8"))
    bad = []
    if [list(c) for c in CELLS] != pay.get("criteria", {}).get("cells"):
        bad.append("cell grid echo differs from the frozen constants")
    if pay.get("criteria", {}).get("min_phases") != MIN_PHASES:
        bad.append("min_phases echo differs")
    rows = pay.get("rows") or []
    if not rows:
        bad.append("face carries no rows")
        print("FAIL:", "; ".join(bad))
        return 2
    rebuilt = summarize(rows)
    for c in rebuilt["per_cell"]:
        pub = next((x for x in pay.get("per_cell") or []
                    if (x["n_hold"], x["rebal"]) == (c["n_hold"], c["rebal"])), None)
        if pub is None:
            bad.append("cell %d/%d missing from the face" % (c["n_hold"], c["rebal"]))
            continue
        for f in ("median_cagr_pp", "p05_cagr_pp", "p95_cagr_pp", "min_cagr_pp", "max_cagr_pp",
                  "share_positive", "median_sharpe", "median_maxdd", "median_oos_cagr_pp"):
            a, b = pub.get(f), c.get(f)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if abs(a - b) > max(GATE_TOL, abs(b) * 1e-9):
                    bad.append("cell %d/%d %s published %r but rows give %r"
                               % (c["n_hold"], c["rebal"], f, a, b))
            elif a != b:
                bad.append("cell %d/%d %s published %r but rows give %r"
                           % (c["n_hold"], c["rebal"], f, a, b))
    for f in ("between_cell_spread_pp", "median_cell_band_pp", "cells", "judged_cells", "phases_total"):
        a, b = (pay.get("grid") or {}).get(f), rebuilt["grid"].get(f)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if abs(a - b) > max(GATE_TOL, abs(b) * 1e-9):
                bad.append("grid %s published %r but rows give %r" % (f, a, b))
        elif a != b:
            bad.append("grid %s published %r but rows give %r" % (f, a, b))
    if pay.get("verdict") != rebuilt["verdict"]:
        bad.append("verdict published %r but the rule on the rows says %r"
                   % (pay.get("verdict"), rebuilt["verdict"]))
    if bad:
        print("FAIL:", "; ".join(bad[:6]))
        return 2
    print("CHECK OK: %d cells re-derived from %d rows; verdict=%s; spread %.2fpp vs band %.2fpp"
          % (rebuilt["grid"]["cells"], len(rows), pay["verdict"],
             pay["grid"]["between_cell_spread_pp"], pay["grid"]["median_cell_band_pp"]))
    return 0


def render_md(payload):
    g = payload["grid"]
    a = payload.get("audit") or {}
    lines = [
        "# ETF book -- phase atlas: is the grid's ordering a property of the market or of one calendar?",
        "",
        "Face: `%s` (regenerated by `python %s run`). Evidence cutoff **%s**."
        % (FACE, SCRIPT, payload.get("evidence_cutoff")),
        "",
        "## What was run",
        "",
        "- %d cells (n_hold %s x rebal %s), each on **every** decision origin inside one rebalance"
        " cycle -> %d engine runs, %s workers, cost %.4f/side, buffer k=%.2f, vol target %.2f."
        % (g["cells"], "/".join(sorted({str(c[0]) for c in CELLS})),
           "/".join(sorted({str(c[1]) for c in CELLS})), g["phases_total"],
           a.get("workers"), a.get("cost", 0.0), a.get("buffer_k", 0.0), a.get("target_vol", 0.0)),
        "- A cell's **band** is the p95-p5 of its CAGR across its own cycle. The grid's **spread**"
        " is max-min of the cells' median CAGR. Both in percentage points per year.",
        "",
        "## Reading",
        "",
        "**%s** -- %s." % (payload["verdict"], "; ".join(payload["verdict_reasons"])),
        "",
        "| n_hold | rebal | median CAGR | band (p05..p95) | min..max over cycle | Sharpe | maxDD | phases |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in payload["per_cell"]:
        lines.append("| %d | %d | %+.2fpp | %.2fpp (%+.2f..%+.2f) | %+.2f..%+.2f | %.3f | %.1f%% | %d |"
                     % (c["n_hold"], c["rebal"], c["median_cagr_pp"],
                        c["p95_cagr_pp"] - c["p05_cagr_pp"], c["p05_cagr_pp"], c["p95_cagr_pp"],
                        c["min_cagr_pp"], c["max_cagr_pp"], c["median_sharpe"],
                        100.0 * c["median_maxdd"], c["phases"]))
    lines += [
        "",
        "Grid: spread **%.2fpp** vs median cell band **%.2fpp**; across the %d aligned slots"
        " (offsets 0..%d) the top cell changes **%d** times."
        % (g["between_cell_spread_pp"], g["median_cell_band_pp"], g["aligned_slots"],
           ALIGNED_SLOTS - 1, g["n_distinct_winners"]),
        "",
        "## Why this is a decision and not a description",
        "",
        "The production card and the executable ticket quote different widths off the same panel."
        " A width change is only a decision if the cells it separates are separated by more than"
        " their own phase band; if they are not, the width choice is being read off one calendar"
        " and the honest statement is the band, not the point estimate.",
        "",
        "## Reproduction",
        "",
        "```",
        "python %s run            # rebuild the face (deterministic, zero network)" % SCRIPT,
        "python %s --check        # re-derive every scalar and the verdict from the rows" % SCRIPT,
        "python %s --selftest     # hermetic rule/gate scenarios" % SCRIPT,
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest

def _mk(n_hold, rebal, offset, cagr, sharpe=1.0, maxdd=-0.1, oos=None):
    return {"n_hold": n_hold, "rebal": rebal, "phase_offset": offset,
            "phase": "2020-01-0%d" % (offset + 1), "cagr": cagr, "sharpe": sharpe,
            "maxdd": maxdd, "oos_cagr": cagr if oos is None else oos,
            "turnover_per_decision": 1.0, "decisions": 80,
            "first_decision": "2020-01-0%d" % (offset + 1),
            "last_decision": "2026-10-29"}


def selftest():
    legs = []

    def leg(name, ok, why=""):
        legs.append((name, bool(ok), why))

    # 1. phase offsets are distinct bars inside one cycle
    idx = pd.bdate_range("2020-01-01", periods=200)
    ph = cell_phases(idx, 20)
    leg("phase offsets: 20 distinct bars inside one cycle", len(ph) == 20 and len(set(ph)) == 20)
    leg("phase offsets: all within the first cycle", (ph[-1] - ph[0]).days < 40)

    # 2. a phase-invariant grid is named as such, not silently judged
    flat = [_mk(n, r, o, 0.10) for (n, r) in CELLS for o in range(12)]
    s = summarize(flat)
    leg("invariant: identical phases -> PHASE_INVARIANT", s["verdict"] == "PHASE_INVARIANT", s["verdict"])

    # 3. a between-cell spread inside the band is named within-noise
    noisy = []
    for (n, r) in CELLS:
        base = 0.08 + 0.001 * n
        for o in range(12):
            noisy.append(_mk(n, r, o, base + (0.02 if o % 2 else -0.02)))
    s = summarize(noisy)
    leg("within-noise: +-2pp phase swing dwarfs a 1.2pp grid spread",
        s["verdict"] == "CONFIG_ORDER_WITHIN_PHASE_NOISE", s["verdict"])

    # 4. a spread above the band is named as exceeding it
    sep = []
    for i, (n, r) in enumerate(CELLS):
        for o in range(12):
            sep.append(_mk(n, r, o, 0.05 + 0.01 * i + (0.001 if o % 2 else -0.001)))
    s = summarize(sep)
    leg("exceeds: 11pp grid spread on a 0.2pp band", s["verdict"] == "CONFIG_ORDER_EXCEEDS_PHASE_NOISE",
        s["verdict"])

    # 5. a cell judged on too few phases is refused, not averaged in
    short = [_mk(3, 20, o, 0.10) for o in range(MIN_PHASES - 1)]
    s = summarize(short)
    leg("short cell: %d phases -> NOT_JUDGED" % (MIN_PHASES - 1), s["verdict"] == "NOT_JUDGED", s["verdict"])

    # 6. ties: spearman of identical rankings is 1, of reversed rankings is -1
    leg("spearman: identity=1, reversed=-1",
        spearman([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0 and spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0)
    leg("spearman: constants are 0, not NaN", spearman([2, 2, 2], [1, 2, 3]) == 0.0)

    # 7. the gate: a tampered scalar is caught by the rebuild
    good = [_mk(n, r, o, 0.10 + 0.001 * n + 0.0005 * o) for (n, r) in CELLS for o in range(12)]
    base = summarize(good)
    scratch = OUT_JSON.with_suffix(".selftest.json")
    tam = json.loads(json.dumps(base))
    tam["rows"] = good
    tam["script"], tam["face"] = SCRIPT, FACE
    tam["per_cell"][0]["median_cagr_pp"] += 0.5
    scratch.write_text(json.dumps(tam), encoding="utf-8")
    rc_bad_scalar = check(scratch)
    leg("gate: an edited median is red", rc_bad_scalar == 2, "rc=%d" % rc_bad_scalar)

    tam2 = json.loads(json.dumps(base))
    tam2["rows"] = good
    tam2["verdict"] = "CONFIG_ORDER_EXCEEDS_PHASE_NOISE" if base["verdict"] != "CONFIG_ORDER_EXCEEDS_PHASE_NOISE" else "PHASE_INVARIANT"
    scratch.write_text(json.dumps(tam2), encoding="utf-8")
    rc_bad_verdict = check(scratch)
    leg("gate: an edited verdict is red", rc_bad_verdict == 2, "rc=%d" % rc_bad_verdict)

    honest = json.loads(json.dumps(base))
    honest["rows"] = good
    honest["script"], honest["face"] = SCRIPT, FACE
    scratch.write_text(json.dumps(honest), encoding="utf-8")
    rc_ok = check(scratch)
    leg("gate: an honest face is green", rc_ok == 0, "rc=%d" % rc_ok)

    # 8. an empty face is a failure, not a pass
    scratch.write_text(json.dumps({"rows": []}), encoding="utf-8")
    rc_empty = check(scratch)
    leg("gate: a face with no rows is red", rc_empty == 2, "rc=%d" % rc_empty)

    # 9. r1360 unit guard: a cost written as basis points instead of a fraction is
    # refused up front. --cost=20 crashed 280 cells deep in stats2 (negative equity
    # -> growth ** (1/yr) is complex); the guard must name the unit, not fail later.
    try:
        run(workers=1, cost=20.0)
        leg("unit guard: --cost=20 (2000%/side) is refused, not run", False, "no refusal")
    except SystemExit as exc:
        msg = str(exc)
        leg("unit guard: --cost=20 (2000%/side) is refused, not run",
            "0.0020" in msg and "fraction" in msg, msg[:70])
    except Exception as exc:  # a TypeError here would mean the guard did not fire
        leg("unit guard: --cost=20 (2000%/side) is refused, not run", False,
            type(exc).__name__ + ": " + str(exc)[:50])
    # the scratch file is the only path selftest writes; the real face at OUT_JSON is never
    # created or removed by a test run
    try:
        scratch.unlink()
    except OSError:
        pass

    n_ok = sum(1 for _n, ok, _w in legs if ok)
    for name, ok, why in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + why) if why else ""))
    print("selftest: %d/%d PASS" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--k", type=float, default=0.0)
    ap.add_argument("--cost", type=float, default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None,
                    help="face path (default results/etf_book_phase_atlas.json); the pool rows "
                         "write k/cost variants to their own faces so they never clobber one another")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or a.cmd == "check":
        return check(Path(a.out) if a.out else None)
    return run(workers=a.workers, k=a.k, cost=a.cost, out=Path(a.out) if a.out else None)


if __name__ == "__main__":
    sys.exit(main())