#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2112 bm-c -- triage the hazards that Tools/page_fmt_guard.py just found, and
ask the question the guard cannot ask about itself: is it safe to wire in yet?

Under r1789 a leg that is red on correct code is worse than no leg: readers learn
to skip it.  So before the guard becomes a chain/smoke leg, its hits get sorted.

Reads results/_r2112bmc_page_fmt_guard.scan.json (the guard's own output, produced
with --json so the shared results/page_fmt_guard.scan.json is left to its owner),
classifies every hazard, and writes results/_r2112bmc_page_fmt_guard_triage.json.

Classification is deliberately mechanical (no model calls, no network):
  REAL_SYNTAX_DEFECT        a file in the tree does not compile
  FALSE_DETECTOR_LITERAL    the string IS the defect detector ("%%" in page / assert ...)
  FALSE_MAPPING_FMT         "%(name)s" mapping formats -- valid printf, guard blind spot
  FALSE_VARIABLE_TEMPLATE   built into a variable, %-applied later -- guard blind spot
  TRUE_PAGE_DEFECT          read by eye: this literal reaches the page
  UNVERIFIED                not read this round (printed, never assumed clean)
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCAN = os.path.join(HERE, "_r2112bmc_page_fmt_guard.scan.json")
OUT = os.path.join(HERE, "_r2112bmc_page_fmt_guard_triage.json")

# --- verdicts established by reading the source in this round -----------------
TRUE_PAGE_DEFECT = {
    ("scripts/idx_fut_carry_capital.py", 406),        # lines.append("| ... 净 %%/yr |")   no % op
    ("scripts/idx_fut_roll_gap.py", 498),             # L.append("| ... sum %%/yr |")      no % op
    ("scripts/idx_fut_carry_impact_decay.py", 458),   # L.append("| ... 占 ADV%%/日 |")     no % op
}
FALSE_VARIABLE_TEMPLATE = {
    ("scripts/regime_cap_breach_cash_vs_repo.py", 483),        # head = "...实际%%...";  head % primary
    ("scripts/idx_fut_carry_drawdown_experience.py", 468),     # ("%.1f%%") tuple template, applied later
}
FALSE_DETECTOR_LITERAL = {
    ("scripts/money_subband_jump_audit.py", 1136),   # bad.append("page prints a literal %% ...")
    ("scripts/cash_leg_shelf_decision.py", 606),     # same idiom
}

WIRING = {
    "recommendation": "DO_NOT_WIRE_YET",
    "because": (
        "on the hits read this round the guard is roughly half right: the three page "
        "literals it found are real (a reader sees '%%/yr' in a table header), but it also "
        "flags every defect-detector literal in the tree and every mapping/indirect format "
        "string. A leg wired today would be red on correct code, and r1789 says a leg that "
        "is always red trains readers to skip it."
    ),
    "three_cheap_fixes": [
        "skip a constant whose whole value is '%%' (it is the detector, not the defect)",
        "accept '%(name)[sdif]' as a valid conversion (mapping formats are legal printf)",
        "for containers, follow one assignment: if the name holding this literal is later "
        "used as '<name> % ...', treat the literal as formatted "
        "(the guard already handles the inline BinOp case)",
    ],
    "after_the_fixes": (
        "re-run the same scan; the residue should be genuine page prose, which is worth "
        "fixing at the source in the page writers rather than by another gate"
    ),
    "syntax_error_side_product": (
        "Tools/_r820bmc_close.py does not compile (unterminated string at line 130) -- "
        "independent py_compile confirms it, so it is not a guard artifact"
    ),
}


def classify(path, line, kind, snippet):
    if kind == "SYNTAX_ERROR":
        return "REAL_SYNTAX_DEFECT"
    key = (path, line)
    if key in TRUE_PAGE_DEFECT:
        return "TRUE_PAGE_DEFECT"
    if key in FALSE_VARIABLE_TEMPLATE:
        return "FALSE_VARIABLE_TEMPLATE"
    if key in FALSE_DETECTOR_LITERAL:
        return "FALSE_DETECTOR_LITERAL"
    s = (snippet or "").strip()
    if s == "%%":
        return "FALSE_DETECTOR_LITERAL"
    if "%(" in s:
        return "FALSE_MAPPING_FMT"
    return "UNVERIFIED"


def main():
    if not os.path.exists(SCAN):
        sys.stderr.write("missing %s -- run: python Tools/page_fmt_guard.py scan --json %s\n" % (SCAN, SCAN))
        return 2
    scan = json.load(io.open(SCAN, encoding="utf-8"))
    rows = []
    for h in scan.get("hazards") or []:
        verdict = classify(h.get("file", ""), h.get("line", 0), h.get("kind", ""), h.get("snippet"))
        rows.append({
            "file": h.get("file"),
            "line": h.get("line"),
            "kind": h.get("kind"),
            "where": h.get("where"),
            "snippet": (h.get("snippet") or "")[:120],
            "triage": verdict,
        })
    tally = {}
    for r in rows:
        tally[r["triage"]] = tally.get(r["triage"], 0) + 1
    read = sum(v for k, v in tally.items() if k != "UNVERIFIED")
    false_n = tally.get("FALSE_DETECTOR_LITERAL", 0) + tally.get("FALSE_MAPPING_FMT", 0) + tally.get("FALSE_VARIABLE_TEMPLATE", 0)
    true_n = tally.get("TRUE_PAGE_DEFECT", 0) + tally.get("REAL_SYNTAX_DEFECT", 0)
    out = {
        "schema": "page-fmt-guard-triage/v1",
        "kind": "page_fmt_guard_triage",
        "round": "r2112 bm-c",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "generated_by": "results/_r2112bmc_page_fmt_guard_triage.py",
        "source_scan": os.path.relpath(SCAN, ROOT).replace(os.sep, "/"),
        "source_scan_verdict": scan.get("verdict"),
        "source_scan_scope": scan.get("scope"),
        "wiring_gap": {
            "guard": "Tools/page_fmt_guard.py",
            "references_outside_itself": 0,
            "checked_in": ["Tools/s6_chain_bmc.py", "Tools/s6_chain_bma.py", "smoke_test.py"],
            "meaning": "the guard exists and passes its own selftest 19/19, but nothing runs it, "
                       "so every hazard below is invisible every round (r1282 orphan-guard family)",
        },
        "counts": {"total": len(rows), "read_this_round": read, "unverified": tally.get("UNVERIFIED", 0),
                   "classified_false": false_n, "classified_true": true_n, "tally": tally},
        "wiring": WIRING,
        "hazards": sorted(rows, key=lambda r: (r["triage"], r["file"], r["line"])),
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("triage %d hazards -> %s" % (len(rows), os.path.relpath(OUT, ROOT)))
    print("  read this round: %d  (true %d / false %d)  unverified %d"
          % (read, true_n, false_n, tally.get("UNVERIFIED", 0)))
    for k in sorted(tally):
        print("  %-26s %d" % (k, tally[k]))
    print("  wiring: %s" % WIRING["recommendation"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
