"""Run just the E566 leg of smoke_test.py without launching the other 430+ legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a
single leg is exercised by re-running its assertions from here.  This file mirrors the block at
the end of smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the
suite runs.

  python scripts/run_e566_smoke_leg.py            # expect PASS
  python scripts/run_e566_smoke_leg.py --doctor   # mutate the face, expect the leg to go RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "state_tilt", "receiptcoverage_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


m = importlib.import_module("e566_receipt_coverage_consumer")

doctor = "--doctor" in sys.argv[1:]
if doctor:
    face = json.load(open(FACE, encoding="utf-8"))
    for r in face.get("rows") or []:
        if r.get("source_class") == m.C_READS:
            r["class"] = m.R_OTHER
            break
    problems = m.face_problems(face)
    if not problems:
        print("DOCTOR FAIL: a hand-written reader class was accepted")
        sys.exit(1)
    print("DOCTOR PASS: %d problems, first=%s" % (len(problems), problems[0][:120]))
    sys.exit(0)

face = json.load(open(FACE, encoding="utf-8"))
s = face.get("summary") or {}
rows = face.get("rows") or []

bad.extend(m.face_problems(face))
check(bool(rows), "no source carries a receipt path")
check(s.get(m.C_NAMES), "the naming population is empty, so the split is untested")
check(s.get(m.C_READS), "no source opens a receipt")
check(s.get(m.C_WRITES), "no source writes a receipt")
check(m._mode_of(m.FIX_NAME) == m.C_NAMES, "a path in a payload list is no longer only a name")
check(m._mode_of(m.FIX_WRITE) == m.C_WRITES, "a dumped receipt is no longer a write")
check(m._mode_of(m.FIX_GLOB_READ) == m.C_READS, "a globbed payload read is no longer a read")
check(m.classify_reader(m.FIX_COVERAGE)["class"] == m.R_COVERAGE,
      "a count joined to a table is no longer coverage-aware")
check(m.classify_reader(m.FIX_LITERAL)["class"] == m.R_LITERAL,
      "a literal denominator is no longer its own class")
check(m.classify_reader(m.FIX_RC_ONLY)["class"] == m.R_RC_ONLY,
      "an rc filter without a count is no longer blind")
priced = face.get("priced_pairs") or []
short = [p for p in priced if isinstance(p.get("rows"), int)
         and isinstance(p.get("table_at_its_round"), int)
         and p["rows"] < p["table_at_its_round"]]
check(s.get("pairs_where_the_receipt_was_short") == len(short),
      "the short-pair counter does not match the pair list")

doc = json.loads(json.dumps(face))
doc["verdict"] = "a_verdict_this_study_never_publishes"
check(bool(m.face_problems(doc)), "a hand-written verdict was accepted")

doc = json.loads(json.dumps(face))
doc["summary"]["pairs_where_a_blind_reader_read_a_short_receipt"] = 0
if short:
    check(bool(m.face_problems(doc)), "a zeroed blind-short counter was accepted")

detail = ("%d sources / writes=%d / reads=%d / names-only=%d / readers: aware=%d literal=%d "
          "rc-only=%d other=%d / pairs priced=%d short=%d blind-short=%d / %s"
          % (s.get("sources_scanned", 0), s.get(m.C_WRITES, 0), s.get(m.C_READS, 0),
             s.get(m.C_NAMES, 0), s.get("readers_" + m.R_COVERAGE, 0),
             s.get("readers_" + m.R_LITERAL, 0), s.get("readers_" + m.R_RC_ONLY, 0),
             s.get("readers_" + m.R_OTHER, 0), s.get("reader_receipt_pairs_priced", 0),
             s.get("pairs_where_the_receipt_was_short", 0),
             s.get("pairs_where_a_blind_reader_read_a_short_receipt", 0), face.get("verdict")))
if bad:
    print("LEG E566 FAIL: " + "; ".join(bad)[:400])
    sys.exit(1)
print("LEG E566 PASS: " + detail)
sys.exit(0)