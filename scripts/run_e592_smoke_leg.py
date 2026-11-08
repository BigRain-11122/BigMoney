"""Run just the E592 leg of smoke_test.py without launching the other legs.

smoke_test.py has no leg filter (r1499), so a leg is exercised by re-running its assertions from
here.  This file mirrors the block at the end of smoke_test.py; if the two ever disagree, the block
in smoke_test.py is the one the suite runs.

  python scripts/run_e592_smoke_leg.py            # expect PASS
  python scripts/run_e592_smoke_leg.py --doctor   # move one replayed rate so it no longer
                                                  # re-derives its own gap, expect RED
"""
from __future__ import annotations

import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FACE = os.path.join(ROOT, "results", "etf_book_forward", "CARRYPHASE.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")

bad = []


def check(cond, why):
    if not cond:
        bad.append(why)


def main():
    doctor = "--doctor" in sys.argv[1:]
    m = importlib.import_module("e592_carry_phase")
    face = json.load(open(FACE, encoding="utf-8"))
    bad.extend(m.face_problems(face))

    ledger_bars = [b.get("bar") for b in
                   (json.load(open(LEDGER, encoding="utf-8")).get("bars") or [])]
    rows = face.get("bars") or []
    if rows:
        check(set(r.get("bar") for r in rows) <= set(ledger_bars),
              "the face measures a bar the ledger does not publish")

    arms = face.get("arms") or {}
    a = arms.get("published_origin") or {}
    b = arms.get("fresh_phase_at_first_bar") or {}
    if a.get("bars_reproduced_at_0_001pct") is not None and \
            b.get("bars_reproduced_at_0_001pct") is not None:
        check(int(a["bars_reproduced_at_0_001pct"]) > int(b["bars_reproduced_at_0_001pct"]),
              "replaying from the face's own origin reproduces no more bars than a fresh phase")

    doc = json.loads(json.dumps(face))
    if doctor:
        if doc.get("bars"):
            first = doc["bars"][0]
            first["replayed_rate_per_bar"] = round(
                float(first["replayed_rate_per_bar"]) * 1.05, 12)
        else:
            check(False, "nothing on disk to doctor")
    ok = not bad and not m.face_problems(doc)
    if doctor:
        print("DOCTOR %s (a replayed rate that no longer re-derives its own gap was %s)"
              % ("RED as expected" if not ok else "WRONGLY ACCEPTED",
                 "refused" if not ok else "accepted"))
        return 0 if not ok else 1

    res = face.get("residual") or {}
    prod = (face.get("sweep") or {}).get("product") or {}
    print("%s bars=%d reproduced=%d/%d max_gap=%.4f%% precision=%.4f%% fresh_phase=%s "
          "phase_class=%s/%s | %s"
          % ("FAIL " + "; ".join(bad)[:240] if bad else "PASS",
             res.get("bars_judged") or 0, res.get("bars_reproduced_at_0_001pct") or 0,
             res.get("bars_judged") or 0, res.get("max_abs_gap_pct") or 0.0,
             res.get("max_printed_precision_pct") or 0.0,
             b.get("bars_reproduced_at_0_001pct"),
             prod.get("phases_reproducing_every_bar"), prod.get("phases_tested"),
             face.get("verdict")))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())