#!/usr/bin/env python
"""ETF book -- is the phase spread each start's partial-year stub?

r1921 published `etf_book_phase_depth.py`: on every candidate book the spread of
`top2_share` across the weekly phase starts does not narrow with depth (12.33pp at
depth 5 -> 117.65pp at depth 40).  That face said what the spread is NOT (a
sampling artefact of too few phases).  This face asks what it IS.

Every phase start is the gate's anchor shifted by a multiple of seven days, so each
start lands at a different place inside its first calendar year.  The gate counts a
calendar year with fewer than four cohorts as a *partial* year and deliberately
keeps it in Y3/Y4 ("a loss booked in the current year is a loss") -- so a 7-day
shift of the start rewrites how much of the first year the window contains while
the book itself, the engine and the panel are untouched.  `top2_share` is a ratio
of yearly arithmetic returns, so that stub enters both the numerator and the
denominator.

The gate already prints the friendlier column (`top2_share_full_only`, full years
only) beside the one it judges on.  This face runs the *same* phase criterion on
both columns and asks how much of the spread the stub accounts for.  It is a
diagnosis of the ruler, not a retry of the refusal: the verdict column is the
gate's own and never switches.

Frozen before the first run:
  keep = spread(full_only) / spread(all)          (same starts, same arms)
  STUB_IS_THE_SPREAD        keep <= 0.50
  STUB_SHARES_THE_SPREAD    0.50 < keep < 0.85
  STUB_IS_NOT_THE_SPREAD    keep >= 0.85
  UNDECIDABLE               any arm lacks either column
`candidate_year_gate_phases.adjudicate` is imported, not re-implemented: the only
thing this face changes is which of the gate's own two columns it is fed.

self  python scripts/etf_book_phase_stub.py selftest      # synthetic, no network
run   python scripts/etf_book_phase_stub.py run
check python scripts/etf_book_phase_stub.py check         # re-derives, no repricing
refresh  # pays the repricing only when the panel moved (r1594/r1850 clock)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

SCRIPT = "scripts/etf_book_phase_stub.py"
FACE = "results/etf_book_phase_stub.json"
OUT_JSON = ROOT / FACE
OUT_MD = ROOT / "research" / "ETF_BOOK_PHASE_STUB.md"

ANCHOR = "2020-01-01"
STRIDE_DAYS = 7
DEPTH = 40
IS_THE_SPREAD = 0.50
SHARES_THE_SPREAD = 0.85

RULE = {
    "starts_generator": "every %d days from %s (the gate's own anchor and stride)"
                        % (STRIDE_DAYS, ANCHOR),
    "starts": DEPTH,
    "columns": {
        "all": "year_metrics.top2_share (partial years kept -- the column the gate judges on)",
        "full_only": "year_metrics.top2_share_full_only (full years only -- printed, not judged)",
    },
    "keep": "spread(full_only) / spread(all) on the same starts and arms",
    "words": {
        "STUB_IS_THE_SPREAD": "keep <= %.2f" % IS_THE_SPREAD,
        "STUB_SHARES_THE_SPREAD": "%.2f < keep < %.2f" % (IS_THE_SPREAD, SHARES_THE_SPREAD),
        "STUB_IS_NOT_THE_SPREAD": "keep >= %.2f" % SHARES_THE_SPREAD,
        "UNDECIDABLE": "an arm lacks one of the two columns",
    },
    "why_not_a_retry": "the verdict column is the gate's own in both readings; only the "
                       "dispersion statistic changes columns, and both are published",
}


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def start_grid(depth=DEPTH):
    d0 = date.fromisoformat(ANCHOR)
    return [(d0 + timedelta(days=STRIDE_DAYS * k)).isoformat() for k in range(depth)]


def spread_of(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    return max(vals) - min(vals)


def keep_ratio(spread_all_pp, spread_full_pp):
    if spread_all_pp is None or spread_full_pp is None:
        return None
    if spread_all_pp == 0:
        return None
    return float(spread_full_pp) / float(spread_all_pp)


def word_for(keep):
    if keep is None:
        return "UNDECIDABLE"
    if keep <= IS_THE_SPREAD:
        return "STUB_IS_THE_SPREAD"
    if keep < SHARES_THE_SPREAD:
        return "STUB_SHARES_THE_SPREAD"
    return "STUB_IS_NOT_THE_SPREAD"


def stub_of(years):
    """How much of the first calendar year the window contains (cohorts, partial flag)."""
    if not years:
        return None, None, None
    keys = sorted(years)
    first = years[keys[0]]
    return keys[0], first.get("cohorts"), bool(first.get("cohorts", 0) < 4)


def rows_for_arm(label, vt, floor, close, openp, amt, sc, cap):
    rows = []
    for start in start_grid():
        ser, turn = P.arm(close, openp, amt, sc, vt, floor, start)
        yrs = Y.yearly_returns(ser)
        st = A.stats2(ser, "p")
        blk = G.admission_block(yrs, cap, None, st.get("cagr"))
        ym = blk["year_metrics"]
        first_year, stub_cohorts, stub_partial = stub_of({int(k): v for k, v in yrs.items()})
        rows.append({
            "book": label,
            "start": start,
            "verdict": blk["verdict"],
            "top2_share": ym.get("top2_share"),
            "top2_share_full_only": ym.get("top2_share_full_only"),
            "annual_sum": ym.get("annual_sum"),
            "years": len(yrs),
            "first_year": first_year,
            "stub_cohorts": stub_cohorts,
            "stub_partial": stub_partial,
            "cagr_pct": blk["cagr_pct"],
            "turnover": round(turn, 3),
        })
        print("  %-22s %s stub %s/%s -> top2 %s | full-only %s | %s"
              % (label, start, stub_cohorts, "partial" if stub_partial else "full",
                 _f(rows[-1]["top2_share"]), _f(rows[-1]["top2_share_full_only"]),
                 rows[-1]["verdict"]), flush=True)
    return rows


def _f(v):
    return "n/a" if v is None else "%.4f" % v


def distinct_counts(rows, key="top2_share"):
    """How many different readings 40 starts actually produce, and the loudest repeat.

    Disclosure only, no threshold: a start that re-buckets the same bars cannot add an
    independent draw, and a repeated value says so without any statistical claim.
    """
    vals = [None if r.get(key) is None else round(float(r[key]), 4) for r in rows]
    seen = {}
    for v in vals:
        if v is None:
            continue
        seen[v] = seen.get(v, 0) + 1
    if not seen:
        return {"distinct": 0, "top_value": None, "top_count": 0}
    top_v, top_n = max(seen.items(), key=lambda kv: (kv[1], kv[0]))
    return {"distinct": len(seen), "top_value": top_v, "top_count": top_n}


def summarize(rows, line):
    """Spread of both columns on the same rows + the same phase criterion on each."""
    sp_all = spread_of([r["top2_share"] for r in rows])
    sp_full = spread_of([r["top2_share_full_only"] for r in rows])
    keep = keep_ratio(None if sp_all is None else round(sp_all * 100, 4),
                      None if sp_full is None else round(sp_full * 100, 4))
    state_all = P.adjudicate(rows, line=line)
    full_rows = [dict(r, top2_share=r["top2_share_full_only"]) for r in rows]
    state_full = P.adjudicate(full_rows, line=line)
    partial_n = sum(1 for r in rows if r.get("stub_partial"))
    return {
        "spread_all_pp": None if sp_all is None else round(sp_all * 100, 4),
        "spread_full_only_pp": None if sp_full is None else round(sp_full * 100, 4),
        "keep": keep,
        "word": word_for(keep),
        "state_judged_on_all": state_all["state"],
        "state_judged_on_full_only": state_full["state"],
        "margin_all_pp": state_all.get("margin_pp"),
        "margin_full_only_pp": state_full.get("margin_pp"),
        "distinct_top2": distinct_counts(rows, "top2_share"),
        "distinct_top2_full_only": distinct_counts(rows, "top2_share_full_only"),
        "median_all": state_all.get("median_top2_share"),
        "median_full_only": state_full.get("median_top2_share"),
        "rows": len(rows),
        "partial_stub_rows": partial_n,
        "reason_all": state_all.get("reason"),
        "reason_full_only": state_full.get("reason"),
    }


def run():
    t0 = time.time()
    close, openp, amt, sc, _nf = S.nobond_universe()
    cap = S.published_capacity()
    line = G.TOP2_SHARE_MAX
    rows = []
    per_arm = {}
    for label, vt, floor in P.ARMS:
        arm_rows = rows_for_arm(label, vt, floor, close, openp, amt, sc, cap)
        rows.extend(arm_rows)
        per_arm[label] = summarize(arm_rows, line)
        blob = per_arm[label]
        print("%-22s keep %s -> %s | spread %.2fpp -> %.2fpp | %s -> %s"
              % (label, "n/a" if blob["keep"] is None else "%.3f" % blob["keep"],
                 blob["word"], blob["spread_all_pp"] or 0.0,
                 blob["spread_full_only_pp"] or 0.0,
                 blob["state_judged_on_all"], blob["state_judged_on_full_only"]),
              flush=True)

    face = {
        "face": FACE,
        "script": SCRIPT,
        "question": "depth 40 widened the phase spread instead of narrowing it -- is that "
                    "spread the book, or each start's partial-year stub?",
        "rule": RULE,
        "evidence_cutoff": str(close.index[-1].date()),
        "line_top2_share": line,
        "start_grid": start_grid(),
        "arms": per_arm,
        "rows": rows,
        "audit": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_sec": round(time.time() - t0, 1),
            "cells": len(rows),
            "universe_bars": int(len(close)),
            "universe_last_bar": str(close.index[-1].date()),
        },
    }
    sentences = []
    for label, blob in per_arm.items():
        d_all, d_full = blob["distinct_top2"], blob["distinct_top2_full_only"]
        sentences.append(
            "%s: %s (spread %.2fpp judged -> %.2fpp full-only, keep %s); even on full-only the "
            "criterion still reads %s (%.2fpp vs a %.2fpp margin), and the %d starts collapse to "
            "%d different full-only readings (loudest %.4f repeats %d times, against %.4f repeats "
            "%d times on the judged column)"
            % (label, blob["word"], blob["spread_all_pp"] or 0.0,
               blob["spread_full_only_pp"] or 0.0,
               "n/a" if blob["keep"] is None else "%.3f" % blob["keep"],
               blob["state_judged_on_full_only"], blob["spread_full_only_pp"] or 0.0,
               blob["margin_full_only_pp"] or 0.0,
               blob["rows"], d_full["distinct"],
               d_full["top_value"] or 0.0, d_full["top_count"],
               d_all["top_value"] or 0.0, d_all["top_count"]))
    face["sentence"] = "; ".join(sentences)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(face, ensure_ascii=False, indent=1), encoding="utf-8")
    write_doc(face)
    print("wrote %s" % OUT_JSON)
    print("wrote %s" % OUT_MD)
    print(face["sentence"])
    return face


def write_doc(face):
    parts = ["# ETF book -- is the phase spread the partial-year stub?", "",
             "Generated by `%s` (read `--check` for the recomputation)." % SCRIPT, "",
             "**evidence_cutoff**: %s  |  **bars**: %d  |  **cells**: %d"
             % (face["evidence_cutoff"], face["audit"]["universe_bars"],
                face["audit"]["cells"]), "",
             "## What this asks", "",
             face["question"], "",
             "Every phase start is the gate's own anchor stepped by seven days, so each start",
             "lands at a different point inside its first calendar year. The gate counts a",
             "calendar year with fewer than four cohorts as *partial* and keeps it in Y3/Y4.",
             "A seven-day shift therefore rewrites the first year's slice without touching the",
             "book, the engine or the panel. `top2_share` is a ratio of yearly arithmetic",
             "returns, so that slice enters both numerator and denominator.", "",
             "## Rule (frozen before the first run)", "", "```json",
             json.dumps(face["rule"], ensure_ascii=False, indent=1), "```", "",
             "## Readings", "", "| arm | word | spread judged | spread full-only | keep |",
             "|---|---|---|---|---|"]
    for label, blob in face["arms"].items():
        parts.append("| %s | %s | %.2fpp | %.2fpp | %s |"
                     % (label, blob["word"], blob["spread_all_pp"] or 0.0,
                        blob["spread_full_only_pp"] or 0.0,
                        "n/a" if blob["keep"] is None else "%.3f" % blob["keep"]))
    parts += ["", "## Same criterion, both columns", "",
              "| arm | judged on all | judged on full-only | median all | median full-only | partial stubs |",
              "|---|---|---|---|---|---|"]
    for label, blob in face["arms"].items():
        parts.append("| %s | %s | %s | %.4f | %.4f | %d/%d |"
                     % (label, blob["state_judged_on_all"], blob["state_judged_on_full_only"],
                        blob["median_all"] or 0.0, blob["median_full_only"] or 0.0,
                        blob["partial_stub_rows"], blob["rows"]))
    parts += ["", "## Are forty starts forty draws?", "",
              "| arm | distinct readings (judged) | loudest repeat | distinct readings (full-only) |",
              "|---|---|---|---|"]
    for label, blob in face["arms"].items():
        d1 = blob["distinct_top2"]
        d2 = blob["distinct_top2_full_only"]
        parts.append("| %s | %d of %d | %s x%d | %d of %d |"
                     % (label, d1["distinct"], blob["rows"],
                        "n/a" if d1["top_value"] is None else "%.4f" % d1["top_value"],
                        d1["top_count"], d2["distinct"], blob["rows"]))
    parts += ["", "A start shifted by a week re-buckets the same panel into different calendar",
              "years; a repeated reading is that, not a second piece of evidence. No threshold is",
              "attached to these counts -- they are disclosure.", ""]
    parts += ["", "## What this settles", "",
              "- `STUB_IS_THE_SPREAD` means more than half of the phase width is the start's own",
              "  partial-year slice: the phase set is not a sample of the book's behaviour, it is",
              "  the same bars re-bucketed into different calendar years.",
              "- It does not by itself rescue or condemn the ruler. Each arm's full-only state is",
              "  printed above: when it is still `UNADJUDICABLE_PHASE`, removing the stub leaves a",
              "  spread that still cannot adjudicate, so the adoption question has to be asked a",
              "  different way (fixed-length windows or the single-window record) -- not by",
              "  adding more starts.",
              "- Neither column is a verdict about the book: the verdict column above is the",
              "  gate's own and is unchanged by this face.", ""]
    parts += ["", "## In one sentence", "", face["sentence"], ""]
    OUT_MD.write_text("\n".join(parts), encoding="utf-8")


def check(path=None):
    p = Path(path) if path else OUT_JSON
    face = _read_json(p)
    if not face or not face.get("rows"):
        print("CHECK FAIL: no rows")
        return 2
    rows = face["rows"]
    line = face.get("line_top2_share")
    problems = []
    if line is None:
        problems.append("the frozen line is missing")
    if len(face.get("start_grid") or []) != DEPTH:
        problems.append("start grid is not %d rows" % DEPTH)
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["book"], []).append(r)
    for label, blob in (face.get("arms") or {}).items():
        arm_rows = by_arm.get(label) or []
        if len(arm_rows) != DEPTH:
            problems.append("%s has %d rows, not %d" % (label, len(arm_rows), DEPTH))
            continue
        rebuilt = summarize(arm_rows, line)
        for key in ("spread_all_pp", "spread_full_only_pp", "keep", "word",
                    "state_judged_on_all", "state_judged_on_full_only",
                    "margin_all_pp", "margin_full_only_pp", "partial_stub_rows",
                    "distinct_top2", "distinct_top2_full_only"):
            got, want = rebuilt.get(key), blob.get(key)
            if isinstance(got, float) or isinstance(want, float):
                if not _near(got, want):
                    problems.append("%s %s %s != %s" % (label, key, want, got))
            elif got != want:
                problems.append("%s %s %s != %s" % (label, key, want, got))
    if problems:
        print("CHECK FAIL: %d" % len(problems))
        for x in problems[:12]:
            print("  " + x)
        return 1
    words = {b["word"] for b in (face.get("arms") or {}).values()}
    print("CHECK OK: %d arms re-derived from %d rows; words %s"
          % (len(face.get("arms") or {}), len(rows), ",".join(sorted(words))))
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
        import pandas as pd
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
        print("REFRESH_STALE panel or receipt unreadable (receipt=%s, panel=%s)" % (had, live))
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

    import candidate_year_gate_phases as P2
    leg("grid: depth 40 on the gate's own anchor",
        start_grid()[0] == ANCHOR and len(start_grid()) == DEPTH)
    leg("grid: depth 5 prefix == the frozen PHASE_STARTS",
        start_grid(5) == list(P2.PHASE_STARTS))

    # spread/keep arithmetic
    leg("spread: two values give their width", abs(spread_of([0.7, 0.9]) - 0.2) < 1e-12)
    leg("spread: one value is not a spread, it is None", spread_of([0.7]) is None)
    leg("keep: half the width is 0.5", abs(keep_ratio(20.0, 10.0) - 0.5) < 1e-12)
    leg("keep: a zero judged width is undecidable, not infinite",
        keep_ratio(0.0, 5.0) is None and keep_ratio(None, 5.0) is None)

    # the three words, at their edges
    leg("word: keep 0.50 is the stub", word_for(0.50) == "STUB_IS_THE_SPREAD")
    leg("word: keep 0.51 shares it", word_for(0.51) == "STUB_SHARES_THE_SPREAD")
    leg("word: keep 0.85 is no longer the stub", word_for(0.85) == "STUB_IS_NOT_THE_SPREAD")
    leg("word: a missing keep is UNDECIDABLE, never a pass", word_for(None) == "UNDECIDABLE")

    # summarize() runs the imported criterion on both columns, not a copy
    rows = []
    for i, s in enumerate(start_grid(10)):
        rows.append({"book": "x", "start": s, "verdict": "ADMIT",
                     "top2_share": 0.80 + 0.002 * i,
                     "top2_share_full_only": 0.70 + 0.0005 * i,
                     "annual_sum": 1.0, "years": 6, "first_year": 2020,
                     "stub_cohorts": 4, "stub_partial": False,
                     "cagr_pct": 5.0, "turnover": 0.0})
    blob = summarize(rows, G.TOP2_SHARE_MAX)
    leg("summarize: two columns, two widths",
        blob["spread_all_pp"] is not None and blob["spread_full_only_pp"] is not None
        and blob["spread_full_only_pp"] < blob["spread_all_pp"], str(blob["spread_full_only_pp"]))
    leg("summarize: the full-only reading is narrower -> stub word",
        blob["word"] == "STUB_IS_THE_SPREAD", blob["word"])
    leg("summarize: an identical column keeps everything (no false relief)",
        summarize([dict(r, top2_share_full_only=r["top2_share"]) for r in rows],
                  G.TOP2_SHARE_MAX)["word"] == "STUB_IS_NOT_THE_SPREAD")
    leg("summarize: a missing column is UNDECIDABLE",
        summarize([dict(r, top2_share_full_only=None) for r in rows],
                  G.TOP2_SHARE_MAX)["word"] == "UNDECIDABLE")

    # the criterion is the imported function
    same = summarize(rows, G.TOP2_SHARE_MAX)
    leg("criterion: state came from candidate_year_gate_phases.adjudicate",
        same["state_judged_on_all"] == P2.adjudicate(rows, line=G.TOP2_SHARE_MAX)["state"])

    # repetition disclosure
    rep = [{"top2_share": 0.8}, {"top2_share": 0.8}, {"top2_share": 0.9},
           {"top2_share": None}]
    leg("distinct: repeats are counted, missing readings dropped",
        distinct_counts(rep) == {"distinct": 2, "top_value": 0.8, "top_count": 2},
        str(distinct_counts(rep)))
    leg("distinct: no readings at all is 0, never a crash",
        distinct_counts([{"top2_share": None}])["distinct"] == 0)

    # refresh gate both directions
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
    print("usage: etf_book_phase_stub.py [run|check|refresh|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
