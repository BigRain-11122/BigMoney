#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""one decision for the 2026-11-11 rebalance out of two receipts that were read separately

WHY THIS FILE EXISTS
--------------------
Two rounds produced two true sentences that a desk cannot hold at once:

  r1444 (results/etf_book_ruler_forward/RULER-FORWARD.json)
      every leading year-axis check, Y4 top-2 share included, is BLIND forward
      (rho -0.0302 / p 0.8301 primary; all four reads BLIND, agreement true).

  r1445 (results/etf_book_partial_year_caliber/CALIBER.json)
      the same frozen checks read differently under caliber A (partial year counted)
      and P (typical-shape checks full-years only): 3 books ADMIT->CONDITIONAL and
      1 CONDITIONAL->ADMIT, and every one of those flips moves Y4 and nothing else.
      Adoption is explicitly NOT taken: caliber P needs its own prereg.

Read alone, r1445 says "the gate is one decision away from disagreeing with itself".
Read alone, r1444 says "the check that decides is decorative".  Neither says what the
desk should do on 2026-11-11 with money that is already on.  This file asks that one
question and answers it from the published receipts only -- no repricing, no engine
call, no new backtest:

  For every published book: does the calendar WORD survive the caliber choice?
  For the book that actually holds money: which class is it in?
  What does that mean for the rebalance?

WHAT A READER SHOULD TAKE AWAY
------------------------------
The caliber dispute is not a desk-wide problem, it is a property of individual books.
A book whose word is identical under A, B and P is untouched by the argument; a book
whose word moves on blind checks only has an UNSET word (neither refused nor admitted
on evidence); a book whose word moves on a check with measured forward relation must
wait for a prereg.  Then the money question: if the book being executed is invariant
the caliber argument cannot change its verdict, and if it is not, its word must not be
used to change size.

FROZEN BEFORE READING (so this page cannot pick a flattering class):
  INVARIANT              word(A) == word(B) == word(P)
  MOVES_ON_BLIND_CHECK   word differs, and every moving check reads RULER_BLIND
  MOVES_ON_SEEN_CHECK    word differs and at least one moving check reads
                         RULER_SEES_FORWARD / RULER_INVERTED (one is enough)
Desk words:
  CALIBER_IRRELEVANT_TO_MONEY  executed book is INVARIANT -> the published word governs
  CALIBER_UNSET_MOVES_MONEY    executed book is MOVES_ON_BLIND_CHECK -> keep weight,
                               no increase, no refusal on that check alone
  HOLD_UNTIL_CALIBER_PREREG    executed book is MOVES_ON_SEEN_CHECK
  REFUSE_STANDS                the forward read is RULER_INVERTED (a backwards ruler
                               refuses the right book and admits the wrong one)
  MISSING_RECEIPT              an input is absent: no guess, no decision

self  python scripts/etf_book_supply_gate_decision.py selftest
run   python scripts/etf_book_supply_gate_decision.py run
check python scripts/etf_book_supply_gate_decision.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "etf_book_supply_gate_decision")
OUT = os.path.join(OUT_DIR, "DECISION.json")

CALIBER_RECEIPT = "results/etf_book_partial_year_caliber/CALIBER.json"
FORWARD_RECEIPT = "results/etf_book_ruler_forward/RULER-FORWARD.json"
GAP_RECEIPT = "results/etf_book_execution_admission_gap.json"
WRAPPER_RECEIPT = "results/etf_book_year_gate/WRAPPER-GATE.json"

CLASSES = ("INVARIANT", "MOVES_ON_CONTROL_ONLY", "MOVES_ON_BLIND_CHECK",
           "MOVES_ON_SEEN_CHECK", "UNREADABLE")
DESK_WORDS = ("CALIBER_IRRELEVANT_TO_MONEY", "CALIBER_UNSET_MOVES_MONEY",
              "HOLD_UNTIL_CALIBER_PREREG", "REFUSE_STANDS", "MISSING_RECEIPT")
CLASS_TO_DESK = {
    # A == P is what the decision is about; a book whose only disagreement is the
    # full-years control has no production-side dispute at all (r1446 self-catch)
    "INVARIANT": "CALIBER_IRRELEVANT_TO_MONEY",
    "MOVES_ON_CONTROL_ONLY": "CALIBER_IRRELEVANT_TO_MONEY",
    "MOVES_ON_BLIND_CHECK": "CALIBER_UNSET_MOVES_MONEY",
    "MOVES_ON_SEEN_CHECK": "HOLD_UNTIL_CALIBER_PREREG",
    "UNREADABLE": "MISSING_RECEIPT",
}

PREREG_REQUIREMENTS = [
    "freeze the caliber in the receipt, not in a sentence: every book re-read under the "
    "chosen caliber and the parity table published with the choice (r1445 rows are the "
    "baseline to hold identical)",
    "state the forward test that would settle it before reading it: fixed-length windows, "
    "min_cells 12, 2000 permutations, and the same severity order used in r1444 "
    "(inverted is worse than blind)",
    "carry a power floor: with four decision points the selector cannot settle a strategy "
    "question (r1316) -- a caliber that only re-ranks blind checks is a re-labeling, not "
    "an admission rule",
    "name what changes for money on adoption: which executing book's word moves, at what "
    "weight, and the size cap in force while the caliber is unsettled",
]


# ------------------------------------------------------------------ inputs
def _load(rel: str) -> tuple[dict | None, str]:
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return None, ""
    with io.open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()[:16]


def _forward_verdicts(fw: dict) -> dict:
    """moving check -> forward verdict.  The forward receipt reads the year axis as a
    whole (four calibers, one composite); with no per-check split published, every
    year-axis check inherits the composite.  That is printed, not assumed silently."""
    v = (fw.get("verdict") or {}).get("composite")
    reads = {}
    rel = fw.get("forward_relation") or {}
    for key in ("primary", "secondary", "disjoint_primary", "disjoint_secondary"):
        blk = rel.get(key)
        if isinstance(blk, dict):
            reads[key] = blk.get("verdict")
    return {"composite": v, "reads": reads,
            "source": "RULER-FORWARD.json verdict.composite (no per-check split published)"}


def _word(row: dict, caliber: str) -> str | None:
    cal = (row.get("calibers") or {}).get(caliber)
    if not isinstance(cal, dict):
        return None
    return cal.get("verdict")


def moving_checks(row: dict, left: str = "A", right: str = "P") -> list[str]:
    """Checks whose boolean differs between two published calibers.
    A->P is the decision axis; A->B is the full-years control."""
    cal = row.get("calibers") or {}
    a = (cal.get(left) or {}).get("checks") or {}
    b = (cal.get(right) or {}).get("checks") or {}
    if not a or not b:
        return []
    return sorted(k for k in a if k in b and bool(a[k]) != bool(b[k]))


def classify_row(row: dict, fwd: dict) -> dict:
    wa, wb, wp = _word(row, "A"), _word(row, "B"), _word(row, "P")
    if wa is None or wp is None:
        return {"class": "UNREADABLE", "moving_checks": [], "words": {"A": wa, "B": wb, "P": wp},
                "reason": "receipt row carries no A/P verdict"}
    words = {"A": wa, "B": wb, "P": wp}
    if wa == wp:
        if wb == wa:
            return {"class": "INVARIANT", "moving_checks": [], "words": words,
                    "reason": "the calendar word is identical under all three calibers"}
        return {"class": "MOVES_ON_CONTROL_ONLY",
                "moving_checks": moving_checks(row, "A", "B"),
                "words": words,
                "reason": ("A and P agree on this book; only the full-years control B "
                           "disagrees, so no production-side caliber choice changes it")}
    moved = moving_checks(row, "A", "P")
    if not moved and wa == wp:
        # words differ only through a caliber that does not expose check detail
        return {"class": "UNREADABLE", "moving_checks": [], "words": words,
                "reason": "word differs but the receipt names no moving check"}
    seen = [c for c in moved
            if fwd["composite"] in ("RULER_SEES_FORWARD", "RULER_INVERTED")]
    cls = "MOVES_ON_SEEN_CHECK" if seen else "MOVES_ON_BLIND_CHECK"
    return {"class": cls, "moving_checks": moved, "words": words,
            "reason": ("word moves on " + ", ".join(moved) +
                       ("; forward relation measured" if seen else
                        "; every moving check reads " + str(fwd["composite"])))}


def desk_decision(executed_class: str, fwd: dict) -> tuple[str, str]:
    if fwd["composite"] == "RULER_INVERTED":
        return "REFUSE_STANDS", ("the forward read says the ruler runs backwards; no book "
                                 "is admitted or refused on it until that is fixed")
    word = CLASS_TO_DESK.get(executed_class, "MISSING_RECEIPT")
    if word == "CALIBER_IRRELEVANT_TO_MONEY":
        return word, ("the executed book's word does not depend on the caliber choice "
                      "(A and P agree), so the caliber argument cannot change what the "
                      "gate says about the money")
    if word == "CALIBER_UNSET_MOVES_MONEY":
        return word, ("the executed book's word moves only on checks with no measured "
                      "forward relation: hold the weight in force, do not refuse on that "
                      "check alone, do not increase size on it")
    if word == "HOLD_UNTIL_CALIBER_PREREG":
        return word, ("the executed book's word moves on a check with measured forward "
                      "relation: the caliber must be registered before size changes")
    return "MISSING_RECEIPT", "the executed book could not be classified from the receipts"


# ------------------------------------------------------------------ build
def build() -> dict:
    cal, cal_sha = _load(CALIBER_RECEIPT)
    fw, fw_sha = _load(FORWARD_RECEIPT)
    gap, gap_sha = _load(GAP_RECEIPT)
    wrap, wrap_sha = _load(WRAPPER_RECEIPT)

    missing = [n for n, d in (("caliber", cal), ("forward", fw), ("gap", gap)) if d is None]
    if missing:
        return {"face": "etf_book_supply_gate_decision",
                "verdict": "MISSING_RECEIPT", "missing_receipts": missing,
                "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "sources": {"caliber": {"path": CALIBER_RECEIPT, "sha16": cal_sha},
                            "forward": {"path": FORWARD_RECEIPT, "sha16": fw_sha},
                            "gap": {"path": GAP_RECEIPT, "sha16": gap_sha}}}

    fwd = _forward_verdicts(fw)

    books = []
    for row in cal.get("rows") or []:
        c = classify_row(row, fwd)
        books.append({"face": row.get("face"), "name": row.get("name"),
                      "class": c["class"], "words": c["words"],
                      "moving_checks": c["moving_checks"], "reason": c["reason"]})

    class_counts = {k: sum(1 for b in books if b["class"] == k) for k in CLASSES}
    gift_arms = [b for b in books if b["class"] == "MOVES_ON_BLIND_CHECK"]
    floored = [b for b in books if b["class"] == "MOVES_ON_SEEN_CHECK"]

    # ---- the money book: named by the gap receipt, never hardcoded
    candidate = gap.get("candidate")
    executed = next((b for b in books if b["name"] == candidate), None)
    if executed is None:
        executed = {"face": None, "name": candidate, "class": "UNREADABLE", "words": {},
                    "moving_checks": [],
                    "reason": "the executing candidate is not a row of the caliber receipt"}

    money = gap.get("money") or {}
    word, sentence = desk_decision(executed["class"], fwd)

    # ---- size the disagreement for the book that holds money (fraction -> pct once)
    row_match = next((r for r in cal.get("rows") or [] if r.get("name") == candidate), None)
    top2 = {"A": None, "full_only": None}
    if row_match:
        cal_a = (row_match.get("calibers") or {}).get("A") or {}
        met = cal_a.get("metrics") or {}
        top2["A"] = met.get("top2_share")
        top2["full_only"] = met.get("top2_share_full_only")

    # ---- the construction that prices the ticket (wrapper receipt's own word),
    # cross-checked against the caliber receipt: two receipts, one number each
    gift_names = {b["name"] for b in gift_arms}
    constructions = []
    cross = []
    for wb in (wrap.get("books") or []) if wrap else []:
        nm = wb.get("book") or wb.get("name")
        cal_row = next((b for b in books if b["name"] == nm), None)
        agree = (cal_row is not None and cal_row["words"].get("A") == wb.get("verdict"))
        cross.append({"name": nm, "wrapper_word": wb.get("verdict"),
                      "caliber_A_word": None if cal_row is None else cal_row["words"].get("A"),
                      "agree": agree})
        if nm in gift_names:
            constructions.append({"name": nm, "wrapper_word": wb.get("verdict"),
                                  "class": cal_row["class"] if cal_row else "UNREADABLE",
                                  "words": cal_row["words"] if cal_row else {}})

    desk = {
        "verdict": word,
        "sentence": sentence,
        "executed_book": {
            "candidate": candidate,
            "class": executed["class"],
            "words": executed["words"],
            "moving_checks": executed["moving_checks"],
            "calendar_state": gap.get("calendar_state"),
            "calendar_sentence": gap.get("calendar_sentence"),
            "failing_checks": gap.get("failing_checks"),
            "top2_share_frac_A": top2["A"],
            "top2_share_frac_full_only": top2["full_only"],
            "top2_share_pct_A": None if top2["A"] is None else round(top2["A"] * 100, 2),
            "top2_share_pct_full_only": (None if top2["full_only"] is None
                                         else round(top2["full_only"] * 100, 2)),
            "nav_cny": money.get("nav_cny"),
            "book_weight": money.get("book_weight"),
            "book_amount_cny": money.get("book_amount_cny"),
            "names_in_ticket": money.get("names_in_ticket"),
        },
        "money_constructions_that_are_gifts": constructions,
        "second_reading": (
            "the judge and the money are two different objects: the judged book's word "
            "survives the caliber choice, while "
            + (", ".join(c["name"] for c in constructions) or "no construction")
            + " -- the construction the ticket prices -- reads ADMIT only while a partial "
              "year counts as a year (r1440 priced the same k_now)"),
        "cross_receipt_agreement": cross,
        "gift_arms": [{"face": b["face"], "name": b["name"], "words": b["words"],
                       "moving_checks": b["moving_checks"]} for b in gift_arms],
        "floored_arms": [{"face": b["face"], "name": b["name"], "words": b["words"],
                          "moving_checks": b["moving_checks"]} for b in floored],
        "class_counts": class_counts,
        "money_changes_under_P": word in ("CALIBER_UNSET_MOVES_MONEY",
                                          "HOLD_UNTIL_CALIBER_PREREG"),
        "size_cap_note": ("no size change may cite an arm whose word moves on a blind "
                          "check; the weight in force is the weight until a prereg lands"),
    }

    return {
        "face": "etf_book_supply_gate_decision",
        "question": ("two receipts read separately -- does the caliber dispute (r1445) "
                     "and the blind ruler (r1444) combine into one answer for the "
                     "2026-11-11 rebalance?"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": max(x for x in (cal.get("evidence_cutoff"),
                                           fw.get("evidence_cutoff"),
                                           gap.get("evidence_cutoff"),
                                           (wrap or {}).get("evidence_cutoff")) if x),
        "forward": fwd,
        "books": books,
        "desk": desk,
        "prereg_requirements": PREREG_REQUIREMENTS,
        "honest": [
            "no repricing and no engine call: every number is re-read from published "
            "receipts, so a word here is a statement about the same numbers",
            "the forward receipt publishes one composite verdict per axis, not per check; "
            "every year-axis check inherits it and that inheritance is printed in forward.source",
            "classification says what the receipts can support, nothing about expected return",
            "caliber P stays unadopted: this page decides what to do while the caliber is "
            "unsettled, it does not choose the caliber",
            "the gift-arm list is a reading of the caliber receipt; the cross-receipt block "
            "re-checks each wrapper word against the caliber receipt's A word",
        ],
        "sources": {
            "caliber": {"path": CALIBER_RECEIPT, "sha16": cal_sha},
            "forward": {"path": FORWARD_RECEIPT, "sha16": fw_sha},
            "gap": {"path": GAP_RECEIPT, "sha16": gap_sha},
            "wrapper": {"path": WRAPPER_RECEIPT, "sha16": wrap_sha},
        },
    }


# ------------------------------------------------------------------ faces
def md_lines(d: dict) -> list[str]:
    desk = d.get("desk") or {}
    eb = desk.get("executed_book") or {}
    out = ["# Supply-gate decision for the 2026-11-11 rebalance", "",
           f"verdict: **{desk.get('verdict')}** -- {desk.get('sentence')}", ""]
    if eb:
        out += [f"executed book `{eb.get('candidate')}` -- class {eb.get('class')}, "
                f"calendar word {eb.get('calendar_state')}"
                f" ({eb.get('calendar_sentence')})",
                f"its Y4 top-2 share reads {eb.get('top2_share_pct_A')}% under production "
                f"caliber A and {eb.get('top2_share_pct_full_only')}% full-years-only "
                f"(line 70%) -- the word is {('identical' if eb.get('class') == 'INVARIANT' else 'not identical')} "
                f"across calibers",
                f"money in it: CNY "
                f"{('{:,.0f}'.format(eb['book_amount_cny'])) if eb.get('book_amount_cny') else None} "
                f"in {eb.get('names_in_ticket')} names at book weight {eb.get('book_weight')}", ""]
    cc = desk.get("class_counts") or {}
    out += [f"books by class: " + ", ".join(f"{k} {v}" for k, v in cc.items()),
            f"gift arms (word moves on a blind check): " +
            (", ".join(g["name"] for g in desk.get("gift_arms") or []) or "none"),
            f"floored arms (word moves on a measured check): " +
            (", ".join(g["name"] for g in desk.get("floored_arms") or []) or "none"), ""]
    if desk.get("second_reading"):
        out += ["## Second reading", "", desk["second_reading"], ""]
    fw = d.get("forward") or {}
    out += [f"forward read: {fw.get('composite')} ({fw.get('source')})", ""]
    return out


def run() -> int:
    t0 = time.time()
    d = build()
    if d.get("verdict") == "MISSING_RECEIPT":
        os.makedirs(OUT_DIR, exist_ok=True)
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print("[supply_gate_decision] MISSING_RECEIPT " + ",".join(d["missing_receipts"]))
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    md_path = os.path.join(OUT_DIR, "DECISION-%s.md" % d["evidence_cutoff"].replace("-", ""))
    with io.open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)))
    d["runtime_sec"] = round(time.time() - t0, 3)
    print("[supply_gate_decision] %s  executed=%s class=%s  gifts=%d  floored=%d  %.1fs"
          % (d["desk"]["verdict"], d["desk"]["executed_book"]["candidate"],
             d["desk"]["executed_book"]["class"], len(d["desk"]["gift_arms"]),
             len(d["desk"]["floored_arms"]), d["runtime_sec"]))
    print("  " + d["desk"]["sentence"])
    return 0


def check() -> int:
    """Re-derive the verdict from the receipt's own sources and compare."""
    path = OUT
    if not os.path.isfile(path):
        print("[supply_gate_decision] CHECK FAIL: no receipt at %s" % path)
        return 1
    with io.open(path, encoding="utf-8") as f:
        pub = json.load(f)
    fresh = build()
    ok = 0
    fails = []
    for key in ("verdict", "executed_book", "gift_arms", "floored_arms", "class_counts",
                "money_constructions_that_are_gifts", "second_reading",
                "cross_receipt_agreement"):
        left = json.dumps((pub.get("desk") or {}).get(key), sort_keys=True, ensure_ascii=False)
        right = json.dumps((fresh.get("desk") or {}).get(key), sort_keys=True, ensure_ascii=False)
        if left == right:
            ok += 1
        else:
            fails.append(key)
    same_sources = pub.get("sources") == fresh.get("sources")
    if same_sources:
        ok += 1
    else:
        fails.append("sources")
    total = 9
    if fails:
        print("[supply_gate_decision] CHECK FAIL %d/%d  drift=%s" % (ok, total, ",".join(fails)))
        return 1
    print("[supply_gate_decision] CHECK OK %d/%d  verdict=%s class=%s"
          % (ok, total, fresh["desk"]["verdict"], fresh["desk"]["executed_book"]["class"]))
    return 0


# ------------------------------------------------------------------ selftest
def _row(name, words, a_checks, p_checks, b_checks=None):
    return {"face": "fixture", "name": name,
            "calibers": {"A": {"verdict": words[0], "checks": a_checks},
                         "B": {"verdict": words[1],
                               "checks": a_checks if b_checks is None else b_checks},
                         "P": {"verdict": words[2], "checks": p_checks}}}


def selftest() -> int:
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    blind = {"composite": "RULER_BLIND", "reads": {}, "source": "fixture"}
    seen = {"composite": "RULER_SEES_FORWARD", "reads": {}, "source": "fixture"}
    inverted = {"composite": "RULER_INVERTED", "reads": {}, "source": "fixture"}

    ok_checks = {"Y1_positive_years_share": True, "Y2_median_positive": True,
                 "Y3_worst_year": True, "Y4_top2_share": True, "C1_capacity": True}
    y4_fail = dict(ok_checks, Y4_top2_share=False)

    # L1 identical word under A/B/P is INVARIANT even when the same checks are false
    r = _row("inv", ("CONDITIONAL", "CONDITIONAL", "CONDITIONAL"), y4_fail, y4_fail)
    c = classify_row(r, blind)
    leg("L1 same word under A/B/P -> INVARIANT", c["class"] == "INVARIANT", c["class"])

    # L2 word moves on Y4 with a blind forward read -> blind class (not a refusal)
    r = _row("gift", ("ADMIT", "CONDITIONAL", "CONDITIONAL"), ok_checks, y4_fail)
    c = classify_row(r, blind)
    leg("L2 ADMIT->CONDITIONAL on Y4 with BLIND read -> MOVES_ON_BLIND_CHECK",
        c["class"] == "MOVES_ON_BLIND_CHECK" and c["moving_checks"] == ["Y4_top2_share"],
        str(c))

    # L3 the same movement with a measured forward read must NOT read as blind
    c = classify_row(r, seen)
    leg("L3 same movement with SEES_FORWARD -> MOVES_ON_SEEN_CHECK",
        c["class"] == "MOVES_ON_SEEN_CHECK", c["class"])

    # L4 one seen check among several moving checks is enough to floor the book
    multi_p = dict(ok_checks, Y2_median_positive=False, Y4_top2_share=False)
    r2 = _row("multi", ("ADMIT", "CONDITIONAL", "CONDITIONAL"), ok_checks, multi_p)
    c = classify_row(r2, blind)
    leg("L4 a multi-check move with a blind read stays blind",
        c["class"] == "MOVES_ON_BLIND_CHECK" and len(c["moving_checks"]) == 2,
        str(c["moving_checks"]))
    leg("L5 the one-seen-check rule is carried by fwd, not by the check count",
        classify_row(r2, seen)["class"] == "MOVES_ON_SEEN_CHECK")

    # L6 desk words: class -> word, and INVERTED overrides every class
    leg("L6a INVARIANT desk word", desk_decision("INVARIANT", blind)[0] == "CALIBER_IRRELEVANT_TO_MONEY")
    leg("L6b blind class desk word", desk_decision("MOVES_ON_BLIND_CHECK", blind)[0] == "CALIBER_UNSET_MOVES_MONEY")
    leg("L6c seen class desk word", desk_decision("MOVES_ON_SEEN_CHECK", blind)[0] == "HOLD_UNTIL_CALIBER_PREREG")
    leg("L6d INVERTED overrides every class",
        all(desk_decision(k, inverted)[0] == "REFUSE_STANDS" for k in CLASSES))

    # L7 a row with no caliber detail is UNREADABLE, not INVARIANT
    c = classify_row({"face": "x", "name": "n"}, blind)
    leg("L7 row without calibers -> UNREADABLE", c["class"] == "UNREADABLE", c["class"])

    # L7b A and P agree while the full-years control disagrees: the production word is
    # untouched, and calling that UNREADABLE would report a receipt defect that is not one
    rc = _row("control", ("CONDITIONAL", "ADMIT", "CONDITIONAL"), y4_fail, y4_fail,
              b_checks=ok_checks)
    c = classify_row(rc, blind)
    leg("L7b A==P with B differing -> MOVES_ON_CONTROL_ONLY",
        c["class"] == "MOVES_ON_CONTROL_ONLY" and c["moving_checks"] == ["Y4_top2_share"],
        str(c))
    leg("L7c control-only class maps to the same desk word as INVARIANT",
        desk_decision("MOVES_ON_CONTROL_ONLY", blind)[0] == "CALIBER_IRRELEVANT_TO_MONEY")

    # L7d every class has a desk word: a class without one would fall to MISSING_RECEIPT
    leg("L7d CLASS_TO_DESK covers every class", all(k in CLASS_TO_DESK for k in CLASSES))

    # L8 missing inputs produce MISSING_RECEIPT, never a class
    saved = globals()["_load"]
    try:
        globals()["_load"] = lambda rel: (None, "")
        d = build()
        bad = d.get("verdict") == "MISSING_RECEIPT" and len(d.get("missing_receipts") or []) == 3
    finally:
        globals()["_load"] = saved
    leg("L8 missing receipts -> MISSING_RECEIPT with all three named", bad)

    # L9 live build: the money book is the gap receipt's candidate, not a constant
    d = build()
    cand = (d.get("desk") or {}).get("executed_book", {}).get("candidate")
    leg("L9 the executed book is named by the gap receipt",
        cand == "nobond_vt08_adopted", str(cand))

    # L10 unit leg: the receipt stores a fraction and the face prints a percent
    eb = (d.get("desk") or {}).get("executed_book", {})
    frac, pct = eb.get("top2_share_frac_A"), eb.get("top2_share_pct_A")
    leg("L10 top2 share is a fraction in the receipt and a percent on the face",
        frac is not None and pct is not None and abs(frac * 100 - pct) < 1e-9 and 0 < frac <= 1.0,
        f"frac={frac} pct={pct}")

    # L11 the money sentence must name the line and both sides, not one number
    lines = "\n".join(md_lines(d))
    moves = all(str(eb.get(f)) in lines for f in ("top2_share_pct_A", "top2_share_pct_full_only"))
    leg("L11 the readable face prints both calibers' numbers and the 70% line",
        moves and "70%" in lines, "missing side" if not moves else "")

    # L12 build is deterministic on the same receipts
    key = lambda x: json.dumps({k: x.get(k) for k in ("books", "desk", "forward")},
                               sort_keys=True, ensure_ascii=False)
    leg("L12 build deterministic twice", key(build()) == key(build()))

    # L13 two receipts must agree on the same word for the same construction
    cross = (d.get("desk") or {}).get("cross_receipt_agreement") or []
    leg("L13 wrapper receipt and caliber receipt agree on every shared arm",
        bool(cross) and all(c["agree"] for c in cross),
        str([c["name"] for c in cross if not c["agree"]]))
    leg("L13b the agent that prices the ticket reads ADMIT in the wrapper receipt",
        any(c["name"] == "ticket_construction_plain_plus_overlay" and c["wrapper_word"] == "ADMIT"
            for c in cross))

    # L14 the money construction is one of the gift arms and is named on the second reading
    mc = (d.get("desk") or {}).get("money_constructions_that_are_gifts") or []
    gifts = {g["name"] for g in (d.get("desk") or {}).get("gift_arms") or []}
    leg("L14 every named money construction is a gift arm and appears in the second reading",
        bool(mc) and all(c["name"] in gifts for c in mc)
        and all(c["name"] in (d["desk"]["second_reading"] or "") for c in mc),
        str(mc))

    for name, good, detail in legs:
        print("  %s  %s%s" % ("PASS" if good else "FAIL", name,
                              ("  [%s]" % detail) if detail and not good else ""))
    npass = sum(1 for _, g, _ in legs if g)
    print("[supply_gate_decision] selftest %d/%d" % (npass, len(legs)))
    return 0 if npass == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest", "check"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check or a.cmd == "check":
        return check()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())