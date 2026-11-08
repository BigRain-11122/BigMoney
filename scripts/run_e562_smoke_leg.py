"""Run just the E562 leg of smoke_test.py without launching the other 400+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e562_smoke_leg.py            # expect PASS
  python scripts/run_e562_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "singlelegprovenance_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e562_single_leg_provenance")

doctor = "--doctor" in sys.argv[1:]
if doctor:
    face = json.load(open(FACE, encoding="utf-8"))
    victim = next(r for r in face["rows"] if r.get("class") == m.C_SUBSET)
    victim["writer_position"] = m.W_INSIDE
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a subset class beside an inside-loop writer was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:120]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

bad.extend(m.face_problems(face))
check(bool(rows), "the short-receipt population is empty")
check(s.get("short_receipts") == len(rows), "the short count is not the row count")
check(sum(s.get(k, 0) for k in ("deliberate_subset", "killed_chain_could_leave_this_file",
                                "unexplained", "runners_unreachable")) == len(rows),
      "a short receipt is in no class or in two")
check(s.get("runners_joined", 0) > 0, "not one short receipt joined to its runner blob")
check(bool((face.get("population_source") or {}).get("sha16")),
      "the population is not pinned to a vintage")
check(m.analyse_runner(m.FIXTURES["inside_loop"])["writer_position"] == m.W_INSIDE,
      "a per-leg writer is no longer visible")
check(m.classify(1, m.analyse_runner(m.FIXTURES["inside_loop"])) == m.C_KILL,
      "a per-leg writer no longer admits a killed chain")
check(m.classify(1, m.analyse_runner(m.FIXTURES["skip_arm"])) == m.C_SKIP,
      "a skipping loop is no longer its own explanation")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
doc["summary"]["short_receipts"] = doc["summary"]["short_receipts"] + 1
check(bool(m.face_problems(doc)), "an inflated short count was accepted")

detail = ("%d short receipts / %d single-leg / joined=%d / after-loop=%d / only-arm=%d / "
          "killed-could-leave=%d / subset=%d / %s"
          % (s.get("short_receipts", 0), s.get("single_leg_receipts", 0),
             s.get("runners_joined", 0), s.get("writer_after_the_loop", 0),
             s.get("honours_an_only_argument", 0),
             s.get("killed_chain_could_leave_this_file", 0),
             s.get("deliberate_subset", 0), face.get("verdict")))
if bad:
    print("LEG E562 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E562 PASS: " + detail)
sys.exit(0)