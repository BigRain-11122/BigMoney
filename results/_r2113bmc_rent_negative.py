#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2113 negative control for scripts/idx_fut_carry_rent_by_component.py.

Every leg drives the real check() on a mutated copy of the published face; the published face
and the published page are never modified (restored in `finally`).
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_rent_by_component as M  # noqa: E402

ok = 0
total = 0


def chk(cond, msg):
    global ok, total
    total += 1
    if cond:
        ok += 1
    else:
        print("FAIL: %s" % msg)


def run_check(face_path):
    old = M.OUT
    M.OUT = face_path
    try:
        return M.check()
    finally:
        M.OUT = old


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    face_path = M.OUT
    chk(os.path.exists(face_path), "published face must exist: %s" % face_path)
    if not os.path.exists(face_path):
        print("NEG %d/%d" % (ok, total))
        return 1
    tmpdir = tempfile.mkdtemp(prefix="r2113bmc_neg_")
    copy = os.path.join(tmpdir, "face.json")
    shutil.copyfile(face_path, copy)
    orig_bytes = io.open(face_path, "rb").read()
    try:
        # 0) the published face is green, and green is not "STALE" wording
        rc, msg = run_check(copy)
        chk(rc == 0, "published copy must pass, got rc=%d %s" % (rc, msg))
        chk("STALE" not in msg, "a green check must not say STALE")

        # 1) arithmetic broken (a component's contribution inflated) -> CHECK FAILED, no STALE
        f = load(copy)
        f["rungs"]["1/1"]["components"][1]["ann_arith_pct"] += 1.0
        dump(copy, f)
        rc, msg = run_check(copy)
        chk(rc == 1, "inflated component must fail the sum identity, got rc=%d" % rc)
        chk("CHECK FAILED" in msg, "it must say CHECK FAILED, got %r" % msg)
        chk("STALE" not in msg, "an internal inconsistency must NOT say STALE, got %r" % msg)
        shutil.copyfile(face_path, copy)

        # 2) an input digest drifts -> STALE (this is the refresh trigger the chain reads)
        f = load(copy)
        f["inputs"]["l1_arm"]["sha256"] = "0" * 64
        dump(copy, f)
        rc, msg = run_check(copy)
        chk(rc == 3, "drifted input digest must be rc=3 (stale), got rc=%d" % rc)
        chk("STALE" in msg, "drift must say STALE, got %r" % msg)
        shutil.copyfile(face_path, copy)

        # 3) a judgment token flipped -> CHECK FAILED (verdicts are recomputed, not trusted)
        f = load(copy)
        f["rungs"]["1/1"]["judgment"]["rent"] = "EVERY_COMPONENT_PAYS_ITS_RENT"
        dump(copy, f)
        rc, msg = run_check(copy)
        chk(rc == 1, "flipped verdict must fail, got rc=%d" % rc)
        chk("judgment" in msg and "STALE" not in msg, "verdict failure wording, got %r" % msg)
        shutil.copyfile(face_path, copy)

        # 4) a risk share moved -> CHECK FAILED (shares are recomputed from covariances)
        f = load(copy)
        f["rungs"]["1/1"]["components"][2]["risk_share"] = 0.6
        dump(copy, f)
        rc, msg = run_check(copy)
        chk(rc == 1, "moved risk share must fail, got rc=%d" % rc)
        chk("risk share" in msg, "it must name the risk share, got %r" % msg)
        shutil.copyfile(face_path, copy)

        # 5) return shares that no longer sum to 1 -> CHECK FAILED
        f = load(copy)
        f["rungs"]["1/1"]["components"][3]["return_share"] = 0.5
        dump(copy, f)
        rc, msg = run_check(copy)
        chk(rc == 1, "broken share sum must fail, got rc=%d" % rc)
        shutil.copyfile(face_path, copy)

        # 6) restoring the published bytes brings it back green (behavioural, not asserted
        #    from a stub)
        rc, msg = run_check(copy)
        chk(rc == 0, "restored copy green again, got rc=%d %s" % (rc, msg))

        # 7) the published page prints the tokens this face promises
        page = io.open(M.DOC, encoding="utf-8").read()
        f = load(face_path)
        for token in (f["judgment"]["engine"]["rent"], f["judgment"]["engine"]["neutrality"],
                      f["judgment"]["engine"]["rebudget"]):
            chk(token in page, "page must print the token %s" % token)
        chk("rent" in page, "page must explain rent")
        chk("100% NAV" in page, "page must print the notional cap it applied")

        # 8) the module's own selftest still passes
        chk(M._selftest() == 0, "module selftest must pass")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        after = io.open(face_path, "rb").read()
        chk(after == orig_bytes, "published face must be byte-identical after the control")
    print("NEG %d/%d %s" % (ok, total, "ALL_CONTROLS_PASS" if ok == total else "CONTROLS_FAILED"))
    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
