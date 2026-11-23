#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative control for scripts/verified_lines_money_caliber.py (r2002, bm-c).

A check that only ever prints CHECK OK is not a check.  This harness copies the
published face to a scratch path, plants four independent defects, and asserts
the real ``check``/``verdict_of`` machinery goes red on each one -- then leaves
the published face byte-identical.

Legs
----
  N1  plant the r2001 defect again (L2 read as its annualised rate): the check
      must name the row and fail.
  N2  plant the r2001 defect again (L3 read as its simple sum): same.
  N3  off-by-one-basis-point recovery: verdict_of must REFUSE, not round it away.
  N4  a missing line read as zero: mean_row must not silently produce a number.
  N5  after every plant is undone, the face on disk is byte-identical.
"""
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import verified_lines_money_caliber as C  # noqa: E402

FACE = C.OUT
SCRATCH = os.path.join(ROOT, "results", "_r2002bmc_caliber_negative_face.json")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" :: " + detail) if detail else ""))
    return bool(ok)


def main() -> int:
    if not os.path.exists(FACE):
        print("FAIL face missing: %s" % FACE)
        return 2
    before = sha(FACE)
    legs = []

    with open(FACE, encoding="utf-8") as fh:
        base = json.load(fh)

    def run_check_on(face_obj):
        """Drive the real cmd_check against a scratch face, return (rc, text)."""
        with open(SCRATCH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face_obj, fh, ensure_ascii=False)
        old = C.OUT
        C.OUT = SCRATCH
        try:
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = C.cmd_check()
            return rc, buf.getvalue()
        finally:
            C.OUT = old

    # N0 sanity: the unmodified face passes, so a red below means the plant
    rc0, txt0 = run_check_on(base)
    legs.append(check("N0 untouched face passes the real check", rc0 == 0, txt0.strip()[:120]))

    # N1: re-introduce the r2001 reading of L2 (annualised instead of total)
    n1 = json.loads(json.dumps(base))
    for row in n1["rows"]:
        row["corrected"]["L2_astock_veto"] = row["published"]["L2_astock_veto"]
    rc1, txt1 = run_check_on(n1)
    legs.append(check("N1 L2 read as its annualised rate -> check red", rc1 != 0,
                      "rc=%d" % rc1))

    # N2: re-introduce the r2001 reading of L3 (simple sum instead of total)
    n2 = json.loads(json.dumps(base))
    for row in n2["rows"]:
        row["corrected"]["L3_idx_carry"] = row["published"]["L3_idx_carry"]
    rc2, txt2 = run_check_on(n2)
    legs.append(check("N2 L3 read as its simple sum -> check red", rc2 != 0, "rc=%d" % rc2))

    # N3: a one-basis-point error must be refused by the verdict gate
    fake = json.loads(json.dumps(base["proof"]))
    fake["L2_astock_veto"]["abs_delta"] = 1e-4
    v = C.verdict_of({"state": "OK", "proof": fake})
    legs.append(check("N3 1bp-off L2 recovery -> REFUSE", v == "REFUSE_L2_NOT_AN_IDENTITY", v))

    fake2 = json.loads(json.dumps(base["proof"]))
    fake2["L3_idx_carry"]["abs_delta_pct"] = 1.0
    v2 = C.verdict_of({"state": "OK", "proof": fake2})
    legs.append(check("N3b 1pp-off L3 recovery -> REFUSE", v2 == "REFUSE_L3_NOT_AN_IDENTITY", v2))

    # N4: a missing line must never be read as zero
    legs.append(check("N4 mean_row([0.02, None, 0.04]) == 0.03, not 0.02",
                      abs(C.mean_row([0.02, None, 0.04]) - 0.03) < 1e-12))
    legs.append(check("N4b mean_row([None, None]) is None", C.mean_row([None, None]) is None))

    # N5: the published face is untouched
    after = sha(FACE)
    legs.append(check("N5 published face byte-identical after the plants", before == after,
                      "%s -> %s" % (before[:12], after[:12])))

    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)

    print("%d/%d PASS" % (sum(1 for x in legs if x), len(legs)))
    return 0 if all(legs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
