# -*- coding: utf-8 -*-
"""r2066 negative controls for etf_book_headroom_two_readings.check().

Three things a check must do, proven on the live face instead of asserted:
  1. a one-field edit in the published face is caught, and the message does NOT claim
     STALE (the numbers were re-derived from the same inputs -> a real disagreement,
     r1934);
  2. a missing face IS STALE (the chain only pays to rebuild on that word, r1850);
  3. restoring the backup brings the file back byte-for-byte, so the control leaves no
     residue.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "etf_book_headroom_two_readings.json")
SCRIPT = os.path.join(ROOT, "scripts", "etf_book_headroom_two_readings.py")


def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _run_check():
    p = subprocess.run([sys.executable, SCRIPT, "check"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    ok = tot = 0

    def leg(name, cond, detail=""):
        nonlocal ok, tot
        tot += 1
        ok += 1 if cond else 0
        print("  %s %s %s" % ("ok  " if cond else "FAIL", name, detail if not cond else ""))

    if not os.path.exists(FACE):
        print("FAIL: face missing before the control starts: %s" % FACE)
        return 1
    before = _sha(FACE)
    bak = tempfile.mktemp(suffix="-headroom.json")
    shutil.copy2(FACE, bak)
    try:
        # 1. a hand edit of one published number
        with open(FACE, encoding="utf-8") as f:
            face = json.load(f)
        face["headroom"]["strict_pp"] = round(float(face["headroom"]["strict_pp"]) + 1.0, 4)
        with open(FACE, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=2)
            f.write("\n")
        rc, out = _run_check()
        leg("edited face is caught", rc == 1, "rc=%s" % rc)
        leg("and the message is CHECK FAILED", "CHECK FAILED" in out, out.strip()[:160])
        leg("and it does not claim STALE", "STALE" not in out, out.strip()[:160])

        # 2. a missing face
        os.remove(FACE)
        rc, out = _run_check()
        leg("missing face returns rc 3", rc == 3, "rc=%s" % rc)
        leg("and says STALE", "STALE" in out, out.strip()[:160])

        # 3. restore
        shutil.copy2(bak, FACE)
        leg("restore is byte-identical", _sha(FACE) == before)
        rc, out = _run_check()
        leg("and the restored face checks green", rc == 0, "rc=%s %s" % (rc, out.strip()[:120]))
    finally:
        if os.path.exists(bak):
            if not os.path.exists(FACE):
                shutil.copy2(bak, FACE)
            os.remove(bak)

    print("negctl: %d/%d OK" % (ok, tot))
    return 0 if ok == tot else 1


if __name__ == "__main__":
    sys.exit(main())
