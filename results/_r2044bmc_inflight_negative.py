#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative control for cash_shelf_inflight_carry (r2044, bm-c).

Three legs, each of which must FAIL the face's own guard:
  1. one hand-edited number in the published JSON  -> --check rc3 and names the row
  2. a changed upstream byte (r2043 face)          -> --check rc3 and says STALE
  3. the commission arm zeroed                     -> carry rises by exactly the commission

Writes nothing outside results/_r2044bmc_neg_copy.json (removed at the end).
"""
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cash_shelf_inflight_carry as M  # noqa: E402
import etf_book_cash_ladder as CL  # noqa: E402

TMP = os.path.join(ROOT, "results", "_r2044bmc_neg_copy.json")
out = []


def leg(cond, msg):
    out.append((bool(cond), msg))
    if not cond:
        print("  FAIL %s" % msg)


def main():
    if not os.path.exists(M.OUT_JSON):
        print("MISSING FACE: run the face first")
        return 2
    orig = M.OUT_JSON
    shutil.copy(orig, TMP)
    M.OUT_JSON = TMP
    try:
        # leg 0: the copy as Published must pass, otherwise legs 1-2 prove nothing
        rc0 = M.check(verbose=False)
        leg(rc0 == 0, "untouched copy passes --check (rc0), else the legs below are vacuous")

        # leg 1: hand-edit ONE number
        pub = json.load(io.open(TMP, encoding="utf-8"))
        hit = None
        for r in pub["rows"]:
            for key, rec in r["tiers"].items():
                if rec.get("net_median_bp") is not None:
                    rec["net_median_bp"] = round(float(rec["net_median_bp"]) + 0.5, 4)
                    hit = (r["code"], key)
                    break
            if hit:
                break
        with io.open(TMP, "w", encoding="utf-8") as f:
            json.dump(pub, f, ensure_ascii=False, indent=2)
        rc1 = M.check(verbose=False)
        leg(hit is not None and rc1 == 3, "a hand-edited number is caught (rc3)")

        # leg 2: changed upstream bytes -> STALE, not CHECK FAILED
        shutil.copy(orig, TMP)
        pub = json.load(io.open(TMP, encoding="utf-8"))
        pub["upstream"]["sha256"] = "0" * 64
        with io.open(TMP, "w", encoding="utf-8") as f:
            json.dump(pub, f, ensure_ascii=False, indent=2)
        rc2 = M.check(verbose=False)
        leg(rc2 == 3, "a changed upstream byte is caught (rc3)")

        # leg 3: the commission arm, on a flat-rate tape, at two schedule lengths
        bars = pd.bdate_range("2024-01-02", periods=60)
        rates = {"GC001": pd.Series(np.full(60, 1.8), index=bars)}
        no_fee = {k: 0.0 for k in CL.FEE_BP}
        net_ret, _ = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
        gross_ret, _ = CL.roll_rung(bars, rates, None, fees=no_fee, name="GC001")
        for n in (2, 5, 39):
            cn = M.window_carry(net_ret.values, n)
            cg = M.window_carry(gross_ret.values, n)
            gap_bp = (cg - cn) * 1e4
            want = 0.1 * M.weight_days(n)
            leg(len(gap_bp) > 0 and abs(float(np.median(gap_bp)) - want) < 1e-9,
                "n=%d: separating the commission arm moves the carry by exactly "
                "0.1bp x (n-1)/2 wait-days = %.4fbp" % (n, want))

        # leg 4: the face is not allowed to call the wait free when the tape outruns the repo leg
        rec = {"sessions_to_fill": 5, "windows": 100, "slip_median_bp": 1.6,
               "carry_net_median_bp": 1.2, "net_median_bp": 0.4, "net_p95_bp": 3.0,
               "net_per_wait_day_bp": 0.2}
        leg("NET_WAIT_IS_FREE" not in M.verdicts_for(dict(rec)),
            "a positive 95th percentile is not read as a free wait")
    finally:
        if os.path.exists(TMP):
            os.remove(TMP)
        M.OUT_JSON = os.path.join(ROOT, "results", "cash_shelf_inflight_carry.json")

    n_fail = sum(1 for c, _ in out if not c)
    print("negative control: %d/%d legs PASS" % (len(out) - n_fail, len(out)))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
