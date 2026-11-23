#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative controls for results/astock_veto_size_layers.json.

r1934: a check that classifies every red as "stale" cannot tell a real defect
from a moved face, and a check that only recomputes itself can never go red at
all.  Each leg below breaks exactly one thing and asserts both the exit code
and whether the word STALE is present, so the two failure modes stay apart.

Every leg rewrites the face from the ORIGINAL bytes first: a leg that inherits
the previous leg's edit passes for the wrong reason (r1999 caught that).
"""
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_size_layers as m  # noqa: E402

OUT = m.OUT


def read_bytes():
    with open(OUT, "rb") as fh:
        return fh.read()


def write_bytes(b):
    with open(OUT, "wb") as fh:
        fh.write(b)


def run_check():
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = m.cmd_check(None)
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def mutate(fn):
    face = json.loads(ORIG.decode("utf-8"))
    fn(face)
    write_bytes(json.dumps(face, ensure_ascii=False, indent=2).encode("utf-8"))


def main():
    global ORIG
    ORIG = read_bytes()
    orig_sha = hashlib.sha256(ORIG).hexdigest()

    # one panel read for the whole harness (load_panel walks 5k CSVs)
    panel = m.load_panel()
    m.load_panel = lambda *a, **k: panel

    legs = []

    # L1: a moved cutoff is a real defect, not a stale face
    mutate(lambda f: f.__setitem__("evidence_cutoff", "2026-11-10"))
    rc, out = run_check()
    legs.append(("cutoff tampered -> rc3, no STALE", rc == 3 and "STALE" not in out))
    write_bytes(ORIG)

    # L2: anchor mean tampered
    mutate(lambda f: f["pool_net_anchor"]["paired"].__setitem__("mean", 0.0030))
    rc, out = run_check()
    legs.append(("anchor mean tampered -> rc3, no STALE", rc == 3 and "STALE" not in out))
    write_bytes(ORIG)

    # L3: anchor n tampered
    mutate(lambda f: f["pool_net_anchor"]["paired"].__setitem__("n", 76))
    rc, out = run_check()
    legs.append(("anchor n tampered -> rc3", rc == 3))
    write_bytes(ORIG)

    # L4: anchor t tampered
    mutate(lambda f: f["pool_net_anchor"]["paired"].__setitem__("t", 4.0))
    rc, out = run_check()
    legs.append(("anchor t tampered -> rc3", rc == 3))
    write_bytes(ORIG)

    # L5: a layer removed
    mutate(lambda f: f["cuts"]["liquidity"]["layers"].pop("mid"))
    rc, out = run_check()
    legs.append(("missing layer -> rc3", rc == 3))
    write_bytes(ORIG)

    # L6: two layers made identical (the cut did nothing)
    def same_layers(f):
        f["cuts"]["size"]["layers"]["mid"]["mean"] = f["cuts"]["size"]["layers"]["lo"]["mean"]
        f["cuts"]["size"]["layers"]["hi"]["mean"] = f["cuts"]["size"]["layers"]["lo"]["mean"]
    mutate(same_layers)
    rc, out = run_check()
    legs.append(("identical layer means -> rc3", rc == 3))
    write_bytes(ORIG)

    # L7: layer period count disagrees with rebalances
    mutate(lambda f: f["cuts"]["liquidity"]["layers"]["hi"].__setitem__("n", 76))
    rc, out = run_check()
    legs.append(("layer periods wrong -> rc3", rc == 3))
    write_bytes(ORIG)

    # L8: verdict flipped by hand (must be re-derivable from the table)
    mutate(lambda f: f["verdicts"].__setitem__("size", "EDGE_WEAK_SIZE"))
    rc, out = run_check()
    legs.append(("verdict flipped -> rc3, no STALE", rc == 3 and "STALE" not in out))
    write_bytes(ORIG)

    # L9: missing face is STALE, not a defect
    os.remove(OUT)
    rc, out = run_check()
    legs.append(("missing face -> rc3 with STALE", rc == 3 and "STALE" in out))
    write_bytes(ORIG)

    # L10: the untouched face must pass
    rc, out = run_check()
    legs.append(("pristine face -> rc0", rc == 0))
    write_bytes(ORIG)

    # closing byte-identity
    end_sha = hashlib.sha256(read_bytes()).hexdigest()
    legs.append(("face restored byte-for-byte", end_sha == orig_sha))

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("NEGATIVE %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
