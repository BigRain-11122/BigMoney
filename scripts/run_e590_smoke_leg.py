"""Run just the E590 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e590_smoke_leg.py            # expect PASS
  python scripts/run_e590_smoke_leg.py --doctor   # reshape a step's gap so its forfeit no longer
                                                  # re-derives, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "etf_book_order", "CASHSILENCE.json")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e590_cash_silence")
    face = json.load(open(FACE, encoding="utf-8"))
    s = face.get("summary") or {}
    bad.extend(m.face_problems(face))

    rows = (face.get("bars_past_the_panel") or {}).get("rows") or []
    ages = [r.get("quote_age_bars") for r in rows]
    if len(set(ages)) > 1:
        check(not s.get("quote_age_is_the_same_on_every_bar_past_the_panel"),
              "a moving age table is published flat")
    tickets = face.get("tickets") or []
    # the population on the face must be the tickets on disk, not a remembered count
    on_disk = sorted(os.path.basename(p) for p in
                     __import__("glob").glob(os.path.join(TICKET_DIR, "TICKET-*.json"))
                     if not os.path.basename(p).endswith("-card.json"))
    check(sorted(t.get("ticket") for t in tickets) == on_disk,
          "the face's tickets are not the tickets on disk")
    for t in tickets:
        if t.get("steps_rederive_the_ticket_block") is False:
            check(False, "%s: the step count disagrees with the ticket's own block"
                  % t.get("ticket"))
        w = t.get("window") or {}
        if w.get("calendar_matches_published_bars") is False:
            check(False, "%s: the calendar misses the ticket's own window_bars"
                  % t.get("ticket"))

    doc = json.loads(json.dumps(face))
    if doctor:
        stepped = [t for t in doc.get("tickets") or [] if t.get("step_rows")]
        if stepped:
            stepped[0]["step_rows"][0]["gap_days"] += 5
        else:                                    # nothing on disk to doctor: forge a step row
            blk = doc["tickets"][0]
            blk["step_rows"] = [{"prev_bar": "2026-01-07", "bar": "2026-01-09", "gap_days": 7,
                                 "nearest_prior_quote_bar": "2026-01-07",
                                 "nearest_prior_quote_pct": 1.09,
                                 "forfeited_at_nearest_quote_cny": 1.0,
                                 "forfeited_at_window_mean_cny": 1.0}]
            blk["unquoted_steps"] = 1
    ok = not m.face_problems(doc) and not bad
    if doctor:
        print("DOCTOR %s (a step whose gap no longer matches its forfeit was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1

    print("%s tickets=%d with_steps=%d steps=%d forfeit=%.2f CNY (%.3f bp) ages=%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             s.get("tickets", 0), s.get("tickets_with_unquoted_steps", 0),
             s.get("unquoted_steps_total", 0),
             s.get("forfeited_at_nearest_quote_cny_total") or 0.0,
             s.get("forfeited_bp_of_that_cash") or 0.0,
             "%s..%s" % (ages[0], ages[-1]) if ages else "-", face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())