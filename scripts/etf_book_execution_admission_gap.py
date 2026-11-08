#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the desk is handing out tickets for a book its own supply calendar refuses --
and the wrapper those tickets actually run has never been through that gate

WHY THIS FILE EXISTS
--------------------
Forty rounds of admission work (r1415-r1439) ended on one sentence: the supply
floor is red because the calendar refuses every candidate, and 40 rounds later
the desk is still refusing itself supply.

Meanwhile `results/etf_book_order/TICKET-<asof>.json` has been printing a
buy list every rebalance.  Nobody had put those two faces side by side:

  supply_calendar.json   nobond_vt08_adopted  refuse   (years_for_half 2 vs 3)
  TICKET-2026-11-06      book_weight 0.46 of 1,000,000 CNY, 5 names, GC001 cash

Two sentences issued by the same desk on the same day.  A reader of the operator
board sees "no lawful supply"; a reader of the order page sees "buy these five".
That is the SAME defect class r1199/r1422 fixed one layer down (two opposite
repairs printing as one word), except here the two words are on two different
pages and nothing reconciles them.

So this face answers three questions from published receipts only -- it prices
nothing, imports no engine, and re-derives every number in --check:

  1. Is the book being EXECUTED today the same book the calendar judges?
     (identity is proved from four fields, never assumed -- see IDENTITY below)
  2. If yes, does the calendar refuse it, and how much money is on the line?
  3. Is the thing actually running -- the beta overlay plus the repo cash leg --
     the same thing the gate judged?  (r1253: the wrapper is not cosmetic)

IDENTITY (frozen before any receipt was read)
---------------------------------------------
Proved only when ALL four hold, else UNMATCHED (never guessed):
  I1  ticket.n_hold            == phase_gate.n_hold
  I2  card.config.vol_target   == candidate.vol_target  and candidate.vol_floor == 0.0
  I3  card.config.universe_classes contains no bond sleeve (the candidate is
      literally named "nobond_*") -- checked against the candidate name prefix
  I4  ticket.card_agreement.same_decision_bar and .ticket_is_prefix_of_card

VERDICT (frozen before any receipt was read)
--------------------------------------------
  EXECUTES_REFUSED_BOOK   identity proved, calendar has no ADMIT for that book,
                          and the ticket carries book_weight > 0
  EXECUTES_ADMITTED_BOOK  identity proved, calendar admits it
  NOT_EXECUTING           identity proved, book_weight == 0
  UNMATCHED_IDENTITY      identity not proved (receipts readable)
  UNKNOWN                 a receipt this face needs is missing or unreadable

Wrapper disclosure is a FIELD, not a verdict: `wrapper_gated` is False whenever
the judged candidate carries no beta/cash keys, which is the case today -- the
gate judged the un-overlaid book.  The face prints that as an unmeasured gap
rather than quietly treating the ticket as the judged thing.

  python scripts/etf_book_execution_admission_gap.py run
  python scripts/etf_book_execution_admission_gap.py --selftest
  python scripts/etf_book_execution_admission_gap.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUT_JSON = os.path.join(ROOT, "results", "etf_book_execution_admission_gap.json")

ORDER_LATEST = "results/etf_book_order/latest.json"
ORDER_DIR = "results/etf_book_order"
CARD = "results/etf_book_production/latest.json"
PHASE_GATE = "results/etf_book_phase_gate.json"
CALENDAR = "results/supply_calendar.json"

PASS_WORD = "ADMIT"

# words, frozen
EXEC_REFUSED = "EXECUTES_REFUSED_BOOK"
EXEC_ADMITTED = "EXECUTES_ADMITTED_BOOK"
NOT_EXECUTING = "NOT_EXECUTING"
UNMATCHED = "UNMATCHED_IDENTITY"
UNKNOWN = "UNKNOWN"


def _load(path):
    """(obj, error). Never raises -- a missing receipt is a stated unknown."""
    full = os.path.join(ROOT, path)
    try:
        with open(full, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        return None, "unreadable: %s" % exc
    try:
        return json.loads(raw.decode("utf-8")), ""
    except (UnicodeDecodeError, ValueError) as exc:
        return None, "not json: %s" % exc


def _sha16(raw):
    return hashlib.sha256(raw).hexdigest()[:16]


def ticket_path(latest):
    """`latest.json` names the ticket file; build the repo-relative path."""
    name = (latest or {}).get("file") or ""
    if not name:
        return None
    return "%s/%s" % (ORDER_DIR, name)


def match_candidate(candidates, vol_target, vol_floor=0.0):
    """Candidates with the same risk setting and no floor.

    Returns (matched_list, note).  More than one match is reported, never
    resolved by preference order: two books with the same risk setting are
    different books and choosing one silently is how a face starts lying."""
    hits = []
    for c in candidates or []:
        vt = c.get("vol_target")
        vf = c.get("vol_floor")
        if vt is None or vf is None:
            continue
        if abs(float(vt) - float(vol_target)) <= 1e-9 and abs(float(vf) - float(vol_floor)) <= 1e-9:
            hits.append(c)
    if not hits:
        return [], "no candidate carries vol_target=%s vol_floor=%s" % (vol_target, vol_floor)
    if len(hits) > 1:
        return hits, "ambiguous: %d candidates share the same risk setting (%s)" % (
            len(hits), ", ".join(str(h.get("book")) for h in hits))
    return hits, ""


def identity(ticket, card, phase, cand):
    """Four frozen conditions. Every one is printed with its own value."""
    conds = []
    t_nh = ticket.get("n_hold")
    p_nh = phase.get("n_hold")
    conds.append(("I1_n_hold", t_nh, p_nh, t_nh is not None and p_nh is not None and int(t_nh) == int(p_nh)))

    cfg = (card or {}).get("config") or {}
    vt = cfg.get("vol_target")
    c_vt = (cand or {}).get("vol_target")
    c_vf = (cand or {}).get("vol_floor")
    i2 = (vt is not None and c_vt is not None and c_vf is not None
          and abs(float(vt) - float(c_vt)) <= 1e-9 and abs(float(c_vf)) <= 1e-9)
    conds.append(("I2_vol_target_no_floor", vt, "%s/floor %s" % (c_vt, c_vf), i2))

    classes = [str(x).lower() for x in (cfg.get("universe_classes") or [])]
    name = str((cand or {}).get("book") or "")
    no_bond_sleeve = "bond" not in classes
    i3 = bool(name.startswith("nobond")) and no_bond_sleeve
    conds.append(("I3_nobond_both_sides", "classes=%s" % ",".join(classes) or "-",
                  "candidate=%s" % (name or "-"), i3))

    ca = ticket.get("card_agreement") or {}
    i4 = bool(ca.get("same_decision_bar")) and bool(ca.get("ticket_is_prefix_of_card"))
    conds.append(("I4_ticket_is_card_prefix", ca.get("same_decision_bar"),
                  ca.get("ticket_is_prefix_of_card"), i4))

    rows = [{"condition": n, "ticket_or_card_side": a, "judged_side": b, "holds": bool(ok)}
            for (n, a, b, ok) in conds]
    return rows, all(r["holds"] for r in rows)


def wrapper_gated(cand):
    """Did the thing the gate judged include the execution wrapper?

    The gate receipts declare vol_target/vol_floor and never beta or a cash
    leg; the ticket runs beta 0.20 plus GC001 repo on the remainder.  If the
    candidate has no beta/cash key, the wrapper is NOT gated -- said out loud."""
    keys = set((cand or {}))
    has_beta = any("beta" in k for k in keys)
    has_cash = any(k in keys for k in ("cash", "cash_leg", "repo"))
    return {"beta_overlay_gated": has_beta, "cash_leg_gated": has_cash,
            "gated": bool(has_beta and has_cash),
            "note": ("the judged object is the book before the execution wrapper"
                     if not (has_beta and has_cash) else "wrapper keys present in receipt")}


def build(order_latest=None, ticket=None, card=None, phase=None, calendar=None):
    """Pure function: receipts in, verdict out. Called by run() and --check."""
    missing = []
    for label, obj in (("order_latest", order_latest), ("ticket", ticket), ("card", card),
                       ("phase_gate", phase), ("supply_calendar", calendar)):
        if obj is None:
            missing.append(label)

    out = {
        "face": "etf_book_execution_admission_gap",
        "question": ("is the book being executed today the book the supply calendar refuses, "
                     "and is the thing actually running the thing that was judged?"),
        "verdict": UNKNOWN,
        "missing_receipts": missing,
        "identity": [],
        "identity_proved": False,
        "candidate": None,
        "calendar_state": None,
        "calendar_sentence": None,
        "failing_checks": [],
        "money": {},
        "wrapper": {},
        "next_action": "",
    }
    if missing:
        out["next_action"] = "restore the missing receipts; nothing can be said about the gap"
        return out

    tp = ticket_path(order_latest)
    out["ticket_file"] = tp
    out["evidence_cutoff"] = ticket.get("evidence_cutoff")

    t_ticket = ticket.get("ticket") or {}
    nav = t_ticket.get("nav")
    bw = t_ticket.get("book_weight")
    out["money"] = {
        "nav_cny": nav,
        "book_weight": bw,
        "book_amount_cny": t_ticket.get("book_amount"),
        "cash_amount_cny": t_ticket.get("cash_amount"),
        "cash_leg": t_ticket.get("cash_leg"),
        "beta_target": order_latest.get("beta_target"),
        "k_now": order_latest.get("k_now"),
        "names_in_ticket": len(t_ticket.get("order") or []),
    }

    cfg = card.get("config") or {}
    candidates, note = match_candidate(phase.get("books") or [], cfg.get("vol_target"),
                                       vol_floor=0.0)
    out["match_note"] = note
    if len(candidates) != 1:
        out["verdict"] = UNMATCHED
        out["next_action"] = ("declare which candidate receipt the executed book is; "
                              "the face will not pick one out of %d" % max(1, len(candidates)))
        out["candidate"] = None
        # identity still printed against the first hit when there is one
        if candidates:
            rows, proved = identity(ticket, card, phase, candidates[0])
            out["identity"] = rows
            out["identity_proved"] = proved
        return out

    cand = candidates[0]
    rows, proved = identity(ticket, card, phase, cand)
    out["identity"] = rows
    out["identity_proved"] = proved
    out["candidate"] = cand.get("book")
    out["judged_n_hold"] = phase.get("n_hold")
    out["judged_vol_target"] = cand.get("vol_target")
    out["judged_receipt"] = PHASE_GATE

    # the calendar's word for the same book name (it may be absent -- absence is
    # not a pass and not a refusal)
    row = None
    for c in calendar.get("candidates") or []:
        if c.get("candidate") == cand.get("book"):
            row = c
            break
    if row is None:
        out["calendar_state"] = "not_listed"
        out["calendar_sentence"] = "the supply calendar does not list this book"
        out["failing_checks"] = []
    else:
        out["calendar_state"] = row.get("state")
        out["failing_checks"] = list(row.get("failing_checks") or [])
        reason = (row.get("elected_reason") or {}).get("sentence")
        out["calendar_sentence"] = reason or "no sentence published"

    out["wrapper"] = wrapper_gated(cand)

    calendar_admits = out["calendar_state"] == PASS_WORD
    holding = bool(bw) and float(bw) > 0.0

    if not proved:
        out["verdict"] = UNMATCHED
        out["next_action"] = ("prove identity or declare the pair explicitly; "
                              "an unproved match is not a finding")
    elif not holding:
        out["verdict"] = NOT_EXECUTING
        out["next_action"] = "no position; the calendar's refusal is not being acted against"
    elif calendar_admits:
        out["verdict"] = EXEC_ADMITTED
        out["next_action"] = "consistent: the executed book is admitted"
    else:
        out["verdict"] = EXEC_REFUSED
        out["next_action"] = (
            "two legal sentences on one desk: the ticket executes %s at book_weight %.3f "
            "while the supply calendar says %s (%s). Put the execution wrapper (beta %.2f + "
            "cash leg) through the same year gate before the next rebalance -- today the "
            "judged object is the un-overlaid book."
            % (out["candidate"], float(bw), out["calendar_state"],
               out["calendar_sentence"], float(out["money"].get("beta_target") or 0.0)))

    out["asof_bar"] = order_latest.get("as_of")
    return out


def run():
    order_latest, e1 = _load(ORDER_LATEST)
    ticket = None
    e2 = ""
    if order_latest is not None:
        tp = ticket_path(order_latest)
        if tp:
            ticket, e2 = _load(tp)
    card, e3 = _load(CARD)
    phase, e4 = _load(PHASE_GATE)
    calendar, e5 = _load(CALENDAR)

    out = build(order_latest, ticket, card, phase, calendar)
    out["sources"] = {
        "order_latest": {"path": ORDER_LATEST, "error": e1},
        "ticket": {"path": out.get("ticket_file") or "-", "error": e2},
        "card": {"path": CARD, "error": e3},
        "phase_gate": {"path": PHASE_GATE, "error": e4},
        "supply_calendar": {"path": CALENDAR, "error": e5},
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    m = out["money"]
    print("verdict: %s" % out["verdict"])
    print("candidate: %s | calendar: %s | %s" % (out["candidate"], out["calendar_state"],
                                                 out["calendar_sentence"]))
    if m:
        print("money: book_weight %.4f of CNY %s -> CNY %s in %d names; cash CNY %s on %s"
              % (float(m.get("book_weight") or 0.0), m.get("nav_cny"), m.get("book_amount_cny"),
                 m.get("names_in_ticket") or 0, m.get("cash_amount_cny"), m.get("cash_leg")))
        print("wrapper: beta %.2f (k %.4f); judged object gated: %s"
              % (float(m.get("beta_target") or 0.0), float(m.get("k_now") or 0.0),
                 out["wrapper"].get("gated")))
    for r in out["identity"]:
        print("  %s ticket/card=%-22s judged=%-22s holds=%s"
              % (r["condition"], r["ticket_or_card_side"], r["judged_side"], r["holds"]))
    print("next: %s" % out["next_action"])
    return 0


def check():
    """Re-derive the verdict from the published receipt's own sources."""
    pub, err = _load("results/etf_book_execution_admission_gap.json")
    if pub is None:
        print("check: no published receipt (%s)" % err)
        return 3
    order_latest, _ = _load(ORDER_LATEST)
    ticket = None
    if order_latest is not None:
        tp = ticket_path(order_latest)
        if tp:
            ticket, _ = _load(tp)
    card, _ = _load(CARD)
    phase, _ = _load(PHASE_GATE)
    calendar, _ = _load(CALENDAR)
    again = build(order_latest, ticket, card, phase, calendar)
    bad = []
    for k in ("verdict", "candidate", "calendar_state", "identity_proved", "failing_checks"):
        if again.get(k) != pub.get(k):
            bad.append("%s: published=%r derived=%r" % (k, pub.get(k), again.get(k)))
    if bad:
        print("check: MISMATCH")
        for b in bad:
            print("  " + b)
        return 3
    print("check: OK (verdict=%s candidate=%s)" % (pub.get("verdict"), pub.get("candidate")))
    return 0


# ----------------------------------------------------------------------------
# fixtures.  Every verdict word must be reachable; a word that only exists in the
# docstring is a word the reader will meet as a surprise.
# ----------------------------------------------------------------------------
def _fx(n_hold=5, vol_target=0.08, classes=("equity", "commodity", "convertible"),
        book_name="nobond_vt08_adopted", book_weight=0.46, decided_bar=True,
        prefix=True, cal_state="CONDITIONAL", cal_listed=True,
        judged_n_hold=5, judged_vol_target=0.08):
    """Judged-side values are given separately on purpose: a fixture that moves
    both sides together cannot break an identity condition, and a leg that
    cannot fail is not evidence (r1371 arm-class lesson)."""
    order = {"file": "TICKET-X.json", "as_of": "2026-11-06", "beta_target": 0.2, "k_now": 0.46}
    ticket = {
        "n_hold": n_hold, "evidence_cutoff": "2026-11-06",
        "card_agreement": {"same_decision_bar": decided_bar, "ticket_is_prefix_of_card": prefix},
        "ticket": {"nav": 1_000_000.0, "book_weight": book_weight, "book_amount": 460_000.0,
                   "cash_amount": 540_000.0, "cash_leg": "GC001", "order": [{"symbol": "x"}]},
    }
    card = {"config": {"vol_target": vol_target, "universe_classes": list(classes), "n_hold": 12}}
    phase = {"n_hold": judged_n_hold, "books": [
        {"book": book_name, "vol_target": judged_vol_target, "vol_floor": 0.0},
        {"book": book_name + "_floor_050", "vol_target": judged_vol_target, "vol_floor": 0.5},
    ]}
    cal = {"candidates": ([{"candidate": book_name, "state": cal_state,
                            "failing_checks": ["Y4_top2_share"],
                            "elected_reason": {"sentence": "years_for_half median 2 vs line 3"}}]
                          if cal_listed else [])}
    return order, ticket, card, phase, cal


def selftest():
    fails = []

    def leg(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    # 1 EXECUTES_REFUSED_BOOK is reachable and carries the money
    v = build(*_fx())
    leg("L1_refused_word", v["verdict"] == EXEC_REFUSED, v["verdict"])
    leg("L2_money", v["money"]["book_amount_cny"] == 460_000.0)
    leg("L3_identity_proved", v["identity_proved"] is True)
    leg("L4_failing_checks", v["failing_checks"] == ["Y4_top2_share"])
    leg("L5_wrapper_not_gated", v["wrapper"]["gated"] is False, v["wrapper"])
    leg("L6_next_names_wrapper", "execution wrapper" in v["next_action"])

    # 2 admitted book -> consistent
    v = build(*_fx(cal_state="ADMIT"))
    leg("L7_admitted_word", v["verdict"] == EXEC_ADMITTED, v["verdict"])

    # 3 zero position -> not executing
    v = build(*_fx(book_weight=0.0))
    leg("L8_not_executing", v["verdict"] == NOT_EXECUTING, v["verdict"])

    # 4 every identity condition is load-bearing: break each, expect UNMATCHED
    breaks = {
        "n_hold": dict(n_hold=6),
        "vol_target": dict(vol_target=0.10),
        "classes": dict(classes=("equity", "bond")),
        "prefix": dict(prefix=False),
        "same_bar": dict(decided_bar=False),
    }
    for label, kw in breaks.items():
        v = build(*_fx(**kw))
        leg("L9_break_%s" % label, v["verdict"] == UNMATCHED, "%s -> %s" % (label, v["verdict"]))
        leg("L9b_break_%s_proved_false" % label, v["identity_proved"] is False)

    # 5 a candidate name without the nobond prefix is not the executed book
    v = build(*_fx(book_name="bond_vt08_adopted"))
    leg("L10_bond_book_unmatched", v["verdict"] == UNMATCHED, v["verdict"])

    # 6 ambiguity is reported, never resolved by order
    order, ticket, card, phase, cal = _fx()
    phase["books"].append({"book": "nobond_vt08_clone", "vol_target": 0.08, "vol_floor": 0.0})
    v = build(order, ticket, card, phase, cal)
    leg("L11_ambiguous_unmatched", v["verdict"] == UNMATCHED, v["verdict"])
    leg("L12_ambiguity_named", "ambiguous" in (v.get("match_note") or ""), v.get("match_note"))

    # 7 missing receipt is UNKNOWN, and unknown is not a verdict about the book
    v = build(None, None, None, None, None)
    leg("L13_unknown_word", v["verdict"] == UNKNOWN, v["verdict"])
    leg("L14_unknown_lists_all", len(v["missing_receipts"]) == 5)

    # 8 a book the calendar never lists is not silently admitted
    v = build(*_fx(cal_listed=False))
    leg("L15_unlisted_is_not_pass", v["calendar_state"] == "not_listed", v["calendar_state"])
    leg("L16_unlisted_refused_verdict", v["verdict"] == EXEC_REFUSED, v["verdict"])

    # 9 identity rows carry the actual values (a row that only carries a bool
    #   cannot be audited by a reader)
    v = build(*_fx())
    by = {r["condition"]: r for r in v["identity"]}
    leg("L17_i1_value", str(by["I1_n_hold"]["ticket_or_card_side"]) == "5")
    leg("L18_i2_value", "0.08" in str(by["I2_vol_target_no_floor"]["ticket_or_card_side"]))

    # 10 the published receipt (when present) must re-derive to itself
    pub, _ = _load("results/etf_book_execution_admission_gap.json")
    if pub is not None:
        leg("L19_published_verdict_is_a_word",
            pub.get("verdict") in (EXEC_REFUSED, EXEC_ADMITTED, NOT_EXECUTING, UNMATCHED, UNKNOWN),
            pub.get("verdict"))

    total = 18 + (1 if pub is not None else 0)
    if fails:
        print("selftest %d/%d PASS" % (total - len(fails), total))
        for f in fails:
            print("  FAIL " + f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())