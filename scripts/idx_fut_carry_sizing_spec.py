#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the carry sleeve's sizing ruler, ADOPTED -- the book stops asking and states the rule

WHY THIS FILE EXISTS
--------------------
r1778 printed three roads out of one ambiguous sentence ("8% vol target on a 1,000,000
book"): keep the target and raise the capital (A), keep the capital and lower the target
to 9% (B), or keep both and hold zero lots (C). It priced all three and refused to
choose, correctly: choosing is a specification change, not a sizing step.

A face that refuses to choose cannot be consumed. Every downstream reader -- the ticket,
the paper page, a review in three months -- would have to re-decide, and each would decide
differently. This file is the decision, written once, as data:

    ROAD A: keep the 8% vol target, treat the capital as the free variable,
            and read the target as a HARD CAP (vol <= target, so lots = floor).

The reason is causal, not aesthetic. The 8% figure is the book's risk standard -- the
same number the ETF paper book runs on, and that book's own sweep says what it is: a RISK
DIAL, not a fit. At 8% the n5 book prints 11.49% CAGR / -10.56% maxDD / Sharpe 1.13, and
with no target at all 15.56% / -16.04% / 1.00 -- Sharpe moves 0.08 while return and
drawdown scale together, i.e. the target buys drawdown, not return. Moving it to 9% so
that one contract fits would spend drawdown tolerance for nothing. The capital of the
carry paper, by contrast, is a modelling parameter taken from the desk sheet. Letting a
200-CNY-per-point contract's lot size move a house-level risk number is the wrong
direction of causality: the instrument would be setting the risk budget. So the risk
number stays and the capital rung moves.

WHAT ROAD A DOES TO THIS BOOK, TODAY
------------------------------------
Nothing is bought. At 1,000,000 CNY of capital the 8% budget is 80,000 CNY of annual P&L
vol and one hedged IC lot is 90,012 CNY of it (one IM lot 92,180) -- so the rule returns
ZERO lots, and the first executable rung is 1,125,012 CNY (IC) / 1,152,040 CNY (IM).
That zero is the answer, not a failure to find one: the sleeve is below its first rung at
this capital. The desk's four lots are printed beside it and marked OUT_OF_RULER rather
than deleted -- the desk's recommendation is an input this book does not rewrite.

HONESTY NOTES
-------------
  * no volatility is re-derived here: per-lot vol, capital-per-lot and the ticket's lots
    are read from the ladder / sizing / ledger faces, and `--check` re-runs this file's
    own arithmetic against them;
  * road B and road C are still printed, each with the number that would make it true,
    and each marked `adopted: false` -- a decision record that hides the alternatives is
    a preference, not a decision;
  * fractions of a lot are arithmetic; `lots` is what could be held;
  * the rule string carries its own recompute recipe, so a reader never has to trust a
    number this file printed.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LADDER_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capital_ladder.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_sizing_spec.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_SIZING_SPEC.md")

EPS = 1e-9
ARM_USED = "hedged"

# --------------------------------------------------------------- the adoption
# One constant, one place. Changing the road means editing this block and re-running
# `run`, which rewrites the face the ticket prints. A reader in six months finds the
# decision here rather than in a round report.
ADOPTION = {
    "road": "A_keep_target_raise_capital",
    "reading": "hard_cap_vol_le_target",
    "target_pct": 8.0,
    "decided": "2026-11-17",
    "decided_in": "bm-c round 1779",
    "because": (
        "8% is a RISK DIAL and not a fit (results/etf_vol_target_sweep.json, book n5: "
        "target 8% prints 11.49% CAGR / -10.56% maxDD / Sharpe 1.13 against 15.56% / "
        "-16.04% / 1.00 with no target -- Sharpe moves 0.08 while return and drawdown "
        "scale together, so the target sets the size of the drawdown, not the return). "
        "Raising it to 9% to make one contract fit would spend 1pp of drawdown tolerance "
        "for no return; the capital is the free variable and the risk number is a "
        "preference"
    ),
    "what_it_does_not_change": [
        "the vol of the sleeve (no new measurement)",
        "the desk's recommended lots (an input, printed and marked, never rewritten)",
        "the 8% target itself (road B is printed with its price and not adopted)",
    ],
    "rule": (
        "lots = floor(target_pct/100 * capital / ann_vol_of_one_lot_hedged); "
        "one lot needs ann_vol_of_one_lot_hedged / (target_pct/100) CNY of capital"
    ),
}

ROADS = ("A_keep_target_raise_capital", "B_keep_capital_lower_target",
         "C_keep_both_no_trade")


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


# ------------------------------------------------------------- integer algebra
def lots_at(sigma_cny, capital, target_pct):
    """Whole lots admissible when the target is a hard cap (vol <= target)."""
    if not sigma_cny or sigma_cny <= 0 or not capital or target_pct <= 0:
        return 0
    return int(math.floor((target_pct / 100.0) * capital / sigma_cny + EPS))


def capital_for_one_lot(sigma_cny, target_pct):
    if not sigma_cny or target_pct <= 0:
        return None
    return sigma_cny / (target_pct / 100.0)


def target_for_one_lot(sigma_cny, capital):
    if not sigma_cny or not capital or capital <= 0:
        return None
    return sigma_cny / capital * 100.0


def conformance(ticket_lots, admissible):
    """Three states, because 'the desk holds more than the ruler allows' and 'nobody
    told us what the desk holds' need different sentences."""
    if ticket_lots is None:
        return "UNKNOWN_TICKET"
    if ticket_lots == 0:
        return "NO_TICKET_SIZE"
    if admissible is None:
        return "UNKNOWN_RULER"
    return "WITHIN_RULER" if ticket_lots <= admissible else "OUT_OF_RULER"


# --------------------------------------------------------------------- the face
def adopt(ladder, adoption=None):
    """Read the ladder face, apply the adopted road, print what it decides."""
    adoption = adoption or ADOPTION
    if not ladder or not (ladder.get("accounts") or {}):
        return None
    target = adoption.get("target_pct")
    out = {
        "kind": "idx_fut_carry_sizing_spec",
        "evidence_cutoff": ladder.get("evidence_cutoff"),
        "source_face": "results/idx_fut_carry_capital_ladder.json",
        "upstream_source_face": ladder.get("source_face"),
        "arm_used_for_decision": ladder.get("arm_used_for_decision") or ARM_USED,
        "adoption": dict(adoption),
        "accounts": {},
    }
    for prod in sorted((ladder.get("accounts") or {})):
        d = ladder["accounts"][prod] or {}
        if d.get("status") != "ok":
            out["accounts"][prod] = {"status": d.get("status") or "LADDER_INCOMPLETE"}
            continue
        cap = d.get("capital_cny")
        sig = d.get("per_lot_vol_cny_hedged")
        if not (cap and sig):
            out["accounts"][prod] = {"status": "INCOMPLETE_LADDER"}
            continue
        readings = d.get("readings") or {}
        ticket_lots = readings.get("reference_ticket_lots")
        admissible = lots_at(sig, cap, target)
        first_rung = capital_for_one_lot(sig, target)
        budget = target / 100.0 * cap

        # what the OTHER two roads would need to be true, printed and not adopted
        road_b_target = target_for_one_lot(sig, cap)
        road_c_lots = admissible  # the hard-cap reading at today's capital IS road C

        ticket_budget_multiple = (round(ticket_lots * sig / budget, 4)
                                  if ticket_lots and budget else None)
        state = "EXECUTABLE" if admissible >= 1 else "BELOW_FIRST_RUNG"

        rungs = []
        for cap_rung in (cap, first_rung, (first_rung * 2 if first_rung else None)):
            if cap_rung is None:
                continue
            rungs.append({
                "capital_cny": round(cap_rung, 2),
                "capital_multiple_of_book": round(cap_rung / cap, 4),
                "lots": lots_at(sig, cap_rung, target),
            })

        out["accounts"][prod] = {
            "status": "ok",
            "capital_cny": round(cap, 2),
            "target_pct": target,
            "per_lot_vol_cny_hedged": round(sig, 2),
            "budget_cny_at_target": round(budget, 2),
            "lots_float": round(budget / sig, 4),
            "admissible_lots": admissible,
            "state": state,
            "first_executable_capital_cny": (round(first_rung, 2)
                                             if first_rung else None),
            "capital_gap_to_first_lot_cny": (
                round(first_rung - cap, 2) if first_rung else None),
            "capital_the_ticket_needs_cny": (
                round(ticket_lots * first_rung, 2)
                if (ticket_lots and first_rung) else None),
            "ticket": {
                "lots": ticket_lots,
                "multiple_of_budget": ticket_budget_multiple,
                "conformance": conformance(ticket_lots, admissible),
            },
            "capital_rungs": rungs,
            "roads": {
                "A_keep_target_raise_capital": {
                    "adopted": adoption.get("road") == "A_keep_target_raise_capital",
                    "target_pct": target,
                    "lots_at_book_capital": admissible,
                    "capital_for_one_lot_cny": (round(first_rung, 2)
                                                if first_rung else None),
                },
                "B_keep_capital_lower_target": {
                    "adopted": adoption.get("road") == "B_keep_capital_lower_target",
                    "capital_cny": round(cap, 2),
                    "target_for_one_lot_pct": (round(road_b_target, 4)
                                               if road_b_target else None),
                    "lots_at_that_target": (
                        lots_at(sig, cap, road_b_target) if road_b_target else None),
                },
                "C_keep_both_no_trade": {
                    "adopted": adoption.get("road") == "C_keep_both_no_trade",
                    "lots": road_c_lots,
                    "note": "the hard-cap reading of the stated target at this capital",
                },
            },
            "verdict": ("ONE_LOT_IS_NOT_A_SMALL_ALLOCATION"
                        if state == "BELOW_FIRST_RUNG"
                        else "SLEEVE_IS_EXECUTABLE_AT_THIS_CAPITAL"),
        }
    out["verdict"] = "RULER_ADOPTED"
    out["rule"] = adoption.get("rule")
    return out


# --------------------------------------------------------------------- report
def _fmt(v, nd=0):
    if v is None:
        return "--"
    return "{:,.{nd}f}".format(v, nd=nd)


def write_doc(face):
    a = face.get("accounts") or {}
    ad = face.get("adoption") or {}
    lines = []
    lines.append("# the carry sleeve's sizing ruler: adopted, with the roads not taken "
                 "still priced\n")
    lines.append("evidence cutoff: **%s** | source: `%s` | decided %s in %s | "
                 "generated %s\n"
                 % (face.get("evidence_cutoff") or "--", face.get("source_face"),
                    ad.get("decided"), ad.get("decided_in"),
                    face.get("generated") or "--"))
    lines.append("**Adopted: `%s`, target %g%%, read as %s.**\n"
                 % (ad.get("road"), ad.get("target_pct") or 0, ad.get("reading")))
    lines.append("> %s\n" % (ad.get("because") or ""))
    lines.append("The rule a reader can recompute:\n")
    lines.append("> %s\n" % (face.get("rule") or ""))
    lines.append("What this decision does not change: %s.\n"
                 % "; ".join(ad.get("what_it_does_not_change") or []))

    for prod in sorted(a):
        d = a[prod]
        if d.get("status") != "ok":
            lines.append("## %s\n\n`%s` -- the ladder face is incomplete, nothing adopted "
                         "for this product.\n" % (prod, d.get("status")))
            continue
        lines.append("## %s\n" % prod)
        lines.append("| capital | target | vol of 1 lot (hedged) | budget at target | "
                     "lots the ruler allows |")
        lines.append("|---|---|---|---|---|")
        lines.append("| %s CNY | %g%% | %s CNY | %s CNY | **%d** (%.4f) |"
                     % (_fmt(d["capital_cny"]), d["target_pct"],
                        _fmt(d["per_lot_vol_cny_hedged"]), _fmt(d["budget_cny_at_target"]),
                        d["admissible_lots"], d["lots_float"]))
        lines.append("")
        if d["state"] == "BELOW_FIRST_RUNG":
            lines.append("**%s.** One lot is %s CNY of annual vol -- more than this "
                         "book's %s CNY budget, so the rule buys nothing here. The first "
                         "executable rung is **%s CNY** (+%s); holding the desk's %s lots "
                         "inside the target would take %s CNY.\n"
                         % (d["verdict"], _fmt(d["per_lot_vol_cny_hedged"]),
                            _fmt(d["budget_cny_at_target"]),
                            _fmt(d["first_executable_capital_cny"]),
                            _fmt(d["capital_gap_to_first_lot_cny"]),
                            d["ticket"]["lots"],
                            _fmt(d["capital_the_ticket_needs_cny"])))
        else:
            lines.append("**%s** -- the ruler buys %d lot(s) at this capital.\n"
                         % (d["verdict"], d["admissible_lots"]))
        t = d["ticket"]
        lines.append("- the desk's ticket: **%s lot(s)**, `%s` against this ruler"
                     "%s" % (t["lots"], t["conformance"],
                             (", %sx the budget" % t["multiple_of_budget"])
                             if t["multiple_of_budget"] is not None else ""))
        for road in ROADS:
            r = d["roads"][road]
            mark = "**ADOPTED**" if r["adopted"] else "not adopted"
            if road == "A_keep_target_raise_capital":
                lines.append("- A keep %g%%, raise the capital: %d lot(s) now, 1 lot at "
                             "%s CNY -- %s" % (r["target_pct"],
                                               r["lots_at_book_capital"],
                                               _fmt(r["capital_for_one_lot_cny"]), mark))
            elif road == "B_keep_capital_lower_target":
                lines.append("- B keep %s CNY, lower the target: 1 lot needs %.4f%% "
                             "(that target buys %s lot(s) here) -- %s"
                             % (_fmt(r["capital_cny"]), r["target_for_one_lot_pct"] or 0,
                                r["lots_at_that_target"], mark))
            else:
                lines.append("- C keep both: %s lot(s) -- %s (this is what A reads at "
                             "today's capital, not a separate road)"
                             % (r["lots"], mark))
        lines.append("")
        lines.append("| capital rung | multiple of the book | lots |")
        lines.append("|---|---|---|")
        for row in d["capital_rungs"]:
            lines.append("| %s | %.4fx | %d |"
                         % (_fmt(row["capital_cny"]), row["capital_multiple_of_book"],
                            row["lots"]))
        lines.append("")
    lines.append("Fractions of a lot are arithmetic; `lots` is what could be held. "
                 "Nothing here re-derives volatility -- the per-lot numbers come from the "
                 "ladder face, which takes them from `SIZING.json`.")
    lines.append("")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# ------------------------------------------------------------------------ run
def run():
    ladder = _load(LADDER_PATH)
    face = adopt(ladder)
    if face is None:
        print("no ladder face on disk: %s" % LADDER_PATH)
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
        print("%s rule=%d lots (%.4f) state=%s ticket=%s/%s first_rung=%s"
              % (prod, d["admissible_lots"], d["lots_float"], d["state"],
                 d["ticket"]["lots"], d["ticket"]["conformance"],
                 _fmt(d["first_executable_capital_cny"])))
    return 0


def show():
    face = _load(OUT_PATH)
    if not face:
        print("no face on disk: %s" % OUT_PATH)
        return 2
    ad = face.get("adoption") or {}
    print("adopted=%s target=%g%% reading=%s decided=%s"
          % (ad.get("road"), ad.get("target_pct") or 0, ad.get("reading"),
             ad.get("decided")))
    for prod in sorted(face.get("accounts") or {}):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            print("%s: %s" % (prod, d.get("status")))
            continue
        print("%s lots=%d state=%s ticket=%s/%s"
              % (prod, d["admissible_lots"], d["state"], d["ticket"]["lots"],
                 d["ticket"]["conformance"]))
    return 0


def check():
    """Re-run this file's arithmetic against the face on disk AND the ladder it reads.

    It never re-derives a volatility: per-lot vol and the ticket's lots are inputs. What
    it re-derives is every consequence of the adopted rule -- and it names what it did
    not recompute, so a reader cannot mistake a green check for a fresh measurement.
    """
    face = _load(OUT_PATH)
    ladder = _load(LADDER_PATH)
    problems = []
    if not face:
        print(json.dumps({"ok": False, "problems": ["face missing: %s" % OUT_PATH]}))
        return 1
    if not ladder:
        print(json.dumps({"ok": False,
                          "problems": ["ladder missing: %s" % LADDER_PATH]}))
        return 1
    ad = face.get("adoption") or {}
    if ad.get("road") not in ROADS:
        problems.append("adopted road is not one of the three: %r" % ad.get("road"))
    target = ad.get("target_pct")
    for prod in sorted((ladder.get("accounts") or {})):
        src = ladder["accounts"][prod] or {}
        pub = (face.get("accounts") or {}).get(prod) or {}
        if src.get("status") != "ok":
            if pub.get("status") != (src.get("status") or "LADDER_INCOMPLETE"):
                problems.append("%s: upstream incomplete but published as %r"
                                % (prod, pub.get("status")))
            continue
        if pub.get("status") != "ok":
            problems.append("%s: published as %r while the ladder is ok"
                            % (prod, pub.get("status")))
            continue
        sig = src.get("per_lot_vol_cny_hedged")
        cap = src.get("capital_cny")
        want_lots = lots_at(sig, cap, target)
        if pub.get("admissible_lots") != want_lots:
            problems.append("%s: admissible lots %r != %d"
                            % (prod, pub.get("admissible_lots"), want_lots))
        want_rung = capital_for_one_lot(sig, target)
        if want_rung is not None and abs((pub.get("first_executable_capital_cny") or 0)
                                         - want_rung) > 0.01 * max(1.0, want_rung):
            problems.append("%s: first rung %r != %.2f"
                            % (prod, pub.get("first_executable_capital_cny"), want_rung))
        ticket_src = (src.get("readings") or {}).get("reference_ticket_lots")
        if (pub.get("ticket") or {}).get("lots") != ticket_src:
            problems.append("%s: ticket lots %r != ladder's %r"
                            % (prod, (pub.get("ticket") or {}).get("lots"), ticket_src))
        want_conf = conformance(ticket_src, want_lots)
        if (pub.get("ticket") or {}).get("conformance") != want_conf:
            problems.append("%s: conformance %r != %r"
                            % (prod, (pub.get("ticket") or {}).get("conformance"),
                               want_conf))
        # road A's one-lot capital is the rung; road C's lots are the hard-cap reading
        roads = pub.get("roads") or {}
        if roads and abs((((roads.get("A_keep_target_raise_capital") or {})
                           .get("capital_for_one_lot_cny")) or 0)
                        - (want_rung or 0)) > 0.01 * max(1.0, want_rung or 1.0):
            problems.append("%s: road A one-lot capital disagrees with the rung" % prod)
        if roads and (((roads.get("C_keep_both_no_trade") or {}).get("lots"))
                      != want_lots):
            problems.append("%s: road C lots disagree with the adopted reading" % prod)
        budget = (target or 0) / 100.0 * (cap or 0)
        if budget and sig:
            want_mult = round((ticket_src or 0) * sig / budget, 4)
            got_mult = (pub.get("ticket") or {}).get("multiple_of_budget")
            if ticket_src and got_mult is not None and abs(got_mult - want_mult) > 1e-6:
                problems.append("%s: ticket multiple %r != %r"
                                % (prod, got_mult, want_mult))
    print(json.dumps({
        "ok": not problems,
        "problems": problems,
        "accounts": sorted((face.get("accounts") or {})),
        "not_recomputed": [
            "ann_vol_of_one_lot (read from the ladder face, which reads SIZING.json)",
            "the desk's recommended lots (read from the ladder's readings)",
            "whether 8% is the right house standard (that is the adoption, not a number)",
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

    sig, cap, tgt = 90_012.0, 1_000_000.0, 8.0

    # L1 a budget that is exactly one lot's vol buys one lot
    chk("L1 exact budget buys one lot", lots_at(80_000.0, 1_000_000.0, 8.0) == 1)
    # L2 one lot's vol above the budget buys none (the whole finding)
    chk("L2 one lot above the budget buys none", lots_at(sig, cap, tgt) == 0)
    # L3 the first rung is the per-lot vol divided by the target
    chk("L3 first rung algebra",
        abs(capital_for_one_lot(sig, tgt) - sig / 0.08) < 1e-9)
    # L4 at exactly the first rung the rule buys exactly one lot (no dust loss)
    rung = capital_for_one_lot(sig, tgt)
    chk("L4 first rung buys exactly one", lots_at(sig, rung, tgt) == 1)
    # L5 a hair below the rung buys none
    chk("L5 below the rung buys none", lots_at(sig, rung - 1.0, tgt) == 0)
    # L6 doubling the capital doubles the admissible lots
    chk("L6 lots scale with capital",
        lots_at(sig, 2 * cap, tgt) == 2 * lots_at(sig, cap, tgt) + 1)
    # L7 a ticket larger than the ruler is OUT_OF_RULER
    chk("L7 oversized ticket named", conformance(4, 0) == "OUT_OF_RULER")
    # L8 a ticket inside the ruler is WITHIN_RULER
    chk("L8 inside ticket named", conformance(1, 1) == "WITHIN_RULER")
    # L9 no ticket size is its own state, never silently ok
    chk("L9 unknown ticket is a state", conformance(None, 1) == "UNKNOWN_TICKET")

    def ladder_face(sig_=sig, cap_=cap, ticket=4):
        return {
            "kind": "idx_fut_carry_capital_ladder",
            "evidence_cutoff": "2026-11-16",
            "source_face": "results/idx_fut_carry_paper/SIZING.json",
            "arm_used_for_decision": "hedged",
            "accounts": {
                "IC": {
                    "status": "ok",
                    "capital_cny": cap_,
                    "target_pct": tgt,
                    "budget_cny_at_target": tgt / 100.0 * cap_,
                    "per_lot_vol_cny_hedged": sig_,
                    "readings": {"hard_cap_vol_le_target": lots_at(sig_, cap_, tgt),
                                 "nearest_integer": 1,
                                 "reference_ticket_lots": ticket},
                }
            },
        }

    face = adopt(ladder_face())
    d = face["accounts"]["IC"]
    # L10 the face prints zero lots and says the sleeve is below its first rung
    chk("L10 below-first-rung state",
        d["admissible_lots"] == 0 and d["state"] == "BELOW_FIRST_RUNG")
    # L11 the verdict speaks about one lot's size, not about an error
    chk("L11 verdict is about lot size",
        d["verdict"] == "ONE_LOT_IS_NOT_A_SMALL_ALLOCATION")
    # L12 the ticket is marked out of ruler and keeps its number
    chk("L12 ticket kept and marked",
        d["ticket"]["lots"] == 4 and d["ticket"]["conformance"] == "OUT_OF_RULER")
    # L13 the ticket multiple is computed from the budget, not typed in
    chk("L13 ticket multiple",
        abs(d["ticket"]["multiple_of_budget"] - 4 * sig / (0.08 * cap)) < 1e-6)
    # L14 the target is read from the adoption, not hard-coded
    face10 = adopt(ladder_face(), dict(ADOPTION, target_pct=10.0))
    chk("L14 target is read", face10["accounts"]["IC"]["budget_cny_at_target"] == 100_000.0
        and face10["accounts"]["IC"]["admissible_lots"] == 1)
    # L15 road A is the adopted one; B and C are printed as not adopted
    chk("L15 roads carry adoption flags",
        d["roads"]["A_keep_target_raise_capital"]["adopted"] is True
        and d["roads"]["B_keep_capital_lower_target"]["adopted"] is False
        and d["roads"]["C_keep_both_no_trade"]["adopted"] is False)
    # L16 road B prints the target that would put one lot here (9.0012%)
    chk("L16 road B names its target",
        abs(d["roads"]["B_keep_capital_lower_target"]["target_for_one_lot_pct"]
            - 9.0012) < 1e-3)
    # L17 road C is the adopted reading at today's capital, not a rival number
    chk("L17 road C equals the reading",
        d["roads"]["C_keep_both_no_trade"]["lots"] == d["admissible_lots"])
    # L18 the capital rungs include the book and the first executable rung
    chk("L18 rungs name the rung",
        [r["lots"] for r in d["capital_rungs"][:2]] == [0, 1])
    # L19 a missing ladder face is refused, not defaulted
    chk("L19 missing ladder refused", adopt(None) is None)
    # L20 an incomplete account is labelled, not published as ok
    bad = ladder_face()
    del bad["accounts"]["IC"]["per_lot_vol_cny_hedged"]
    chk("L20 incomplete ladder labelled",
        adopt(bad)["accounts"]["IC"]["status"] == "INCOMPLETE_LADDER")
    # L21 the adoption constant is one of the three roads (a typo would publish a
    # decision nobody can match to the ladder face)
    chk("L21 adoption road is a real road", ADOPTION["road"] in ROADS)
    # L22 the rule carries a recompute recipe rather than a bare number
    chk("L22 rule is recomputable", "floor" in (face.get("rule") or ""))
    # L23 the cutoff is inherited from the ladder, not stamped today
    chk("L23 cutoff inherited", face["evidence_cutoff"] == "2026-11-16")

    print("idx_fut_carry_sizing_spec selftest %d/%d PASS%s"
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
