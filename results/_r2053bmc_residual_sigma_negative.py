#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for r2053 bm-c: money_residual_sigma_recovery.

Each leg is a way the published face could be wrong while still printing a verdict.
Run:  python results/_r2053bmc_residual_sigma_negative.py
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import money_residual_sigma_recovery as F  # noqa: E402

FACE = os.path.join(ROOT, F.FACE)


def tape(n=400, accrue_bp=0.5, noise_bp=0.2, seed=5, bumps=()):
    """A calm money tape with optional (position, bp) one-bar bumps."""
    rng = np.random.default_rng(seed)
    px = [100.0]
    for _ in range(n):
        px.append(px[-1] * (1.0 + (accrue_bp + rng.normal(0.0, noise_bp)) / 1e4))
    for pos, bp in bumps:
        for j in range(pos, len(px)):
            px[j] *= (1.0 + bp / 1e4)
    return pd.Series(px, index=pd.bdate_range("2021-01-04", periods=len(px)))


def main() -> int:
    fails, n_ok = [], 0

    def ok(cond, msg):
        nonlocal n_ok
        if cond:
            n_ok += 1
        else:
            fails.append(msg)

    # L1 the reader is a pure function of the series
    a = F.read_one(tape(seed=7, bumps=((200, -80.0),)))
    b = F.read_one(tape(seed=7, bumps=((200, -80.0),)))
    ok(a == b, "L1 read_one is not deterministic")

    # L2 inflation is computed, not asserted: a calm tape sits near 1, a spiked one does not
    calm = F.read_one(tape(seed=3))
    spiked = F.read_one(tape(seed=3, bumps=((200, -900.0), (201, 890.0))))
    ok(calm["inflation"] is not None and calm["inflation"] < 2.0,
       "L2a calm tape inflation %.2f" % (calm["inflation"] or 0))
    ok(spiked["inflation"] is not None and spiked["inflation"] > calm["inflation"],
       "L2b a spike did not raise the plain sigma more than the robust one")

    # L3 the contamination split follows accrual speed only
    ok(F.read_one(tape(accrue_bp=8.0))["equity_speed"] is True,
       "L3a an 8 bp/day tape was not called equity speed")
    ok(F.read_one(tape(accrue_bp=0.5))["equity_speed"] is False,
       "L3b a 0.5 bp/day tape was called equity speed")

    # L4 the 20 bp floor binds on a dead-flat tape
    flat = pd.Series(100.0, index=pd.bdate_range("2021-01-04", periods=400))
    e19 = F.classify_events(flat.copy().where(flat.index != flat.index[200], 99.81))   # -19 bp
    e21 = F.classify_events(flat.copy().where(flat.index != flat.index[200], 99.79))   # -21 bp
    ok(all(abs(e["bar_bp"]) >= F.MIN_BAR_BP for e in e19), "L4a a -19 bp bar passed the floor")
    ok(any(abs(e["bar_bp"]) >= F.MIN_BAR_BP for e in e21), "L4b a -21 bp bar did not pass the floor")

    # L5 NEVER needs a gap bigger than carry can rebuild -- the face says so, and it holds
    small = F.classify_events(tape(accrue_bp=0.5, bumps=((200, -80.0),)))
    huge = F.classify_events(tape(accrue_bp=0.5, bumps=((200, -2000.0),)))
    ok(any(e["shape"] == "ACCRUAL_PACED" for e in small),
       "L5a an 80 bp drop on a 0.5 bp clock was not read as accrual-paced: %s" % small[:2])
    ok(any(e["shape"] == "NEVER" for e in huge), "L5b a -20%% drop was not read as NEVER")

    # L6 swap the estimator and the verdict must move: the tag depends on it
    real = F.robust_sigma_bp
    try:
        F.robust_sigma_bp = lambda ret_bp: float(np.std(ret_bp, ddof=1))
        same = F.read_one(tape(seed=3, bumps=((200, -900.0), (201, 890.0))))
    finally:
        F.robust_sigma_bp = real
    ok(abs((same["inflation"] or 0) - 1.0) < 0.02,
       "L6 plain-as-robust estimator did not collapse inflation to 1 (%.2f)" % (same["inflation"] or 0))

    # L7 the published face is the census money set minus the equity-speed names
    with open(FACE, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    priced = [r for r in face["rows"] if r.get("priced")]
    money = [r for r in face["rows"] if r.get("priced") and not r.get("equity_speed")]
    ok(len(priced) == face["universe"]["money_priced"] + face["universe"]["equity_speed_excluded"],
       "L7a priced rows do not add up to money + excluded")
    ok(len(money) == face["universe"]["money_priced"], "L7b the money subset size moved")
    ok(all(("现金流" in (r.get("name") or "")) or r["accrual_bp"] >= F.EQUITY_SPEED_BP
           for r in face["rows"] if r.get("priced") and r.get("equity_speed")),
       "L7c an excluded row is neither cash-flow named nor equity-speed")

    # L8 dropping the contamination really moves the shelf median (why the split exists)
    infl_all = sorted(r["inflation"] for r in priced if r.get("inflation"))
    infl_money = sorted(r["inflation"] for r in money if r.get("inflation"))
    med_all = float(np.median(infl_all))
    med_money = float(np.median(infl_money))
    ok(abs(med_all - face["headline"]["inflation_median"]) > 1e-9,
       "L8a the published median is already the filtered one (no contamination effect)")
    ok(med_money >= med_all, "L8b filtering raised the median -- direction is suspicious")

    # L9 the six accrual-paced events all come from vehicles with a real clock
    ap = [(r["code"], e) for r in money for e in r["events"] if e["shape"] == "ACCRUAL_PACED"]
    ok(all(any(r["code"] == code and r["has_usable_clock"] for r in money) for code, _ in ap),
       "L9 an accrual-paced event came from a vehicle with no clock")
    ok(all(F.PACE_LO <= e["pace_ratio"] <= F.PACE_HI for _, e in ap),
       "L9b an accrual-paced event sits outside the frozen pace band")

    # L10 the doc block prints this face's own verdict
    with open(os.path.join(ROOT, F.DOC), "r", encoding="utf-8") as fh:
        block = F._block_of(fh.read())
    ok("`%s`" % face["verdict"] in block and "`%s`" % face["shape_verdict"] in block,
       "L10 the published doc does not carry the face's verdicts")

    print("negative control %d/%d PASS" % (n_ok, n_ok + len(fails)))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
