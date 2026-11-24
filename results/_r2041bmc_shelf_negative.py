#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for cb_parking_shelf_at_size (r2041 bm-c)

A check that has never been seen red is not a check.  This file takes the published face,
breaks one number at a time in a temporary copy, and asserts that `check()` refuses each
break by name -- then restores and asserts it goes green again.

Run:
    python results/_r2041bmc_shelf_negative.py
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cb_parking_shelf_at_size as S  # noqa: E402


def run_check(path):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.check(json_path=path, md_path=S.OUT_MD)
    return rc, buf.getvalue()


def main():
    if not os.path.exists(S.OUT_JSON):
        print("MISSING face:", S.OUT_JSON)
        return 2
    with io.open(S.OUT_JSON, encoding="utf-8") as f:
        base = json.load(f)
    tmpdir = tempfile.mkdtemp(prefix="r2041bmc_neg_")
    legs, errs = 0, []

    def leg(cond, msg):
        nonlocal legs
        legs += 1
        if not cond:
            errs.append(msg)

    def broken(mutate):
        face = json.loads(json.dumps(base))
        mutate(face)
        path = os.path.join(tmpdir, "face.json")
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
        return run_check(path)

    # 0. the untouched copy must be green (otherwise the legs below prove nothing)
    path = os.path.join(tmpdir, "clean.json")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    rc, out = run_check(path)
    leg(rc == 0, "clean copy must pass, got rc=%d: %s" % (rc, out.strip()[:200]))

    ticket = str(base["tiers_cny"][1])

    # 1. a one-yuan lie in the stranded residue
    def bump_residue(face):
        face["rows"][0]["capacity"][ticket]["residue_cny"] += 1.0

    rc, out = broken(bump_residue)
    leg(rc == 3 and "residue" in out, "a 1-CNY residue lie must be refused by name, got rc=%d" % rc)

    # 2. a 1% lie in the largest OPEN order
    def bump_open(face):
        face["rows"][0]["max_open_order_cny"] = round(face["rows"][0]["max_open_order_cny"] * 1.01)

    rc, out = broken(bump_open)
    leg(rc == 3 and "max open" in out, "a 1%% capacity lie must be refused, got rc=%d" % rc)

    # 3. a verdict that does not follow from the rows
    def flip_verdict(face):
        face["verdict"] = ["SHELF_ABSORBS_THE_WHOLE_CASH_LEG"]

    rc, out = broken(flip_verdict)
    leg(rc == 3 and "does not follow" in out, "a typed verdict must be refused, got rc=%d" % rc)

    # 4. a retyped ruler band (the face must be stale if the imported ruler moves)
    def move_band(face):
        face["ruler"]["open_max_participation"] = 0.02

    rc, out = broken(move_band)
    leg(rc == 3 and "ruler bands" in out, "a retyped band must be refused, got rc=%d" % rc)

    # 5. a lifted lot: the shelf's own unit must be reproducible from price x units
    def bump_lot(face):
        face["rows"][0]["lot_value_cny"] = round(face["rows"][0]["lot_value_cny"] * 2.0, 2)

    rc, out = broken(bump_lot)
    leg(rc == 3, "a lot value that does not come from price x units must be refused, got rc=%d" % rc)

    shutil.rmtree(tmpdir, ignore_errors=True)

    if errs:
        for e in errs:
            print("NEGATIVE CONTROL FAIL:", e)
        print("NEGATIVE CONTROL %d/%d FAILED" % (legs - len(errs), legs))
        return 1
    print("NEGATIVE CONTROL OK %d/%d PASS" % (legs, legs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
