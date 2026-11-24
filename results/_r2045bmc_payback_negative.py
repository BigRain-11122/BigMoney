#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for cash_shelf_wait_payback (r2045 bm-c).

Runs the real code paths and proves each one fails when it must:
  N1 a hand-edited payback cell is caught by --check (rc1, not STALE)
  N2 a byte-changed upstream face is caught as STALE (rc3) before any recompute
  N3 the verdict is driven by ADOPTION: widen the budget and 511380 moves inside
  N4 the rendered page carries both shelters' numbers (a page nobody can read is a fail)

Every mutation is reverted and the file is asserted byte-identical afterwards, so a
red control cannot leave the tree poisoned.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cash_shelf_wait_payback as M  # noqa: E402

FACE = os.path.join(ROOT, M.FACE)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    base = sha(FACE)
    raw = io.open(FACE, encoding="utf-8").read()

    # ---- N1: hand-edited cell must be a CHECK FAILED, not STALE ------------------
    face = json.loads(raw)
    target = None
    for r in face["rows"]:
        for k, t in r["tiers"].items():
            if t["payback_days_p95"] is not None:
                target = (r["code"], k)
                t["payback_days_p95"] = t["payback_days_p95"] + 1.0
                break
        if target:
            break
    io.open(FACE, "w", encoding="utf-8", newline="\n").write(
        json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    try:
        rc = M.cmd_check()
    finally:
        io.open(FACE, "w", encoding="utf-8", newline="\n").write(raw)
    leg("N1 hand-edited cell -> rc1 CHECK FAILED", rc == 1, "rc=%s target=%s" % (rc, target))
    leg("N1b face restored byte-identical", sha(FACE) == base)

    # ---- N2: upstream byte change must be STALE (rc3) ----------------------------
    tmp = os.path.join(ROOT, "results", "_r2045tmp_plan_copy.json")
    shutil.copyfile(os.path.join(ROOT, M.PLAN_FACE), tmp)
    with open(tmp, "ab") as f:
        f.write(b"\n")
    old_faces = (M.PLAN_FACE, M.PLAN_SHA_KEY if hasattr(M, "PLAN_SHA_KEY") else None)
    saved = {k: getattr(M, k) for k in ("PLAN_FACE", "FACE", "DOC") if hasattr(M, k)}
    try:
        M.PLAN_FACE = os.path.relpath(tmp, ROOT)
        # silence the check's own stdout so the rc is what the control reads
        rc2 = M.cmd_check()
    finally:
        for k, v in saved.items():
            setattr(M, k, v)
        os.remove(tmp)
    leg("N2 byte-changed upstream -> rc3 STALE", rc2 == 3, "rc=%s" % rc2)
    leg("N2b upstream face untouched", sha(os.path.join(ROOT, M.PLAN_FACE)) ==
        json.loads(raw)["upstream"]["plan_sha256"])

    # ---- N3: the budget is ADOPTION's, not the code's mood -----------------------
    face = json.loads(raw)
    tight = M.headline(M.compute(M._load(M.PLAN_FACE), M._load(M.CARRY_FACE)),
                       565245.9, "565246")
    old_budget = M.ADOPTION["budget_sessions"]
    try:
        M.ADOPTION["budget_sessions"] = 1000
        wide = M.headline(M.compute(M._load(M.PLAN_FACE), M._load(M.CARRY_FACE)),
                          565245.9, "565246")
    finally:
        M.ADOPTION["budget_sessions"] = old_budget
    leg("N3 widening the budget moves 511380 inside",
        ("511380" not in tight["inside_budget"]) and ("511380" in wide["inside_budget"]),
        "tight=%s wide=%s" % (tight["inside_budget"], wide["inside_budget"]))

    # ---- N4: the page must carry both numbers a reader compares -----------------
    block = M.render_block(face)
    leg("N4 page names 511360 and 511380", ("`511360`" in block) and ("`511380`" in block))
    leg("N4b page prints the 13-point payback for 511360", "13.1" in block)
    leg("N4c page carries the frozen budget", str(face["headline"]["budget_sessions"]) in block)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    print("NEGATIVE %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
