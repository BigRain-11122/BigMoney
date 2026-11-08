"""Run just the E567 leg of smoke_test.py without launching the other 430+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e567_smoke_leg.py            # expect PASS
  python scripts/run_e567_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "chainclaim_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e567_chain_claim")

doctor = "--doctor" in sys.argv[1:]
if doctor:
    face = json.load(open(FACE, encoding="utf-8"))
    done = False
    for r in face.get("claims") or []:
        if r.get("class") == m.CNT_SILENT:
            r["class"] = m.CNT_EQUALS
            done = True
            break
    if not done:
        for r in face.get("claims") or []:
            if r.get("class") == m.CNT_NO_RECEIPT:
                r["receipt"] = "results/_r0bmx_s6_chain.json"
                r["table_at_its_round"] = r["denominator"]
                r["class"] = m.CNT_EQUALS
                break
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a doctored claim was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
claims = face.get("claims") or []

bad.extend(m.face_problems(face))
check(bool(claims), "no claim was parsed, so the parse rule is untested")
check(s.get(m.CNT_EQUALS), "no claim names a whole table, so the join is untested")
arms = m._check_arms()
check(not arms, "control arms moved: %s" % (arms[0][:200] if arms else ""))
check(s.get(m.CNT_SILENT) == sum(1 for c in claims if c.get("class") == m.CNT_SILENT),
      "the silent-subset counter does not re-derive from the claim list")
check(not s.get(m.CNT_LABELLED) or any(
    c.get("subset_label") for c in claims if c.get("class") == m.CNT_LABELLED),
    "a labelled subset carries no label")

doc = json.loads(json.dumps(face))
for c in doc.get("claims") or []:
    if c.get("class") == m.CNT_SILENT:
        c["class"] = m.CNT_EQUALS
        break
check(bool(m.face_problems(doc)), "a silent subset relabelled as the whole table was accepted")

doc = json.loads(json.dumps(face))
for c in doc.get("claims") or []:
    if c.get("class") == m.CNT_NO_RECEIPT:
        c["receipt"] = "results/_r0bmx_s6_chain.json"
        c["table_at_its_round"] = c["denominator"]
        c["class"] = m.CNT_EQUALS
        break
check(bool(m.face_problems(doc)), "an unjudged claim was accepted as judged")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

detail = ("%d claims / equals=%d labelled=%d silent=%d above=%d / unjudged=%d / %s"
          % (s.get("claims_total", 0), s.get(m.CNT_EQUALS, 0), s.get(m.CNT_LABELLED, 0),
             s.get(m.CNT_SILENT, 0), s.get(m.CNT_ABOVE, 0), s.get("unjudgeable", 0),
             face.get("verdict")))
if bad:
    print("LEG E567 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E567 PASS: " + detail)
sys.exit(0)