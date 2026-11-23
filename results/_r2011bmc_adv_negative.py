#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Negative control for scripts/astock_veto_adv_capacity.py (r1934 law).

Every leg writes a real byte, calls the real `check()`, and asserts on the
words it prints.  A guard that only recomputes itself never learns it is
stale -- so this file must prove, on this machine, that:

  * a moved panel says STALE
  * a moved number with the same inputs does NOT wear the STALE word
  * a missing face is reported, not crashed on
  * a broken parent anchor says STALE

Usage: python results/_r2011bmc_adv_negative.py
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

import astock_veto_adv_capacity as m  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="advcap-neg-")
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


def load() -> dict:
    with open(_FACE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(obj) -> None:
    with open(_FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def base() -> dict:
    with open(_BACKUP, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    shutil.copy2(m.OUT, _BACKUP)
    shutil.copy2(_BACKUP, _FACE)
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

        # 2. a number moved, inputs identical -> real defect, no STALE word
        obj = base()
        obj["summary"]["B"]["mean_n"] = obj["summary"]["B"]["mean_n"] + 1.0
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "CHECK FAILED" in out and "STALE" not in out,
            "mean_n moved -> rc3 CHECK FAILED without the STALE word")

        # 3. one capital's median moved -> real defect
        obj = base()
        obj["summary"]["B"]["fillable_share_by_capital"]["10000000"]["median"] = 0.123456
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "STALE" not in out, "capital median moved -> rc3 without STALE")

        # 4. missing face -> reported, not crashed
        os.remove(_FACE)
        rc, out = run_check()
        leg(rc == 3 and "face missing" in out, "missing face -> rc3 face missing")
        shutil.copy2(_BACKUP, _FACE)

        # 5. broken parent anchor -> STALE (the anchor is an input, not a claim)
        real_parent = m.PARENT
        m.PARENT = os.path.join(_TMP, "no-such-parent.json")
        try:
            rc, out = run_check()
        finally:
            m.PARENT = real_parent
        leg(rc == 3 and "STALE" in out, "unreadable parent -> rc3 with STALE")

        # 6. arm A median moved too (both arms are checked, not just B)
        obj = base()
        obj["summary"]["A"]["fillable_share_by_capital"]["500000000"]["median"] = 0.5
        save(obj)
        rc, out = run_check()
        leg(rc == 3 and "arm A" in out, "arm A drift is caught as well")

        # 7. restoration: the untouched backup must still be green
        shutil.copy2(_BACKUP, _FACE)
        rc, out = run_check()
        leg(rc == 0, "restored face -> rc0 again")
    finally:
        m.OUT = os.path.join(ROOT, "results", "astock_veto_adv_capacity.json")
        shutil.rmtree(_TMP, ignore_errors=True)
    print("negative control %d/%d PASS" % (_LEGS[0], _LEGS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
