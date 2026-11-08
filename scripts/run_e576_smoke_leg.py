"""Run just the E576 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the
block in smoke_test.py is the one the suite runs.

  python scripts/run_e576_smoke_leg.py            # expect PASS
  python scripts/run_e576_smoke_leg.py --doctor   # relabel a late row as cross-machine, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "gapcalls_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e576_gap_calls")
    face = json.load(open(LATEST, encoding="utf-8"))
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    bad.extend(m.face_problems(face))
    check(s.get("population_agrees_with_e575") is True,
          "the re-derived population disagrees with E575's own count")
    check(s.get("corpus_executions", 0) >= 1,
          "no chain execution was read, so the population was not rebuilt")
    check(s.get("rows") == s.get("corpus_unattributed"),
          "the published rows do not equal the unattributed executions")
    for r in rows:
        k = r.get("class")
        nr = r.get("next_row_any_machine")
        if k == m.C_CROSS and not (nr and nr.get("inside_tolerance")):
            bad.append("%s: a cross-machine row names no row inside the tolerance" % r.get("ts"))
            break
        if k == m.C_DUP and not r.get("duplicate_of"):
            bad.append("%s: a duplicate was published without what it duplicates" % r.get("ts"))
            break
    doc = json.loads(json.dumps(face))
    if doctor:
        for r in doc.get("rows") or []:
            if r.get("class") == m.C_LATE:
                r["class"] = m.C_CROSS
                break
    ok = not m.face_problems(doc)
    if doctor:
        print("DOCTOR %s (a late row relabelled as cross-machine was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1
    print("%s gap=%d duplicate=%d cross=%d late=%d nothing=%d | hours=%d with_switch=%d "
          "| corpus=%d e575=%d"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("rows", 0), s.get("duplicates_of_attributed_runs", 0),
             s.get("cross_machine_inside_tolerance", 0), s.get("beyond_tolerance", 0),
             s.get("no_later_row_at_all", 0), s.get("hours_hit", 0),
             s.get("executions_carrying_the_switch", 0), s.get("corpus_executions", 0),
             s.get("e575_unattributed_again", 0)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())