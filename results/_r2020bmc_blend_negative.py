"""Negative controls for results/two_book_blend.json (r2020 bm-c).

Purpose: prove the published face's own `check` actually refuses each way this face
could be wrong, instead of printing a green tick beside a broken number.

Every control copies the published JSON to a temp path, mutates exactly one thing,
runs the real `two_book_blend.check()` against it, and asserts the expected rc and
that the failure text names the mutated field.  The live face is never touched; the
last legs prove the original file is byte-identical afterwards and that the
script's own selftest still passes.

  python results/_r2020bmc_blend_negative.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import two_book_blend as T  # noqa: E402

FACE = os.path.join(ROOT, "results", "two_book_blend.json")
LEGS = []


def ok(cond, msg):
    if not cond:
        raise AssertionError(msg)
    LEGS.append(msg)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def with_mutation(mutate):
    """Copy the live face to a temp file, mutate the parsed dict, return its rc."""
    tmpdir = tempfile.mkdtemp(prefix="twobook_")
    try:
        dst = os.path.join(tmpdir, "two_book_blend.json")
        shutil.copy2(FACE, dst)
        with open(dst, encoding="utf-8") as f:
            d = json.load(f)
        mutate(d)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        prev = T.OUT
        T.OUT = dst
        try:
            return T.check()
        finally:
            T.OUT = prev
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    original = sha(FACE)

    # 0) the published face must pass as shipped
    prev = T.OUT
    rc = T.check()
    ok(rc == 0, "published face passes check as shipped (rc=%d)" % rc)
    T.OUT = prev

    # 1) a single moved return in book A
    def m1(d):
        d["rows"]["a"][5] = d["rows"]["a"][5] + 0.01
    rc = with_mutation(m1)
    ok(rc == 1, "one moved book-A return is refused (rc=%d)" % rc)

    # 2) a typed correlation
    def m2(d):
        d["corr"]["all"]["pearson"] = d["corr"]["all"]["pearson"] + 0.5
    rc = with_mutation(m2)
    ok(rc == 1, "a typed pearson is refused (rc=%d)" % rc)

    # 3) a flipped verdict
    def m3(d):
        d["verdict"] = "BLEND_ADDS" if d["verdict"] != "BLEND_ADDS" else "BLEND_REDUNDANT"
    rc = with_mutation(m3)
    ok(rc == 1, "a verdict that contradicts its own numbers is refused (rc=%d)" % rc)

    # 4) a moved blend weight
    def m4(d):
        d["blends"]["equal"]["weight_on_a"] = 0.6
    rc = with_mutation(m4)
    ok(rc == 1, "a moved equal-weight is refused (rc=%d)" % rc)

    # 5) a fitted-on-the-wrong-half weight
    def m5(d):
        d["blends"]["invvol_is"]["weight_on_a"] = 0.75
    rc = with_mutation(m5)
    ok(rc == 1, "an inverse-vol weight that the IS half cannot reproduce is refused (rc=%d)" % rc)

    # 6) a moved book statistic
    def m6(d):
        d["books"]["b"]["sharpe"] = 1.5
    rc = with_mutation(m6)
    ok(rc == 1, "a typed book-B Sharpe is refused (rc=%d)" % rc)

    # 7) truncated rows
    def m7(d):
        d["rows"]["a"] = d["rows"]["a"][:-1]
    rc = with_mutation(m7)
    ok(rc == 1, "a shortened return stream is refused (rc=%d)" % rc)

    # 8) missing face
    tmpdir = tempfile.mkdtemp(prefix="twobook_missing_")
    try:
        prev = T.OUT
        T.OUT = os.path.join(tmpdir, "nope.json")
        rc = T.check()
        T.OUT = prev
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    ok(rc == 3, "a missing face is 'face missing' rc=3, not a green tick (rc=%d)" % rc)

    # 9) duplicate books must read as redundancy, not as diversification
    with open(FACE, encoding="utf-8") as f:
        d = json.load(f)
    import numpy as np
    a = np.array(d["rows"]["a"], dtype=np.float64)
    c = T.corr_pair(a, a)
    ok(abs(c["pearson"] - 1.0) < 1e-12, "duplicating book A gives corr=1, as it must")
    sr = T.period_stats(a)["sharpe"]
    dup = T.verdict(sr, sr, sr, sr)
    ok(dup == "BLEND_REDUNDANT", "duplicate books verdict is REDUNDANT (got %s)" % dup)

    # 10) the selftest still passes
    rc = T.selftest()
    ok(rc == 0, "script selftest still green after the controls")

    # 11) the live face was never touched
    ok(sha(FACE) == original, "live face is byte-identical after the controls")

    print("negative controls %d/%d PASS" % (len(LEGS), len(LEGS)))
    for msg in LEGS:
        print("  ok -", msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
