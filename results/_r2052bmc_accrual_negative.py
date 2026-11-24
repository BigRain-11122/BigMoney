#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative control for money_accrual_level_decomposition (r2052 bm-c).

A ruler that cannot fail is not a ruler.  These legs take the face's own functions and feed
them series whose answer is known in advance, so a green run proves the ruler discriminates:

  N1 false positive -- a pure accrual series must read ACCRUAL_EXPLAINS_THE_RETURN and
     must NOT be tagged as a reset artifact.
  N2 true positive  -- a series whose entire printed return is a handful of jump bars must
     be tagged LEVEL_PART_IS_A_RESET_ARTIFACT (raw level material, trimmed level collapses).
  N3 discrimination -- a level part built from 40% of the bars must survive trimming
     (LEVEL_PART_SURVIVES_TRIMMING): the artifact tag is not "any big level".
  N4 contract       -- tampering one printed row while the panel is unchanged must return
     CHECK FAILED (rc1) and must not borrow the word STALE (r1934).

Run:  python results/_r2052bmc_accrual_negative.py
"""

from __future__ import annotations

import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import money_accrual_level_decomposition as F  # noqa: E402

LEGS = 0
FAILS = []


def chk(ok, msg):
    global LEGS
    LEGS += 1
    if not ok:
        FAILS.append(msg)


def main() -> int:
    # N1: pure accrual, no jumps
    clean = F.decompose(F._series(mode="clean"))
    rows = [dict(clean, code="CLEAN", trimmed_level_pp=clean["trimmed_level_pp"])]
    chk(F.verdict_of([clean["level_pp"]]) == "ACCRUAL_EXPLAINS_THE_RETURN",
        "N1 verdict: pure accrual must read ACCRUAL_EXPLAINS, got %s"
        % F.verdict_of([clean["level_pp"]]))
    chk("LEVEL_PART_IS_A_RESET_ARTIFACT" not in F.tags_of(rows, set()),
        "N1 tag: pure accrual must not be called an artifact")

    # N2: the printed return is a few jump bars
    reset = F.decompose(F._series(mode="reset"))
    chk(abs(reset["level_pp"]) >= F.MATERIAL_PP,
        "N2 raw: reset series must print a material level, got %.2f" % reset["level_pp"])
    chk(abs(reset["trimmed_level_pp"]) < F.MILD_PP,
        "N2 trimmed: reset series' trimmed level must collapse, got %.2f" % reset["trimmed_level_pp"])
    chk("LEVEL_PART_IS_A_RESET_ARTIFACT" in F.tags_of([dict(reset, code="RESET")], set()),
        "N2 tag: reset artifact must be tagged")

    # N3: a level part built from many bars survives trimming
    skew = F.decompose(F._series(mode="skewed"))
    chk(abs(skew["trimmed_level_pp"]) >= F.MILD_PP,
        "N3 trimmed: a 40%%-of-bars level must survive, got %.2f" % skew["trimmed_level_pp"])
    chk("LEVEL_PART_SURVIVES_TRIMMING" in F.tags_of([dict(skew, code="SKEW")], set()),
        "N3 tag: a many-bar level must not be called an artifact")

    # N4: tampering one row must be CHECK FAILED, never STALE
    face = F.build()
    F.write_doc(face)
    dirty = copy.deepcopy(face)
    dirty["rows"][0]["accrual_pp"] = float(dirty["rows"][0].get("accrual_pp") or 0.0) + 0.5
    rc, msg = F.check(dirty)
    chk(rc == 1 and "CHECK FAILED" in msg, "N4 rc: tampered row must be rc1, got rc%d" % rc)
    chk(not msg.startswith("STALE"), "N4 word: tampered row must not say STALE, got %s" % msg[:40])

    # N5: an unchanged face must be green (a control that always fails is not a control)
    rc2, msg2 = F.check(face)
    chk(rc2 == 0, "N5 green: unchanged face must be rc0, got rc%d %s" % (rc2, msg2[:60]))

    print("negative control: %d legs, %d failed" % (LEGS, len(FAILS)))
    for f in FAILS:
        print("  FAIL " + f)
    print("RESULT: " + ("ALL PASS" if not FAILS else "FAILED"))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
