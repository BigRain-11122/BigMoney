"""Run just the E579 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the
block in smoke_test.py is the one the suite runs.

  python scripts/run_e579_smoke_leg.py            # expect PASS
  python scripts/run_e579_smoke_leg.py --doctor   # label a machine that loses rows as "the
                                                  # dialect costs nothing", expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "livenessdialect_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e579_liveness_dialect")
    face = json.load(open(LATEST, encoding="utf-8"))
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    bad.extend(m.face_problems(face))

    check(s.get("machines") == len(rows),
          "the summary machine count does not match the published rows")
    check(s.get("wide_rows_total", 0) >= s.get("strict_rows_total", 0),
          "the wide dialect reports fewer rows than the shipped one")
    check(s.get("rows_invisible_to_the_shipped_reader", 0)
          == s.get("wide_rows_total", 0) - s.get("strict_rows_total", 0),
          "the invisible row count does not re-derive from the two totals")
    check(all(r.get("class") in (m.C_FLIP, m.C_MOVES, m.C_LOST, m.C_NOTHING) for r in rows),
          "a machine carries a class the study does not define")
    # the point of the study: the verdict axis is answered separately from the disclosure axis
    check(s.get("machines_that_flip") is not None
          and s.get("machines_whose_disclosure_moves") is not None,
          "the face does not separate a flipped verdict from a moved number")
    strict_verdicts = [(r["machine"], (r.get("strict") or {}).get("verdict")) for r in rows]
    check(len(strict_verdicts) == len(rows) and all(v for _, v in strict_verdicts),
          "a machine has no shipped verdict to compare against")

    doc = json.loads(json.dumps(face))
    if doctor:
        for r in doc.get("rows") or []:
            if r.get("class") == m.C_LOST:
                r["class"] = m.C_NOTHING
                break
    ok = not m.face_problems(doc)
    if doctor:
        print("DOCTOR %s (a machine whose rows are lost but whose published numbers did not move, "
              "relabelled as costing nothing, was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1
    print("%s machines=%d flips=%d disclosure_moves=%d rows_lost=%d invisible=%d/%d worst_gap_"
          "overstatement=%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("machines", 0),
             s.get("machines_that_flip", 0),
             s.get("machines_whose_disclosure_moves", 0),
             s.get("machines_whose_rows_are_lost_without_a_number_moving", 0),
             s.get("rows_invisible_to_the_shipped_reader", 0),
             s.get("wide_rows_total", 0),
             s.get("largest_worst_gap_overstatement_min"),
             face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())