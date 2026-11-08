"""Run just the E583 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e583_smoke_leg.py            # expect PASS
  python scripts/run_e583_smoke_leg.py --doctor   # price a stale sheet as if it named its own bar,
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

LATEST = os.path.join(ROOT, "results", "state_tilt", "repricedtickets_latest.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e583_ticket_repricing")
    face = json.load(open(LATEST, encoding="utf-8"))
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    bad.extend(m.face_problems(face))

    check(s.get("tickets_total") == len(rows),
          "the summary ticket count does not match the published rows")
    check(s.get("tickets_without_an_order_sheet", 0) + s.get("order_sheets", 0) == len(rows),
          "the no-sheet count does not re-derive from the population")
    check((s.get("sheets_priced_on_the_bar_they_name", 0)
           + s.get("sheets_priced_on_an_earlier_bar", 0)
           + s.get("sheets_priced_on_a_later_bar", 0)) == s.get("order_sheets"),
          "the sheet classes do not cover every order sheet")
    check(s.get("legs_total") == sum((s.get("leg_adjudication") or {}).values()),
          "the leg count does not re-derive from the leg classes")
    check(all(r.get("class") in m.CLASSES for r in rows),
          "a ticket carries a class the study does not define")
    # the two arms answer different questions and must not be collapsed into one
    check(all((r.get("money") or {}).get("keep_shares_at_named_bar") is not None
              and (r.get("money") or {}).get("reissued_at_named_bar") is not None
              for r in rows if r.get("class") != m.C_NO_SHEET),
          "an order sheet publishes only one of the two money arms")
    # a stale sheet must not be counted as priced on its own bar
    stale = [r for r in rows if r.get("class") == m.C_EARLIER]
    check(all((r.get("leg_classes") or {}).get(m.L_DECISION, 0) > 0 for r in stale),
          "a sheet called priced-on-an-earlier-bar names no leg priced at the decision bar")

    doc = json.loads(json.dumps(face))
    if doctor:
        for r in doc.get("rows") or []:
            if r.get("class") == m.C_EARLIER:
                r["class"] = m.C_OWN
                break
    ok = not m.face_problems(doc) and not bad
    if doctor:
        print("DOCTOR %s (a sheet priced on an earlier bar, relabelled as priced on the bar it "
              "names, was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1

    print("%s tickets=%d sheets=%d on_their_bar=%d earlier=%d legs=%d keep_delta_cny=%.2f "
          "worst=%.2f%% | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("tickets_total", 0), s.get("order_sheets", 0),
             s.get("sheets_priced_on_the_bar_they_name", 0),
             s.get("sheets_priced_on_an_earlier_bar", 0), s.get("legs_total", 0),
             s.get("keep_shares_delta_cny_total") or 0.0,
             s.get("keep_shares_delta_pct_nav_worst") or 0.0,
             face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())