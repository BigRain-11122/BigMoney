"""Run just the E560 leg of smoke_test.py without launching the other 400+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the
block at the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is
the one the suite runs.
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e560_chain_receipt_shape")
face = json.load(open(os.path.join(ROOT, "results", "state_tilt",
                                   "chainreceiptshape_latest.json"), encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("runners") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the runner population is empty")
check(s.get("runners") == len(rows), "the runner count is not the row count")
check(all(r.get("legs_in_table", 0) > 0 for r in rows), "a runner's leg table could not be read")
check(s.get("tables_imported", 0) >= 1,
      "no imported leg table is published (bm-a imports bm-c's list)")
check(all(r.get("output_chars_kept", 0) > 0 for r in rows),
      "a runner's output budget could not be read")
check((face.get("receipt_census") or {}).get("count", 0) > 0, "no receipt on disk was measured")
check(all((a or {}).get("found") for a in (face.get("control_arms") or {}).values()),
      "a control arm is blind")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

if rows:
    doc = json.loads(json.dumps(face))
    doc["runners"][0]["its_own_output"] = m.OUT_WITH_STDERR
    check(any("stderr" in p for p in m.face_problems(doc)),
          "a runner credited with stderr it never reads was accepted")

f = m._facts_from_source(m.CONTROL_SOURCES["abort_on_failure"])
check(f["loop_failure_policy"] == m.P_ABORTS, "a break in the loop is no longer read as an abort")
f = m._facts_from_source(m.CONTROL_SOURCES["states_table_size"])
check(f["expected_total"] == m.TOT_EXPECTED, "len(LEGS) in the payload is no longer the table size")

detail = ("%d runners / %d legs / continues=%d / stderr=%d / triage=%d/%d / %d receipts / %s"
          % (len(rows), s.get("legs_total_in_tables", 0), s.get("continues_after_failure", 0),
             s.get("keeps_stderr", 0), s.get("usable_triage_fields_total", 0),
             s.get("triage_fields_available", 0),
             (face.get("receipt_census") or {}).get("count", 0), face.get("verdict")))
if bad:
    print("LEG E560 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E560 PASS: " + detail)
sys.exit(0)