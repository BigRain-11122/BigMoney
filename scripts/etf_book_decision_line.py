#!/usr/bin/env python3
"""The one line a desk needs on 2026-11-11: what size, and what the gate says about that size.

Every ingredient is already published by an earlier receipt.  This face reads them and
prints a single decision row; it does not re-price, re-judge, or re-run a book.

    results/etf_book_cut_order_gap.json              the ticket's k vs the permission, and the trim in lots
    results/etf_book_cut_gate_pass/CUT-GATE-PASS.json does obeying the permission move the calendar gate (three arms)
    results/etf_book_year_gate/YEAR-GATE.json         the book the desk actually holds

Three rules, all of them learned the hard way:
  * a number that appears in two receipts must agree here -- otherwise this face is RED, not
    "pick the newer one" (E289 / the two-copies family);
  * a missing receipt is UNKNOWN, never zero and never a pass (r98);
  * the same statistic measured on two panels must be printed with both denominators
    (E293: top-2 share of the overlay book vs the untargeted book are different objects).

Usage: python scripts/etf_book_decision_line.py [run|--check|selftest]
  run      derive the row and publish results/etf_book_decision_line.json
  --check  re-derive from the same receipts and compare with what was published (rc1 on drift)
  selftest offline legs on fixtures, no receipt files needed
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

CST = timezone(timedelta(hours=8))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP = os.path.join(ROOT, "results", "etf_book_cut_order_gap.json")
CUT = os.path.join(ROOT, "results", "etf_book_cut_gate_pass", "CUT-GATE-PASS.json")
YEAR = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
LATE = os.path.join(ROOT, "results", "etf_book_late_sheet_price.json")
DOW = os.path.join(ROOT, "results", "etf_book_do_or_wait.json")
OUT = os.path.join(ROOT, "results", "etf_book_decision_line.json")

HELD_ARM = "nobond_vt08"  # the arm the year gate holds; the late-sheet price is quoted for it

TRIM_TOL = 2e-3  # per-leg prices and a sleeve-level target weight cannot agree to the bp


def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def late_block(late):
    """The third price this line never carried: what it costs if today's sheet is filled
    tomorrow.  Read from the published face, never typed in (r1480 priced the policy,
    r1481 priced one sheet; this line only quotes it)."""
    if not late:
        return {"status": "UNKNOWN_MISSING_FACE"}
    arms = late.get("arms") or []
    a0 = next((a for a in arms if a.get("arm") == HELD_ARM), None) or (arms[0] if arms else None)
    if not a0:
        return {"status": "UNKNOWN_MISSING_FACE"}
    cny = a0.get("dist_cny") or {}
    bps = a0.get("dist_bps") or {}
    dcagr = [p.get("dcagr_pp") for p in (a0.get("phases") or []) if p.get("dcagr_pp") is not None]
    return {
        "status": "OK",
        "face": "results/etf_book_late_sheet_price.json",
        "arm": a0.get("arm"),
        "verdict": a0.get("verdict"),
        "capital_cny": late.get("capital_cny"),
        "events": bps.get("n"),
        "median_cny_one_sheet": cny.get("median"),
        "mean_bps_one_sheet": bps.get("mean"),
        "t": bps.get("t"),
        "share_late_helps": bps.get("share_late_helps"),
        "aggregate_pp_per_year": (sorted(dcagr)[len(dcagr) // 2] if dcagr else None),
        "note": "this is one sheet's price on the face's stated capital, not the "
                "aggregate arm; on this book the per-sheet prices add up to that arm exactly",
    }


def wait_block(dow):
    """The today-or-wait table, read from its own face (r1482).  It is not a second
    opinion: it is the trim's price plus the wait's price, both already published."""
    if not dow:
        return {"status": "UNKNOWN_MISSING_FACE"}
    dec = dow.get("decision") or {}
    if dec.get("verdict") in (None, "UNKNOWN_MISSING_LADDER", "UNKNOWN_MISSING_RECEIPT"):
        return {"status": "UNKNOWN", "verdict": dec.get("verdict")}
    return {
        "status": "OK",
        "face": "results/etf_book_do_or_wait.json",
        "verdict": dec.get("verdict"),
        "best_k": dec.get("best_k"),
        "today_cost_cny": dec.get("today_cost_cny"),
        "trim_owed": dec.get("trim_owed"),
        "table": dec.get("table"),
    }


def derive(gap, cut, year, late=None, dow=None):
    """Fold three receipts into one decision row.  Pure function of its inputs."""
    missing = [n for n, v in (("cut_order_gap", gap), ("cut_gate_pass", cut), ("year_gate", year)) if v is None]
    if missing:
        return {"verdict": "UNKNOWN_MISSING_RECEIPT", "missing": missing, "conflicts": [], "row": None}

    perm = gap.get("permitted_k")
    k_now = gap.get("k_now")
    trim = gap.get("trim") or {}
    cost = gap.get("cost") or {}
    cp = cut.get("permission") or {}
    flags = cut.get("flags") or {}

    conflicts = []
    if perm is not None and cp.get("permitted_k") is not None and abs(perm - cp["permitted_k"]) > 1e-9:
        conflicts.append("PERMITTED_K_DISAGREES %.6f vs %.6f" % (perm, cp["permitted_k"]))
    if k_now is not None and cp.get("k_now") is not None and abs(k_now - cp["k_now"]) > 1e-9:
        conflicts.append("K_NOW_DISAGREES %.6f vs %.6f" % (k_now, cp["k_now"]))
    if (gap.get("decision_date") or "") != (cp.get("decision_date") or ""):
        conflicts.append("DECISION_DATE_DISAGREES %s vs %s" % (gap.get("decision_date"), cp.get("decision_date")))

    k_after = trim.get("k_after_integer_lots")
    ordered = gap.get("ordered_book_cny")
    sold = trim.get("sold_cny")
    nav = gap.get("nav_cny")
    if None not in (k_after, ordered, sold, nav) and nav:
        implied = (ordered - sold) / nav
        if abs(implied - k_after) > TRIM_TOL:
            conflicts.append("TRIM_MATH_INCONSISTENT implied %.6f vs published %.6f" % (implied, k_after))
    if k_after is not None and perm is not None and k_after > perm:
        conflicts.append("TRIM_DOES_NOT_REACH_PERMISSION %.6f > %.6f" % (k_after, perm))

    if flags.get("gate_flips") is True and cut.get("verdict") == "CUT_CHANGES_NO_VERDICT":
        conflicts.append("GATE_FLIP_FLAG_CONTRADICTS_VERDICT")

    books = {b.get("book"): b for b in (cut.get("books") or [])}
    own = {b.get("book"): b for b in (year.get("books") or [])}
    held = own.get("nobond_vt08_adopted") or {}
    no_cut = books.get("ticket_k_no_cut") or {}
    capped = books.get("permission_cap_applied_history") or {}
    impl = books.get("permission_cap_from_decision_date") or {}

    # Two panels, two denominators -- both printed on purpose (E293).
    hd = (held.get("year_metrics") or {})
    nd = (no_cut.get("year_metrics") or {})

    row = {
        "decision_date": gap.get("decision_date"),
        "evidence_cutoff": gap.get("evidence_cutoff"),
        "order_k": k_now,
        "permission_k": perm,
        "cut_k": gap.get("gap_k"),
        "size_cny": {
            "ordered": ordered,
            "permitted": gap.get("permitted_book_cny"),
            "refused": gap.get("cut_cny"),
            "nav": nav,
        },
        "trim": {
            "lots": trim.get("lots_sell_total"),
            "cny": sold,
            "k_after": k_after,
            "legs": len(trim.get("legs") or []),
            "basis": trim.get("basis"),
        },
        "price_of_obeying": {
            "tx_cny_one_side": cost.get("tx_cny_one_side"),
            "carry_cny_per_year": cost.get("carry_cny_per_year"),
            "giveup_cny_per_year_ex_post": (cost.get("giveup_cny_per_year_ex_post") or {}).get("book_realized"),
        },
        "gate": {
            "held_book": held.get("book"),
            "held_verdict": held.get("verdict"),
            "held_top2_share": hd.get("top2_share"),
            "held_top2_share_full_years_only": hd.get("top2_share_full_only"),
            "held_note": "this is the overlay book the desk actually holds; the ticket arm below is a different object",
            "ticket_arm_verdict": no_cut.get("verdict"),
            "ticket_arm_top2_share": nd.get("top2_share"),
            "ticket_arm_top2_share_full_years_only": nd.get("top2_share_full_only"),
            "capped_arm_verdict": capped.get("verdict"),
            "capped_arm_top2_share": (capped.get("year_metrics") or {}).get("top2_share"),
            "implementable_arm_verdict": impl.get("verdict"),
            "cap_binding_share": flags.get("cap_binding_share"),
            "gate_flips": flags.get("gate_flips"),
            "top2_share_delta_pp": (cut.get("deltas") or {}).get("top2_share_pp"),
            "cagr_delta_pp": (cut.get("deltas") or {}).get("cagr"),
        },
        "verdict": None,
        "sentence": None,
    }
    row["late_sheet"] = late_block(late)
    row["do_or_wait"] = wait_block(dow)

    if conflicts:
        row["verdict"] = "CONFLICT_BETWEEN_RECEIPTS"
        row["sentence"] = "the receipts do not agree with each other; no size is quoted until they do"
    elif not trim:
        # r1471: the sheet now sizes from the executed account, so a within-permission
        # ticket is a real state -- and it owes no cut at all, not a zero-lot cut.
        row["verdict"] = "NO_CUT_OWED"
        row["sentence"] = (
            "on %s the ticket orders k=%s under a permission of %s: no cut is owed, so the "
            "only question left is whether the next decision bar re-sizes over the floor "
            "(it does unless the same trim is applied there)"
            % (row["decision_date"],
               "%.6f" % (k_after if k_after is not None else k_now),
               None if perm is None else "%.6f" % perm))
    else:
        row["verdict"] = "SIZE_AT_THE_PERMISSION_THE_GATE_DOES_NOT_MOVE"
        row["sentence"] = (
            "on %s sell %s lots (CNY %s) from the %s-leg sleeve so it lands at k=%s under a permission of %s; "
            "the calendar gate reads %s -> %s, so obeying is free on the gate face and costs CNY %s one side "
            "plus CNY %s/yr of carry, against CNY %s/yr of foregone return"
            % (
                row["decision_date"],
                trim.get("lots_sell_total"),
                ("%.0f" % sold) if sold is not None else "?",
                row["trim"]["legs"],
                k_after,
                perm,
                no_cut.get("verdict"),
                capped.get("verdict"),
                ("%.2f" % cost.get("tx_cny_one_side")) if cost.get("tx_cny_one_side") is not None else "?",
                ("%.2f" % cost.get("carry_cny_per_year")) if cost.get("carry_cny_per_year") is not None else "?",
                ("%.2f" % (cost.get("giveup_cny_per_year_ex_post") or {}).get("book_realized"))
                if (cost.get("giveup_cny_per_year_ex_post") or {}).get("book_realized") is not None
                else "?",
            )
        )
    # the third price: a sheet filled one open late. Read from the published face; a
    # missing face is UNKNOWN and the sentence says so instead of quoting a zero.
    lb = row["late_sheet"]
    if lb.get("status") == "OK":
        toll = cost.get("tx_cny_one_side")
        ratio = (lb["median_cny_one_sheet"] / toll) if (toll and lb.get("median_cny_one_sheet") is not None) else None
        if ratio is not None:
            against = "%sx the trim's own %s CNY one-side toll" % ("%.0f" % ratio, "%.2f" % toll)
        else:
            against = ("and this sheet owes no trim at all, so being a day late is the only "
                       "price on it")
        row["sentence"] += (
            "; filling this sheet one open late costs about %s CNY of NAV on %s "
            "(median over %s sheets; waiting helped on %.0f%% of them, t=%s), %s"
            % ("{:,.0f}".format(abs(lb["median_cny_one_sheet"] or 0.0)),
               "{:,.0f}".format(lb["capital_cny"] or 0),
               lb.get("events"),
               100.0 * (lb.get("share_late_helps") or 0.0),
               ("%.2f" % lb["t"]) if lb.get("t") is not None else "n/a",
               against))
    else:
        row["sentence"] += "; the price of filling this sheet one open late is UNKNOWN (no late-sheet face)"
    # the one question a desk asks: today or tomorrow.  Read from the ladder face; a
    # missing face is UNKNOWN and says so instead of defaulting to "do it today".
    wb = row["do_or_wait"]
    if wb.get("status") == "OK":
        best = None
        for x in (wb.get("table") or []):
            if x.get("k") == wb.get("best_k"):
                best = x
                break
        row["sentence"] += (
            "; today-or-wait: %s%s"
            % (wb.get("verdict"),
               (" (cheapest at k=%s, %+.0f CNY vs today)" % (wb.get("best_k"), best["cost_cny_vs_today"])
                if best and best.get("cost_cny_vs_today") is not None else "")))
    else:
        row["sentence"] += "; today-or-wait: UNKNOWN (no ladder face)"
    return {"verdict": row["verdict"], "missing": [], "conflicts": conflicts, "row": row}


def _published_body(obj):
    """Strip runtime metadata so two runs of the same receipts compare byte-for-byte."""
    return {k: v for k, v in obj.items() if k not in ("asof", "elapsed_sec")}


def cmd_run():
    t0 = datetime.now(timezone.utc)
    res = derive(_load(GAP), _load(CUT), _load(YEAR), _load(LATE), _load(DOW))
    res["face"] = "etf_book_decision_line"
    res["asof"] = datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+0800")
    res["elapsed_sec"] = round((datetime.now(timezone.utc) - t0).total_seconds(), 2)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(res["verdict"])
    for c in res["conflicts"]:
        print("  CONFLICT", c)
    if res.get("row"):
        print("  " + res["row"]["sentence"])
    print("  -> " + OUT)
    return 0 if res["verdict"] != "CONFLICT_BETWEEN_RECEIPTS" else 1


def cmd_check():
    old = _load(OUT)
    if old is None:
        print("NO_PUBLISHED_FACE: run first")
        return 1
    fresh = derive(_load(GAP), _load(CUT), _load(YEAR), _load(LATE), _load(DOW))
    a, b = _published_body(old), dict(fresh)
    diffs = []
    for k in sorted(set(a) | set(b)):
        if k == "face":
            continue
        if a.get(k) != b.get(k):
            diffs.append(k)
    if diffs:
        print("CHECK_FAIL drift in: " + ", ".join(diffs))
        return 1
    print("CHECK_OK %d fields re-derived from the same receipts" % len([k for k in b if k != "face"]))
    return 0


# ---------------------------------------------------------------- fixtures
def _fixture(perm=0.393073, k_now=0.460253, k_after=0.392964, flips=False, cut_verdict="CUT_CHANGES_NO_VERDICT"):
    gap = {
        "decision_date": "2026-11-11",
        "evidence_cutoff": "2026-11-06",
        "k_now": k_now,
        "permitted_k": perm,
        "gap_k": round(k_now - perm, 6),
        "nav_cny": 1000000.0,
        "ordered_book_cny": 459796.0,
        "permitted_book_cny": 392616.0,
        "cut_cny": 67180.0,
        "trim": {
            "basis": "fixture",
            "legs": [{"symbol": "X"}],
            "lots_sell_total": 445,
            "sold_cny": 67289.1,
            "k_after_integer_lots": k_after,
        },
        "cost": {
            "tx_cny_one_side": 53.83,
            "carry_cny_per_year": 796.08,
            "giveup_cny_per_year_ex_post": {"book_realized": 7574.55},
        },
    }
    cut = {
        "permission": {"permitted_k": perm, "k_now": k_now, "decision_date": "2026-11-11"},
        "deltas": {"top2_share_pp": -2.87, "cagr": -0.68},
        "flags": {"cap_binding_share": 0.3203, "gate_flips": flips},
        "verdict": cut_verdict,
        "books": [
            {"book": "ticket_k_no_cut", "verdict": "ADMIT", "year_metrics": {"top2_share": 0.6752, "top2_share_full_only": 0.7757}},
            {"book": "permission_cap_applied_history", "verdict": "ADMIT", "year_metrics": {"top2_share": 0.6465, "top2_share_full_only": 0.7484}},
            {"book": "permission_cap_from_decision_date", "verdict": "ADMIT", "year_metrics": {"top2_share": 0.6752, "top2_share_full_only": 0.7757}},
        ],
    }
    year = {
        "books": [
            {"book": "nobond_vt08_adopted", "verdict": "CONDITIONAL", "year_metrics": {"top2_share": 0.7108, "top2_share_full_only": 0.7278}},
        ]
    }
    return gap, cut, year


def cmd_selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    g, c, y = _fixture()
    r = derive(g, c, y)
    leg("baseline verdict", r["verdict"] == "SIZE_AT_THE_PERMISSION_THE_GATE_DOES_NOT_MOVE")
    leg("baseline row quotes the trim", r["row"]["trim"]["lots"] == 445 and r["row"]["trim"]["cny"] == 67289.1)
    leg("baseline sentence carries the three prices",
        "53.83" in r["row"]["sentence"] and "796.08" in r["row"]["sentence"] and "7574.55" in r["row"]["sentence"])
    leg("both denominators printed",
        r["row"]["gate"]["held_top2_share"] == 0.7108 and r["row"]["gate"]["held_top2_share_full_years_only"] == 0.7278
        and r["row"]["gate"]["ticket_arm_top2_share"] == 0.6752)

    g2, c2, y2 = _fixture()
    c2["permission"]["permitted_k"] = 0.400000
    r2 = derive(g2, c2, y2)
    leg("two receipts disagree on k", r2["verdict"] == "CONFLICT_BETWEEN_RECEIPTS"
        and any(x.startswith("PERMITTED_K_DISAGREES") for x in r2["conflicts"]))

    g3, c3, y3 = _fixture()
    r3 = derive(g3, None, y3)
    leg("missing receipt is UNKNOWN not zero", r3["verdict"] == "UNKNOWN_MISSING_RECEIPT" and r3["row"] is None
        and r3["missing"] == ["cut_gate_pass"])

    g4, c4, y4 = _fixture(k_after=0.400000)
    r4 = derive(g4, c4, y4)
    leg("trim that does not reach the permission", r4["verdict"] == "CONFLICT_BETWEEN_RECEIPTS"
        and any(x.startswith("TRIM_DOES_NOT_REACH_PERMISSION") for x in r4["conflicts"]))

    g5, c5, y5 = _fixture(k_after=0.450000)  # maths does not close against ordered-sold
    r5 = derive(g5, c5, y5)
    leg("trim arithmetic must close", any(x.startswith("TRIM_MATH_INCONSISTENT") for x in r5["conflicts"]))

    g6, c6, y6 = _fixture(flips=True)
    r6 = derive(g6, c6, y6)
    leg("flip flag contradicting the verdict", any(x.startswith("GATE_FLIP_FLAG") for x in r6["conflicts"]))

    g7, c7, y7 = _fixture()
    c7["permission"]["decision_date"] = "2026-11-12"
    r7 = derive(g7, c7, y7)
    leg("decision date must agree", any(x.startswith("DECISION_DATE_DISAGREES") for x in r7["conflicts"]))

    g8, c8, y8 = _fixture()
    y8["books"] = [{"book": "some_other_book", "verdict": "ADMIT", "year_metrics": {}}]
    r8 = derive(g8, c8, y8)
    leg("held book absent from the year gate is visible",
        r8["row"]["gate"]["held_verdict"] is None and r8["verdict"] == "SIZE_AT_THE_PERMISSION_THE_GATE_DOES_NOT_MOVE")

    # the late-sheet price: quoted when the face exists, UNKNOWN (never zero) when it does not
    g9, c9, y9 = _fixture()
    late_face = {
        "capital_cny": 1000000.0,
        "arms": [{"arm": "nobond_vt08", "verdict": "MEAN_IS_PRICED_EACH_SHEET_IS_NOT",
                  "dist_cny": {"n": 415, "median": -932.0},
                  "dist_bps": {"n": 415, "mean": -12.2, "t": -4.61, "share_late_helps": 0.41},
                  "phases": [{"dcagr_pp": -1.87}, {"dcagr_pp": -2.30}, {"dcagr_pp": -0.68}]}],
    }
    r9 = derive(g9, c9, y9, late_face)
    lb = r9["row"]["late_sheet"]
    leg("late price is read off the face, not typed",
        lb["status"] == "OK" and lb["median_cny_one_sheet"] == -932.0 and lb["events"] == 415)
    leg("late price shows up in the sentence with its own noise",
        "932" in r9["row"]["sentence"] and "41%" in r9["row"]["sentence"] and "t=-4.61" in r9["row"]["sentence"])
    leg("late price is stated against what it is not",
        "17x the trim's own 53.83" in r9["row"]["sentence"])
    g9b, c9b, y9b = _fixture()
    g9b["cost"]["tx_cny_one_side"] = 0.0
    r9b = derive(g9b, c9b, y9b, late_face)
    leg("a sheet that owes no trim says so instead of a 0.00x ratio",
        "owes no trim at all" in r9b["row"]["sentence"] and "x the trim" not in r9b["row"]["sentence"])
    r10 = derive(g9, c9, y9, None)
    leg("missing late face is UNKNOWN, never a zero",
        r10["row"]["late_sheet"]["status"] == "UNKNOWN_MISSING_FACE"
        and "UNKNOWN" in r10["row"]["sentence"] and "0 CNY" not in r10["row"]["sentence"])

    # the today-or-wait table: quoted from its own face, UNKNOWN (never "do it today")
    # when that face is absent
    dow_face = {"decision": {"verdict": "DO_TODAY", "best_k": 1, "today_cost_cny": 53.28,
                             "trim_owed": True,
                             "table": [{"k": 1, "cost_cny_vs_today": 932.0}]}}
    r11 = derive(g9, c9, y9, late_face, dow_face)
    leg("today-or-wait is quoted from the ladder face",
        r11["row"]["do_or_wait"]["status"] == "OK"
        and r11["row"]["do_or_wait"]["verdict"] == "DO_TODAY"
        and "DO_TODAY" in r11["row"]["sentence"] and "k=1" in r11["row"]["sentence"])
    r12 = derive(g9, c9, y9, late_face, None)
    leg("missing ladder face is UNKNOWN, not 'do it today'",
        r12["row"]["do_or_wait"]["status"] == "UNKNOWN_MISSING_FACE"
        and "today-or-wait: UNKNOWN" in r12["row"]["sentence"])

    ok = all(x[1] for x in legs)
    for name, passed, note in legs:
        print(("PASS " if passed else "FAIL ") + name + ((" | " + note) if note else ""))
    print("selftest %d/%d" % (sum(1 for x in legs if x[1]), len(legs)))
    return 0 if ok else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(cmd_selftest())
    if cmd in ("--check", "check"):
        sys.exit(cmd_check())
    sys.exit(cmd_run())