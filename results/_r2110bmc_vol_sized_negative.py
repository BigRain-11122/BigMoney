#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for idx_fut_carry_vol_sized_lots (r2110 bm-c).

Each control breaks the published face in exactly one way and asserts the guard notices,
and that it uses the right word: drift in an input is STALE (rebuildable), a number that
disagrees with its own recomputation is CHECK FAILED and must NOT carry STALE (r1850 /
r1934).  The face is copied aside, so the published file is never left touched; the copy
is restored in a finally block and the restored bytes are compared with the original.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import idx_fut_carry_vol_sized_lots as F

OUT = F.OUT
FAILURES = []
STATE = {"legs": 0}


def leg(name, cond, detail=""):
    STATE["legs"] += 1
    if not cond:
        FAILURES.append("%s %s" % (name, detail))
    print(("  ok   " if cond else "  FAIL ") + name + (("  " + detail) if detail else ""))


def main():
    if not os.path.exists(OUT):
        print("face missing: run the face first")
        return 2
    with open(OUT, "rb") as f:
        original = f.read()
    backup = OUT + ".negctl.bak"
    shutil.copyfile(OUT, backup)
    try:
        # 0. the published face must pass as-is
        rc, msgs = F.check()
        leg("clean face passes", rc == 0, repr(msgs[:1]))

        # 1. a ruler number is wrong -> CHECK FAILED, and the word STALE must not appear
        face = json.loads(original.decode("utf-8"))
        face["rulers"][1]["block_vol_pct"] = round(face["rulers"][1]["block_vol_pct"] + 1.0, 3)
        F.write_json(OUT, face)
        rc, msgs = F.check()
        text = "\n".join(msgs)
        leg("tampered ruler -> rc3", rc == 3)
        leg("tampered ruler -> CHECK FAILED", "CHECK FAILED" in text)
        leg("tampered ruler -> no STALE", "STALE" not in text)

        # 2. the window history is wrong -> CHECK FAILED
        face = json.loads(original.decode("utf-8"))
        face["history"]["windows"] += 1
        F.write_json(OUT, face)
        rc, msgs = F.check()
        leg("tampered history -> rc3", rc == 3)
        leg("tampered history -> CHECK FAILED", "CHECK FAILED" in "\n".join(msgs))

        # 3. a frozen token is flipped -> CHECK FAILED
        face = json.loads(original.decode("utf-8"))
        face["judgment"]["pressure"] = F.V_PRESS_ONE
        F.write_json(OUT, face)
        rc, msgs = F.check()
        leg("flipped judgment -> CHECK FAILED", "CHECK FAILED" in "\n".join(msgs))

        # 4. an input's digest is stale -> STALE, and NOT CHECK FAILED
        face = json.loads(original.decode("utf-8"))
        face["inputs"]["stability"]["sha256"] = "0" * 64
        F.write_json(OUT, face)
        rc, msgs = F.check()
        text = "\n".join(msgs)
        leg("stale input -> rc3", rc == 3)
        leg("stale input -> STALE", "STALE" in text)
        leg("stale input -> no CHECK FAILED", "CHECK FAILED" not in text)

        # 5. the page a reader opens must print all three tokens and the cross-face verdict
        with open(F.DOC, encoding="utf-8") as f:
            doc = f.read()
        j = json.loads(original.decode("utf-8"))["judgment"]
        leg("page prints declaration token", j["declaration"] in doc)
        leg("page prints pressure token", j["pressure"] in doc)
        leg("page prints ticket token", j["ticket"] in doc)
        leg("page prints cross-face status",
            ("CROSS_FACE_MATCHES" in doc) or ("DIFFERENT_BOOK_NAMED" in doc))

        # 6. the identity the page relies on: blocks * block_vol == target
        for r in json.loads(original.decode("utf-8"))["rulers"]:
            leg("identity %s" % r["ruler"],
                abs(r["blocks_float_at_book"] * r["block_vol_pct"] - 8.0) < 1e-3,
                "%.6f" % (r["blocks_float_at_book"] * r["block_vol_pct"]))
    finally:
        with open(OUT, "wb") as f:
            f.write(original)
        if os.path.exists(backup):
            os.remove(backup)
        with open(OUT, "rb") as f:
            restored = f.read()
        leg("face restored byte-identical", restored == original)

    print("NEGATIVE %d/%d %s" % (STATE["legs"] - len(FAILURES), STATE["legs"],
                                 "ALL_CONTROLS_PASS" if not FAILURES else "FAILED"))
    for f in FAILURES:
        print("  FAIL " + f)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    raise SystemExit(main())
