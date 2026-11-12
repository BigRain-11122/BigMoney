"""r1613 disclosed a ladder. A disclosure is not an adoption decision.

The ladder (scripts/etf_book_vt_ladder.py) priced seven vol-target rungs on one
decision grid and printed which of them clear the frozen calendar gate. Two rungs
cleared it -- vt15 with 14.37% CAGR / -16.04% dd / 0.998 Sharpe, and above it
vt20/vt25 whose targets never bind -- and the round that produced them changed no
production config. That was deliberate, but it leaves the desk with a number and no
decision.

The reason a disclosure is not a decision is the r1325 lesson (E188: run a path test
before adopting a rule): a single decision grid can make a rule look better than it
is, because changing only the phase of the decision calendar changes the book. So
this face prices every rung on four phases spread through one rebalance cycle and
asks the only question that settles it: **does the rung clear the gate on all four
phases, and is the margin to the line wider than the phase spread?**

What it refuses to do:

* It does not re-implement the gate. `candidate_year_gate.admission_block` is
  imported as it stands, and the phases come from
  `etf_book_buffer_adoption.phase_starts` -- the same helper the buffer test used,
  not a second copy of it (E289: one implementation, two readers).
* It does not call a 3-of-4 rung "mostly passing". A rung whose verdict depends on
  where the calendar starts is a rung that cannot be adopted, and the receipt says
  which phase refused it.
* It does not treat a bigger CAGR as a better rung. Every cell prints CAGR,
  drawdown and realised vol beside the verdict so the trade stays visible.

Usage:
    python scripts/etf_book_vt_phases.py run
    python scripts/etf_book_vt_phases.py check
    python scripts/etf_book_vt_phases.py selftest
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402
import etf_book_vt_ladder as L  # noqa: E402
import etf_book_buffer_adoption as B  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_vt_phases")
OUT = os.path.join(OUT_DIR, "VT-PHASES.json")


def cell(close, openp, amt, score, label, vt, start):
    """One (rung, phase) cell through the production engine.

    `start` is the only thing that differs between a rung's four cells, so any
    disagreement between them is the calendar's, never a different book.
    """
    diag = []
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score,
        L.CELL["rebalance_days"], L.CELL["top_n"], L.CELL["cost"],
        vol_target=vt, start=str(pd.Timestamp(start).date()), diag=diag)
    years = L.yearly_returns(ser)
    cagr = A.stats2(ser, label).get("cagr")
    blk = G.admission_block(years, None, None, cagr)
    decision_dates = [str(pd.Timestamp(r["date"]).date()) for r in diag]
    return {
        "phase_start": str(pd.Timestamp(start).date()),
        "verdict": blk["verdict"],
        "checks": blk["checks"],
        "top2_share": blk["year_metrics"]["top2_share"],
        "worst_year_pp": blk["year_metrics"].get("worst_year_pp"),
        "positive_years_share": blk["year_metrics"].get("positive_years_share"),
        "cagr_pct": cagr,
        "sharpe": A.stats2(ser, label).get("sharpe"),
        "maxdd_pct": A.stats2(ser, label).get("maxdd"),
        "vol_realised_pct": (None if L.realised_vol(ser) is None
                             else round(L.realised_vol(ser) * 100.0, 3)),
        "turnover_per_side": round(float(turn), 3),
        # the phase signature is the DECISION DATES, not a count: four phases inside one
        # cycle can share a count and still never decide on the same day (r1261/r1325).
        "first_decision": decision_dates[0] if decision_dates else None,
        "last_decision": decision_dates[-1] if decision_dates else None,
        "n_decisions": len(decision_dates),
    }


def reference_cells(close, cols, starts) -> list:
    """The same universe held equally -- the most diversified shape this basket allows.

    r1614 refused every rung on at least one phase and called it NO_RUNG_SURVIVES.
    Before that sentence can be read as "the books are bad", it has to be measured
    whether the line can pass anything of this shape at all. Y4 divides the two best
    annual nets by the SUM of all annual nets (candidate_year_gate.year_metrics), so
    the number moves with the book's return level as much as with its skew: a
    low-return book can print a huge share while holding every name in the basket.

    This arm holds all of `cols` equally, rebalanced every bar, zero cost -- no
    selection, no timing, no vol target. It is deliberately generous (no cost) and
    deliberately naive; its only job is to say what the line reads on a book that
    makes no decisions at all. It is printed, never used to admit a rung.
    """
    rets = close[cols].pct_change()
    eq = (1.0 + rets.mean(axis=1).fillna(0.0)).cumprod()
    out = []
    for start in starts:
        s = eq[eq.index >= pd.Timestamp(start)]
        years = L.yearly_returns(s)
        st = A.stats2(s, "reference")
        cagr = st.get("cagr")
        blk = G.admission_block(years, None, None, cagr)
        after = close.index[close.index >= pd.Timestamp(start)]
        alive = int(close[cols].loc[after[0]].notna().sum()) if len(after) else None
        out.append({
            "phase_start": str(pd.Timestamp(start).date()),
            "top2_share": blk["year_metrics"]["top2_share"],
            "worst_year_pp": blk["year_metrics"].get("worst_year_pp"),
            "positive_years_share": blk["year_metrics"].get("positive_years_share"),
            "cagr_pct": cagr,
            "sharpe": st.get("sharpe"),
            "maxdd_pct": st.get("maxdd"),
            "vol_realised_pct": (None if L.realised_vol(s) is None
                                 else round(L.realised_vol(s) * 100.0, 3)),
            "verdict": blk["verdict"],
            "names_alive_at_start": alive,
        })
    return out


def reference_verdict(cells: list, line=None) -> dict:
    """Did the gate clear on the book that makes no decisions?

    `REFERENCE_ALSO_REFUSED` is the case that makes the rung verdicts unreadable as
    a ranking: the line refuses the most diversified shape in the same basket, so a
    rung that is refused is not thereby worse than the universe. It turns no rung into
    an adoption -- it names why the answer cannot be used to pick one.
    """
    line = G.TOP2_SHARE_MAX if line is None else float(line)
    tops = [c["top2_share"] for c in cells if c.get("top2_share") is not None]
    if not cells:
        return {"verdict": "NO_READING", "detail": "the reference priced no phase"}
    if not tops:
        return {"verdict": "NO_READING", "detail": "no phase produced a top-2 share"}
    admits = [c for c in cells if c.get("verdict") == "ADMIT"]
    out = {
        "phases": len(cells),
        "pass_phases": len(admits),
        "top2_min": round(min(tops), 4),
        "top2_max": round(max(tops), 4),
        "top2_median": round(float(np.median(tops)), 4),
        "line": line,
        "method": "equal_weight_daily_rebalance_zero_cost",
    }
    if admits:
        out["verdict"] = "REFERENCE_CLEARS"
        out["detail"] = ("the same universe held equally clears the line on %d of %d "
                         "phases, so the line can pass this shape" % (len(admits), len(cells)))
    else:
        out["verdict"] = "REFERENCE_ALSO_REFUSED"
        out["detail"] = ("the same universe held equally -- no selection, no timing -- "
                         "scores top-2 %.2f..%.2f on %d phases and is refused too, so the "
                         "line is not ranking the rungs"
                         % (min(tops), max(tops), len(cells)))
    return out


def judge(rung: str, cells: list, line=None, reference_top2=None) -> dict:
    """Read the rung's answer off its own four cells -- never hand-written.

    Adoptable requires BOTH: the gate clears on every phase (no calendar luck) and
    the tightest phase still sits further from the line than the phases spread among
    themselves (`margin > spread`). A rung that clears four times but whose spread is
    wider than its margin is one bad calendar away from failing, and is reported as
    brittle instead of passing.
    """
    line = G.TOP2_SHARE_MAX if line is None else float(line)
    tops = [c["top2_share"] for c in cells if c.get("top2_share") is not None]
    admits = [c for c in cells if c.get("verdict") == "ADMIT"]
    refused = [c["phase_start"] for c in cells if c.get("verdict") != "ADMIT"]
    if not cells:
        return {"rung": rung, "verdict": "NO_CELLS", "detail": "no phase was priced"}
    if not tops:
        return {"rung": rung, "verdict": "NO_READING",
                "detail": "not one phase produced a top-2 share"}
    spread = max(tops) - min(tops)
    margin = line - max(tops)
    out = {
        "rung": rung,
        "phases": len(cells),
        "pass_phases": len(admits),
        "refused_phases": refused,
        "top2_min": round(min(tops), 4),
        "top2_max": round(max(tops), 4),
        "spread": round(spread, 4),
        "margin_to_line": round(margin, 4),
        "line": line,
    }
    # r1615: the rung's worst phase against the shape reference's median phase. Below
    # 1.0 the rung is less concentrated than the same universe held equally, which is
    # the only reading of Y4 that survives the reference arm refusing the line itself.
    if reference_top2:
        out["top2_vs_reference"] = round(max(tops) / float(reference_top2), 4)
    if len(admits) != len(cells):
        out["verdict"] = "PHASE_DEPENDENT"
        out["detail"] = ("%d of %d phases clear the line; %s refused"
                         % (len(admits), len(cells), ",".join(refused)))
        return out
    if margin > spread:
        out["verdict"] = "ADOPTABLE"
        out["detail"] = ("all %d phases clear, and the tightest sits %.4f from the "
                         "line against a phase spread of %.4f" % (len(cells), margin, spread))
    else:
        out["verdict"] = "BRITTLE"
        out["detail"] = ("all %d phases clear, but the phase spread %.4f is not "
                         "narrower than the margin %.4f -- one other calendar could "
                         "refuse it" % (len(cells), spread, margin))
    return out


def decide(judgements: list, reference=None) -> dict:
    """The face's single answer: which rung, if any, survives the path test.

    `reference` is the equal-weight shape arm (r1615). It can never admit a rung; it
    only decides whether the sentence "no rung survives" is a ranking or a ruler
    problem, and says so on the answer itself so no reader has to cross-reference.
    """
    ok = [j for j in judgements if j.get("verdict") == "ADOPTABLE"]
    brittle = [j for j in judgements if j.get("verdict") == "BRITTLE"]
    if ok:
        best = max(ok, key=lambda j: (j["margin_to_line"], j["rung"]))
        return {"answer": "RUNG_SURVIVES_PATH_TEST", "rung": best["rung"],
                "detail": best["detail"]}
    if brittle:
        return {"answer": "ONLY_BRITTLE_RUNGS",
                "rungs": [j["rung"] for j in brittle],
                "detail": ("no rung clears every phase with more margin than phase "
                           "spread; %s clear all phases but sit inside their own noise"
                           % ",".join(j["rung"] for j in brittle))}
    ans = {"answer": "NO_RUNG_SURVIVES",
           "detail": "every rung is refused on at least one phase"}
    if reference and reference.get("verdict") == "REFERENCE_ALSO_REFUSED":
        ans["gate_comparability"] = "LINE_REFUSES_THE_MOST_DIVERSIFIED_SHAPE"
        ans["reference_top2_median"] = reference.get("top2_median")
        ans["reference_pass_phases"] = reference.get("pass_phases")
        ans["detail"] = (
            "every rung is refused on at least one phase, and so is the same universe "
            "held equally (top-2 %.2f on %s of %s phases) -- the line is not ranking "
            "these books, it is refusing the shape"
            % (reference.get("top2_median") or 0.0,
               reference.get("pass_phases"), reference.get("phases")))
    return ans


def run(rungs=None) -> dict:
    t0 = time.time()
    rungs = rungs or L.RUNGS
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    starts = B.phase_starts(close.index)
    print("phases: %s" % ", ".join(str(pd.Timestamp(d).date()) for d in starts), flush=True)
    # r1615: the same basket held equally, priced on the same four phases first, so the
    # rung verdicts are read against a book that made no decisions.
    ref_cells = reference_cells(close[cols], cols, starts)
    ref = {"cells": ref_cells, "judgement": reference_verdict(ref_cells),
           "question": ("what does the frozen Y4 line read on the same universe held "
                        "equally -- no selection, no timing, no vol target"),
           "note": ("this arm is the shape reference, not a candidate: a rung is never "
                    "admitted by beating it, and a line that refuses it cannot rank "
                    "rungs of the same shape")}
    print("REFERENCE %s | %s" % (ref["judgement"]["verdict"], ref["judgement"]["detail"]),
          flush=True)
    ref_top2 = ref["judgement"].get("top2_median")
    books = []
    for label, vt in rungs:
        cells = []
        for start in starts:
            c = cell(close[cols], openp[cols], amt[cols], sc, label, vt, start)
            cells.append(c)
            print("%-5s %s top2=%s verdict=%s cagr=%s"
                  % (label, c["phase_start"], c["top2_share"], c["verdict"],
                     c["cagr_pct"]), flush=True)
        books.append({"rung": label, "vol_target": vt, "cells": cells,
                      "judgement": judge(label, cells, reference_top2=ref_top2)})
        print("  -> %s: %s" % (label, books[-1]["judgement"]["detail"]), flush=True)
    out = {
        "face": "etf_book_vt_phases",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(close.index[-1].date()),
        "cell": "N5_R20_10bp",
        "question": ("r1613 disclosed which vol-target rungs clear the frozen calendar "
                     "gate on one decision grid; does any of them clear on every phase "
                     "of the calendar, with more margin than its own phase spread -- and "
                     "can that gate pass this shape at all (r1615 reference arm)"),
        "gate_rules": {
            "source": "scripts/candidate_year_gate.py (imported, not copied)",
            "top2_share_max": G.TOP2_SHARE_MAX,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "positive_years_share_min": G.POSITIVE_YEARS_SHARE,
        },
        "phases": [str(pd.Timestamp(d).date()) for d in starts],
        "phase_source": ("scripts/etf_book_buffer_adoption.py::phase_starts "
                         "(one implementation, two readers)"),
        "data": {"bars": int(len(close)), "first": str(close.index[0].date()),
                 "last": str(close.index[-1].date()),
                 "flips_repaired": int(n_flip),
                 "bond_free_universe": len(cols), "cell": dict(L.CELL)},
        "books": books,
        "reference": ref,
        "answer": decide([b["judgement"] for b in books], reference=ref["judgement"]),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("ANSWER %s %s" % (out["answer"]["answer"], out["answer"]["detail"]), flush=True)
    print("elapsed %.1fs" % out["elapsed_sec"], flush=True)
    return out


def load():
    if not os.path.exists(OUT):
        return None
    with io.open(OUT, encoding="utf-8") as f:
        return json.load(f)


def refresh() -> int:
    """The producer half of check(), keyed on the only clock that moves.

    A check leg that re-derives from the receipt is green on a three-day-old receipt
    (r1594), so this face needs a writer of its own or it decays exactly like the ladder
    did. The clock is the price panel's newest bar, never the wall clock: when the panel
    has not moved, a repricing would reproduce the same 28 cells and cost 89s to say so.
    """
    d = load()
    last = L.panel_last_bar()
    if d and last and d.get("evidence_cutoff") == last:
        print("NO-OP panel has not moved past %s since the face was priced (pid %d)"
              % (last, os.getpid()))
        return 0
    if not last:
        print("MISSING panel last bar -- cannot tell whether a repricing is due")
        return 2
    print("REPRICING: panel %s -> %s" % ((d or {}).get("evidence_cutoff"), last))
    run()
    return 0


def check() -> int:
    """Re-derive every judgement and the answer from the published cells."""
    d = load()
    if d is None:
        print("MISSING %s" % OUT)
        return 1
    errs = []
    books = d.get("books") or []
    if not books:
        errs.append("face publishes no books")
    phases = d.get("phases") or []
    # r1615: the reference arm is part of the verdict, so check() must re-derive it too.
    ref = d.get("reference") or {}
    ref_cells = ref.get("cells") or []
    ref_judgement = ref.get("judgement") or {}
    if not ref_cells:
        errs.append("face publishes no reference arm -- the rung verdicts cannot be "
                    "read as a ranking without it")
    elif {c.get("phase_start") for c in ref_cells} != set(phases):
        errs.append("reference priced a different set of phases than the rungs")
    for c in ref_cells:
        t = c.get("top2_share")
        if t is not None and (c.get("verdict") == "ADMIT") != (t <= G.TOP2_SHARE_MAX):
            errs.append("reference/%s verdict disagrees with its own top2 (%.4f vs %.2f)"
                        % (c.get("phase_start"), t, G.TOP2_SHARE_MAX))
    again_ref = reference_verdict(ref_cells)
    if again_ref.get("verdict") != ref_judgement.get("verdict"):
        errs.append("reference verdict re-derives: %s != %s"
                    % (again_ref.get("verdict"), ref_judgement.get("verdict")))
    if again_ref.get("top2_median") != ref_judgement.get("top2_median"):
        errs.append("reference top2_median re-derives: %s != %s"
                    % (again_ref.get("top2_median"), ref_judgement.get("top2_median")))
    ref_median = again_ref.get("top2_median")
    for b in books:
        cells = b.get("cells") or []
        if len(cells) != len(phases):
            errs.append("%s has %d cells for %d phases"
                        % (b["rung"], len(cells), len(phases)))
        if len({c["phase_start"] for c in cells}) != len(cells):
            errs.append("%s priced one phase twice" % b["rung"])
        for c in cells:
            # the verdict must be the gate's own, recomputed from the printed numbers
            yrs_at = c.get("top2_share")
            if yrs_at is not None and (c["verdict"] == "ADMIT") != (
                    yrs_at <= G.TOP2_SHARE_MAX):
                errs.append("%s/%s verdict disagrees with its own top2 (%.4f vs %.2f)"
                            % (b["rung"], c["phase_start"], yrs_at, G.TOP2_SHARE_MAX))
        again = judge(b["rung"], cells, reference_top2=ref_median)
        if again["verdict"] != b["judgement"]["verdict"]:
            errs.append("%s judgement re-derives: %s != %s"
                        % (b["rung"], again["verdict"], b["judgement"]["verdict"]))
        if again.get("pass_phases") != b["judgement"].get("pass_phases"):
            errs.append("%s pass_phases re-derives" % b["rung"])
        if again.get("top2_vs_reference") != b["judgement"].get("top2_vs_reference"):
            errs.append("%s top2_vs_reference re-derives: %s != %s"
                        % (b["rung"], again.get("top2_vs_reference"),
                           b["judgement"].get("top2_vs_reference")))
    answer = decide([b["judgement"] for b in books], reference=ref_judgement)
    if answer["answer"] != d["answer"]["answer"]:
        errs.append("answer re-derives: %s != %s" % (answer["answer"], d["answer"]["answer"]))
    if answer.get("gate_comparability") != d["answer"].get("gate_comparability"):
        errs.append("gate_comparability re-derives: %s != %s"
                    % (answer.get("gate_comparability"), d["answer"].get("gate_comparability")))
    ok = [b["rung"] for b in books if b["judgement"]["verdict"] == "ADOPTABLE"]
    if bool(ok) != (d["answer"]["answer"] == "RUNG_SURVIVES_PATH_TEST"):
        errs.append("answer word disagrees with the adoptable list")
    if errs:
        print("CHECK_FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("CHECK_OK books=%d answer=%s" % (len(books), d["answer"]["answer"]))
    return 0


def _c(rung, top2, verdict="ADMIT", phase="2026-01-01"):
    return {"phase_start": phase, "top2_share": top2, "verdict": verdict}


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    line = 0.70
    # 1. all four phases clear with a margin wider than the spread -> adoptable
    j = judge("vtA", [_c("vtA", 0.60, phase="p1"), _c("vtA", 0.62, phase="p2"),
                      _c("vtA", 0.61, phase="p3"), _c("vtA", 0.63, phase="p4")], line=line)
    leg("four clear phases with a narrow spread are adoptable",
        j["verdict"] == "ADOPTABLE" and j["pass_phases"] == 4
        and abs(j["spread"] - 0.03) < 1e-9, j["verdict"] + " spread=%.4f" % j["spread"])
    # 2. same four passes, but the spread is wider than the margin -> brittle, not passing
    j = judge("vtB", [_c("vtB", 0.64, phase="p1"), _c("vtB", 0.69, phase="p2"),
                      _c("vtB", 0.65, phase="p3"), _c("vtB", 0.69, phase="p4")], line=line)
    leg("a rung that clears four times inside its own noise is brittle, not adoptable",
        j["verdict"] == "BRITTLE" and j["margin_to_line"] < j["spread"],
        "%s margin=%.4f spread=%.4f" % (j["verdict"], j["margin_to_line"], j["spread"]))
    # 3. one refused phase makes the whole rung phase-dependent and names that phase
    j = judge("vtC", [_c("vtC", 0.60, phase="p1"), _c("vtC", 0.71, phase="p2", verdict="CONDITIONAL"),
                      _c("vtC", 0.58, phase="p3"), _c("vtC", 0.59, phase="p4")], line=line)
    leg("one refused phase is enough to refuse the rung, and the phase is named",
        j["verdict"] == "PHASE_DEPENDENT" and j["refused_phases"] == ["p2"],
        j["verdict"] + " refused=" + ",".join(j["refused_phases"]))
    # 4. the answer prefers a surviving rung over a brittle one, and says so honestly
    d = decide([{"rung": "x", "verdict": "BRITTLE", "detail": ""},
                {"rung": "y", "verdict": "ADOPTABLE", "margin_to_line": 0.05, "detail": ""}])
    leg("the answer names the surviving rung, not the brittle one",
        d["answer"] == "RUNG_SURVIVES_PATH_TEST" and d["rung"] == "y", d["answer"])
    d = decide([{"rung": "x", "verdict": "BRITTLE", "detail": ""}])
    leg("brittle-only is reported as such, never as a pass",
        d["answer"] == "ONLY_BRITTLE_RUNGS" and d["rungs"] == ["x"], d["answer"])
    d = decide([{"rung": "x", "verdict": "PHASE_DEPENDENT", "detail": ""}])
    leg("zero survivors is reported as zero",
        d["answer"] == "NO_RUNG_SURVIVES", d["answer"])
    # 5. a monitor-less rung is not silently adoptable
    j = judge("vtD", [{"phase_start": "p1", "top2_share": None, "verdict": "UNKNOWN"}], line=line)
    leg("a rung with no reading is NO_READING, never a pass", j["verdict"] == "NO_READING",
        j["verdict"])
    # 6. the gate line used by judge() is the frozen one by default
    j = judge("vtE", [_c("vtE", 0.65, phase="p1")])
    leg("judge() defaults to the frozen gate line",
        abs(j["line"] - G.TOP2_SHARE_MAX) < 1e-12, "%.4f" % j["line"])
    # 7. phases come from the shared helper, and it really moves the calendar
    idx = pd.bdate_range("2020-01-01", periods=200)
    starts = B.phase_starts(idx)
    leg("phase_starts yields distinct phases (the mechanism moved)",
        len(starts) == B.N_PHASES and len(set(starts)) == len(starts),
        str([str(pd.Timestamp(s).date()) for s in starts]))
    # 8. r1615 reference arm: the line refuses the book that makes no decisions
    _ref = [_c("ref", 1.47, verdict="REFUSE", phase="p1"),
            _c("ref", 1.49, verdict="REFUSE", phase="p2"),
            _c("ref", 1.50, verdict="REFUSE", phase="p3"),
            _c("ref", 1.47, verdict="REFUSE", phase="p4")]
    rv = reference_verdict(_ref)
    leg("an equal-weight reference that the line refuses is named as such",
        rv["verdict"] == "REFERENCE_ALSO_REFUSED" and rv["pass_phases"] == 0
        and abs(rv["top2_median"] - 1.48) < 1e-9,
        "%s median=%s" % (rv["verdict"], rv.get("top2_median")))
    rv_ok = reference_verdict([_c("ref", 0.60, phase="p1"), _c("ref", 0.62, phase="p2")])
    leg("a reference that clears the line is NOT reported as a ruler problem",
        rv_ok["verdict"] == "REFERENCE_CLEARS", rv_ok["verdict"])
    leg("a reference with no reading never claims a verdict",
        reference_verdict([])["verdict"] == "NO_READING",
        reference_verdict([])["verdict"])
    # 9. the answer keeps the refusal and adds the cause; it never turns into a pass
    d = decide([{"rung": "x", "verdict": "PHASE_DEPENDENT", "detail": ""}],
               reference=rv)
    leg("no survivor + refused reference keeps NO_RUNG_SURVIVES and names the cause",
        d["answer"] == "NO_RUNG_SURVIVES"
        and d.get("gate_comparability") == "LINE_REFUSES_THE_MOST_DIVERSIFIED_SHAPE",
        d["answer"] + " / " + str(d.get("gate_comparability")))
    d2 = decide([{"rung": "x", "verdict": "PHASE_DEPENDENT", "detail": ""}],
                reference=rv_ok)
    leg("a reference that clears the line must NOT print a ruler complaint",
        d2["answer"] == "NO_RUNG_SURVIVES" and "gate_comparability" not in d2,
        str(d2.get("gate_comparability")))
    # 10. the ratio is arithmetic, and it is bounded by the reference it divides by
    j = judge("vtF", [_c("vtF", 0.84, phase="p1"), _c("vtF", 0.80, phase="p2"),
                      _c("vtF", 0.82, phase="p3"), _c("vtF", 0.81, phase="p4")],
              line=line, reference_top2=rv["top2_median"])
    leg("top2_vs_reference divides the worst phase by the reference median",
        abs(j["top2_vs_reference"] - 0.5676) < 1e-4 and j["top2_vs_reference"] < 1.0,
        "%.4f" % j["top2_vs_reference"])
    # 11. load-bearing: change only the reference numbers, the conclusion must move
    rv_low = reference_verdict([_c("ref", 0.55, phase="p1"), _c("ref", 0.57, phase="p2")])
    d3 = decide([{"rung": "x", "verdict": "PHASE_DEPENDENT", "detail": ""}],
                reference=rv_low)
    leg("the ruler complaint is data-driven, not a constant of the code",
        "gate_comparability" not in d3, str(d3.get("gate_comparability")))

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", n, (" | " + detail) if detail else ""))
    print("SELFTEST %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "refresh", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        run()
        return 0
    if args.cmd == "refresh":
        return refresh()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
