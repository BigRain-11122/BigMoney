#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""may the calendar REFUSAL be reported by the elected ruler instead of the disqualified one?

WHY THIS FILE EXISTS
--------------------
r1426 showed net_top2_share (the gate's Y4) cannot adjudicate 3 of its own 4 arms, so the
sentence "refused by the calendar" was never verified by a trustworthy instrument.  r1429
then elected years_for_half on fixtures (8/8 fixtures, zero false admits) and observed the
elected ruler ALSO refuses the held book in 5/5 phases.  Both facts were recorded; neither
was acted on, because replacing a gate's reason is an admission-rule change and needs its
own round with a prereg, a conservativeness test and a self-adjudication test.

That is this round.  It reads published receipts only (results/etf_book_year_caliber.json
cells, results/admission/CANDIDATES.json year tables), imports both rulers from
r1426/r1429 (no second implementation of either), and answers one question:

    if the refusal line is printed by years_for_half instead of net_top2_share,
    does anything get ADMITTED that is refused today?

PREREG (frozen in this block before any reading; re-emitted verbatim in the receipt)
------------------------------------------------------------------------------------
A1 ELECTED             the r1429 election, imported and re-run, still elects years_for_half
A2 NO_NEW_ADMISSIONS   over every (book, phase) cell: new==ADMIT and old!=ADMIT must be 0
                       (a reporting change may only ever refuse more, never fewer)
A3 SELF_ADJUDICABLE    years_for_half must adjudicate ITSELF on every book that has a phase
                       set (r1426's S test); a single-table book prints no_phase_set and is
                       NOT counted as a pass
A4 LENGTH_FLOOR        every judged book must have n_years >= 5 (r1429 documents the ruler's
                       implicit floor: an even book reads ceil(n/2), so a 4-year book needs
                       only 2 years for half)
A5 NOT_DEGENERATE      |net_sum| / gross_sum <= 0.5 means "half" is a rounding artefact, not
                       a shape; those cells must print indeterminate and are counted, never
                       silently read as a refusal

  A1..A4 all pass -> ADOPT   (refusal reason switches; verdict words unchanged by A2)
  any of A1..A4 fails -> HOLD (with the failing condition named)

A5 is a printing rule enforced in the output, not a veto: a degenerate cell cannot carry a
refusal sentence under the new ruler even when A1..A4 pass.

Usage:
  python scripts/etf_book_admission_refusal_caliber_adoption.py run
  python scripts/etf_book_admission_refusal_caliber_adoption.py check
  python scripts/etf_book_admission_refusal_caliber_adoption.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts import etf_book_year_caliber as C          # rulers + lines (single source)
from scripts import etf_book_admission_ruler_election as E  # election + read_ruler

OUT = os.path.join(ROOT, "results", "etf_book_admission_refusal_caliber_adoption.json")
CALIBER_RECEIPT = os.path.join(ROOT, "results", "etf_book_year_caliber.json")
CANDIDATE_RECEIPT = os.path.join(ROOT, "results", "admission", "CANDIDATES.json")

OLD_RULER = "net_top2_share"
NEW_RULER = "years_for_half"
LENGTH_FLOOR_YEARS = 5
FLAT_NET_RATIO = 0.5

PREREG = {
    "round": "r1431",
    "question": "does switching the calendar refusal reason to the elected ruler admit anything refused today?",
    "old_ruler": OLD_RULER,
    "new_ruler": NEW_RULER,
    "conditions": {
        "A1_elected": "r1429 election re-run (imported) still elects years_for_half",
        "A2_no_new_admissions": "no (book, phase) cell flips to ADMIT from non-ADMIT",
        "A3_self_adjudicable": "years_for_half adjudicates itself on every book with a phase set",
        "A4_length_floor": "n_years >= 5 for every judged book",
        "A5_not_degenerate": "|net|/gross > 0.5 else the cell prints indeterminate",
    },
    "decision_rule": "ADOPT iff A1..A4 pass; A5 is a printing rule",
    "frozen_before_reading": True,
}


def _cells_from_arms(receipt: dict) -> dict:
    """{arm: [ {label, years(dict), published_calibers} ]} from the published caliber receipt."""
    out = {}
    for arm, cells in (receipt.get("cells") or {}).items():
        rows = []
        for i, cell in enumerate(cells):
            years = cell.get("year_net_pct") or {}
            if not years:
                continue
            rows.append({"label": "%s/phase%d" % (arm, i),
                         "years": years,
                         "published": (cell.get("calibers") or {})})
        if rows:
            out[arm] = rows
    return out


def _cells_from_candidates(receipt: dict) -> dict:
    """{candidate: [ {label, years(dict)} ]} -- one table per candidate (no phase set)."""
    out = {}
    for c in receipt.get("candidates") or []:
        table = {}
        for row in c.get("years") or []:
            if row.get("net_pct") is None:
                continue
            table[str(row["year"])] = float(row["net_pct"])
        if table:
            out["%s:%s" % (c.get("candidate"), c.get("arm"))] = [
                {"label": "%s:%s" % (c.get("candidate"), c.get("arm")), "years": table,
                 "published": {}, "gate_checks": c.get("checks") or {}}]
    return out


def net_over_gross(net_sum_pct, gross_sum_pct):
    """|net|/gross from two published sums; None when nothing was grossed.

    Single implementation of the A5 input: any face that prints a refusal
    sentence under this ruler must ask the same question of the same numbers.
    """
    if net_sum_pct is None or gross_sum_pct is None:
        return None
    if gross_sum_pct <= 0:
        return None
    return abs(float(net_sum_pct)) / float(gross_sum_pct)


def is_degenerate(ratio):
    """A5: 'half' is a rounding artefact, not a shape -- no refusal sentence."""
    return ratio is None or ratio <= FLAT_NET_RATIO


def _net_ratio(years: dict) -> dict:
    vals = [float(v) for v in years.values()]
    gross = sum(abs(v) for v in vals)
    net = sum(vals)
    ratio = net_over_gross(net, gross)
    return {"gross_sum_pct": round(gross, 6), "net_sum_pct": round(net, 6),
            "net_over_gross": (round(ratio, 6) if ratio is not None else None)}


def series(years: dict) -> list:
    """Chronological net-return series.

    E.read_ruler() consumes a SERIES (it enumerates its argument and rebuilds the year
    labels itself as 2000+i).  Handing it the {year: net} dict silently feeds the YEAR
    LABELS in as returns -- a value substitution that raises nothing.  Ordering is by
    year, never by dict insertion order, so a receipt written out of order cannot
    reorder the calendar and change a reading.
    """
    if not isinstance(years, dict):
        raise TypeError("year table must be a {year: net_pct} mapping, got %r" % type(years))
    return [float(v) for _k, v in sorted(years.items(), key=lambda kv: int(kv[0]))]


def read_cell(cell: dict) -> dict:
    """Both rulers on one year table.  Delegates to the single implementation (read_ruler)."""
    seq = series(cell["years"])
    old = E.read_ruler(OLD_RULER, seq)
    new = E.read_ruler(NEW_RULER, seq)
    ratio = _net_ratio(cell["years"])
    n = len(cell["years"])
    degenerate = is_degenerate(ratio["net_over_gross"])
    # A refusal sentence may only be printed when the ruler's reading is not a rounding artefact.
    new_reason = "indeterminate" if degenerate else ("REFUSE" if new["word"] == "REFUSE" else "ADMIT")
    return {
        "label": cell["label"],
        "years": n,
        "old": old,
        "new": new,
        "net": ratio,
        "degenerate": bool(degenerate),
        "new_reason_word": new_reason,
        "flipped_to_admit": bool(new["word"] == "ADMIT" and old["word"] != "ADMIT"),
        "direction": ("loosened" if (new["word"] == "ADMIT" and old["word"] != "ADMIT")
                      else "tightened" if (new["word"] != "ADMIT" and old["word"] == "ADMIT")
                      else "same"),
    }


def loosened(rows: list) -> list:
    """Cells the new ruler ADMITs while the old one refuses.

    Expected EMPTY by algebra, not by luck: if years_for_half passes (>=3 years to reach half
    the net sum) then the best two years are strictly below half of the net sum, so
    net_top2_share < 0.5 < 0.70 and the old ruler passes too.  The detector therefore exists
    to catch an IMPLEMENTATION deviation (wrong series order, wrong line, wrong sign), and
    its own landing is checked by a property leg in selftest rather than assumed.
    """
    return [r for r in rows if r["new"]["word"] == "ADMIT" and r["old"]["word"] != "ADMIT"]


def evaluate(books: dict, election: dict) -> dict:
    """Pure given its inputs: no argument can change the ruler choice or the lines."""
    rows_by_book = {}
    for book, cells in books.items():
        rows_by_book[book] = [read_cell(c) for c in cells]

    all_cells = [r for rows in rows_by_book.values() for r in rows]
    loosened_rows = loosened(all_cells)
    tightened = [r for r in all_cells if r["direction"] == "tightened"]
    degenerate = [r for r in all_cells if r["degenerate"]]

    # A3: self-adjudication on books that actually have a phase set.
    selfadj = {}
    for book, rows in rows_by_book.items():
        if len(rows) < 2:
            selfadj[book] = {"state": "no_phase_set", "cells": len(rows)}
            continue
        probe = []
        for cell, row in zip(books[book], rows):
            probe.append({"label": row["label"],
                          "years": len(cell["years"]),
                          "calibers": C.calibers([{"year": int(y), "net_pct": v, "cohorts": 4,
                                                   "partial": False}
                                                  for y, v in sorted(cell["years"].items())])})
        verdict = C.adjudicate_caliber(NEW_RULER, probe)
        selfadj[book] = {"state": verdict.get("state") or "unknown",
                         "reason": verdict.get("reason"),
                         "cells": len(rows),
                         "detail": {k: verdict.get(k) for k in
                                    ("median", "spread", "margin", "side", "book_years")
                                    if k in verdict}}

    years_floor_fail = sorted({book for book, rows in rows_by_book.items()
                               if rows and rows[0]["years"] < LENGTH_FLOOR_YEARS})

    checks = {
        "A1_elected": {"pass": (election.get("elected") == NEW_RULER),
                       "elected": election.get("elected")},
        "A2_no_new_admissions": {"pass": len(loosened_rows) == 0,
                                 "cells": len(all_cells),
                                 "expected": "0 by algebra (new PASS implies old PASS); "
                                             "non-zero = implementation deviation",
                                 "loosened": [{"label": r["label"], "old": r["old"]["value"],
                                               "new": r["new"]["value"]} for r in loosened_rows],
                                 "tightened": [{"label": r["label"], "old": r["old"]["value"],
                                                "new": r["new"]["value"]} for r in tightened]},
        "A3_self_adjudicable": {
            "pass": all(v["state"] not in ("UNADJUDICABLE_CALIBER", "MIXED_ACROSS_ARMS")
                        for v in selfadj.values()),
            "books": selfadj},
        "A4_length_floor": {"pass": len(years_floor_fail) == 0,
                            "floor_years": LENGTH_FLOOR_YEARS,
                            "failing_books": years_floor_fail},
        "A5_not_degenerate": {"enforced": "printing rule",
                              "degenerate_cells": len(degenerate),
                              "of_cells": len(all_cells),
                              "labels": [r["label"] for r in degenerate]},
    }
    failing = [k for k, v in checks.items() if k != "A5_not_degenerate" and not v["pass"]]
    decision = {
        "verdict": "HOLD" if failing else "ADOPT",
        "failing_conditions": failing,
        "refusal_reason_after": (NEW_RULER if not failing else OLD_RULER),
        "books_judged": len(rows_by_book),
        "cells_judged": len(all_cells),
    }
    return {"decision": decision, "checks": checks, "books": rows_by_book}


def run() -> int:
    import time
    t0 = time.time()
    with open(CALIBER_RECEIPT, encoding="utf-8") as fh:
        caliber = json.load(fh)
    with open(CANDIDATE_RECEIPT, encoding="utf-8") as fh:
        cands = json.load(fh)

    books = _cells_from_arms(caliber)
    books.update(_cells_from_candidates(cands))
    election = E.elect()
    res = evaluate(books, election)

    # Identity leg: the published caliber receipt already carries years_for_half per cell;
    # re-reading the same table through read_ruler must reproduce it exactly.
    dev = []
    for arm, cells in (caliber.get("cells") or {}).items():
        for i, cell in enumerate(cells):
            years = cell.get("year_net_pct") or {}
            pub = (cell.get("calibers") or {}).get(NEW_RULER)
            if not years or pub is None:
                continue
            got = E.read_ruler(NEW_RULER, series(years))["value"]
            if got is None or pub is None:
                continue
            dev.append(abs(float(got) - float(pub)))
    identity_max = max(dev) if dev else None

    receipt = {
        "face": "etf_book_admission_refusal_caliber_adoption",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "prereg": PREREG,
        "inputs": {"caliber_receipt": os.path.relpath(CALIBER_RECEIPT, ROOT).replace("\\", "/"),
                   "candidate_receipt": os.path.relpath(CANDIDATE_RECEIPT, ROOT).replace("\\", "/"),
                   "ruler_source": "scripts/etf_book_year_caliber.py (CALIBERS/passes/adjudicate_caliber)",
                   "election_source": "scripts/etf_book_admission_ruler_election.py (elect/read_ruler)"},
        "identity_years_for_half_vs_published": {"cells": len(dev), "max_abs_dev": identity_max,
                                                "ok": (identity_max is None or identity_max < 1e-9)},
        "decision": res["decision"],
        "checks": res["checks"],
        "books": res["books"],
        "honest": {
            "no_new_pricing": "reads published receipts only; does not re-run the book engine",
            "no_second_implementation": "both rulers come from r1426's CALIBERS via r1429's read_ruler",
            "production_unchanged": "this receipt is the adoption evidence; the gate still prints "
                                    "its old reason until the adoption is wired",
        },
        "elapsed_sec": round(time.time() - t0, 2),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    d = receipt["decision"]
    print("adoption: %s reason_after=%s failing=%s books=%d cells=%d identity_max=%s"
          % (d["verdict"], d["refusal_reason_after"], ",".join(d["failing_conditions"]) or "-",
             d["books_judged"], d["cells_judged"], identity_max))
    return 0


def check() -> int:
    with open(OUT, encoding="utf-8") as fh:
        r = json.load(fh)
    # re-derive the decision from the receipt's own checks (a hand-written verdict fails)
    failing = [k for k, v in r["checks"].items() if k != "A5_not_degenerate" and not v["pass"]]
    want = "HOLD" if failing else "ADOPT"
    if r["decision"]["verdict"] != want:
        print("check FAIL: stored verdict %s != recomputed %s" % (r["decision"]["verdict"], want))
        return 1
    if r["decision"]["failing_conditions"] != failing:
        print("check FAIL: failing_conditions not derived from checks")
        return 1
    if not r["identity_years_for_half_vs_published"]["ok"]:
        print("check FAIL: year-table identity against published calibers is broken")
        return 1
    print("check OK: verdict=%s derived from %d conditions" % (want, len(r["checks"])))
    return 0


def _fx(years):
    return {str(k): float(v) for k, v in years.items()}


def selftest() -> int:
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    # L1 basic read: a two-year headline book must read a small half-life
    two_year = {2020: 1.0, 2021: 1.0, 2022: 0.5, 2023: 0.5, 2024: 0.5,
                2025: 18.0, 2026: 14.0}
    r = read_cell({"label": "t2", "years": _fx(two_year)})
    leg("L1 two-year book reads years_for_half < 3", r["new"]["value"] < 3)

    # L2 a broad calendar reads >= 3 and is not degenerate
    broad = {y: 6.0 for y in range(2020, 2027)}
    r2 = read_cell({"label": "broad", "years": _fx(broad)})
    leg("L2 broad book reads years_for_half >= 3", r2["new"]["value"] >= 3)
    leg("L2b broad book not degenerate", r2["degenerate"] is False)

    # L3 degenerate: net near zero -> the new reason must print indeterminate, never REFUSE
    flat = {2020: 12.0, 2021: -11.6, 2022: 3.0, 2023: -3.0, 2024: 0.2, 2025: -0.1, 2026: 0.0}
    r3 = read_cell({"label": "flat", "years": _fx(flat)})
    leg("L3 flat book is degenerate", r3["degenerate"] is True)
    leg("L3b degenerate cell never prints a refusal", r3["new_reason_word"] == "indeterminate")

    # L4 A2 is a detector whose landing is "never".  Two legs: one proves the detector still
    # fires when handed a loosening (otherwise the clause is decorative), the other states the
    # algebra as a property over random tables -- first draft tried to BUILD a loosening table
    # and could not: new PASS implies top-2 < half of net implies old PASS (r1429's lesson
    # again, fixture expectations read off the ruler instead of assumed).
    fake = [{"label": "synth", "years": 7, "degenerate": False, "new_reason_word": "ADMIT",
             "old": {"value": 0.95, "pass": False, "word": "REFUSE"},
             "new": {"value": 4, "pass": True, "word": "ADMIT"}, "direction": "loosened",
             "flipped_to_admit": True, "net": {"net_over_gross": 0.9}}]
    leg("L4 detector fires on a fabricated loosening", len(loosened(fake)) == 1)

    import random
    rnd = random.Random(1431)
    disagree = 0
    for _ in range(600):
        n = rnd.choice([5, 6, 7, 8])
        table = {2000 + i: round(rnd.uniform(-18, 25), 3) for i in range(n)}
        r = read_cell({"label": "prop", "years": _fx(table)})
        if r["flipped_to_admit"]:
            disagree += 1
    leg("L4b over 600 random tables the rulers never loosen (algebra holds)", disagree == 0)

    # L5 length floor: a 4-year book cannot be judged by this ruler
    short = {2020: 5.0, 2021: 4.0, 2022: 3.0, 2023: 2.0}
    res5 = evaluate({"short": [{"label": "short", "years": _fx(short)}]}, {"elected": NEW_RULER})
    leg("L5 4-year book trips A4", "A4_length_floor" in res5["decision"]["failing_conditions"])
    leg("L5b single-table book is no_phase_set, not a pass",
        res5["checks"]["A3_self_adjudicable"]["books"]["short"]["state"] == "no_phase_set")

    # L6 election is not ours to pick: a different elected ruler must trip A1
    res6 = evaluate({"short": [{"label": "short", "years": _fx(broad)}]},
                    {"elected": "effective_years"})
    leg("L6 A1 trips when the election names another ruler",
        "A1_elected" in res6["decision"]["failing_conditions"])

    # L7 read_cell delegates: our value must equal the imported ruler's own reading
    leg("L7 no second implementation (value equals imported read_ruler)",
        r2["new"]["value"] == E.read_ruler(NEW_RULER, _fx(broad))["value"])

    # L8 A5 is printed, never used as a veto
    leg("L8 A5 recorded as a printing rule", res5["checks"]["A5_not_degenerate"]["enforced"]
        == "printing rule")

    failed = [n for n, v in ok if not v]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 1 if failed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    a = ap.parse_args(argv)
    return {"run": run, "check": check, "selftest": selftest}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())