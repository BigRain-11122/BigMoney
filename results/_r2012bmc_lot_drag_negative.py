#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Negative control for scripts/astock_veto_lot_drag.py (r1934 law).

Every leg writes a real byte, calls the real `check()`, and asserts on the words
it prints.  A guard that only recomputes itself never learns it is stale -- so
this file must prove, on this machine, that:

  * a moved panel says STALE
  * a moved number with the same inputs does NOT wear the STALE word
  * a moved tilt (the headline number of this face) is caught, not just the level
  * a missing face is reported, not crashed on
  * a broken parent anchor says STALE
  * restoration brings the face back to green

Usage: python results/_r2012bmc_lot_drag_negative.py
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

import astock_veto_lot_drag as m  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="lotdrag-neg-")
_FACE = os.path.join(_TMP, "face.json")
_BACKUP = os.path.join(_TMP, "face.bak.json")
_LEGS = [0]


def leg(cond, msg):
    _LEGS[0] += 1
    if not cond:
        raise AssertionError("negative leg %d failed: %s" % (_LEGS[0], msg))
    print("  leg %d ok: %s" % (_LEGS[0], msg))


def run_check() -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.check()
    return rc, buf.getvalue()


def save(obj) -> None:
    with open(_FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def base() -> dict:
    with open(_BACKUP, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    shutil.copy2(m.OUT, _BACKUP)
    shutil.copy2(_BACKUP, _FACE)
    real_out = m.OUT
    m.OUT = _FACE
    try:
        rc, out = run_check()
        leg(rc == 0, "unchanged face -> rc0 (%s)" % out.strip()[:60])

        # 1. panel moved -> STALE
        obj = base()
        obj["evidence_cutoff"] = "1999-01-01"
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "STALE" in out, "moved cutoff -> rc3 with STALE")

        # 2. a level number moved, inputs identical -> real defect, no STALE word
        obj = base()
        obj["summary"]["B"]["mean_n"] = obj["summary"]["B"]["mean_n"] + 1.0
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "CHECK FAILED" in out and "STALE" not in out,
            "mean_n moved -> rc3 CHECK FAILED without the STALE word")

        # 3. one capital's invested share moved -> real defect
        obj = base()
        obj["summary"]["B"]["by_capital"]["10000000"]["invested_share_median"] = 0.5
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "STALE" not in out, "invested share moved -> rc3 without STALE")

        # 4. the tilt gap (this face's headline) moved by 1e-9 -> caught
        obj = base()
        key = "10000000"
        obj["summary"]["B"]["by_capital"][key]["tilt_gap_per_period_mean"] += 1e-9
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "tilt" in out and "STALE" not in out,
            "tilt gap moved by 1e-9 -> rc3 without STALE")

        # 5. missing face -> reported, not crashed
        os.remove(_FACE)
        rc, out = run_check()
        leg(rc == 3 and "face missing" in out, "missing face -> rc3 face missing")
        shutil.copy2(_BACKUP, _FACE)

        # 6. broken parent anchor -> STALE (the anchor is an input, not a claim)
        real_parent = m.PARENT
        m.PARENT = os.path.join(_TMP, "no-such-parent.json")
        try:
            rc, out = run_check()
        finally:
            m.PARENT = real_parent
        leg(rc == 3 and "STALE" in out, "unreadable parent -> rc3 with STALE")

        # 7. arm A is checked too, not just B
        obj = base()
        obj["summary"]["A"]["by_capital"]["500000000"]["invested_share_median"] = 0.1
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "arm A" in out, "arm A drift is caught as well")

        # 8. restoration: the untouched backup must still be green
        shutil.copy2(_BACKUP, _FACE)
        rc, out = run_check()
        leg(rc == 0, "restored face -> rc0 again")
    finally:
        m.OUT = real_out
        shutil.rmtree(_TMP, ignore_errors=True)
    print("negative control %d/%d PASS" % (_LEGS[0], _LEGS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
