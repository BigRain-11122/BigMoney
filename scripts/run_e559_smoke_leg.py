"""Run just the E559 leg of smoke_test.py without launching the other 400+ legs.

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


m = importlib.import_module("e559_chain_rc_consumer")
face = json.load(open(os.path.join(ROOT, "results", "state_tilt",
                                   "chainrcconsumer_latest.json"), encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("spawn_sites") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the spawn population is empty")
check(sum((s.get("by_class") or {}).values()) == len(rows),
      "the class table does not partition the spawn rows")
check(all(r.get("class") == m.classify_spawn(bool(r.get("waits")), bool(r.get("reads_rc")),
                                             bool(r.get("can_fail"))) for r in rows),
      "a spawn row's class is not what its own fields say")
check(bool(s.get("runners_present")), "no chain runner is on disk")
check(not s.get("runners_exiting_non_zero_on_a_failing_leg"),
      "a runner carries a failing leg out of the process")
check(s.get("receipt_writers", 0) >= 1, "no writer of a chain receipt was found")
check(all((a or {}).get("found") for a in (face.get("control_arms") or {}).values()),
      "a control arm is blind")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

if rows:
    doc = json.loads(json.dumps(face))
    doc["spawn_sites"][0]["class"] = m.S_FAILS
    doc["spawn_sites"][0]["can_fail"] = False
    check(any("class is not what its own fields say" in p for p in m.face_problems(doc)),
          "a detached spawn relabelled failing was accepted")

doc = json.loads(json.dumps(face))
doc["summary"]["receipt_readers_outside_the_writer"] = (
    (s.get("receipt_readers_outside_the_writer") or 0) + 1)
check(any("reader count" in p for p in m.face_problems(doc)),
      "an inflated outside-reader count was accepted")

check(m._wrapper_class_in_text("& T\\outer.ps1\nif ($LASTEXITCODE -ne 0) { exit 1 }\n")
      == m.W_NULL, "the $LASTEXITCODE-after-a-ps1-call trap is no longer separated")
check(not m._spawn_class_from_source(
    "import subprocess\ndef run(a, b):\n    return 0\nrun('x', ['Tools/s6_chain_bmb.py'])\n"),
    "a local helper named run is counted as a spawn again")

detail = ("%d spawn sites / %s / %d receipt writers / %d readers outside the writer / %s"
          % (len(rows), ",".join("%s=%d" % (k, v) for k, v in (s.get("by_class") or {}).items() if v)
             or "no rows", s.get("receipt_writers", 0),
             s.get("receipt_readers_outside_the_writer", 0), face.get("verdict")))
if bad:
    print("LEG E559 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E559 PASS: " + detail)
sys.exit(0)