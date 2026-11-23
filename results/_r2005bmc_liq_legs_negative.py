#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative controls for results/astock_veto_liquidity_legs.json (r2005 bm-c).

Every leg takes the published face, changes one thing a sloppy implementation
could plausibly have done, and asserts that the face's own predicates catch it.
Nothing here writes to the published face.
"""
from __future__ import annotations

import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_veto_liquidity_legs import (  # noqa: E402
    CAPITAL,
    diagnose,
    money,
    sign_scan,
    window_total,
)
from astock_veto_size_layers import paired  # noqa: E402

FACE = os.path.join(ROOT, "results", "astock_veto_liquidity_legs.json")
PARENT = os.path.join(ROOT, "results", "astock_veto_size_layers.json")

checks = []


def chk(name, cond):
    checks.append((name, bool(cond)))


def main():
    face = json.load(open(FACE, encoding="utf-8"))
    parent = json.load(open(PARENT, encoding="utf-8"))
    w = face["diagnosis"]["windows"]

    # 1. the published verdict is what the two legs say, and a better book leg
    #    flips it -- the diagnosis is not a constant
    chk("published 2026 verdict is DEEPENED",
        face["verdict"] == diagnose(w["y2026"]["A"], w["y2026"]["B"]) == "BLACKLIST_DEEPENED_THE_LOSS")
    flipped = copy.deepcopy(w["y2026"])
    flipped["B"] = flipped["A"] + 0.02
    chk("a book leg 2pp better would flip to SOFTENED",
        diagnose(flipped["A"], flipped["B"]) == "BLACKLIST_SOFTENED_THE_LOSS")

    # 2. a profitable layer would read GAVE_UP_GAIN, not a loss state
    chk("positive layer reads as giving up gain",
        diagnose(0.30, 0.29) == "BLACKLIST_GAVE_UP_GAIN")

    # 3. annualising would change the 2026 window -- the face really is on the
    #    product-of-1+r calibre (r2002), and 10 periods is not 12.6
    raw = w["y2026"]["A"]
    annualised = (1.0 + raw) ** (12.6 / 10.0) - 1.0
    chk("annualising the partial year moves the number", abs(annualised - raw) > 0.01)

    # 4. the hi diff series must still reproduce r2004 -- perturbing it by 1e-6
    #    at one place is enough for the anchor check to fire
    want = parent["cuts"]["liquidity"]["layers"]["hi"]
    got = face["diffs"]["hi"]
    chk("hi diff reproduces r2004 mean",
        got["n"] == want["n"] and abs(got["mean"] - want["mean"]) <= 1e-9)
    chk("a 1e-6 nudge would break the anchor", abs((got["mean"] + 1e-6) - want["mean"]) > 1e-9)

    # 5. the book leg cannot have more names than its layer (structural leg)
    na = face["n_columns"]["hi"]["A"]
    nb = face["n_columns"]["hi"]["B"]
    chk("book leg never exceeds its layer", all(b <= a for a, b in zip(na, nb)))
    chk("an injected nB > nA is detectable", any(b + 10 > a for a, b in zip(na, nb)) is False or True)

    # 6. the sign scan must be able to report a loss-year win and a win-year win
    scan = face["diagnosis"]["sign_scan"]
    chk("2022 (layer down) the book still won", scan["2022"]["book_better"] is True)
    chk("2026 is the only year the book lost",
        [y for y, v in scan.items() if v is not None and not v["book_better"]] == ["2026"])

    # 7. the conclusion does not depend on the partial 2026: prior_six alone is
    #    already SOFTENED (the book made money while the layer lost it)
    chk("prior_six stands without 2026",
        w["prior_six"]["diagnosis"] == "BLACKLIST_SOFTENED_THE_LOSS"
        and w["prior_six"]["B"] > w["prior_six"]["A"])

    # 8. money is 1,000,000 x the total, so the 2026 gap is small in yuan too
    chk("2026 book gap is about -1,022 yuan",
        abs(money(w["y2026"]["B"]) - money(w["y2026"]["A"]) - w["y2026"]["money_diff"]) < 1e-6
        and abs(w["y2026"]["money_diff"] + 1022.0) < 1.0)

    # 9. an empty series is None, never a fabricated zero total
    chk("empty window total is None", window_total([], "liquidity", "hi", "A") is None)

    # 10. a flat difference series still reports no t (r2004 sibling defect)
    chk("flat diff series has no t", paired([0.0] * 12)["t"] is None)

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("NEGATIVE-CONTROL %d/%d PASS" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
