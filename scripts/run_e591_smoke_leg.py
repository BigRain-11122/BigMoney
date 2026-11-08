"""Run just the E591 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e591_smoke_leg.py            # expect PASS
  python scripts/run_e591_smoke_leg.py --doctor   # reshape one row's CNY so it no longer
                                                  # re-derives from its own carry, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "etf_book_order", "CASHDIVERGE.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e591_cash_diverge")
    face = json.load(open(FACE, encoding="utf-8"))
    s = face.get("summary") or {}
    bad.extend(m.face_problems(face))

    ledger_bars = [b.get("bar") for b in
                   (json.load(open(LEDGER, encoding="utf-8")).get("bars") or [])]
    rows = face.get("bars") or []
    if rows:
        check(set(r.get("bar") for r in rows) <= set(ledger_bars),
              "the face measures a bar the ledger does not publish")
    if s.get("gap_cny_total") and not s.get("bars_where_the_ticket_books"):
        check(False, "a gap is published while the ticket is said to book nothing")

    doc = json.loads(json.dumps(face))
    if doctor:
        if doc.get("bars"):
            doc["bars"][0]["ledger_cny_on_ticket_cash"] = (
                float(doc["bars"][0]["ledger_cny_on_ticket_cash"]) + 7.0)
        else:
            check(False, "nothing on disk to doctor")
    ok = not m.face_problems(doc) and not bad
    if doctor:
        print("DOCTOR %s (a row whose CNY no longer re-derives from its own carry was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1

    rep = face.get("reproducibility") or {}
    print("%s bars=%d ledger=%.2f CNY vs ticket=%.2f (rule %.2f) gap=%.2f (%.3f bp) "
          "ticket_books=%d replay=%s/%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("book_bars_past_the_panel", 0),
             s.get("ledger_cny_total_on_ticket_cash") or 0.0,
             s.get("ticket_actual_cny_total") or 0.0,
             s.get("ticket_rule_cny_total") or 0.0,
             s.get("gap_cny_total") or 0.0,
             s.get("gap_bp_of_ticket_cash") or 0.0,
             s.get("bars_where_the_ticket_books", 0),
             rep.get("bars_reproduced"), rep.get("bars_judged"), face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())