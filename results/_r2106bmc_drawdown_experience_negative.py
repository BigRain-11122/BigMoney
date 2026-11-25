#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for idx_fut_carry_drawdown_experience (r2106 bm-c).

Every other leg of this family ships one; the point is to prove the check *bites* on a
poisoned copy rather than trusting a green self-consistent face (r1282 / r1850 lesson:
a guard that only re-derives itself never says "I am stale").  All mutation is on an
in-memory deep copy -- no shared file is touched.

Run:  python results/_r2106bmc_drawdown_experience_negative.py
"""
from __future__ import annotations

import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import idx_fut_carry_drawdown_experience as E


def main():
    if not os.path.exists(E.OUT):
        print("NO FACE to test: %s" % E.OUT)
        return 2
    face = E.read_json(E.OUT)
    eng = face["engine_rung"]
    results = []

    def expect(name, rc, msg, want_rc, want_in=None, want_not_in=None):
        ok = (rc == want_rc)
        if want_in is not None:
            ok = ok and (want_in in msg)
        if want_not_in is not None:
            ok = ok and (want_not_in not in msg)
        results.append((name, ok, "rc=%d %s" % (rc, msg)))

    # N1: break the calmar identity (digests intact) -> CHECK FAILED, and the word STALE
    #     must NOT appear (the token is a contract: a real defect is not a stale face)
    f = copy.deepcopy(face)
    f["measured"]["rungs"][eng]["calmar"] = (f["measured"]["rungs"][eng]["calmar"] or 0.0) + 1.0
    rc, msg = E.check(f)
    expect("N1 calmar identity broken", rc, msg, 1, want_in="CHECK FAILED",
           want_not_in="STALE")

    # N2: ladder digest drift -> STALE
    f = copy.deepcopy(face)
    f["inputs"]["lattice"]["sha256"] = "0" * 64
    rc, msg = E.check(f)
    expect("N2 ladder drifted", rc, msg, 3, want_in="STALE")

    # N3: the risk face this reconciles against drifted -> STALE (cross-face pin)
    f = copy.deepcopy(face)
    if f.get("cross_face"):
        f["cross_face"]["sha256"] = "0" * 64
        rc, msg = E.check(f)
        expect("N3 cross-face drifted", rc, msg, 3, want_in="STALE")
    else:
        results.append(("N3 cross-face drifted", False, "no cross_face block to test"))

    # N4: equity arm digest drift -> STALE
    f = copy.deepcopy(face)
    f["inputs"]["l1_arm"]["sha256"] = "0" * 64
    rc, msg = E.check(f)
    expect("N4 equity arm drifted", rc, msg, 3, want_in="STALE")

    # N5: instructed rung too short -> CHECK FAILED (never silently green on a 10-bar rung)
    f = copy.deepcopy(face)
    f["measured"]["rungs"][eng]["days"] = 10
    rc, msg = E.check(f)
    expect("N5 short rung", rc, msg, 1, want_in="CHECK FAILED", want_not_in="STALE")

    # N6: ladder face missing -> STALE (refuse, never default to 0)
    orig = E.LATTICE
    E.LATTICE = orig + ".does-not-exist"
    try:
        rc, msg = E.check(copy.deepcopy(face))
    finally:
        E.LATTICE = orig
    expect("N6 ladder missing", rc, msg, 3, want_in="STALE")

    # N7: the published face itself must be green
    rc, msg = E.check(face)
    expect("N7 published face green", rc, msg, 0, want_in="CHECK_OK")

    # N8: verdict token is one of the frozen set
    frozen = {E.V_TRACKS, E.V_DISAGREE, E.V_BAND_IMPROVES, E.V_BAND_WORSENS, E.V_BAND_MIXED}
    tok = face["judgment"]["experience_vs_return"]
    results.append(("N8 verdict token frozen",
                    tok in frozen, "experience_vs_return=%s" % tok))

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print("%-32s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
    print("NEGATIVE %d/%d %s" % (npass, len(results),
                                  "ALL_CONTROLS_PASS" if npass == len(results) else "FAILED"))
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
