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
OUT = os.path.join(ROOT, "results", "etf_book_decision_line.json")

TRIM_TOL = 2e-3  # per-leg prices and a sleeve-level target weight cannot agree to the bp


def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def derive(gap, cut, year):
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

    if conflicts:
        row["verdict"] = "CONFLICT_BETWEEN_RECEIPTS"
        row["sentence"] = "the receipts do not agree with each other; no size is quoted until they do"
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
    return {"verdict": row["verdict"], "missing": [], "conflicts": conflicts, "row": row}


def _published_body(obj):
    """Strip runtime metadata so two runs of the same receipts compare byte-for-byte."""
    return {k: v for k, v in obj.items() if k not in ("asof", "elapsed_sec")}


def cmd_run():
    t0 = datetime.now(timezone.utc)
    res = derive(_load(GAP), _load(CUT), _load(YEAR))
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
    fresh = derive(_load(GAP), _load(CUT), _load(YEAR))
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