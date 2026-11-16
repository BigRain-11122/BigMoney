#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the carry sleeve's vol target, read as an integer problem

WHY THIS FILE EXISTS
--------------------
r1777 re-read the desk ticket under the book's 8% vol target and printed the answer
the eye skips over: hedged to the discount, ONE IC lot carries 9.00% of a 1,000,000
CNY book (one IM lot 9.22%).  So the 8% budget -- 80,000 CNY of annual P&L vol --
cannot buy a single lot, and the ticket's four lots sit at 180%/193% of capital, i.e.
4.5x the budget.  That is not a rounding nuisance: "8% vol target" and "1,000,000 CNY
capital" are two numbers from two different rulers, and whichever one is taken as the
hard one decides the position from 4 lots down to zero.

This file does not re-derive volatility.  `results/idx_fut_carry_paper/SIZING.json`
already holds, per product and per arm, the annualised vol of one lot and the capital
one lot needs at the target; those two numbers are the whole input.  What was missing
is the question they answer only when you ask it as an integer:

  * a CAPITAL LADDER  -- k = 1..8 lots: the capital that puts k lots at the target,
    so a reader can see which rung the desk's 1,000,000 sits on (the answer is below
    the first rung);
  * a TARGET LADDER   -- k = 1..8 lots at the stated capital: the vol target k lots
    would actually produce, so "down to 9%" has a name and a size;
  * a GRID             -- capital x target, with the integer lot count in each cell;
  * and the same cell read three ways, because the sentence is ambiguous: a CEILING
    (vol <= target: floor), a POINT TARGET (nearest integer), or a REFERENCE (the
    drawdown-survival size the ticket already prints).  At 1,000,000 / 8% those three
    readings give 0, 1 and 4 lots -- the same sentence, three positions.

The output is a decision face, not a recommendation: each of the three roads carries
its own price tag (capital to add, vol to accept), and the face states which roads
exist.  Choosing among them is a specification change, and the face says so.

HONESTY NOTES
-------------
  * fractions of a lot are printed but never rounded into a position: a futures
    contract is not divisible, so `lots_float` is arithmetic and `lots_ceiling` is
    what could be held;
  * the hedged arm is the one read for the decision, because only it puts the discount
    on the P&L without index beta -- the unhedged arm's 45% per lot is mostly the
    index, and sizing that to an 8% budget is a statement about the index, not the
    sleeve (r1776's note);
  * the ticket's lots come from the LEDGER's own ticket line, not from this file's
    opinion, and the overrun is printed as a multiple of the budget with both operands
    named.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SIZING_PATH = os.path.join(ROOT, "results", "idx_fut_carry_paper", "SIZING.json")
LEDGER_PATH = os.path.join(ROOT, "results", "idx_fut_carry_paper", "LEDGER.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_capital_ladder.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_CAPITAL_LADDER.md")

CAPITAL_GRID = [1_000_000.0, 1_250_000.0, 1_500_000.0, 2_000_000.0, 3_000_000.0]
TARGET_GRID = [4.0, 6.0, 8.0, 9.0, 10.0, 12.0]
LADDER_MAX_K = 8
EPS = 1e-9

ARM_USED_FOR_DECISION = "hedged"


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
def lots_float(sigma_cny, capital, target_pct):
    """Fractional lots whose annualised vol equals `target_pct` of capital."""
    if not sigma_cny or sigma_cny <= 0:
        return 0.0
    return (target_pct / 100.0) * capital / sigma_cny


def lots_ceiling(sigma_cny, capital, target_pct):
    """Lots you may hold if the target is a HARD CAP (vol <= target)."""
    return int(math.floor(lots_float(sigma_cny, capital, target_pct) + EPS))


def lots_nearest(sigma_cny, capital, target_pct):
    """Lots if the target is the CLOSEST ACHIEVABLE reading (half up)."""
    return int(math.floor(lots_float(sigma_cny, capital, target_pct) + 0.5 + EPS))


def capital_for_lots(k, sigma_cny, target_pct):
    if target_pct <= 0:
        return None
    return k * sigma_cny / (target_pct / 100.0)


def target_for_lots(k, sigma_cny, capital):
    if not capital or capital <= 0:
        return None
    return k * sigma_cny / capital * 100.0


def _rel_close(a, b, tol=1e-5):
    """The sizing face publishes its vol rounded to two decimals and its per-cent
    figures to four, so an identity that holds up to that rounding has to be read
    relatively, not absolutely (9.2163 vs 9.216318 is the same number here)."""
    if a is None or b is None:
        return False
    if a == 0 and b == 0:
        return True
    return abs(a - b) <= tol * max(abs(a), abs(b))


# ---------------------------------------------------------------- the face
def build(sizing, ledger, capital_grid=None, target_grid=None):
    """Everything this face prints, from SIZING.json only (plus the ticket's lots)."""
    if not sizing or not (sizing.get("accounts") or {}):
        return None
    capital_grid = capital_grid or CAPITAL_GRID
    target_grid = target_grid or TARGET_GRID
    ledger_accounts = ((ledger or {}).get("accounts") or {})
    out = {
        "kind": "idx_fut_carry_capital_ladder",
        "evidence_cutoff": sizing.get("evidence_cutoff"),
        "source_face": "results/idx_fut_carry_paper/SIZING.json",
        "arm_used_for_decision": ARM_USED_FOR_DECISION,
        "capital_grid": capital_grid,
        "target_grid": target_grid,
        "accounts": {},
    }
    for prod in sorted((sizing.get("accounts") or {})):
        s = sizing["accounts"][prod] or {}
        h = s.get(ARM_USED_FOR_DECISION) or {}
        u = s.get("unhedged") or {}
        cap = s.get("capital_cny")
        tgt = s.get("target_pct")
        sig = h.get("ann_vol_per_lot_cny")
        if not (cap and tgt and sig):
            out["accounts"][prod] = {"status": "INCOMPLETE_SIZING"}
            continue
        budget = tgt / 100.0 * cap
        led_acct = ledger_accounts.get(prod) or {}
        ticket_lots = led_acct.get("lots")
        multif = led_acct.get("multiplier")

        grid = []
        for c in capital_grid:
            row = {"capital_cny": c,
                   "capital_multiple_of_book": round(c / cap, 4)}
            for g in target_grid:
                row["%g%%" % g] = lots_ceiling(sig, c, g)
            row["lots_float_at_book_target"] = round(lots_float(sig, c, tgt), 4)
            grid.append(row)

        cap_ladder = []
        tgt_ladder = []
        for k in range(1, LADDER_MAX_K + 1):
            need = capital_for_lots(k, sig, tgt)
            cap_ladder.append({
                "lots": k,
                "capital_needed_cny": round(need, 2),
                "delta_vs_book_capital_cny": round(need - cap, 2),
                "affordable_at_book_capital": lots_ceiling(sig, cap, tgt) >= k,
            })
            t_lots = target_for_lots(k, sig, cap)
            tgt_ladder.append({
                "lots": k,
                "target_needed_pct": round(t_lots, 4),
                "delta_vs_book_target_pp": round(t_lots - tgt, 4),
                "achievable_at_book_target": lots_ceiling(sig, cap, tgt) >= k,
            })

        readings = {
            "hard_cap_vol_le_target": lots_ceiling(sig, cap, tgt),
            "nearest_integer": lots_nearest(sig, cap, tgt),
            "reference_ticket_lots": ticket_lots,
        }
        distinct = len({v for v in readings.values() if v is not None})

        overrun = None
        if ticket_lots:
            overrun = {
                "ticket_lots": ticket_lots,
                "per_lot_vol_cny": round(sig, 2),
                "ticket_vol_cny": round(ticket_lots * sig, 2),
                "budget_cny": round(budget, 2),
                "multiple_of_budget": round(ticket_lots * sig / budget, 4),
                "ticket_vol_pct_of_capital": round(ticket_lots * sig / cap * 100.0, 4),
                "capital_the_ticket_needs_at_target": round(
                    capital_for_lots(ticket_lots, sig, tgt), 2),
            }

        one_lot_capital = h.get("capital_for_one_lot_at_target")
        one_lot_target = h.get("vol_pct_of_capital_per_lot")
        options = {
            "A_keep_target_raise_capital": {
                "target_pct": tgt,
                "capital_for_one_lot_cny": round(capital_for_lots(1, sig, tgt), 2),
                "capital_delta_for_one_lot_cny": round(
                    capital_for_lots(1, sig, tgt) - cap, 2),
                "capital_for_the_ticket_cny": (
                    round(capital_for_lots(ticket_lots, sig, tgt), 2)
                    if ticket_lots else None),
                "gives_lots": 1,
            },
            "B_keep_capital_lower_target": {
                "capital_cny": cap,
                "target_needed_pct_for_one_lot": round(target_for_lots(1, sig, cap), 4),
                "target_delta_pp_for_one_lot": round(
                    target_for_lots(1, sig, cap) - tgt, 4),
                "target_needed_pct_for_the_ticket": (
                    round(target_for_lots(ticket_lots, sig, cap), 4)
                    if ticket_lots else None),
                "gives_lots": 1,
            },
            "C_keep_both_no_trade": {
                "lots": lots_ceiling(sig, cap, tgt),
                "note": "the hard-cap reading of the stated target at the stated capital",
            },
        }

        if distinct > 1:
            verdict = "THE_RULER_DECIDES_THE_LOTS"
        else:
            verdict = "READINGS_AGREE"

        identity = None
        if one_lot_capital and one_lot_target:
            identity = {
                "one_lot_capital_matches_sizing_face": _rel_close(
                    one_lot_capital, capital_for_lots(1, sig, tgt)),
                "one_lot_target_matches_sizing_face": _rel_close(
                    one_lot_target, target_for_lots(1, sig, cap)),
            }

        out["accounts"][prod] = {
            "status": "ok",
            "capital_cny": cap,
            "target_pct": tgt,
            "budget_cny_at_target": round(budget, 2),
            "multiplier": multif,
            "per_lot_vol_cny_hedged": round(sig, 2),
            "per_lot_vol_cny_unhedged": (
                round(u.get("ann_vol_per_lot_cny"), 2)
                if u.get("ann_vol_per_lot_cny") else None),
            "lots_float_at_book": round(lots_float(sig, cap, tgt), 4),
            "readings": readings,
            "readings_distinct": distinct,
            "verdict": verdict,
            "capital_ladder": cap_ladder,
            "target_ladder": tgt_ladder,
            "grid": grid,
            "overrun": overrun,
            "options": options,
            "identity_vs_sizing_face": identity,
            "hedge_product": ((s.get("hedge") or {}).get("cheapest") or {}).get(
                "hedge_product"),
        }
    return out


# --------------------------------------------------------------------- report
def _fmt(v, nd=2):
    if v is None:
        return "--"
    return "{:,.{nd}f}".format(v, nd=nd)


def write_doc(face):
    a = (face.get("accounts") or {})
    prods = sorted(a)
    lines = []
    lines.append("# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer"
                 "\n")
    lines.append("evidence cutoff: **%s** | source: `%s` | generated %s\n"
                 % (face.get("evidence_cutoff") or "--", face.get("source_face"),
                    face.get("generated") or "--"))
    lines.append("One lot's annualised vol, hedged to the discount, is the whole input "
                 "here; the face does not re-derive it. ")
    lines.append("A fraction of a lot is printed as arithmetic and never as a position: "
                 "a futures contract is not divisible.\n")

    for prod in prods:
        d = a[prod]
        if d.get("status") != "ok":
            lines.append("## %s\n\n`%s` -- sizing face incomplete, nothing to read.\n"
                         % (prod, d.get("status")))
            continue
        cap, tgt = d["capital_cny"], d["target_pct"]
        sig = d["per_lot_vol_cny_hedged"]
        r = d["readings"]
        lines.append("## %s\n" % prod)
        lines.append("| capital | target | vol of 1 lot (hedged) | budget at target | "
                     "lots (fraction) |")
        lines.append("|---|---|---|---|---|")
        lines.append("| %s CNY | %g%% | %s CNY | %s CNY | %.4f |"
                     % (_fmt(cap, 0), tgt, _fmt(sig), _fmt(d["budget_cny_at_target"]),
                        d["lots_float_at_book"]))
        lines.append("")
        lines.append("**The same sentence, read three ways at this capital and target: "
                     "`%d` / `%d` / `%s` lots** (vol <= target / nearest integer / the "
                     "ticket's own size). Verdict: **%s**.\n"
                     % (r["hard_cap_vol_le_target"], r["nearest_integer"],
                        r["reference_ticket_lots"], d["verdict"]))
        ov = d.get("overrun")
        if ov:
            lines.append("The ticket's %d lot(s) carry %s CNY of annual vol against a "
                         "%s CNY budget -- **%sx the budget**, %.2f%% of capital; holding "
                         "them inside the target would take %s CNY of capital.\n"
                         % (ov["ticket_lots"], _fmt(ov["ticket_vol_cny"]),
                            _fmt(ov["budget_cny"]), ov["multiple_of_budget"],
                            ov["ticket_vol_pct_of_capital"],
                            _fmt(ov["capital_the_ticket_needs_at_target"], 0)))

        lines.append("### capital ladder (k lots at the stated target)\n")
        lines.append("| lots | capital needed (CNY) | vs the book's capital | affordable |")
        lines.append("|---|---|---|---|")
        for row in d["capital_ladder"]:
            lines.append("| %d | %s | %s%s | %s |"
                         % (row["lots"], _fmt(row["capital_needed_cny"], 0),
                            "+" if row["delta_vs_book_capital_cny"] > 0 else "",
                            _fmt(row["delta_vs_book_capital_cny"], 0),
                            "yes" if row["affordable_at_book_capital"] else "no"))
        lines.append("")

        lines.append("### target ladder (k lots at the stated capital)\n")
        lines.append("| lots | target that would be (%) | vs the stated target (pp) | "
                     "achievable |")
        lines.append("|---|---|---|---|")
        for row in d["target_ladder"]:
            lines.append("| %d | %.4f | %+.4f | %s |"
                         % (row["lots"], row["target_needed_pct"],
                            row["delta_vs_book_target_pp"],
                            "yes" if row["achievable_at_book_target"] else "no"))
        lines.append("")

        lines.append("### capital x target -> whole lots (vol <= target)\n")
        head = "| capital (CNY) | " + " | ".join("%g%%" % g for g in face["target_grid"]) \
               + " | lots at the book's %g%% (fraction) |" % tgt
        lines.append(head)
        lines.append("|---" * (len(face["target_grid"]) + 2) + "|")
        for row in d["grid"]:
            cells = " | ".join(str(row["%g%%" % g]) for g in face["target_grid"])
            lines.append("| %s | %s | %.4f |"
                         % (_fmt(row["capital_cny"], 0), cells,
                            row["lots_float_at_book_target"]))
        lines.append("")

        o = d["options"]
        lines.append("### the three roads, each with its price\n")
        lines.append("- **A keep %g%%, raise the capital**: 1 lot needs %s CNY "
                     "(+%s); the ticket's %s lot(s) need %s CNY."
                     % (tgt, _fmt(o["A_keep_target_raise_capital"]["capital_for_one_lot_cny"], 0),
                        _fmt(o["A_keep_target_raise_capital"]["capital_delta_for_one_lot_cny"], 0),
                        r["reference_ticket_lots"],
                        _fmt(o["A_keep_target_raise_capital"]["capital_for_the_ticket_cny"], 0)))
        lines.append("- **B keep %s CNY, lower the target**: 1 lot needs %.4f%% "
                     "(+%.4fpp); the ticket's %s lot(s) need %.4f%%."
                     % (_fmt(cap, 0),
                        o["B_keep_capital_lower_target"]["target_needed_pct_for_one_lot"],
                        o["B_keep_capital_lower_target"]["target_delta_pp_for_one_lot"],
                        r["reference_ticket_lots"],
                        o["B_keep_capital_lower_target"]["target_needed_pct_for_the_ticket"]
                        or float("nan")))
        lines.append("- **C keep both**: %d lot(s) -- the sleeve is not expressible at "
                     "this rung and simply does not trade.\n"
                     % o["C_keep_both_no_trade"]["lots"])
        lines.append("The three roads are not a preference ordering: A spends capital, B "
                     "spends risk, C spends the sleeve. Picking one changes the "
                     "specification (either the capital rung or the vol target), so this "
                     "face prints their prices and stops there.\n")

    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return DOC_PATH


def run(write=True):
    sizing = _load(SIZING_PATH)
    if not sizing:
        print("sizing face missing: %s" % SIZING_PATH)
        return 2
    ledger = _load(LEDGER_PATH)
    face = build(sizing, ledger)
    if not face:
        print("sizing face carries no accounts -- nothing to read")
        return 2
    if write:
        face["generated"] = _now()
        _dump(OUT_PATH, face)
        write_doc(face)
    ok = [p for p, d in (face["accounts"] or {}).items() if d.get("status") == "ok"]
    for p in sorted(ok):
        d = face["accounts"][p]
        r = d["readings"]
        print("%s: 1 lot = %s CNY/yr (%.4f%% of %s) | budget at %g%% = %s | "
              "readings %d/%d/%s -> %s"
              % (p, _fmt(d["per_lot_vol_cny_hedged"], 0),
                 d["per_lot_vol_cny_hedged"] / d["capital_cny"] * 100.0,
                 _fmt(d["capital_cny"], 0), d["target_pct"],
                 _fmt(d["budget_cny_at_target"], 0), r["hard_cap_vol_le_target"],
                 r["nearest_integer"], r["reference_ticket_lots"], d["verdict"]))
    if not ok:
        print("no account reached status=ok")
        return 2
    return 0


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


# --------------------------------------------------------------------- check
def check():
    """Re-derive the published face from SIZING.json and compare cell by cell.

    The numbers checked here all come from the sizing face on disk, so the check
    also asserts the identity that ties it to that face (one-lot capital and one-lot
    target), and cross-reads the ticket's lots from the LEDGER -- a second file --
    rather than from this face's own copy.
    """
    sizing = _load(SIZING_PATH)
    ledger = _load(LEDGER_PATH)
    face = _load(OUT_PATH)
    if not (sizing and face):
        print(json.dumps({"ok": False, "problems": ["sizing or face missing"]}))
        return 2
    fresh = build(sizing, ledger)
    problems = []
    for prod in sorted((fresh.get("accounts") or {})):
        f = face["accounts"].get(prod)
        n = fresh["accounts"][prod]
        if not f:
            problems.append("%s: absent from the published face" % prod)
            continue
        if f.get("status") != n.get("status"):
            problems.append("%s: status %s vs %s" % (prod, f.get("status"), n.get("status")))
            continue
        if n.get("status") != "ok":
            continue
        for key in ("capital_cny", "target_pct", "budget_cny_at_target",
                    "per_lot_vol_cny_hedged", "lots_float_at_book", "verdict",
                    "readings_distinct"):
            if f.get(key) != n.get(key):
                problems.append("%s: %s %r vs %r" % (prod, key, f.get(key), n.get(key)))
        if f.get("readings") != n.get("readings"):
            problems.append("%s: readings %r vs %r"
                            % (prod, f.get("readings"), n.get("readings")))
        if f.get("grid") != n.get("grid"):
            problems.append("%s: grid differs" % prod)
        if f.get("capital_ladder") != n.get("capital_ladder"):
            problems.append("%s: capital ladder differs" % prod)
        if f.get("target_ladder") != n.get("target_ladder"):
            problems.append("%s: target ladder differs" % prod)
        if f.get("options") != n.get("options"):
            problems.append("%s: options differ" % prod)
        if f.get("overrun") != n.get("overrun"):
            problems.append("%s: overrun differs" % prod)
        idn = f.get("identity_vs_sizing_face") or {}
        for k, v in idn.items():
            if not v:
                problems.append("%s: identity %s is false on the published face" % (prod, k))
        # cross-source: the ticket's lots must be the LEDGER's, not this face's opinion
        led_lots = (((ledger or {}).get("accounts") or {}).get(prod) or {}).get("lots")
        pub_lots = (f.get("readings") or {}).get("reference_ticket_lots")
        if led_lots != pub_lots:
            problems.append("%s: ticket lots %r vs ledger %r" % (prod, pub_lots, led_lots))
        # a hard-cap reading above the nearest reading is impossible
        rr = f.get("readings") or {}
        if rr.get("hard_cap_vol_le_target", 0) > rr.get("nearest_integer", 0):
            problems.append("%s: ceiling above nearest" % prod)
        # ladder monotonicity (capital needed grows with lots)
        cl = f.get("capital_ladder") or []
        for i in range(1, len(cl)):
            if cl[i]["capital_needed_cny"] <= cl[i - 1]["capital_needed_cny"]:
                problems.append("%s: capital ladder not increasing at k=%d"
                                % (prod, cl[i]["lots"]))
        tl = f.get("target_ladder") or []
        for i in range(1, len(tl)):
            if tl[i]["target_needed_pct"] <= tl[i - 1]["target_needed_pct"]:
                problems.append("%s: target ladder not increasing at k=%d"
                                % (prod, tl[i]["lots"]))
        if not idn:
            problems.append("%s: face carries no identity block to check" % prod)
    print(json.dumps({"ok": not problems, "problems": problems,
                      "accounts": sorted((face.get("accounts") or {}))}, ensure_ascii=False))
    return 0 if not problems else 1


def show():
    face = _load(OUT_PATH)
    if not face:
        print("no face on disk: %s" % OUT_PATH)
        return 2
    for prod in sorted((face.get("accounts") or {})):
        d = face["accounts"][prod]
        if d.get("status") != "ok":
            print("%s: %s" % (prod, d.get("status")))
            continue
        r = d["readings"]
        print("%s cap=%s target=%g%% sig=%s readings=%d/%d/%s verdict=%s"
              % (prod, _fmt(d["capital_cny"], 0), d["target_pct"],
                 _fmt(d["per_lot_vol_cny_hedged"], 0), r["hard_cap_vol_le_target"],
                 r["nearest_integer"], r["reference_ticket_lots"], d["verdict"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []
    checks = []

    def chk(name, cond, extra=""):
        checks.append(name)
        if not cond:
            fails.append("%s%s" % (name, (" -- " + extra) if extra else ""))

    # L1 a target that divides the budget exactly buys one lot, not zero
    chk("L1 exact budget buys one lot",
        lots_ceiling(80_000.0, 1_000_000.0, 8.0) == 1)
    # L2 budget just short of one lot's vol buys none under a hard cap
    chk("L2 sidebar ceiling is zero", lots_ceiling(90_001.0, 1_000_000.0, 8.0) == 0)
    # L3 ... but the nearest reading is one, which is why the sentence is ambiguous
    chk("L3 nearest rounds up", lots_nearest(90_001.0, 1_000_000.0, 8.0) == 1)
    # L4 the two ladders invert each other: the capital that buys k lots at the target,
    # read back through target_for_lots, must be that same target again
    sig, cap, tgt = 90_001.0, 1_000_000.0, 8.0
    chk("L4 capital ladder inverts target ladder",
        abs(target_for_lots(1, sig, capital_for_lots(1, sig, tgt)) - tgt) < 1e-9)
    # L5 a ladder is increasing in lots
    chk("L5 capital ladder increasing",
        capital_for_lots(2, sig, tgt) > capital_for_lots(1, sig, tgt))
    # L6 floating dust does not lose a whole lot
    chk("L6 dust tolerance", lots_ceiling(80_000.0000001, 1_000_000.0, 8.0) == 1)

    # a synthetic sizing face in the shape the real one has
    def sizing_face(sig_=90_001.0, cap_=1_000_000.0, tgt_=8.0):
        return {
            "kind": "idx_fut_carry_paper_sizing",
            "evidence_cutoff": "2026-11-16",
            "target_pct": tgt_,
            "accounts": {
                "IC": {
                    "status": "ok",
                    "capital_cny": cap_,
                    "target_pct": tgt_,
                    "hedged": {
                        "ann_vol_per_lot_cny": sig_,
                        "capital_for_one_lot_at_target": capital_for_lots(1, sig_, tgt_),
                        "vol_pct_of_capital_per_lot": target_for_lots(1, sig_, cap_),
                        "lots_float": lots_float(sig_, cap_, tgt_),
                    },
                    "unhedged": {"ann_vol_per_lot_cny": 450_208.26},
                    "hedge": {"cheapest": {"hedge_product": "IF"}},
                }
            },
        }

    led = {"accounts": {"IC": {"lots": 4, "multiplier": 200}}}
    face = build(sizing_face(), led)
    d = face["accounts"]["IC"]
    chk("L7 three readings differ", d["readings_distinct"] == 3)
    chk("L8 verdict names the ruler", d["verdict"] == "THE_RULER_DECIDES_THE_LOTS")
    chk("L9 overrun is a multiple of the budget",
        abs(d["overrun"]["multiple_of_budget"] - 4 * 90_001.0 / 80_000.0) < 1e-4)
    chk("L10 option A one-lot capital equals the ladder",
        abs(d["options"]["A_keep_target_raise_capital"]["capital_for_one_lot_cny"]
            - d["capital_ladder"][0]["capital_needed_cny"]) < 1e-6)
    chk("L11 option B one-lot target equals the target ladder",
        abs(d["options"]["B_keep_capital_lower_target"]["target_needed_pct_for_one_lot"]
            - d["target_ladder"][0]["target_needed_pct"]) < 1e-6)
    chk("L12 grid cell agrees with the ceiling",
        all(row["8%"] == lots_ceiling(90_001.0, row["capital_cny"], 8.0)
            for row in d["grid"]))
    chk("L13 identity block is true on a coherent face",
        all((d["identity_vs_sizing_face"] or {}).values()))
    # L14 the face follows the target it is handed instead of a hard-coded 8
    face10 = build(sizing_face(tgt_=10.0), led)
    d10 = face10["accounts"]["IC"]
    chk("L14 target is read, not hard-coded",
        d10["target_pct"] == 10.0 and d10["readings"]["nearest_integer"] == 1
        and d10["budget_cny_at_target"] == 100_000.0)
    # L15 a coherent face (exactly one lot) reports the readings agreeing
    coherent = build(sizing_face(sig_=80_000.0), {"accounts": {"IC": {"lots": 1}}})
    chk("L15 agreeing readings are named",
        coherent["accounts"]["IC"]["verdict"] == "READINGS_AGREE")
    # L16 no ticket -> no overrun, and the face still reads
    no_ticket = build(sizing_face(), {"accounts": {"IC": {"lots": 0}}})
    chk("L16 no ticket prints no overrun",
        no_ticket["accounts"]["IC"]["overrun"] is None)
    # L17 a missing sizing face is refused, not defaulted
    chk("L17 missing sizing refused", build(None, led) is None)
    # L18 unhedged per-lot vol is carried through untouched (two arms, two trades)
    chk("L18 unhedged arm carried",
        abs(d["per_lot_vol_cny_unhedged"] - 450_208.26) < 1e-6)
    # L19 the hard-cap reading never exceeds the nearest reading on any grid cell
    chk("L19 ceiling <= nearest everywhere",
        all(row["%g%%" % g] <= lots_nearest(90_001.0, row["capital_cny"], g)
            for row in d["grid"] for g in face["target_grid"]))
    # L20 an incomplete sizing account is not silently published as ok
    broken = sizing_face()
    del broken["accounts"]["IC"]["hedged"]
    chk("L20 incomplete sizing is labelled",
        build(broken, led)["accounts"]["IC"]["status"] == "INCOMPLETE_SIZING")

    print("idx_fut_carry_capital_ladder selftest %d/%d PASS%s"
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
