"""Run just the E575 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499: any argv is ignored and the whole suite runs), so a leg
is exercised by re-running its assertions from here.  This file mirrors the block at the end of
smoke_test.py; if the two ever disagree, the block in smoke_test.py is the one the suite runs.

  python scripts/run_e575_smoke_leg.py            # expect PASS
  python scripts/run_e575_smoke_leg.py --doctor   # empty a passing row's executions, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "onlyflag_latest.json")
E573 = os.path.join(ROOT, "results", "state_tilt", "silentchain_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e575_only_flag")
    face = json.load(open(LATEST, encoding="utf-8"))
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    chk = json.load(open(E573, encoding="utf-8"))
    pop = [r for r in (chk.get("rows") or [])
           if (r.get("script") or {}).get("scope_switch_tokens")]
    bad.extend(m.face_problems(face))
    check(len(pop) == len(rows), "the population no longer matches E573's scope-switch rows "
                                 "(%d vs %d)" % (len(pop), len(rows)))
    check(s.get("corpus_executions", 0) >= 1,
          "no chain execution was read, so the arm that decides did not run")
    for r in rows:
        for x in (r.get("call_arm") or {}).get("executions") or []:
            line = x.get("line", "")
            if "git add" in line or "Select-String" in line:
                bad.append("r%s: a mention was published as an execution" % r.get("round"))
                break
            if not m.EXEC_LINE.search(line):
                bad.append("r%s: a published witness is not an interpreter launch"
                           % r.get("round"))
                break
    doc = json.loads(json.dumps(face))
    if doctor:
        for r in doc.get("rows") or []:
            if r.get("class") == m.C_FLAG and (r.get("call_arm") or {}).get("executions"):
                r["call_arm"]["executions"] = []
                r["call_arm"]["with_switch"] = 0
                break
        if not m.face_problems(doc):
            bad.append("a passing row whose executions were emptied was accepted")
    detail = ("rows=%d passed=%d without_it=%d none=%d off_host=%d "
              "| corpus_executions=%d with_flag=%d mentions_not_executions=%d | %s"
              % (s.get("rows", 0),
                 s.get("by_class", {}).get(m.C_FLAG, 0),
                 s.get("by_class", {}).get(m.C_NOFLAG, 0),
                 s.get("by_class", {}).get(m.C_NONE, 0),
                 s.get("by_class", {}).get(m.C_OFF, 0),
                 s.get("corpus_executions", 0), s.get("corpus_executions_with_flag", 0),
                 s.get("corpus_mentions_that_do_not_execute", 0), face.get("verdict")))
    if doctor:
        verdict_ok = not bad
        print("%s %s" % ("PASS (red as designed)" if verdict_ok else "FAIL (doctor stayed green)",
                         detail))
        return 0 if verdict_ok else 1
    print("%s %s" % ("PASS" if not bad else "FAIL", "; ".join(bad)[:240] or detail))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())