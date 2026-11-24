#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for cash_shelf_build_out_plan (r2043, bm-c)

Three things are proven here, none of which the face's own selftest can prove because
they involve the published artifact and the real panel:

  1. the published face can FAIL its own check -- flip one decimal and rc must be 1
     (a check that cannot fail is not a check, r1282 family)
  2. a moved upstream face is reported as STALE, not as a defect (r1935 family)
  3. the slippage reader actually tracks the tape -- add a known drift to the price
     index and the measured slippage must grow by that drift x the average holding
     time, not stay put

Run:  python results/_r2043bmc_buildout_negative.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402

import cash_shelf_build_out_plan as F  # noqa: E402

FACE = F.OUT_JSON
UPSTREAM = F.R2041_JSON
fails = []


def chk(ok, msg):
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def main():
    print("[1] the published face must pass its own check as published")
    rc = F.check()
    chk(rc == 0, "baseline check rc=0 (got %d)" % rc)

    print("[2] flip one published decimal -> check must fail with rc=1")
    bak = FACE + ".negbak"
    shutil.copyfile(FACE, bak)
    try:
        with io.open(FACE, encoding="utf-8") as f:
            pub = json.load(f)
        row = next(r for r in pub["rows"] if r["code"] == "511380")
        before = row["tiers"]["565246"]["slip_p95_bp"]
        row["tiers"]["565246"]["slip_p95_bp"] = round(before + 0.5, 4)
        with io.open(FACE, "w", encoding="utf-8") as f:
            json.dump(pub, f, ensure_ascii=False, indent=2)
            f.write("\n")
        rc2 = F.check()
        chk(rc2 == 1, "a +0.5bp edit must fail the check with rc=1 (got %d)" % rc2)
    finally:
        shutil.copyfile(bak, FACE)
        os.remove(bak)
    chk(F.check() == 0, "restoring the published face returns the check to rc=0")

    print("[3] a moved upstream face must be STALE, not a defect")
    backup = UPSTREAM + ".negbak"
    shutil.copyfile(UPSTREAM, backup)
    try:
        with io.open(UPSTREAM, "rb") as f:
            blob = f.read()
        with io.open(UPSTREAM, "wb") as f:
            f.write(blob + b"\n")
        rc3 = F.check()
        chk(rc3 == 3, "a touched upstream must return rc=3 (got %d)" % rc3)
    finally:
        shutil.copyfile(backup, UPSTREAM)
        os.remove(backup)
    chk(F.check() == 0, "restoring the upstream returns the check to rc=0")

    print("[4] the slippage reader must track the tape")
    flat = np.ones(400)
    base = float(np.max(np.abs(F.batch_slippage_bp(flat, 5))))
    chk(base == 0.0, "a perfectly flat tape gives exactly zero slippage (got %.6f)" % base)
    drift_per_day = 1e-4                      # +1bp per session
    ramp = np.cumprod(np.full(400, 1.0 + drift_per_day))
    s = F.batch_slippage_bp(ramp, 5)
    # equal cash over n sessions against a constant +1bp/session ramp averages the
    # sessions 0..n-1, i.e. about (n-1)/2 sessions of drift = 2bp for n=5
    expect = drift_per_day * (5 - 1) / 2.0 * 1e4
    chk(abs(float(np.median(s)) - 2.0) < 0.35,
        "a 1bp/session ramp over 5 sessions must land near %.2fbp (got %.3f)"
        % (expect, float(np.median(s))))
    doubled = F.batch_slippage_bp(np.cumprod(np.full(400, 1.0 + 2 * drift_per_day)), 5)
    chk(abs(float(np.median(doubled)) - 2.0 * float(np.median(s))) < 0.01,
        "doubling the drift must double the measured slippage")

    print("[5] the harmonic mean must beat the arithmetic mean when batching up-trends")
    two = F.harmonic_mean([100.0, 101.0])
    arith = (100.0 + 101.0) / 2.0
    chk(two < arith, "harmonic %.4f must be below arithmetic %.4f" % (two, arith))

    print("")
    if fails:
        print("NEGATIVE CONTROL FAILED (%d)" % len(fails))
        return 1
    print("NEGATIVE CONTROL OK  6 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
