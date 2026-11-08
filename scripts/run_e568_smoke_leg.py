"""Run just the E568 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e568_smoke_leg.py            # expect PASS
  python scripts/run_e568_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "oldchaintable_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e568_old_chain_table")
face = json.load(open(LATEST, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []


def _inflate_a_table(doc):
    for r in doc.get("rows") or []:
        if r.get("table") is not None:
            r["table"] += 1
            return True
    return False


if "--doctor" in sys.argv[1:]:
    doc = json.loads(json.dumps(face))
    if not _inflate_a_table(doc):
        print("DOCTOR FAIL: the fixture offers no recovered table to corrupt")
        sys.exit(1)
    problems = m.face_problems(doc)
    if not problems:
        print("DOCTOR FAIL: a table that contradicts its own row was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

bad.extend(m.face_problems(face))
check(bool(rows), "no sentence was read, so the recovery rule is untested")
check(s.get("rounds_with_a_recovered_table", 0) > 0,
      "no table was recovered, so the study concluded nothing")
check(s.get("claims_with_a_recovered_table") == sum(1 for r in rows if r.get("table") is not None),
      "the recovered-table count does not re-derive from the rows")
check(s.get("tree_scan_only_tables", 0) > s.get("canonical_only_tables", 0),
      "the canonical-path arm is not the losing arm, so the scan finding is stale")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
check(_inflate_a_table(doc), "the fixture offers no recovered table to corrupt")
check(bool(m.face_problems(doc)), "a table that contradicts its own row was accepted")

detail = ("population=%d rounds=%d recovered_rounds=%d | judged=%d equal=%d below=%d above=%d | "
          "no_commit=%d no_script=%d no_table=%d | scan_only=%d canonical_only=%d | %s"
          % (s.get("population", 0), s.get("rounds_in_population", 0),
             s.get("rounds_with_a_recovered_table", 0), s.get("judged_from_git", 0),
             s.get(m.G_EQUALS, 0), s.get(m.G_SILENT, 0), s.get(m.G_ABOVE, 0),
             s.get(m.G_NO_COMMIT, 0), s.get(m.G_NO_SCRIPT, 0), s.get(m.G_NO_TABLE, 0),
             s.get("tree_scan_only_tables", 0), s.get("canonical_only_tables", 0),
             face.get("verdict")))

print("%s %s | %s" % ("PASS" if not bad else "FAIL", "E568 pre-receipt table recovery", detail))
if bad:
    for why in bad:
        print("  -", why[:200])
sys.exit(0 if not bad else 1)