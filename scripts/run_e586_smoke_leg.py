"""Run just the E586 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e586_smoke_leg.py            # expect PASS
  python scripts/run_e586_smoke_leg.py --doctor   # move one money-carrying surface's money flag
                                                  # so its own count stops re-deriving, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "TICKETREADERBAR.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e586_ticket_reader_bar")
    face = json.load(open(FACE, encoding="utf-8"))
    bad.extend(m.face_problems(face))

    rc = face.get("reader_counts") or {}
    sc = face.get("surface_counts") or {}
    if rc.get("readers_naming_strict_money_with_no_bar") == 0 and rc.get("silent_readers"):
        check(False, "the face names silent readers while its count says there are none")
    if sc.get("surfaces_carrying_money_with_no_bar") == 0 and sc.get("silent_surfaces"):
        check(False, "the face names silent surfaces while its count says there are none")
    ticket = face.get("ticket") or {}
    for r in face.get("surfaces") or []:
        if r.get("bar_witness") == "prose_dates" and r.get("kind") != "order_page":
            check(False, "a machine face is credited with prose instead of a field")
    if not ticket.get("pricing_bar"):
        check(False, "the face names no pricing bar")

    doc = json.loads(json.dumps(face))
    if doctor:
        rows = doc.get("surfaces") or []
        if rows:
            rows[0]["carries_ticket_money"] = not bool(rows[0].get("carries_ticket_money"))
        else:
            check(False, "nothing on disk to doctor")
    ok = not m.face_problems(doc) and not bad
    if doctor:
        print("DOCTOR %s (a surface whose money flag was flipped so its counts no longer re-derive "
              "was %s)" % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                           "refused" if not ok else "accepted"))
        return 0 if not ok else 1
    if bad:
        print("FAIL " + "; ".join(bad)[:300])
        return 1
    print("PASS E586 | readers=%d money_readers=%d silent=%d | surfaces=%d money_surfaces=%d "
          "silent=%d | witnesses=%s | %s"
          % (rc.get("readers", 0), rc.get("readers_naming_strict_money", 0),
             rc.get("readers_naming_strict_money_with_no_bar", 0), sc.get("surfaces", 0),
             sc.get("surfaces_carrying_ticket_money", 0),
             sc.get("surfaces_carrying_money_with_no_bar", 0),
             sc.get("surfaces_stating_a_bar_by_witness"), doc.get("verdict")))
    return 0


if __name__ == "__main__":
    sys.exit(main())