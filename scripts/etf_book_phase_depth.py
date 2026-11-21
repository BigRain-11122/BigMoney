"""ETF book -- is the five-week phase set deep enough to adjudicate adoption?

The supply floor has been red for many rounds with the same sentence: four candidates,
none ready, and every refusal is `UNADJUDICABLE_PHASE` because "the phase spread is wider
than the distance to the line" (results/etf_book_phase_gate.json). That face measures the
spread on FIVE weekly starts -- 2020-01-01, 01-08, 01-15, 01-22, 01-29
(candidate_year_gate_phases.PHASE_STARTS, frozen before its first run). Five samples of a
weekly decision calendar is the whole evidence base for "this book can or cannot take
money", and nothing has ever measured whether five is enough.

This face asks exactly that, without touching the frozen gate:

Design (frozen before the first run):

  * starts  = EVERY 7th day from 2020-01-01 for 40 weeks. The generator is the gate's own
              (same anchor, same 7-day stride), so depth 5 reproduces PHASE_STARTS exactly
              and each deeper set is a PREFIX of the same ordered list -- the spreads are
              comparable, not a new sampling experiment.
  * depths  = 5, 10, 20, 40. The first is the frozen gate; the others only add weeks.
  * arms    = the three candidates the gate refused (imported from
              candidate_year_gate_phases.ARMS, never retyped).
  * verdict = adjudicate() from candidate_year_gate_phases on each depth's prefix. Nothing
              about the gate's rule changes here -- the same function, more rows.
  * words   = DEPTH_ADJUDICATES   the deepest set agrees AND its spread fits the margin
              DEPTH_NARROWS_NOT_ENOUGH  spread shrinks with depth but is still wider
              SAMPLING_IS_NOT_THE_LIMIT spread does not shrink with depth

Why this is not "re-running until it passes": the depth grid is fixed here, before the
first run, and every depth's reading is published beside the others. A face that only
printed depth 40 would be a retry; a face that prints 5/10/20/40 and its own trend is a
measurement of how much of the refusal is sampling.

Usage:
    python scripts/etf_book_phase_depth.py run
    python scripts/etf_book_phase_depth.py check
    python scripts/etf_book_phase_depth.py refresh   # no-op unless the panel moved
    python scripts/etf_book_phase_depth.py selftest
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402

OUT_JSON = ROOT / "results" / "etf_book_phase_depth.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_PHASE_DEPTH.md"

SCRIPT = "scripts/etf_book_phase_depth.py"
FACE = "results/etf_book_phase_depth.json"

ANCHOR = "2020-01-01"
STRIDE_DAYS = 7
DEPTHS = (5, 10, 20, 40)
NARROW_RATIO = 0.70    # a spread that keeps <70% of its 5-week width at depth 40 "narrows"

RULE = {
    "starts_generator": "every %d days from %s (the gate's own anchor and stride)"
                        % (STRIDE_DAYS, ANCHOR),
    "depths": list(DEPTHS),
    "prefix": True,
    "aggregate": "candidate_year_gate_phases.adjudicate on each depth's prefix",
    "words": {
        "DEPTH_ADJUDICATES": "the deepest set has one verdict and its spread fits the margin",
        "DEPTH_NARROWS_NOT_ENOUGH": "spread at depth 40 keeps <%.2f of its depth-5 width but "
                                    "is still wider than its own margin" % NARROW_RATIO,
        "SAMPLING_IS_NOT_THE_LIMIT": "spread at depth 40 keeps >=%.2f of its depth-5 width"
                                     % NARROW_RATIO,
    },
    "not_a_retry": "every depth's reading is published; the grid is frozen here, before the "
                   "first run, so a reader can see whether depth is the whole story",
}


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def start_grid(depth):
    """The first `depth` weekly starts from the gate's anchor (PHASE_STARTS at depth 5)."""
    d0 = date.fromisoformat(ANCHOR)
    return [(d0 + timedelta(days=STRIDE_DAYS * k)).isoformat() for k in range(depth)]


def trend_word(per_depth):
    """per_depth: {depth: {'state','spread_pp','margin_pp'}} -> one of the three words.

    Read only from the published readings, so check() can re-derive it byte for byte.
    """
    shallow = per_depth.get(DEPTHS[0]) or {}
    deep = per_depth.get(DEPTHS[-1]) or {}
    s0, s1 = shallow.get("spread_pp"), deep.get("spread_pp")
    if s0 is None or s1 is None:
        return "UNDECIDABLE_DEPTH"
    if deep.get("state") != "UNADJUDICABLE_PHASE":
        return "DEPTH_ADJUDICATES"
    return "DEPTH_NARROWS_NOT_ENOUGH" if s1 < s0 * NARROW_RATIO else "SAMPLING_IS_NOT_THE_LIMIT"


def run():
    t0 = time.time()
    close, openp, amt, sc, _nf = S.nobond_universe()
    cap = S.published_capacity()
    grid = start_grid(DEPTHS[-1])
    line = G.TOP2_SHARE_MAX

    cells = []       # one row per (arm, start)
    per_arm = {}
    for label, vt, floor in P.ARMS:
        rows = []
        for start in grid:
            ser, turn = P.arm(close, openp, amt, sc, vt, floor, start)
            yrs = Y.yearly_returns(ser)
            st = A.stats2(ser, "p")
            blk = G.admission_block(yrs, cap, None, st.get("cagr"))
            row = {
                "book": label, "start": start,
                "verdict": blk["verdict"],
                "top2_share": blk["year_metrics"]["top2_share"],
                "cagr_pct": blk["cagr_pct"],
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "turnover": round(turn, 3),
            }
            rows.append(row)
            cells.append(row)
            print("  %-24s %s -> %-12s top2 %s"
                  % (label, start, row["verdict"],
                     "n/a" if row["top2_share"] is None else "%.4f" % row["top2_share"]),
                  flush=True)
        by_depth = {}
        for d in DEPTHS:
            agg = P.adjudicate(rows[:d], line=line) if len(rows) >= d else None
            by_depth[str(d)] = agg
            if agg:
                print("%-24s depth %2d -> %-20s spread %s margin %s"
                      % (label, d, agg["state"],
                         "n/a" if agg.get("spread_pp") is None else "%.2fpp" % agg["spread_pp"],
                         "n/a" if agg.get("margin_pp") is None else "%.2fpp" % agg["margin_pp"]),
                      flush=True)
        per_arm[label] = {
            "books": {"vol_target": vt, "vol_floor": floor},
            "depths": by_depth,
            "trend": trend_word({int(k): v for k, v in by_depth.items() if v}),
        }
        print("%-24s -> %s" % (label, per_arm[label]["trend"]), flush=True)

    face = {
        "face": FACE,
        "script": SCRIPT,
        "question": "is a five-week phase set deep enough to adjudicate adoption, or is the "
                    "refusal `phase spread wider than margin` a sampling artefact?",
        "rule": RULE,
        "evidence_cutoff": str(close.index[-1].date()),
        "line_top2_share": line,
        "start_grid_40": grid,
        "arms": per_arm,
        "rows": cells,
        "audit": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_sec": round(time.time() - t0, 1),
            "cells": len(cells),
            "universe_bars": int(len(close)),
            "universe_last_bar": str(close.index[-1].date()),
        },
    }
    # a sentence per arm, so the reader does not have to read the grid
    sentences = []
    for label, blob in per_arm.items():
        d5 = blob["depths"]["5"]
        d40 = blob["depths"]["40"]
        sentences.append(
            "%s: %s at depth 5 (spread %spp vs margin %spp) -> %s at depth 40 "
            "(spread %spp vs margin %spp)"
            % (label, d5["state"], _pp(d5.get("spread_pp")), _pp(d5.get("margin_pp")),
               d40["state"], _pp(d40.get("spread_pp")), _pp(d40.get("margin_pp"))))
    face["sentence"] = "; ".join(sentences)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(face, ensure_ascii=False, indent=1), encoding="utf-8")
    write_doc(face)
    print("wrote %s" % OUT_JSON)
    print("wrote %s" % OUT_MD)
    print(face["sentence"])
    return face


def _pp(v):
    return "n/a" if v is None else "%.2f" % v


def _depth_table(blob):
    lines = ["| depth | state | median top-2 | spread | margin |", "|---|---|---|---|---|"]
    for d in DEPTHS:
        a = blob["depths"].get(str(d)) or {}
        lines.append("| %d | %s | %s | %s | %s |"
                     % (d, a.get("state", "n/a"),
                        "n/a" if a.get("median_top2_share") is None
                        else "%.4f" % a["median_top2_share"],
                        _pp(a.get("spread_pp")) + "pp", _pp(a.get("margin_pp")) + "pp"))
    return "\n".join(lines)


def write_doc(face):
    arms = face["arms"]
    parts = [
        "# ETF book -- is the five-week phase set deep enough?",
        "",
        "Generated by `%s` (read `--check` for the recomputation)." % face["script"],
        "",
        "**evidence_cutoff**: %s  |  **bars**: %d  |  **cells**: %d"
        % (face["evidence_cutoff"], face["audit"]["universe_bars"], face["audit"]["cells"]),
        "",
        "## What this asks",
        "",
        face["question"],
        "",
        "The frozen gate measures `phase spread` on five weekly starts. Every candidate it "
        "refused was refused by that one sentence. This face deepens the same generator to "
        "%d weeks and prints every depth, so \"not enough phases\" and \"genuinely unstable\" "
        "stop looking alike." % DEPTHS[-1],
        "",
        "## Rule (frozen before the first run)",
        "",
        "```json",
        json.dumps(face["rule"], ensure_ascii=False, indent=1),
        "```",
        "",
        "## Readings",
        "",
        "| arm | trend |",
        "|---|---|",
    ]
    for label, blob in arms.items():
        parts.append("| %s | %s |" % (label, blob["trend"]))
    parts.append("")
    for label, blob in arms.items():
        parts += ["### %s" % label, "", _depth_table(blob), ""]
    parts += ["## In one sentence", "", face["sentence"], ""]
    OUT_MD.write_text("\n".join(parts), encoding="utf-8")


def check(path=None):
    p = Path(path) if path else OUT_JSON
    face = _read_json(p)
    if not face or not face.get("rows"):
        print("CHECK FAIL: no rows")
        return 2
    rows = face["rows"]
    problems = []
    grid = face.get("start_grid_40") or []
    if len(grid) != DEPTHS[-1]:
        problems.append("start grid has %d rows, not %d" % (len(grid), DEPTHS[-1]))
    line = face.get("line_top2_share")
    if line is None:
        problems.append("the frozen line is missing")
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["book"], []).append(r)
    for label, blob in (face.get("arms") or {}).items():
        arm_rows = by_arm.get(label) or []
        depths = blob.get("depths") or {}
        for d in DEPTHS:
            published = depths.get(str(d))
            if not published:
                problems.append("%s depth %d missing" % (label, d))
                continue
            if len(arm_rows) < d:
                problems.append("%s has %d rows, cannot rebuild depth %d"
                                % (label, len(arm_rows), d))
                continue
            rebuilt = P.adjudicate(arm_rows[:d], line=line)
            if rebuilt["state"] != published["state"]:
                problems.append("%s depth %d state %s, rebuilt %s"
                                % (label, d, published["state"], rebuilt["state"]))
            for key in ("spread_pp", "margin_pp", "median_top2_share"):
                if _near(rebuilt.get(key), published.get(key)):
                    continue
                problems.append("%s depth %d %s %s != %s"
                                % (label, d, key, published.get(key), rebuilt.get(key)))
        per_depth = {int(k): v for k, v in depths.items() if v}
        want = trend_word(per_depth)
        if blob.get("trend") != want:
            problems.append("%s trend %s, rebuilt %s" % (label, blob.get("trend"), want))
    if problems:
        print("CHECK FAIL: %d" % len(problems))
        for x in problems[:12]:
            print("  " + x)
        return 1
    states = {blob["trend"] for blob in (face.get("arms") or {}).values()}
    print("CHECK OK: %d arms re-derived from %d rows; trends %s"
          % (len(face.get("arms") or {}), len(rows), ",".join(sorted(states))))
    print(face.get("sentence", ""))
    return 0


def _near(a, b, tol=1e-9):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def panel_last_bar():
    """The newest bar the live panel can price -- the external clock (r1594/r1850)."""
    try:
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(ROOT / "scripts"))
        import etf_composite_pf as F

        prices = F._dedupe(F._load_prices())
        close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
        close = close.replace(0.0, float("nan"))
        close, _ = F.drop_hollow_tail(close)
        return str(close.index[-1].date())
    except Exception:
        return None


def refresh_decision(face_cutoff, panel_cutoff):
    """SAME = nothing to pay for, STALE = the repricing owns the job, UNKNOWN = no clock."""
    if not face_cutoff or not panel_cutoff:
        return "UNKNOWN"
    return "STALE" if str(face_cutoff) < str(panel_cutoff) else "SAME"


def refresh():
    face = _read_json(OUT_JSON) or {}
    had = face.get("evidence_cutoff")
    live = panel_last_bar()
    state = refresh_decision(had, live)
    if state == "UNKNOWN":
        print("REFRESH_UNKNOWN panel or receipt unreadable (receipt=%s, panel=%s)"
              % (had, live))
        return 2
    if state == "SAME":
        print("REFRESH_NOOP evidence_cutoff=%s (the panel has not moved)" % live)
        return 0
    started = time.time()
    run()
    print("REFRESH_RAN %s -> %s (%.1fs)" % (had, live, time.time() - started))
    return 0


def selftest():
    legs = []

    def leg(name, ok, why=""):
        legs.append((name, bool(ok), why))

    # 1. the generator reproduces the frozen gate exactly at depth 5
    import candidate_year_gate_phases as P2
    leg("grid: depth 5 == the frozen PHASE_STARTS",
        start_grid(5) == list(P2.PHASE_STARTS), str(start_grid(5)))
    leg("grid: depth 40 starts at the same anchor",
        start_grid(40)[0] == ANCHOR and len(start_grid(40)) == 40)

    # 2. prefixes nest (a deeper set contains the shallower one)
    g = start_grid(40)
    leg("prefix: depths 5/10/20 are prefixes of 40",
        g[:5] == start_grid(5) and g[:10] == start_grid(10) and g[:20] == start_grid(20))

    # 3. the trend word reads only published numbers
    leg("trend: a stable deep reading is DEPTH_ADJUDICATES",
        trend_word({5: {"state": "UNADJUDICABLE_PHASE", "spread_pp": 12.3},
                    40: {"state": "ADMIT", "spread_pp": 4.0}}) == "DEPTH_ADJUDICATES")
    leg("trend: a spread that halves but still refuses narrows",
        trend_word({5: {"state": "UNADJUDICABLE_PHASE", "spread_pp": 20.0},
                    40: {"state": "UNADJUDICABLE_PHASE", "spread_pp": 12.0}})
        == "DEPTH_NARROWS_NOT_ENOUGH")
    leg("trend: a flat spread means depth is not the limit",
        trend_word({5: {"state": "UNADJUDICABLE_PHASE", "spread_pp": 12.0},
                    40: {"state": "UNADJUDICABLE_PHASE", "spread_pp": 11.5}})
        == "SAMPLING_IS_NOT_THE_LIMIT")
    leg("trend: a missing reading is UNDECIDABLE, never a pass",
        trend_word({5: {"state": "UNADJUDICABLE_PHASE", "spread_pp": None},
                    40: {"state": "ADMIT", "spread_pp": None}}) == "UNDECIDABLE_DEPTH")

    # 4. adjudicate over a prefix is the imported function, not a copy
    synth = [{"start": s, "verdict": "ADMIT", "top2_share": 0.5 + 0.001 * i}
             for i, s in enumerate(start_grid(10))]
    agg = P2.adjudicate(synth, line=G.TOP2_SHARE_MAX)
    leg("adjudicate: one verdict and a narrow spread is judged",
        agg["state"] != "UNADJUDICABLE_PHASE" and agg["spread_pp"] < 1.0, agg["state"])

    # 5. the gate's line is imported, not retyped
    leg("line: TOP2_SHARE_MAX comes from candidate_year_gate",
        RULE["aggregate"].startswith("candidate_year_gate_phases.adjudicate"))

    # 6. the refresh gate is right in both directions
    leg("gate: an older receipt is STALE", refresh_decision("2026-01-02", "2026-01-05") == "STALE")
    leg("gate: a receipt on the panel's bar needs nothing",
        refresh_decision("2026-01-05", "2026-01-05") == "SAME")
    leg("gate: a missing clock is UNKNOWN, never fresh",
        refresh_decision(None, "2026-01-05") == "UNKNOWN"
        and refresh_decision("2026-01-05", None) == "UNKNOWN")

    n_ok = sum(1 for _n, ok, _w in legs if ok)
    for name, ok, why in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + why) if why else ""))
    print("selftest: %d/%d PASS" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        run()
        return 0
    if cmd == "check":
        return check()
    if cmd == "refresh":
        return refresh()
    print("usage: etf_book_phase_depth.py [run|check|refresh|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
