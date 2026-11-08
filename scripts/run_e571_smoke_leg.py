"""Run just the E571 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e571_smoke_leg.py            # expect PASS
  python scripts/run_e571_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "receiptround_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e571_receipt_round_identity")
face = json.load(open(LATEST, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []


def _flip_one_agree(doc):
    for r in doc.get("rows") or []:
        if r.get("identity") == "agrees" and isinstance(r.get("field_round"), int):
            r["field_round"] += 1
            r["identity"] = "disagrees"
            r["delta"] = 1
            return True
    return False


if "--doctor" in sys.argv[1:]:
    doc = json.loads(json.dumps(face))
    if not _flip_one_agree(doc):
        print("DOCTOR FAIL: the fixture offers no agreeing row to corrupt")
        sys.exit(1)
    problems = m.face_problems(doc)
    if not problems:
        print("DOCTOR FAIL: a row that disagrees with its own name was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:140]))
    sys.exit(0)

bad.extend(m.face_problems(face))
check(bool(rows), "no receipt was read, so the name/field comparison is untested")
check(s.get("receipts_on_disk") == len(rows), "the receipt total does not equal the row count")
check((s.get("receipts_stating_a_round") or 0) > 0,
      "no receipt states a round, so the dialect split is vacuous")
check(sum((s.get("dialect") or {}).values()) == (s.get("receipts_stating_a_round") or 0),
      "the dialect split does not add up to the receipts that state a round")
check(s.get("receipts_an_int_keyed_consumer_would_miss", 0)
      == sum(1 for r in rows if r.get("int_keyed_consumer_misses")),
      "the int-keyed exposure count does not re-derive from the rows")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
if _flip_one_agree(doc):
    check(bool(m.face_problems(doc)), "a row that disagrees with its own name was accepted")

# the dialect is a join hazard even when every value agrees; a face that published only
# "identity agrees" and dropped the dialect split would hide the whole finding
check(bool(s.get("dialect")), "the face publishes no dialect split, so a join hazard reads as a lie")

detail = ("receipts=%d stating=%d agrees=%d disagrees=%d unormalisable=%d no_field=%d | "
          "dialect int=%d dec_str=%d label=%d other=%d | int-keyed misses=%d | %s"
          % (s.get("receipts_on_disk", 0), s.get("receipts_stating_a_round", 0),
             (s.get("identity") or {}).get("agrees", 0),
             (s.get("identity") or {}).get("disagrees", 0),
             (s.get("identity") or {}).get("field_unormalisable", 0),
             (s.get("identity") or {}).get("no_round_field", 0),
             (s.get("dialect") or {}).get("int", 0),
             (s.get("dialect") or {}).get("decimal_string", 0),
             (s.get("dialect") or {}).get("label_string", 0),
             (s.get("dialect") or {}).get("other", 0),
             s.get("receipts_an_int_keyed_consumer_would_miss", 0),
             face.get("verdict")))
if bad:
    print("LEG E571 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E571 PASS: " + detail)
sys.exit(0)