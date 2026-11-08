"""Run just the E573 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e573_smoke_leg.py            # expect PASS
  python scripts/run_e573_smoke_leg.py --doctor   # flip one silent row by hand, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "silentchain_latest.json")
E568 = os.path.join(ROOT, "results", "state_tilt", "oldchaintable_latest.json")
SILENT = ("the_denominator_is_below_the_table_and_the_sentence_reads_as_the_whole_chain")
C_SILENT = "no_row_of_that_round_declares_a_subset"

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def _hide_one_declaration(doc):
    """Give a silent row a declaring sibling: the class must then be refused."""
    for r in doc.get("rows") or []:
        if r.get("class") == C_SILENT:
            r["sibling_rows"] = [{"line": 1, "declares_a_subset": True,
                                  "declaration": {"marker": "--only x", "chain_word": "legs"}}]
            return True
    return False


m = importlib.import_module("e573_silent_chain")
face = json.load(open(LATEST, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

if "--doctor" in sys.argv[1:]:
    doc = json.loads(json.dumps(face))
    if not _hide_one_declaration(doc):
        print("DOCTOR FAIL: the fixture offers no silent row to corrupt")
        sys.exit(1)
    problems = m.face_problems(doc)
    if not problems:
        print("DOCTOR FAIL: a silent row carrying a declaring sibling row was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

bad.extend(m.face_problems(face))
e568 = json.load(open(E568, encoding="utf-8"))
population = [r for r in (e568.get("rows") or []) if r.get("class") == SILENT]
check(len(population) == len(rows),
      "the population no longer matches E568's silent class (%d vs %d)"
      % (len(population), len(rows)))
check(s.get("population_from_E568") == len(population),
      "the published population count does not equal E568's silent class")
check(s.get("rows_with_a_naive_marker", 0) > 0,
      "no naive marker was found, so the trap this study publishes is stale")
check(s.get("rows_with_a_scoped_declaration", 0)
      == sum(1 for r in rows if r.get("own_row_declaration")
             or any(x.get("declares_a_subset") for x in r.get("sibling_rows") or [])),
      "the scoped-declaration count does not re-derive from the rows")
check(s.get("scripts_with_a_scope_switch", 0)
      == sum(1 for r in rows if (r.get("script") or {}).get("scope_switch_tokens")),
      "the scope-switch count does not re-derive from the rows")
# the claim that makes this study worth a card: the marker words are not a declaration
check(s.get("rows_where_the_naive_marker_is_not_a_scope", 0) <= s.get("rows_with_a_naive_marker", 0),
      "more rows where the naive marker is not a scope than rows with a naive marker")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
if _hide_one_declaration(doc):
    check(bool(m.face_problems(doc)), "a silent row carrying a declaring sibling row was accepted")

detail = ("rows=%d own_row=%d sibling_row=%d mechanism_only=%d silent=%d "
          "| naive_marker_rows=%d scoped=%d not_a_scope=%d | sibling_rows_seen=%d "
          "| scope_switch_scripts=%d tables_rederived=%d disagree_with_E568=%d | %s"
          % (s.get("by_class", {}).get("rows", 0),
             s.get("by_class", {}).get("the_sentence_s_own_row_declares_a_subset", 0),
             s.get("by_class", {}).get("another_row_of_the_same_round_declares_a_subset", 0),
             s.get("by_class", {}).get("no_row_but_the_round_s_script_can_narrow", 0),
             s.get("by_class", {}).get(C_SILENT, 0), s.get("rows_with_a_naive_marker", 0),
             s.get("rows_with_a_scoped_declaration", 0),
             s.get("rows_where_the_naive_marker_is_not_a_scope", 0),
             s.get("sibling_rows_seen", 0), s.get("scripts_with_a_scope_switch", 0),
             s.get("tables_rederived", 0), s.get("tables_that_disagree_with_E568", 0),
             face.get("verdict")))
if bad:
    print("LEG E573 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E573 PASS: " + detail)
sys.exit(0)