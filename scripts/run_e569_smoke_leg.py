"""Run just the E569 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e569_smoke_leg.py            # expect PASS
  python scripts/run_e569_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "chainnumerator_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e569_chain_numerator")
face = json.load(open(LATEST, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

if "--doctor" in sys.argv[1:]:
    doc = json.loads(json.dumps(face))
    for r in doc.get("rows") or []:
        if isinstance(r.get("stated_rc0"), int) and isinstance(r.get("derived_rc0"), int):
            r["stated_rc0"] += 1
            break
    problems = m.face_problems(doc)
    if not problems:
        print("DOCTOR FAIL: an inflated stated count was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

bad.extend(m.face_problems(face))
check(bool(rows), "no receipt was recounted, so the count rule is untested")
check(s.get("receipts_on_disk") == len(rows), "the receipt total does not equal the row count")
check((s.get("count_disagrees_with_its_own_rows") or 0) == 0,
      "a receipt states a count its own rows do not give (rebuild the face or fix the reader)")
check(s.get("receipts_stating_a_count", 0) > 0,
      "no receipt states a count, so the agreeing arm is vacuous")
arms = m.selftest
check(callable(arms), "the study exposes no selftest")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
for r in doc.get("rows") or []:
    if isinstance(r.get("stated_rc0"), int) and isinstance(r.get("derived_rc0"), int):
        r["stated_rc0"] += 1
        break
check(bool(m.face_problems(doc)), "an inflated stated count was accepted")

detail = ("receipts=%d stating=%d agree=%d disagree=%d | understate=%d red_green=%d | "
          "joined=%d equal=%d differ=%d | %s"
          % (s.get("receipts_on_disk", 0), s.get("receipts_stating_a_count", 0),
             s.get("count_agrees_with_its_own_rows", 0),
             s.get("count_disagrees_with_its_own_rows", 0),
             s.get("receipts_understating_their_own_rc0", 0),
             s.get("receipts_claiming_a_failing_row_is_green", 0),
             s.get("joined_to_a_printed_sentence", 0),
             s.get("printed_numerator_equals_derived_rc0", 0),
             s.get("printed_numerator_differs_from_derived_rc0", 0),
             face.get("verdict")))
if bad:
    print("LEG E569 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E569 PASS: " + detail)
sys.exit(0)