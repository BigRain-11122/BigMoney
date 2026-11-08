"""Run just the E561 leg of smoke_test.py without launching the other 400+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e561_smoke_leg.py            # expect PASS
  python scripts/run_e561_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "receipttable_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e561_receipt_table_join")

doctor = "--doctor" in sys.argv[1:]
if doctor:
    # a one-row receipt relabelled as covering a 30-leg table: the exact lie this study refuses
    face = json.load(open(FACE, encoding="utf-8"))
    victim = next(r for r in face["rows"]
                  if not r.get("unparsed") and r.get("rows") == 1
                  and (r.get("table_at_its_round") or 0) > 1)
    victim["class"] = m.C_COMPLETE
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a one-row receipt relabelled complete was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:120]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the receipt population is empty")
check(s.get("receipts_on_disk") == len(rows), "the receipt count is not the row count")
check(sum(s.get(k, 0) for k in ("complete", "partial", "shrunk", "no_witness", "unreadable"))
      == s.get("receipts_on_disk"), "a receipt is in no class or in two")
check(s.get("joinable", 0) > 0, "not one receipt joined to a runner blob")
check(all((a or {}).get("found") for a in (face.get("control_arms") or {}).values()),
      "a control arm is blind")
check(m.classify(1, 30) == m.C_PARTIAL, "a one-row receipt is no longer read as short")
check(m.classify(30, 30) == m.C_COMPLETE, "equal counts are no longer read as complete")
check(m.classify(5, None, reachable=False) == m.C_NO_WITNESS,
      "an unreachable blob is no longer a no-witness class")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
doc["summary"]["receipts_on_disk"] = doc["summary"]["receipts_on_disk"] + 1
check(bool(m.face_problems(doc)), "an inflated receipt count was accepted")

detail = ("%d receipts / %d joinable / complete=%d / short=%d / no-witness=%d / unreadable=%d / %s"
          % (s.get("receipts_on_disk", 0), s.get("joinable", 0), s.get("complete", 0),
             s.get("partial", 0), s.get("no_witness", 0), s.get("unreadable", 0),
             face.get("verdict")))
if bad:
    print("LEG E561 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E561 PASS: " + detail)
sys.exit(0)