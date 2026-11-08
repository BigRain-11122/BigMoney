"""Run just the E578 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the
block in smoke_test.py is the one the suite runs.

  python scripts/run_e578_smoke_leg.py            # expect PASS
  python scripts/run_e578_smoke_leg.py --doctor   # label a one-ledger reader as "loses every
                                                  # no-pipe row", expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "rowindexconsumers_latest.json")
C_SAME = "loses_the_same_rows_as_the_index_it_inherits"

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e578_round_index_consumers")
    face = json.load(open(LATEST, encoding="utf-8"))
    s = face.get("summary") or {}
    p = face.get("population") or {}
    cells = p.get("by_cell") or {}
    bad.extend(m.face_problems(face))
    check(sum(cells.values()) == p.get("rows"),
          "the 2x2 cells no longer add up to the row population")
    check(s.get("lose_every_row_without_a_leading_pipe"),
          "the verdict names no reader that loses every row without a leading pipe")
    check(s.get("pipe_tolerant_readers"),
          "no pipe-tolerant reader was measured, so the contrast arm is empty")
    rec = p.get("e577_reconciliation") or {}
    check((rec.get("strict_plus_no_pipe_minus_lenient") or 0) > 0,
          "E577's published triple was not reconciled, so the 1,534 is still taken on faith")
    for cid in s.get("lose_every_row_without_a_leading_pipe") or []:
        c = next((x for x in face.get("consumers") or [] if x.get("id") == cid), None)
        if c is None:
            bad.append("%s is named by the verdict but absent from the consumers" % cid)
            continue
        if (c.get("loss_in_scope") or 0) < (c.get("no_pipe_rows_in_scope") or 0):
            bad.append("%s: loss is below its own no-pipe count" % cid)
            break
    doc = json.loads(json.dumps(face))
    if doctor:
        for c in doc.get("consumers") or []:
            if c.get("class") == C_SAME:
                c["reads_files"] = c["reads_files"][:1]
                break
    ok = not m.face_problems(doc)
    if doctor:
        print("DOCTOR %s (a reader relabelled to lose every no-pipe row while reading one ledger "
              "was %s)" % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                           "refused" if not ok else "accepted"))
        return 0 if not ok else 1
    print("%s rows=%d cells=%s index_readers=%d lose_every_no_pipe=%d pipe_tolerant=%d "
          "window=%d e577_gap=%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             p.get("rows", 0),
             ",".join("%s:%d" % (k, v) for k, v in sorted(cells.items())),
             s.get("index_readers", 0),
             len(s.get("lose_every_row_without_a_leading_pipe") or []),
             len(s.get("pipe_tolerant_readers") or []),
             len(s.get("window_limited_readers") or []),
             rec.get("strict_plus_no_pipe_minus_lenient"),
             face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())