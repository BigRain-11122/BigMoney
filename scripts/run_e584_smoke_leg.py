"""Run just the E584 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e584_smoke_leg.py            # expect PASS
  python scripts/run_e584_smoke_leg.py --doctor   # relabel a duplicate row as an accruing one,
                                                  # expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LATEST = os.path.join(ROOT, "results", "state_tilt", "ledgerbars_latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e584_ledger_bar_accrual")
    face = json.load(open(LATEST, encoding="utf-8"))
    led = json.load(open(LEDGER, encoding="utf-8"))
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    bad.extend(m.face_problems(face))

    # the population on the face must be the ledger's own rows, not a remembered count
    check(len(rows) == len(led.get("bars") or []),
          "the face's rows are not the ledger's rows")
    check([r.get("bar") for r in rows] == [b.get("bar") for b in led.get("bars") or []],
          "the face's bars are not the ledger's bars in order")
    check(s.get("capital_cny") == (led.get("seed") or {}).get("capital_cny"),
          "the capital the duplicate is priced on is not the ledger's seed capital")
    # a record with no duplicate must not charge itself for one
    if not s.get("duplicated_bars"):
        check(abs(float(s.get("duplicating_extra_carry") or 0.0)) < 1e-15,
              "a record with no duplicated bar still books extra carry")
        check(abs(float(s.get("bar_count_inflation_pct") or 0.0)) < 1e-9,
              "a record with no duplicated bar reports a bar-count inflation")
    # every multi-day gap must be classed somewhere, never silently absent
    multi = [r for r in rows if (r.get("gap_days") or 0) > 1 and not r.get("is_duplicate")]
    check(all(r.get("class") in (m.C_GAP, m.C_UNDER, m.C_NEG, m.C_NO_RATE) for r in multi),
          "a multi-day gap carries no class")

    doc = json.loads(json.dumps(face))
    if doctor:
        for r in doc.get("rows") or []:
            if r.get("is_duplicate"):
                r["class"] = m.C_GAP
                break
        else:                                    # no duplicate on disk: forge one
            dup = dict(doc["rows"][-1])
            dup["is_duplicate"] = True
            dup["class"] = doc["rows"][-1]["class"]
            doc["rows"].append(dup)
    ok = not m.face_problems(doc) and not bad
    if doctor:
        print("DOCTOR %s (a duplicate row relabelled as an accruing row was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1

    print("%s rows=%d distinct=%d dup=%d gaps=%d multi_day=%d no_ref=%d extra_cny=%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("rows_published", 0), s.get("distinct_bars", 0),
             s.get("duplicated_bars", 0), s.get("rows_that_pay_the_calendar_gap", 0),
             s.get("multi_day_gaps", 0), s.get("rows_without_a_reference_rate", 0),
             s.get("duplicating_extra_cny"), face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())