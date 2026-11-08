"""The yearly gate must be able to say "I cannot tell" -- today it cannot.

r1418 pointed the frozen calendar gate at the desk's adopted book (bond-free ETF composite
+ 8% vol target, nobond_vt08) and got CONDITIONAL on one failing row: Y4 top-2 years =
71.08% of the annual sum, 1.08pp over the 70% line. r1419 then shifted the decision phase by
one week at a time and got 71.08% / 79.46% / 79.58% / 79.82% for the SAME book -- a 8.7pp
swing produced by nothing but where the decision grid starts. It also found an arm (vol
floor 0.5) that ADMITs on one phase and turns CONDITIONAL on another, and correctly refused
to adopt it.

The gap is in the apparatus, not in the book: `candidate_year_gate.admission_block` accepts a
`phase_spread_pp` argument and only ever PRINTS it (beside r1411's 4.74pp rule); it never
lets the spread change the verdict. So a gate that was built to adjudicate adoption will
still hand out ADMIT/CONDITIONAL from a single coin-toss phase.

This file adds the missing third word. A book is adjudicated over a PHASE SET (five weekly
starts = exactly one 20-bar rebalance block) and the result is:

  ADMIT           every phase ADMITs AND the phase spread is narrower than the distance
                  from the median top-2 to the 70% line
  REFUSE          every phase fails to ADMIT AND the spread is narrower than that distance
  UNADJUDICABLE_PHASE
                  the phases do not agree, or the spread across phases is wider than the
                  distance to the line -- the sampling noise is the size of the signal, so
                  no adoption decision may be taken from this book on this evidence

The rule is frozen in RULE below and printed into the receipt. The lines themselves
(TOP2_SHARE_MAX, POSITIVE_YEARS_SHARE, WORST_YEAR_FLOOR_PP, CAPACITY_FLOOR_CNY) are
imported from candidate_year_gate; nothing is retyped. Phase-start and pricing machinery is
reused from r1419's etf_book_scale_floor (its nobond universe + its arm wrapper), so the
numbers are the same numbers, only read as a set.

Usage:
    python scripts/candidate_year_gate_phases.py run
    python scripts/candidate_year_gate_phases.py selftest
"""
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

# etf_book_year_caliber imports THIS module for its own phase set, so the caliber
# arithmetic is imported lazily inside the functions that use it -- a module-level
# import here is a cycle (caliber -> phases -> caliber) and dies on PHASE_STARTS.
def _caliber_module():
    import etf_book_year_caliber as Kmod
    return Kmod

OUT = os.path.join(ROOT, "results", "etf_book_phase_gate.json")
CALIBER_RECEIPT = os.path.join(ROOT, "results", "etf_book_year_caliber.json")

# five weekly starts span one 20-bar rebalance block (0, 5, 10, 15, 20 bars)
PHASE_STARTS = ("2020-01-01", "2020-01-08", "2020-01-15", "2020-01-22", "2020-01-29")

# arms are (label, vol_target or None, vol_floor)
ARMS = (
    ("nobond_vt08_adopted", 0.08, 0.0),
    ("nobond_base", None, 0.0),
    ("nobond_vt08_floor_050", 0.08, 0.5),
)

RULE = {
    "phase_set": list(PHASE_STARTS),
    "admit_word": "ADMIT",
    "line_top2_share": G.TOP2_SHARE_MAX,
    "aggregate": (
        "let v = set of per-phase verdicts, m = median per-phase top-2 share, "
        "spread = max-min of per-phase top-2 share, margin = |m - line|. "
        "If len(v) == 1 and spread <= margin -> v[0]. "
        "Else -> UNADJUDICABLE_PHASE."
    ),
    "reason_for_the_third_word": (
        "a gate that adjudicates adoption must also be allowed to report that the "
        "sampling noise it induces is wider than the distance to its own line"
    ),
    "frozen_before_read": True,
}


# --------------------------------------------------------------- trusted rulers
# r1426 read four year-concentration calibers on the same 20 cells and showed that
# net_top2_share -- the number Y4 actually uses -- cannot adjudicate three of its own
# four arms (its phase spread is wider than its distance to the line).  It left two
# calibers that CAN judge themselves.  So the question this file could not answer
# before: when a book is refused, is the refusal about the book or about the ruler?
TRUSTED_CALIBERS_RULE = (
    "a caliber may carry a re-adjudication only if the published r1426 face marks it "
    "trusted (V and S both true); the caliber VALUES are then re-derived here from the "
    "phase year tables by etf_book_year_caliber.calibers (imported, never retyped) and "
    "each caliber is adjudicated by etf_book_year_caliber.adjudicate_caliber, so the "
    "phase spread test is the same test, applied to this book's own phases")
SURVIVAL_WORDS = {
    "REFUSAL_SURVIVES_TRUSTED_RULER": "at least one self-adjudicable caliber also fails",
    "REFUSAL_WAS_RULER_ARTIFACT": "every self-adjudicable caliber passes",
    "PARTIAL_TRUSTED_READ": "some trusted calibers could not be read on these phases",
    "UNCERTIFIED": "no trusted caliber is on record -- refuses to guess",
}


def trusted_calibers(path=CALIBER_RECEIPT):
    """The caliber names the r1426 receipt marks trusted.  Empty list = fail-closed."""
    try:
        with open(path, encoding="utf-8") as f:
            face = json.load(f)
        return [c["caliber"] for c in face["decision"]["calibers"] if c.get("trusted")]
    except Exception:
        return []


def survival_verdict(states: dict, trusted: list) -> dict:
    """Pure: which trusted rulers, if any, also refuse this book."""
    out = {"trusted": list(trusted), "states": dict(states),
           "fail": [], "pass": [], "unreadable": []}
    if not trusted:
        out.update(word="UNCERTIFIED", reason=SURVIVAL_WORDS["UNCERTIFIED"])
        return out
    for c in trusted:
        st = states.get(c)
        if st == "FAIL":
            out["fail"].append(c)
        elif st == "PASS":
            out["pass"].append(c)
        else:
            out["unreadable"].append(c)
    if out["fail"]:
        out.update(word="REFUSAL_SURVIVES_TRUSTED_RULER",
                   reason="%s also fails: %s"
                          % ("/".join(out["fail"]), SURVIVAL_WORDS["REFUSAL_SURVIVES_TRUSTED_RULER"]))
    elif out["unreadable"]:
        out.update(word="PARTIAL_TRUSTED_READ",
                   reason="unreadable on these phases: %s" % "/".join(out["unreadable"]))
    else:
        out.update(word="REFUSAL_WAS_RULER_ARTIFACT",
                   reason=SURVIVAL_WORDS["REFUSAL_WAS_RULER_ARTIFACT"])
    return out


def arm(close, openp, amt, sc, vol_target, vol_floor, start):
    """One repricing through the published engine; no arithmetic of our own."""
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, 20, 5, 0.0010,
                                      vol_target=vol_target, vol_floor=vol_floor,
                                      start=start)
    return ser, turn


def adjudicate(rows, line=None):
    """rows: [{'start','verdict','top2_share'}] -> the three-word state + the evidence."""
    line = G.TOP2_SHARE_MAX if line is None else line
    verdicts = [r["verdict"] for r in rows]
    top2 = [r["top2_share"] for r in rows if r.get("top2_share") is not None]
    out = {"phases": len(rows), "verdicts": verdicts,
           "distinct_verdicts": sorted(set(verdicts))}
    if not top2:
        out.update(state="UNADJUDICABLE_PHASE", reason="no phase published a top-2 share",
                   median_top2_share=None, spread_pp=None, margin_pp=None)
        return out
    med = float(statistics.median(top2))
    spread = float(max(top2) - min(top2))
    margin = abs(med - line)
    out.update(median_top2_share=round(med, 4), spread_pp=round(spread * 100, 4),
               margin_pp=round(margin * 100, 4),
               worst_top2_share=round(float(max(top2)), 4),
               best_top2_share=round(float(min(top2)), 4),
               phases_above_line=sum(1 for v in top2 if v > line))
    if len(set(verdicts)) > 1:
        out.update(state="UNADJUDICABLE_PHASE",
                   reason="phases disagree on the verdict: %s"
                          % ", ".join(sorted(set(verdicts))))
        return out
    if spread > margin:
        out.update(state="UNADJUDICABLE_PHASE",
                   reason=("phase spread %.2fpp is wider than the %.2fpp distance from the "
                           "median top-2 to the %.0f%% line"
                           % (spread * 100, margin * 100, line * 100)))
        return out
    out.update(state=verdicts[0],
               reason=("all %d phases read %s and the spread %.2fpp is inside the %.2fpp "
                       "distance to the line"
                       % (len(verdicts), verdicts[0], spread * 100, margin * 100)))
    return out


def run():
    t0 = time.time()
    K = _caliber_module()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    cap = S.published_capacity()
    trusted = trusted_calibers()
    books = []
    for label, vt, floor in ARMS:
        rows = []
        cells = []
        for start in PHASE_STARTS:
            ser, turn = arm(close, openp, amt, sc, vt, floor, start)
            yrs = Y.yearly_returns(ser)
            st = A.stats2(ser, "p")
            blk = G.admission_block(yrs, cap, None, st.get("cagr"))
            yrows = list(yrs.values())
            rows.append({
                "start": start,
                "verdict": blk["verdict"],
                "top2_share": blk["year_metrics"]["top2_share"],
                "calibers": K.calibers(yrows),
                "positive_years_share": blk["year_metrics"].get("positive_years"),
                "worst_year_pp": blk["year_metrics"].get("worst"),
                "cagr_pct": blk["cagr_pct"],
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "maxdd": None if st.get("maxdd") is None else round(float(st["maxdd"]), 4),
                "turnover": round(turn, 3),
                "failing_checks": [k for k, v in blk["checks"].items() if v is False],
            })
            cells.append({"start": start, "calibers": rows[-1]["calibers"],
                          "years": len(yrs)})
            print("  %-24s %s -> %-12s top2 %.4f cagr %7.3f sharpe %.3f"
                  % (label, start, blk["verdict"],
                     blk["year_metrics"]["top2_share"] or 0.0,
                     blk["cagr_pct"] or 0.0, st.get("sharpe") or 0.0), flush=True)
        agg = adjudicate(rows)
        # every caliber Y4's control included, so the reader sees the control's own
        # untrustworthiness beside the rulers that carry the verdict
        by_cal = {c: K.adjudicate_caliber(c, cells) for c in K.CALIBERS}
        surv = survival_verdict({c: by_cal[c]["state"] for c in by_cal}, trusted)
        books.append({"book": label, "vol_target": vt, "vol_floor": floor,
                      "phase_rows": rows, "adjudication": agg,
                      "caliber_adjudication": by_cal,
                      "refusal_survival": surv,
                      "single_phase_r1418_reading": rows[0]["verdict"],
                      "single_phase_would_have_passed": rows[0]["verdict"] == "ADMIT"})
        print("%-24s -> %-20s (%s)" % (label, agg["state"], agg["reason"]), flush=True)
        print("%-24s -- trusted rulers: %-34s (%s)"
              % (label, surv["word"], "/".join("%s=%s" % (c, by_cal[c]["state"])
                                               for c in (trusted or [])) or "none on record"),
              flush=True)

    out = {
        "face": "candidate_year_gate_phases",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "question": "should the desk's yearly gate be allowed to answer 'cannot tell', and "
                    "what does it then say about the adopted book and r1419's floor arm?",
        "rule": RULE,
        "gate_lines_imported": {
            "top2_share_max": G.TOP2_SHARE_MAX,
            "positive_years_share": G.POSITIVE_YEARS_SHARE,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "capacity_floor_cny": G.CAPACITY_FLOOR_CNY,
        },
        "data": {"flips_repaired": n_flip, "universe": int(len(close.columns)),
                 "bars": int(len(close.index)),
                 "capacity_cny_1day_5pct": cap,
                 "capacity_from": "results/etf_book_year_gate/YEAR-GATE.json"},
        "cost_per_side": 0.0010, "rebal_bars": 20, "n_hold": 5,
        "books": books,
        "trusted_calibers": trusted,
        "trusted_calibers_rule": TRUSTED_CALIBERS_RULE,
        "survival_words": SURVIVAL_WORDS,
        "summary": {b["book"]: {"state": b["adjudication"]["state"],
                                "median_top2_share": b["adjudication"]["median_top2_share"],
                                "spread_pp": b["adjudication"]["spread_pp"],
                                "margin_pp": b["adjudication"]["margin_pp"],
                                "single_phase_verdict": b["single_phase_r1418_reading"],
                                "refusal_survival": b["refusal_survival"]["word"],
                                "trusted_states": {c: b["caliber_adjudication"][c]["state"]
                                                   for c in trusted}}
                    for b in books},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", OUT, flush=True)
    return out


def selftest() -> int:
    """Fixtures first: the aggregator must be able to reach all three words, and the
    degenerate phases (missing top-2) must not read as a pass."""
    errs = []

    def chk(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    def rows(spec):
        return [{"start": "p%d" % i, "verdict": v, "top2_share": t}
                for i, (v, t) in enumerate(spec)]

    # L1 unanimous and far from the line -> the verdict itself
    r1 = adjudicate(rows([("ADMIT", 0.55), ("ADMIT", 0.57), ("ADMIT", 0.54)]))
    chk(r1["state"] == "ADMIT", "L1 unanimous ADMIT far from the line -> ADMIT (%s)" % r1["state"])

    # L2 the third word must not swallow a clear verdict: r1419's own four readings
    # (71.08/79.46/79.58/79.82) are unanimous CONDITIONAL with an 8.7pp spread inside a
    # 9.5pp margin, so the gate keeps its word and merely discloses the spread
    r2 = adjudicate(rows([("CONDITIONAL", 0.7108), ("CONDITIONAL", 0.7946),
                          ("CONDITIONAL", 0.7958), ("CONDITIONAL", 0.7982)]))
    chk(r2["state"] == "CONDITIONAL" and r2["spread_pp"] > 8.0,
        "L2 unanimous CONDITIONAL with an %.1fpp spread inside a %.1fpp margin keeps the "
        "verdict (%s)" % (r2["spread_pp"], r2["margin_pp"], r2["state"]))

    # L2b same verdict, spread wider than the margin -> the noise is the signal
    r2b = adjudicate(rows([("CONDITIONAL", 0.7400), ("CONDITIONAL", 0.8400)]))
    chk(r2b["state"] == "UNADJUDICABLE_PHASE" and "spread" in r2b["reason"],
        "L2b unanimous CONDITIONAL whose spread exceeds the margin -> UNADJUDICABLE (%s)"
        % r2b["state"])

    # L3 phases disagree -> cannot tell, whatever the median says
    r3 = adjudicate(rows([("ADMIT", 0.6600), ("CONDITIONAL", 0.7458)]))
    chk(r3["state"] == "UNADJUDICABLE_PHASE" and "disagree" in r3["reason"],
        "L3 split verdicts -> UNADJUDICABLE_PHASE (%s)" % r3["state"])

    # L3b the split is not rescued by a comfortable median
    r3b = adjudicate(rows([("ADMIT", 0.50), ("REFUSE", 0.52)]))
    chk(r3b["state"] == "UNADJUDICABLE_PHASE",
        "L3b a comfortable median cannot rescue a split verdict (%s)" % r3b["state"])

    # L4 unanimous QUALITY fail whose spread crosses the line's neighbourhood
    r4 = adjudicate(rows([("REFUSE", 0.6000), ("REFUSE", 0.8100)]))
    chk(r4["state"] == "UNADJUDICABLE_PHASE",
        "L4 unanimous REFUSE whose spread exceeds the margin -> UNADJUDICABLE not REFUSE (%s)"
        % r4["state"])

    # L5 unanimous REFUSE, tight spread, far from the line -> REFUSE
    r5 = adjudicate(rows([("REFUSE", 0.95), ("REFUSE", 0.951)]))
    chk(r5["state"] == "REFUSE", "L5 tight unanimous REFUSE -> REFUSE (%s)" % r5["state"])

    # L6 a phase with no published top-2 must not be read as a pass
    r6 = adjudicate([{"start": "p0", "verdict": "ADMIT", "top2_share": 0.5},
                     {"start": "p1", "verdict": "ADMIT", "top2_share": None}])
    chk(r6["state"] == "ADMIT" and r6["median_top2_share"] == 0.5,
        "L6 a missing phase is dropped from the statistics but never invented "
        "(median %r over %d phases)" % (r6["median_top2_share"], r6["phases"]))
    r7 = adjudicate([{"start": "p0", "verdict": "ADMIT", "top2_share": None}])
    chk(r7["state"] == "UNADJUDICABLE_PHASE", "L7 no top-2 anywhere -> UNADJUDICABLE")

    # L8 live leg: phase 0 must reproduce r1418's own published yearly rows and verdict
    ref = S.published_reference()
    if ref:
        close, openp, amt, sc, _ = S.nobond_universe()
        ser, _ = arm(close, openp, amt, sc, 0.08, 0.0, PHASE_STARTS[0])
        yrs = Y.yearly_returns(ser)
        pubs = ref.get("yearly_returns_pct") or {}
        mine = {y: v["net_pct"] for y, v in yrs.items()}
        worst = max((abs(mine[y] - pubs[y]) for y in pubs if y in mine), default=None)
        blk = G.admission_block(yrs, S.published_capacity(), None,
                                A.stats2(ser, "p").get("cagr"))
        chk(worst is not None and worst < 1e-9,
            "L8 phase start 2020-01-01 reproduces every published yearly row (max|d| %r)"
            % worst)
        chk(blk["verdict"] == ref.get("verdict"),
            "L8b phase start 2020-01-01 reproduces r1418's verdict (%s vs %s)"
            % (blk["verdict"], ref.get("verdict")))
    else:
        chk(False, "L8 skipped: no published r1418 face")

    # L10 the survival word is decided by the trusted rulers, not by Y4's control
    s10 = survival_verdict({"net_top2_share": "FAIL", "years_for_half": "FAIL",
                            "effective_years": "PASS"},
                           ["years_for_half", "effective_years"])
    chk(s10["word"] == "REFUSAL_SURVIVES_TRUSTED_RULER" and s10["fail"] == ["years_for_half"],
        "L10 a failing trusted caliber survives the refusal (%s: %s)"
        % (s10["word"], ",".join(s10["fail"])))

    # L10b the control alone can never carry it: the same states, only untrusted names
    s10b = survival_verdict({"net_top2_share": "FAIL", "effective_years": "PASS"},
                            ["effective_years"])
    chk(s10b["word"] == "REFUSAL_WAS_RULER_ARTIFACT",
        "L10b a FAIL that no trusted caliber repeats reads as artifact, even though the "
        "control fails (%s)" % s10b["word"])

    # L11 fail-closed: no trusted caliber on record is UNCERTIFIED, never a pass
    s11 = survival_verdict({"net_top2_share": "FAIL"}, [])
    chk(s11["word"] == "UNCERTIFIED",
        "L11 no trusted caliber on record -> UNCERTIFIED (%s)" % s11["word"])

    # L12 unreadable is not a pass and not a fail
    s12 = survival_verdict({"years_for_half": "UNADJUDICABLE_CALIBER"}, ["years_for_half"])
    chk(s12["word"] == "PARTIAL_TRUSTED_READ",
        "L12 a trusted caliber that cannot be read on these phases -> PARTIAL (%s)"
        % s12["word"])
    s12b = survival_verdict({"years_for_half": "FAIL",
                             "effective_years": "UNADJUDICABLE_CALIBER"},
                            ["years_for_half", "effective_years"])
    chk(s12b["word"] == "REFUSAL_SURVIVES_TRUSTED_RULER",
        "L12b one unreadable does not bury a trusted fail (%s)" % s12b["word"])

    # L13 the published face must carry exactly the four calibers, derived from its own
    # phases -- an empty/renamed block would leave the viability question unanswerable
    if os.path.exists(OUT):
        K = _caliber_module()
        with open(OUT, encoding="utf-8") as f:
            face = json.load(f)
        cells_ok = all(set(K.CALIBERS) <= set(r.get("calibers") or {})
                       for b in face.get("books", []) for r in b.get("phase_rows", []))
        chk(cells_ok, "L13 every published phase row carries all %d calibers (%r)"
            % (len(K.CALIBERS), cells_ok))
        chk(face.get("trusted_calibers") is not None,
            "L13b the face declares its trusted set (%r)" % (face.get("trusted_calibers"),))
    else:
        chk(False, "L13 skipped: no published phase face")

    # L9 the rule is declared before any number and pinned to the imported line
    chk(RULE["line_top2_share"] == G.TOP2_SHARE_MAX and RULE["frozen_before_read"] is True,
        "L9 the frozen rule quotes the imported line (%.2f)" % RULE["line_top2_share"])
    chk(len(PHASE_STARTS) == 5 and PHASE_STARTS[-1] > PHASE_STARTS[0],
        "L9b the phase set is five weekly starts")

    tot = 21 if ref else 20
    print("selftest %d/%d" % (tot - len(errs), tot), flush=True)
    return 0 if not errs else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))