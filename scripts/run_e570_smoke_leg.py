"""Run just the E570 leg of smoke_test.py without launching the other 430+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e570_smoke_leg.py            # expect PASS
  python scripts/run_e570_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "chainprintsource_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e570_chain_print_source")
face = json.load(open(LATEST, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

if "--doctor" in sys.argv[1:]:
    doc = json.loads(json.dumps(face))
    for r in doc.get("rows") or []:
        r["origin_kind"] = (m.LITERAL if r.get("origin_kind") != m.LITERAL
                            else m.READ_PAYLOAD)
        break
    problems = m.face_problems(doc)
    if not problems:
        print("DOCTOR FAIL: a relabelled origin was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

bad.extend(m.face_problems(face))
check(bool(rows), "no printed chain number was traced, so the trace rule is untested")
check(len({r.get("runner") for r in rows}) == 3,
      "the three runners do not all contribute a printed number")
arms = m._check_arms()
check(not arms, "control arms moved: %s" % (arms[0][:200] if arms else ""))
doc_arm = m.doctored_arm()
check(doc_arm.get("applied"), "the doctored-copy arm could not be applied")
check(doc_arm.get("detected"), "a doctored denominator was not detected")
check(s.get(m.LITERAL) == sum(1 for r in rows if r.get("origin_kind") == m.LITERAL),
      "the literal counter does not re-derive from the rows")
check(s.get(m.READ_PAYLOAD) == sum(1 for r in rows if r.get("origin_kind") == m.READ_PAYLOAD),
      "the payload counter does not re-derive from the rows")
check(s.get("receipts_carrying_legs_total") is not None,
      "the receipt arm did not publish a count")
check((s.get("receipts_whose_total_disagrees_with_their_rows") or 0) == 0,
      "a receipt disagrees with its own rows")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
doc["population_source"]["sha16"]["Tools/s6_chain_bma.py"] = ""
check(bool(m.face_problems(doc)), "an unpinned runner was accepted")

detail = ("%d printed numbers / from_payload=%d literal=%d outside=%d | receipts=%d "
          "with_count=%d no_count=%d | %s"
          % (s.get("printed_numbers", 0),
             s.get("printed_numbers_read_from_the_written_object", 0), s.get(m.LITERAL, 0),
             s.get(m.NOT_FROM_OBJECT, 0), s.get("receipts_on_disk", 0),
             s.get("receipts_carrying_legs_total", 0), s.get("receipts_with_no_count_field", 0),
             face.get("verdict")))
if bad:
    print("LEG E570 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E570 PASS: " + detail)
sys.exit(0)