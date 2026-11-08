"""Run just the E548 leg of smoke_test.py without launching the other 400+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e548_smoke_leg.py            # expect PASS
  python scripts/run_e548_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "extendedresolver_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e548_extended_resolver")

if "--doctor" in sys.argv[1:]:
    face = json.load(open(FACE, encoding="utf-8"))
    face["summary"]["arms_closed_by_bindings_alone"] += 1
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a closed counter that does not add up was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:120]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("arms") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the parent's arm population is empty")
check(s.get("arms_in_parent") == len(rows), "the published arm count is not the population")
check(s.get("arms_that_name_a_parameter", 0) + s.get("arms_without_a_parameter", 0) == len(rows),
      "movable and unmovable arms do not add up")
check(s.get("parent_settlements_this_resolver_reproduces", 0) +
      s.get("parent_settlements_this_resolver_leaves_open", 0) ==
      s.get("arms_the_parent_declared_settled", 0), "the parent settlements do not add up")
check(all(r.get("argument_expression") or r.get("arm_outcome") == m.O_NO_PARAMETER for r in rows),
      "an arm that names a parameter publishes no argument expression")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

detail = ("%d arms / %d movable / %d closed (%d verbatim, %d functions-only, %d bindings-only, "
          "%d both) / parent settled=%d reproduced=%d / %s"
          % (s.get("arms_in_parent", 0), s.get("arms_that_name_a_parameter", 0),
             s.get("arms_closed", 0), s.get("arms_closed_verbatim", 0),
             s.get("arms_closed_by_functions_alone", 0),
             s.get("arms_closed_by_bindings_alone", 0),
             s.get("arms_closed_by_both_together", 0),
             s.get("arms_the_parent_declared_settled", 0),
             s.get("parent_settlements_this_resolver_reproduces", 0),
             face.get("verdict")))
if bad:
    print("LEG E548 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E548 PASS: " + detail)
sys.exit(0)