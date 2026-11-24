#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative controls for r2054 money_shelf_placement.

Three live-fire legs.  Each mutates a real file, runs the real code path, then restores the file
by bytes and proves the restore with a final --check.

L1  an arithmetic lie on the face        -> rc1, text contains CHECK FAILED, text does NOT contain STALE
L2  an upstream face moves               -> rc3, text contains STALE and names the file
L3  the noise gate is turned off         -> the ranking is taken over by tapes whose typical bar is
                                            100x a day of carry, i.e. the refusal is what protects
                                            the ranking (a face that would pass either way proves nothing)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import money_shelf_placement as P  # noqa: E402

FACE = os.path.join(ROOT, P.FACE)
UPSTREAM = os.path.join(ROOT, P.SIGMA_FACE)


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _write(path, blob):
    with open(path, "wb") as fh:
        fh.write(blob)


def main() -> int:
    fails = []
    ok = 0

    def check(label, cond, extra=""):
        nonlocal ok
        if cond:
            ok += 1
            print("  PASS %s" % label)
        else:
            fails.append("%s %s" % (label, extra))
            print("  FAIL %s %s" % (label, extra))

    face_blob = _read(FACE)
    upstream_blob = _read(UPSTREAM)
    upstream_sha = _sha(UPSTREAM)

    try:
        # L1: an arithmetic lie on the face
        payload = json.loads(face_blob.decode("utf-8"))
        victim = next(r for r in payload["rows"] if r.get("priced"))
        victim["cagr_repaired_pct"] = round((victim["cagr_repaired_pct"] or 0.0) + 3.0, 4)
        _write(FACE, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
        rc, lines = P.check()
        text = "\n".join(lines)
        check("L1 arithmetic lie -> rc3", rc == 3, "rc=%d" % rc)
        check("L1 text says CHECK FAILED", "CHECK FAILED" in text, text[:160])
        check("L1 text does not say STALE", "STALE" not in text, text[:160])
        _write(FACE, face_blob)

        # L2: an upstream face moves (bytes only -- the numbers stay right, so this must be STALE)
        _write(UPSTREAM, upstream_blob + b"\n")
        rc, lines = P.check()
        text = "\n".join(lines)
        check("L2 upstream moved -> rc3", rc == 3, "rc=%d" % rc)
        check("L2 text says STALE", "STALE" in text, text[:160])
        check("L2 text names the file", P.SIGMA_FACE in text, text[:200])
        check("L2 text does not say CHECK FAILED", "CHECK FAILED" not in text, text[:160])
        _write(UPSTREAM, upstream_blob)
        check("L2 upstream restored byte-identical", _sha(UPSTREAM) == upstream_sha)

        # L3: with the noise gate off, the ranking is taken by an equity tape
        old = P.NOISE_BP
        P.NOISE_BP = 1e9
        try:
            payload = P.build()
            admitted = [r for r in payload["rows"] if r.get("admission") == "ADMIT"]
            worst = max(admitted, key=lambda r: r.get("cagr_printed_pct") or -99.0)
            check("L3 without the gate an equity tape is admitted",
                  (worst.get("sigma_robust_bp_2053") or 0.0) >= 70.0,
                  "worst=%s sigma=%s" % (worst.get("code"), worst.get("sigma_robust_bp_2053")))
            check("L3 without the gate the count rises",
                  len(admitted) > 17, "admitted=%d" % len(admitted))
        finally:
            P.NOISE_BP = old

        # the face and both upstreams must be back to where they started
        check("F1 face restored byte-identical", _sha(FACE) == hashlib.sha256(face_blob).hexdigest())
        rc, lines = P.check()
        check("F2 final check rc0", rc == 0, "\n".join(lines)[:200])
    finally:
        _write(FACE, face_blob)
        _write(UPSTREAM, upstream_blob)

    print("negative controls %d/%d PASS" % (ok, ok + len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
