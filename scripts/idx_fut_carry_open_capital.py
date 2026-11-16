#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what it costs to open this book at all -- and what that costs the desk's four lots

WHY THIS FILE EXISTS
--------------------
r1779 adopted road A (keep the 8% vol target, treat capital as the free variable) and
published the consequence per contract: at 1,000,000 CNY the rule holds ZERO lots, and the
first executable rung is 1,125,012 CNY (IC) / 1,152,040 CNY (IM). That is a correct answer
and an unusable one. Two questions are left on the floor:

  1. HOW MUCH MONEY OPENS THIS BOOK?  A zero is not a ticket. A reader who wants to fund
     the sleeve needs one number, and the two accounts have two different numbers.
  2. WHAT HAPPENS TO THE DESK'S FOUR LOTS?  The desksheet still prints 4 lots per account
     (ticket conformance OUT_OF_RULER, 4.50x / 4.61x the budget). A face that prints a
     recommendation beside a ruler it violates, and then says nothing, leaves every reader
     to decide -- and r1779's own lesson is that "not choosing" is also a cost: every
     reader re-decides, and each decides differently.

So this file states both, once, as data: the funding line, and the withdrawal.

THE WITHDRAWAL, AND WHY THIS ONE
--------------------------------
Under the adopted hard cap at today's capital the executable size is 0 lots. Keeping the
desk's 4 lots in the ticket would make the ticket an instruction the book's own risk
standard forbids -- and the paper ledger that ran on those 4 lots would keep printing a
forward series that no 1,000,000 CNY account could have held. So the ticket is WITHDRAWN:
the executable line becomes 0 lots, and the desk's 4 lots stay printed beside it with the
reason (`adopted: false` in spirit -- an input, not an instruction).

What is NOT done: the forward paper series is not rewritten, truncated or deleted. It is an
append-only evidence line and it is the only record of what those four lots would have
paid; it is re-labelled FUNDED_BY_A_LARGER_CAPITAL, because that is what it is -- the
behaviour of a 4,500,049 CNY (IC) / 4,608,159 CNY (IM) account, not of this one.

The withdrawal is conditional, not permanent. Fund the account to the first rung and the
same rule hands the ticket back one lot; `roads_that_bring_it_back` prints each road with
the number that would make it true, so nobody has to guess what would change our mind.

HONESTY NOTES
-------------
  * no volatility, no price and no P&L is derived here. Capital, per-lot vol, admissible
    lots, first rung and the desk's lots are READ from results/idx_fut_carry_sizing_spec.json
    (which reads the ladder, which reads the paper SIZING face). `--check` re-derives every
    consequence this file prints, from those inputs, and names what it did not recompute;
  * the forward paper lots are read from the ledger and echoed verbatim -- this file never
    writes that file;
  * "cheapest to open" compares accounts on their own first rung; it is not a preference
    between IC and IM (that is the hedge question, priced elsewhere);
  * a missing upstream face is refused, never defaulted.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SPEC_PATH = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
LADDER_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capital_ladder.json")
LEDGER_PATH = os.path.join(ROOT, "results", "idx_fut_carry_paper", "LEDGER.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_open_capital.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_OPEN_CAPITAL.md")

EPS = 1e-9
ARM_USED = "hedged"

WITHDRAW = "WITHDRAW_FROM_TICKET"
KEEP = "KEEP_THE_DESK_LOTS"
DECISIONS = (WITHDRAW, KEEP)

# --------------------------------------------------------------- the decision
# One constant, one place, same law as the adoption in idx_fut_carry_sizing_spec.py:
# changing the answer means editing this block and re-running `run`, which rewrites the
# face the ticket and the CEO page read.
WITHDRAWAL = {
    "decision": WITHDRAW,
    "decided": "2026-11-17",
    "decided_in": "bm-c round 1780",
    "because": (
        "at today's capital the adopted 8% hard cap allows zero lots (r1779), so a ticket "
        "that carries the desk's four lots is an instruction the book's own risk standard "
        "forbids; leaving it there also keeps a forward paper series alive that no "
        "1,000,000 CNY account could have held -- the series would read as performance "
        "when it is a counterfactual about a larger account"),
    "scope": (
        "the executable ticket only. The forward paper series is an append-only evidence "
        "line: it is re-labelled FUNDED_BY_A_LARGER_CAPITAL, never rewritten, truncated "
        "or deleted"),
    "reversal": (
        "fund the account to the first rung and re-run: the same rule hands the ticket "
        "back one lot and this file prints it -- the withdrawal is conditional on capital, "
        "not a judgement about the sleeve"),
}


# ----------------------------------------------------------------- io helpers
def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def _fmt(v, nd=0):
    if v is None:
        return "n/a"
    return ("{:,.%df}" % nd).format(v)


# ------------------------------------------------------------- the rule's parts
def executable_lots(ticket_lots, admissible_lots, decision):
    """What the ticket may carry once the decision is applied.

    Three states, because 'the desk holds more than the ruler allows' and 'nobody told us
    what the desk holds' need different sentences -- the same three-state discipline the
    sizing spec uses for conformance.
    """
    if ticket_lots is None:
        return {"state": "UNKNOWN_TICKET", "lots": None, "withdrawn_lots": None}
    if decision not in DECISIONS:
        return {"state": "UNKNOWN_DECISION", "lots": None, "withdrawn_lots": None}
    if decision == KEEP:
        return {"state": "KEPT" if ticket_lots else "NOTHING_TO_WITHDRAW",
                "lots": ticket_lots, "withdrawn_lots": 0}
    if admissible_lots is None:
        return {"state": "UNKNOWN_RULER", "lots": None, "withdrawn_lots": None}
    lots = min(ticket_lots, admissible_lots)
    withdrawn = ticket_lots - lots
    return {"state": "WITHDRAWN" if withdrawn else "NOTHING_TO_WITHDRAW",
            "lots": lots, "withdrawn_lots": withdrawn}


def funding_line(capital, first_rung):
    """The one number a reader who wants to fund this sleeve needs."""
    if first_rung is None:
        return {"first_rung_cny": None, "gap_cny": None, "gap_pct_of_capital": None,
                "rung_multiple_of_book": None}
    gap = first_rung - (capital or 0.0)
    return {
        "first_rung_cny": round(first_rung, 2),
        "gap_cny": round(gap, 2),
        "gap_pct_of_capital": (round(gap / (capital or 1.0) * 100.0, 4)
                               if capital else None),
        "rung_multiple_of_book": (round(first_rung / capital, 4) if capital else None),
    }


# --------------------------------------------------------------------- the face
def build(spec, ledger=None, ladder=None, withdrawal=None):
    """Apply the withdrawal to the sizing spec and print the funding line."""
    withdrawal = withdrawal or WITHDRAWAL
    if not spec or not (spec.get("accounts") or {}):
        return None
    decision = withdrawal.get("decision")
    out = {
        "kind": "idx_fut_carry_open_capital",
        "evidence_cutoff": spec.get("evidence_cutoff"),
        "source_face": "results/idx_fut_carry_sizing_spec.json",
        "upstream_source_face": spec.get("source_face"),
        "arm_used_for_decision": spec.get("arm_used_for_decision") or ARM_USED,
        "withdrawal": dict(withdrawal),
        "accounts": {},
    }
    if ladder and (ladder.get("accounts") or {}):
        out["ladder_source_face"] = "results/idx_fut_carry_capital_ladder.json"

    cheapest = None
    rungs_sum = 0.0
    rungs_complete = True
    executable_total = 0
    executable_known = True
    withdrawn_total = 0

    led_accounts = ((ledger or {}).get("accounts") or {})

    for prod in sorted(spec["accounts"]):
        d = spec["accounts"][prod] or {}
        if d.get("status") != "ok":
            out["accounts"][prod] = {"status": d.get("status") or "SPEC_INCOMPLETE"}
            rungs_complete = False
            executable_known = False
            continue
        capital = d.get("capital_cny")
        first = d.get("first_executable_capital_cny")
        ticket = (d.get("ticket") or {}).get("lots")
        admissible = d.get("admissible_lots")
        line = funding_line(capital, first)

        applied = executable_lots(ticket, admissible, decision)
        if applied["lots"] is not None:
            executable_total += applied["lots"]
        else:
            executable_known = False
        if applied["withdrawn_lots"]:
            withdrawn_total += applied["withdrawn_lots"]

        led = led_accounts.get(prod) or {}
        out["accounts"][prod] = {
            "status": "ok",
            "capital_cny": round(capital, 2) if capital else None,
            "target_pct": d.get("target_pct"),
            "budget_cny_at_target": d.get("budget_cny_at_target"),
            "per_lot_vol_cny_hedged": d.get("per_lot_vol_cny_hedged"),
            "funding": line,
            "ruler": {
                "admissible_lots": admissible,
                "state": d.get("state"),
            },
            "desk_ticket": {
                "lots": ticket,
                "conformance": (d.get("ticket") or {}).get("conformance"),
                "multiple_of_budget": (d.get("ticket") or {}).get("multiple_of_budget"),
                "capital_the_ticket_needs_cny": d.get("capital_the_ticket_needs_cny"),
            },
            "executable_ticket": applied,
            "forward_paper": {
                "lots_in_ledger": led.get("lots"),
                "notional_basis_cny": led.get("notional_basis_cny"),
                "last_date": led.get("last_date"),
                "label": ("FUNDED_BY_A_LARGER_CAPITAL"
                          if (led.get("lots") and applied["lots"] is not None
                              and led.get("lots") > applied["lots"]) else "AS_REPORTED"),
                "note": ("kept as an append-only evidence line: it is what a "
                         "capital_the_ticket_needs_cny account would have done"
                         if led.get("lots") and applied["lots"] is not None
                         and led.get("lots") > applied["lots"] else None),
            },
        }

        if first:
            rungs_sum += first
            if cheapest is None or first < cheapest["funding_cny"]:
                cheapest = {"product": prod, "funding_cny": round(first, 2)}
        else:
            rungs_complete = False

    book = {
        "cheapest_to_open": cheapest,
        "funding_for_all_legs_cny": (round(rungs_sum, 2) if rungs_complete else None),
        "executable_lots_total": (executable_total if executable_known else None),
        "withdrawn_lots_total": withdrawn_total,
        "forward_paper_lots_total": sum(
            (a or {}).get("lots") or 0 for a in led_accounts.values()),
    }
    out["book"] = book
    out["sentence"] = _sentence(out)
    out["roads_that_bring_it_back"] = _roads_back(spec, out)
    return out


def _sentence(face):
    book = face.get("book") or {}
    cheapest = book.get("cheapest_to_open") or {}
    parts = []
    if cheapest.get("funding_cny"):
        parts.append("To open this book at all needs %s CNY of capital (%s account)"
                     % (_fmt(cheapest["funding_cny"]), cheapest.get("product")))
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            continue
        f = d.get("funding") or {}
        if f.get("gap_cny") is not None:
            parts.append("%s is %s CNY short of its first lot (capital %s, gap %s%%)"
                         % (prod, _fmt(f["gap_cny"]), _fmt(d.get("capital_cny")),
                            _fmt(f.get("gap_pct_of_capital"), 2)))
    w = face.get("withdrawal") or {}
    ex = _exec_string(face)
    if ex:
        parts.append(ex)
    if book.get("forward_paper_lots_total"):
        parts.append(
            "The forward paper series that ran on %d lot(s) across the accounts is kept "
            "and labelled FUNDED_BY_A_LARGER_CAPITAL: it is what a larger account would "
            "have done, not what this one can" % book["forward_paper_lots_total"])
    if w.get("reversal"):
        parts.append("It comes back the moment the capital does")
    return ". ".join(p[0].upper() + p[1:] for p in parts if p) + "." if parts else ""


def _exec_string(face):
    bits = []
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            continue
        ex = d.get("executable_ticket") or {}
        desk = (d.get("desk_ticket") or {}).get("lots")
        if ex.get("state") == "WITHDRAWN":
            bits.append("%s: the desk's %d lot(s) are withdrawn from the ticket and the "
                        "executable line is %d" % (prod, desk or 0, ex.get("lots") or 0))
        elif ex.get("state") == "KEPT":
            bits.append("%s: the desk's %d lot(s) stay on the ticket (decision KEEP)"
                        % (prod, desk or 0))
        elif ex.get("state") == "NOTHING_TO_WITHDRAW":
            bits.append("%s: nothing to withdraw (ticket %s lots)"
                        % (prod, desk if desk is not None else "unknown"))
    return "; ".join(bits)


def _roads_back(spec, face):
    """Each road that would put a lot back, with the number that makes it true.

    A decision record that hides the alternatives is a preference, not a decision -- and a
    withdrawal with no stated reversal reads as a verdict on the sleeve.
    """
    roads = []
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            continue
        src = (spec.get("accounts") or {}).get(prod) or {}
        f = d.get("funding") or {}
        alt_b = ((src.get("roads") or {}).get("B_keep_capital_lower_target") or {})
        roads.append({
            "product": prod,
            "road": "fund_to_first_rung",
            "needs_cny": f.get("first_rung_cny"),
            "gets": "1 lot (and one more lot per further rung)",
            "adopted": True,
        })
        if alt_b:
            roads.append({
                "product": prod,
                "road": "B_keep_capital_lower_target",
                "needs_pct": alt_b.get("target_for_one_lot_pct"),
                "gets": "%s lot(s)" % alt_b.get("lots_at_that_target"),
                "adopted": False,
                "because_not": ("that road spends drawdown tolerance to fit a contract "
                                "-- see the adoption record"),
            })
    return roads


# ------------------------------------------------------------------ the page
def write_doc(face):
    book = face.get("book") or {}
    lines = []
    lines.append("# the carry book: what it takes to open, and the four lots that came off")
    lines.append("")
    lines.append("_generated by `scripts/idx_fut_carry_open_capital.py` -- do not hand-edit_")
    lines.append("")
    lines.append("**cutoff** %s / **arm** %s / **decision** %s (%s)"
                 % (face.get("evidence_cutoff") or "n/a",
                    face.get("arm_used_for_decision") or "n/a",
                    (face.get("withdrawal") or {}).get("decision"),
                    (face.get("withdrawal") or {}).get("decided")))
    lines.append("")
    lines.append("## the one line")
    lines.append("")
    lines.append("> " + (face.get("sentence") or "n/a"))
    lines.append("")
    lines.append("## the funding line")
    lines.append("")
    lines.append("| account | capital today | 8% budget | one hedged lot | first rung | "
                 "short by | rung x book |")
    lines.append("|---|---|---|---|---|---|---|")
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            lines.append("| %s | %s |" % (prod, d.get("status")))
            continue
        f = d.get("funding") or {}
        lines.append("| %s | %s | %s | %s | **%s** | %s (%s%%) | %sx |"
                     % (prod, _fmt(d.get("capital_cny")),
                        _fmt(d.get("budget_cny_at_target")),
                        _fmt(d.get("per_lot_vol_cny_hedged")),
                        _fmt(f.get("first_rung_cny")),
                        _fmt(f.get("gap_cny")), _fmt(f.get("gap_pct_of_capital"), 2),
                        _fmt(f.get("rung_multiple_of_book"), 4)))
    lines.append("")
    cl = book.get("cheapest_to_open") or {}
    if cl.get("funding_cny"):
        lines.append("Openable at **%s CNY** (%s). Both legs funded at once: **%s CNY**."
                     % (_fmt(cl["funding_cny"]), cl.get("product"),
                        _fmt(book.get("funding_for_all_legs_cny"))))
        lines.append("")
    lines.append("## what the decision did to the ticket")
    lines.append("")
    lines.append("| account | desk lots | conformance | capital that needs | executable lots "
                 "| withdrawn |")
    lines.append("|---|---|---|---|---|---|")
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            continue
        desk = d.get("desk_ticket") or {}
        ex = d.get("executable_ticket") or {}
        lines.append("| %s | %s | %s | %s | **%s** | %s |"
                     % (prod, desk.get("lots"), desk.get("conformance"),
                        _fmt(desk.get("capital_the_ticket_needs_cny")),
                        ex.get("lots"), ex.get("withdrawn_lots")))
    lines.append("")
    lines.append("The desk's lots are **printed, not deleted** -- they are an input this book "
                 "does not rewrite. What changed is their status: from instruction to "
                 "counterfactual.")
    lines.append("")
    lines.append("## the forward paper series")
    lines.append("")
    lines.append("| account | lots in the ledger | notional basis | label |")
    lines.append("|---|---|---|---|")
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            continue
        fw = d.get("forward_paper") or {}
        lines.append("| %s | %s | %s | %s |"
                     % (prod, fw.get("lots_in_ledger"), _fmt(fw.get("notional_basis_cny")),
                        fw.get("label")))
    lines.append("")
    lines.append("Kept on purpose and never rewritten: it is the only record of what those "
                 "lots would have paid. Its label says whose money that was.")
    lines.append("")
    lines.append("## roads that bring a lot back")
    lines.append("")
    lines.append("| account | road | needs | gets | adopted |")
    lines.append("|---|---|---|---|---|")
    for r in face.get("roads_that_bring_it_back") or []:
        needs = (_fmt(r.get("needs_cny")) + " CNY" if r.get("needs_cny") is not None
                 else ("target %s%%" % _fmt(r.get("needs_pct"), 4)))
        lines.append("| %s | %s | %s | %s | %s |"
                     % (r.get("product"), r.get("road"), needs, r.get("gets"),
                        "yes" if r.get("adopted") else "no"))
    lines.append("")
    lines.append("## honesty notes")
    lines.append("")
    lines.append("* no volatility, price or P&L is derived here: capital, per-lot vol, "
                 "admissible lots, first rung and the desk's lots are read from the sizing "
                 "spec, which reads the ladder, which reads the paper SIZING face;")
    lines.append("* `--check` re-derives the funding line, the gap, the executable lots and "
                 "the labels from those inputs, and names what it did not recompute;")
    lines.append("* 'cheapest to open' compares accounts on their own first rung -- it is not "
                 "a preference between the two hedges (that is priced in the hedge face);")
    lines.append("* the withdrawal is conditional on capital, not a verdict on the sleeve: "
                 "the same rule hands back one lot at the first rung;")
    lines.append("* the paper ledger is opened read-only by this file and is never written.")
    lines.append("")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# ------------------------------------------------------------------------ run
def run():
    spec = _load(SPEC_PATH)
    face = build(spec, _load(LEDGER_PATH), _load(LADDER_PATH))
    if face is None:
        print("no sizing spec on disk: %s" % SPEC_PATH)
        return 2
    import datetime
    face["generated"] = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    _dump(OUT_PATH, face)
    write_doc(face)
    for prod in sorted(face["accounts"]):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            print("%s: %s" % (prod, d.get("status")))
            continue
        f = d.get("funding") or {}
        ex = d.get("executable_ticket") or {}
        print("%s capital=%s short=%s first_rung=%s desk=%s executable=%s (%s)"
              % (prod, _fmt(d.get("capital_cny")), _fmt(f.get("gap_cny")),
                 _fmt(f.get("first_rung_cny")), (d.get("desk_ticket") or {}).get("lots"),
                 ex.get("lots"), ex.get("state")))
    print("cheapest_to_open=%s %s" % ((face["book"].get("cheapest_to_open") or {}).get("product"),
                                      _fmt((face["book"].get("cheapest_to_open") or {}).get("funding_cny"))))
    return 0


def show():
    face = _load(OUT_PATH)
    if not face:
        print("no face on disk: %s" % OUT_PATH)
        return 2
    print("decision=%s decided=%s"
          % ((face.get("withdrawal") or {}).get("decision"),
             (face.get("withdrawal") or {}).get("decided")))
    print(face.get("sentence") or "n/a")
    return 0


def check():
    """Re-derive every consequence printed here, from the faces it claims to read."""
    face = _load(OUT_PATH)
    spec = _load(SPEC_PATH)
    ledger = _load(LEDGER_PATH)
    problems = []
    if not face:
        print(json.dumps({"ok": False, "problems": ["face missing: %s" % OUT_PATH]}))
        return 1
    if not spec:
        print(json.dumps({"ok": False,
                          "problems": ["sizing spec missing: %s" % SPEC_PATH]}))
        return 1
    w = face.get("withdrawal") or {}
    if w.get("decision") not in DECISIONS:
        problems.append("withdrawal decision is not one of %r: %r"
                        % (list(DECISIONS), w.get("decision")))
    decision = w.get("decision")
    led_accounts = ((ledger or {}).get("accounts") or {})
    rungs = []
    for prod in sorted((spec.get("accounts") or {})):
        src = spec["accounts"][prod] or {}
        pub = (face.get("accounts") or {}).get(prod) or {}
        if src.get("status") != "ok":
            if pub.get("status") != (src.get("status") or "SPEC_INCOMPLETE"):
                problems.append("%s: upstream incomplete but published as %r"
                                % (prod, pub.get("status")))
            continue
        if pub.get("status") != "ok":
            problems.append("%s: published as %r while the spec is ok"
                            % (prod, pub.get("status")))
            continue
        cap = src.get("capital_cny")
        first = src.get("first_executable_capital_cny")
        if first:
            rungs.append(first)
        want = funding_line(cap, first)
        got = pub.get("funding") or {}
        for key in ("first_rung_cny", "gap_cny"):
            a, b = got.get(key), want.get(key)
            if (a is None) != (b is None) or (
                    a is not None and abs(a - b) > 0.01 * max(1.0, abs(b))):
                problems.append("%s: %s %r != %r" % (prod, key, a, b))
        if (got.get("gap_pct_of_capital") is not None
                and want.get("gap_pct_of_capital") is not None
                and abs(got["gap_pct_of_capital"] - want["gap_pct_of_capital"]) > 1e-3):
            problems.append("%s: gap_pct %r != %r"
                            % (prod, got.get("gap_pct_of_capital"),
                               want.get("gap_pct_of_capital")))
        ticket = (src.get("ticket") or {}).get("lots")
        admitted = src.get("admissible_lots")
        want_ex = executable_lots(ticket, admitted, decision)
        got_ex = pub.get("executable_ticket") or {}
        for key in ("state", "lots", "withdrawn_lots"):
            if got_ex.get(key) != want_ex.get(key):
                problems.append("%s: executable %s %r != %r"
                                % (prod, key, got_ex.get(key), want_ex.get(key)))
        # the desk's lot count is an input: if the spec moved, this face is stale
        if (pub.get("desk_ticket") or {}).get("lots") != ticket:
            problems.append("%s: desk lots %r != spec's %r"
                            % (prod, (pub.get("desk_ticket") or {}).get("lots"), ticket))
        # the ledger is read, never rewritten: compare with the file on disk now
        led_lots = (led_accounts.get(prod) or {}).get("lots")
        if (pub.get("forward_paper") or {}).get("lots_in_ledger") != led_lots:
            problems.append("%s: ledger lots %r != ledger on disk %r"
                            % (prod, (pub.get("forward_paper") or {}).get("lots_in_ledger"),
                               led_lots))
        want_label = ("FUNDED_BY_A_LARGER_CAPITAL"
                      if (led_lots and want_ex.get("lots") is not None
                          and led_lots > want_ex["lots"]) else "AS_REPORTED")
        if (pub.get("forward_paper") or {}).get("label") != want_label:
            problems.append("%s: forward label %r != %r"
                            % (prod, (pub.get("forward_paper") or {}).get("label"),
                               want_label))
    book = face.get("book") or {}
    if rungs:
        cheapest = min(rungs)
        got = (book.get("cheapest_to_open") or {}).get("funding_cny")
        if got is None or abs(got - cheapest) > 0.01 * max(1.0, cheapest):
            problems.append("cheapest_to_open %r != %r" % (got, cheapest))
        if len(rungs) == len([p for p in (spec.get("accounts") or {})
                              if (spec["accounts"][p] or {}).get("status") == "ok"]):
            want_sum = round(sum(rungs), 2)
            if (book.get("funding_for_all_legs_cny") is None
                    or abs(book["funding_for_all_legs_cny"] - want_sum)
                    > 0.01 * max(1.0, want_sum)):
                problems.append("funding_for_all_legs %r != %r"
                                % (book.get("funding_for_all_legs_cny"), want_sum))
    sentence = face.get("sentence") or ""
    cheapest = (book.get("cheapest_to_open") or {}).get("funding_cny")
    if cheapest is not None and _fmt(cheapest) not in sentence:
        problems.append("the sentence does not carry the funding line %s"
                        % _fmt(cheapest))
    if (book.get("forward_paper_lots_total") or 0) > 0 and "FUNDED_BY_A_LARGER_CAPITAL" \
            not in sentence:
        problems.append("the sentence does not carry the counterfactual label")
    print(json.dumps({
        "ok": not problems,
        "problems": problems,
        "accounts": sorted((face.get("accounts") or {})),
        "not_recomputed": [
            "ann_vol_of_one_lot_hedged (read from the sizing spec, which reads the ladder)",
            "the desk's recommended lots and the paper ledger's lots (inputs, echoed)",
            "whether 8% is the right house standard (that is the adoption, not a number)",
            "the hedge choice between the two indices (priced in the hedge face)",
        ],
    }, ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------- selftest
def selftest():
    fails = []
    checks = []

    def chk(name, cond, extra=""):
        checks.append(name)
        if not cond:
            fails.append("%s%s" % (name, (" -- " + extra) if extra else ""))

    spec = {
        "evidence_cutoff": "2026-11-16",
        "source_face": "results/idx_fut_carry_capital_ladder.json",
        "arm_used_for_decision": "hedged",
        "accounts": {
            "IC": {
                "status": "ok", "capital_cny": 1000000.0, "target_pct": 8.0,
                "budget_cny_at_target": 80000.0, "per_lot_vol_cny_hedged": 90000.98,
                "admissible_lots": 0, "state": "BELOW_FIRST_RUNG",
                "first_executable_capital_cny": 1125012.25,
                "capital_the_ticket_needs_cny": 4500049.0,
                "ticket": {"lots": 4, "conformance": "OUT_OF_RULER",
                           "multiple_of_budget": 4.5},
                "roads": {"B_keep_capital_lower_target": {
                    "lots_at_that_target": 1, "target_for_one_lot_pct": 9.0001,
                    "adopted": False}},
            },
            "IM": {
                "status": "ok", "capital_cny": 1000000.0, "target_pct": 8.0,
                "budget_cny_at_target": 80000.0, "per_lot_vol_cny_hedged": 92163.18,
                "admissible_lots": 0, "state": "BELOW_FIRST_RUNG",
                "first_executable_capital_cny": 1152039.75,
                "capital_the_ticket_needs_cny": 4608159.0,
                "ticket": {"lots": 4, "conformance": "OUT_OF_RULER",
                           "multiple_of_budget": 4.6082},
                "roads": {"B_keep_capital_lower_target": {
                    "lots_at_that_target": 1, "target_for_one_lot_pct": 9.2163,
                    "adopted": False}},
            },
        },
    }
    ledger = {"accounts": {"IC": {"lots": 4, "notional_basis_cny": 5100000.0,
                                 "last_date": "2026-11-16"},
                           "IM": {"lots": 4, "notional_basis_cny": 5200000.0,
                                  "last_date": "2026-11-16"}}}
    face = build(spec, ledger)

    # L1 the funding line is the first rung, read from the spec (not re-derived)
    chk("L1 funding line is the first rung",
        face["accounts"]["IC"]["funding"]["first_rung_cny"] == 1125012.25)
    # L2 the gap is the rung minus today's capital
    chk("L2 gap algebra",
        abs(face["accounts"]["IC"]["funding"]["gap_cny"] - 125012.25) < 0.01)
    # L3 the gap as a share of capital says how far off "at this size" is
    chk("L3 gap share of capital",
        abs(face["accounts"]["IC"]["funding"]["gap_pct_of_capital"] - 12.5012) < 1e-3)
    # L4 the withdrawal takes the desk's four lots to the ruler's zero
    chk("L4 withdraw takes 4 to 0",
        face["accounts"]["IC"]["executable_ticket"]["lots"] == 0
        and face["accounts"]["IC"]["executable_ticket"]["withdrawn_lots"] == 4
        and face["accounts"]["IC"]["executable_ticket"]["state"] == "WITHDRAWN")
    # L5 the desk's lots stay printed after the withdrawal (an input, not an instruction)
    chk("L5 desk lots still printed",
        face["accounts"]["IC"]["desk_ticket"]["lots"] == 4)
    # L6 the withdrawn series is labelled as somebody else's money
    chk("L6 forward label is the counterfactual",
        face["accounts"]["IC"]["forward_paper"]["label"] == "FUNDED_BY_A_LARGER_CAPITAL")
    # L7 a ticket the ruler allows is left alone (the decision is not "always zero")
    chk("L7 within-ruler ticket kept",
        executable_lots(2, 4, WITHDRAW)["state"] == "NOTHING_TO_WITHDRAW"
        and executable_lots(2, 4, WITHDRAW)["lots"] == 2)
    # L8 KEEP is honoured rather than silently ignored (a decision record, not a wall)
    chk("L8 keep decision leaves the ticket",
        executable_lots(4, 0, KEEP)["lots"] == 4)
    # L9 an unknown ruler is not read as zero
    chk("L9 unknown ruler is not zero",
        executable_lots(4, None, WITHDRAW)["state"] == "UNKNOWN_RULER")
    # L10 an unknown ticket is not invented
    chk("L10 unknown ticket", executable_lots(None, 0, WITHDRAW)["lots"] is None)
    # L11 a bogus decision is refused, not defaulted
    chk("L11 bogus decision refused",
        executable_lots(4, 0, "DO_WHATEVER")["state"] == "UNKNOWN_DECISION")
    # L12 the funding line is the cheaper of the two accounts, and the sum is offered too
    chk("L12 cheapest + all-legs sum",
        face["book"]["cheapest_to_open"]["product"] == "IC"
        and abs(face["book"]["funding_for_all_legs_cny"] - 2277052.0) < 0.01)
    # L13 the book's executable lots are zero after the withdrawal
    chk("L13 book executable total is 0", face["book"]["executable_lots_total"] == 0)
    # L14 the sentence carries the funding number, the gap and the label
    s = face["sentence"]
    chk("L14 sentence carries the numbers",
        "1,125,012" in s and "125,012" in s and "FUNDED_BY_A_LARGER_CAPITAL" in s)
    # L15 the alternatives are printed with the number that makes each true
    roads = {(r["product"], r["road"]): r for r in face["roads_that_bring_it_back"]}
    chk("L15 reversal roads priced",
        roads[("IC", "fund_to_first_rung")]["needs_cny"] == 1125012.25
        and roads[("IC", "B_keep_capital_lower_target")]["needs_pct"] == 9.0001
        and roads[("IC", "B_keep_capital_lower_target")]["adopted"] is False)
    # L16 a missing spec is refused, not defaulted
    chk("L16 missing spec refused", build(None) is None)
    # L17 an incomplete account is labelled, not published as ok
    bad = json.loads(json.dumps(spec))
    bad["accounts"]["IM"]["status"] = "INCOMPLETE_LADDER"
    chk("L17 incomplete account labelled",
        build(bad, ledger)["accounts"]["IM"]["status"] == "INCOMPLETE_LADDER")
    # L18 the decision constant names a real decision (a typo would publish a face no
    # reader can match to a rule)
    chk("L18 decision is one of the two", WITHDRAWAL["decision"] in DECISIONS)
    # L19 funding a book that is already at its rung leaves a zero gap and one lot
    at_rung = json.loads(json.dumps(spec))
    at_rung["accounts"]["IC"]["capital_cny"] = 1125012.25
    at_rung["accounts"]["IC"]["admissible_lots"] = 1
    g = build(at_rung, ledger)["accounts"]["IC"]
    chk("L19 at the rung the gap is 0 and a lot comes back",
        abs(g["funding"]["gap_cny"]) < 0.01 and g["executable_ticket"]["lots"] == 1)
    # L20 the cutoff is inherited, not stamped today
    chk("L20 cutoff inherited", face["evidence_cutoff"] == "2026-11-16")
    # L21 a ledger that holds no lots gets no counterfactual label
    empty = {"accounts": {"IC": {"lots": 0}, "IM": {"lots": 0}}}
    chk("L21 no lots, no counterfactual label",
        build(spec, empty)["accounts"]["IC"]["forward_paper"]["label"] == "AS_REPORTED")
    # L22 the doc names the decision and its date (a page a reader can date)
    chk("L22 withdrawal record is dated",
        WITHDRAWAL.get("decided") and "bm-c round" in WITHDRAWAL.get("decided_in", ""))
    # L23 a spec with no first rung reports 'not openable', not 0 CNY to open
    norung = json.loads(json.dumps(spec))
    norung["accounts"]["IC"]["first_executable_capital_cny"] = None
    f = build(norung, ledger)
    chk("L23 no rung is not 0 CNY",
        f["accounts"]["IC"]["funding"]["first_rung_cny"] is None
        and f["book"]["funding_for_all_legs_cny"] is None)

    print("idx_fut_carry_open_capital selftest %d/%d PASS%s"
          % (len(checks) - len(fails), len(checks),
             "" if not fails else " -- FAIL: " + "; ".join(fails)))
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    if cmd in ("run", ""):
        return run()
    if cmd == "show":
        return show()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
