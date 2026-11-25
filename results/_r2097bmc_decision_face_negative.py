#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for scripts/idx_fut_carry_decision_face.py (r2097, bm-c)

Every leg here is a way for this face to lie, and the assertion is that it refuses. The
inputs are copies on disk; the real module globals (INPUTS / FACE_REL) are pointed at the
copies, so the real derive() and the real check() run -- not a re-implementation (r1935:
a check that only re-derives its own output can never say it is stale).

Legs:
  N1  a hand-edited number in the published face is a CHECK FAILED, and the message does
      NOT contain the word STALE (r1850: that word is a contract -- it buys a rebuild)
  N2  a moved admitted-ruler number with the face itself unchanged is STALE
  N3  a missing input face refuses (DATA_BLOCKED), it does not default to zero
  N4  flip IC's roll verdicts to PARTIAL_REVERSAL -> IC loses its quotable rate too
      (the gate is the accounting, so it must react to the accounting face alone)
  N5  fund the book to the first rung -> the capital gate clears on the same numbers
  N6  capacity to 0.4 lots -> liquidity gate, not the capital gate
  N7  the published face never carries a single-point rate for a product with no
      admitted ruler (ann_pct_band must be None, not a number)

Run: python results/_r2097bmc_decision_face_negative.py
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import idx_fut_carry_decision_face as F  # noqa: E402


def _load(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _dump(tmp, name, obj):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    return path


def main():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    base = {k: _load(v) for k, v in F.INPUTS.items()}
    published = _load(F.FACE_REL)
    tmp = tempfile.mkdtemp(prefix="r2097bmc_neg_")

    # N1 -- hand-edited output, inputs untouched
    poisoned = copy.deepcopy(published)
    poisoned["products"]["IC"]["capital"]["gap_cny"] = 1.0
    F.FACE_REL = _dump(tmp, "n1.json", poisoned)
    rc = F.check(quiet=True)
    leg("N1 hand-edited number -> CHECK FAILED (rc1)", rc == 1, "rc=%r" % rc)

    # N2 -- inputs moved, output untouched
    moved = copy.deepcopy(base)
    ic_cal = moved["price"]["products"]["IC"]["rulers"]["calendar"]
    ic_cal["always_on_ann_pct"] = round(ic_cal["always_on_ann_pct"] + 0.37, 4)
    paths = {k: _dump(tmp, "n2_%s.json" % k, v)
             for k, v in moved.items()}
    F.INPUTS = paths
    F.FACE_REL = _dump(tmp, "n2_face.json", published)
    rc = F.check(quiet=True)
    leg("N2 moved ruler number -> STALE (rc3)", rc == 3, "rc=%r" % rc)

    # N3 -- missing input
    missing = dict(paths)
    missing["roll"] = "results/__does_not_exist__.json"
    F.INPUTS = missing
    face = F.derive()
    leg("N3 missing input -> DATA_BLOCKED", face.get("verdict") == "DATA_BLOCKED"
        and "roll" in (face.get("why") or ""), str(face.get("why")))

    # N4 -- IC accounting flips to unsettled
    flipped = copy.deepcopy(base)
    for ruler in ("calendar", "strictest"):
        flipped["roll"]["products"]["IC"]["rulers"][ruler]["verdict"] = "PARTIAL_REVERSAL"
    F.INPUTS = {k: _dump(tmp, "n4_%s.json" % k, v)
                for k, v in flipped.items()}
    face = F.derive()
    ic = face["products"]["IC"]
    leg("N4 IC loses accounting -> no quotable rate", ic["state"] == "accounting_unsettled"
        and ic["quotable_rate"]["ann_pct_band"] is None, str(ic["state"]))
    leg("N4 IC now reports the rejection words it was given",
        sorted(ic["rejected_rulers"]) == ["calendar", "published", "strictest"])

    # N5 -- funded to the rung
    funded = copy.deepcopy(base)
    for prod in ("IC", "IM"):
        funded["open_capital"]["accounts"][prod]["capital_cny"] = 1_200_000.0
    F.INPUTS = {k: _dump(tmp, "n5_%s.json" % k, v)
                for k, v in funded.items()}
    face = F.derive()
    leg("N5 funded -> IC reaches the order gate", face["products"]["IC"]["state"] == "order_allowed",
        str(face["products"]["IC"]["state"]))
    leg("N5 funded -> IM still stopped by accounting, not capital",
        face["products"]["IM"]["state"] == "accounting_unsettled",
        str(face["products"]["IM"]["state"]))
    leg("N5 funded -> book token is still NO_ORDER (one leg is enough)",
        face["verdict"] == "NO_ORDER_ON_SOME_LEGS", str(face["verdict"]))

    # N6 -- thin market
    thin = copy.deepcopy(funded)
    thin["capacity"]["products"]["IC"]["capacity"]["adopted_lots"] = 0.4
    F.INPUTS = {k: _dump(tmp, "n6_%s.json" % k, v)
                for k, v in thin.items()}
    face = F.derive()
    leg("N6 0.4 lots -> liquidity gate", face["products"]["IC"]["state"] == "market_too_thin",
        str(face["products"]["IC"]["state"]))

    # N7 -- IM must never carry a number it cannot defend
    im = published["products"]["IM"]
    leg("N7 published IM quotes no rate", im["quotable_rate"]["ann_pct_band"] is None
        and im["quotable_rate"]["excess_over_parking_cny_band"] is None)
    leg("N7 published IM still names what would change it",
        bool(im["what_would_change_it"]))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  <- %s" % detail) if detail and not ok else ""))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
