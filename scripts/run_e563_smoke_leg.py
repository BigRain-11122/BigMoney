"""Run just the E563 leg of smoke_test.py without launching the other 400+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e563_smoke_leg.py            # expect PASS
  python scripts/run_e563_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "receiptprefix_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e563_receipt_prefix")

doctor = "--doctor" in sys.argv[1:]
if doctor:
    face = json.load(open(FACE, encoding="utf-8"))
    if face["rows"]:
        face["rows"][0]["leg_indices"] = [0, 1, 2]
        face["rows"][0]["class"] = m.C_EXACT_PREFIX
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a class that does not re-derive from its indices was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:120]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the short-receipt population is empty")
check(s.get("short_receipts") == len(rows), "the short count is not the row count")
check(s.get("names_in_table_order", 0) > 0, "no receipt is in table order")
check(bool((face.get("population_source") or {}).get("sha16")),
      "the population is not pinned to a vintage")
check(m.classify(["dualrun", "compute_audit"], m.TABLE)[0] == m.C_EXACT_PREFIX,
      "an exact prefix is no longer recognised")
check(m.classify(["dualrun", "update_daily"], m.TABLE)[0] == m.C_PREFIX_GAP,
      "a gap after the head is no longer its own class")
check(m.classify(["update_daily"], m.TABLE)[0] == m.C_SUBSET,
      "a filtered head is no longer its own class")
check(m.classify(["dualrun", "ghost_leg"], m.TABLE)[0] == m.C_FOREIGN,
      "a name absent from the table is no longer foreign")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
doc["summary"]["names_in_table_order"] = doc["summary"].get("names_in_table_order", 0) + 1
check(bool(m.face_problems(doc)), "an inflated in-order count was accepted")

detail = ("%d short receipts / exact-prefix=%d / prefix-with-gap=%d / subset=%d / "
          "out-of-order=%d / foreign=%d (%d exist in today's table, %d in none) / "
          "single-leg-at-head=%d / %s"
          % (s.get("short_receipts", 0), s.get(m.C_EXACT_PREFIX, 0), s.get(m.C_PREFIX_GAP, 0),
             s.get(m.C_SUBSET, 0), s.get(m.C_OUT_OF_ORDER, 0), s.get(m.C_FOREIGN, 0),
             s.get("foreign_names_that_exist_in_today_s_table", 0),
             s.get("foreign_names_that_exist_in_no_current_table", 0),
             s.get("single_leg_that_is_the_table_head", 0), face.get("verdict")))
if bad:
    print("LEG E563 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E563 PASS: " + detail)
sys.exit(0)