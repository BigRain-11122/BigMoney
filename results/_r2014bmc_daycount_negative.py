"""Negative control for scripts/astock_veto_cash_daycount.py (r2014 bm-c).

The face must fail *loudly* and *specifically*: a moved input wears STALE, a
number that moved with the same inputs wears CHECK FAILED and must never wear
STALE (r1850: the wording is a contract, the chain pays the writer only when it
sees the literal word STALE).

Every leg restores both faces byte-for-byte at the end (sha256 checked), so a
failed run never leaves a poisoned artifact behind.
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
SCRIPT = os.path.join(ROOT, "scripts", "astock_veto_cash_daycount.py")
OUT = os.path.join(ROOT, "results", "astock_veto_cash_daycount.json")
PARENT = os.path.join(ROOT, "results", "astock_veto_cash_leg.json")

_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("negative leg %d failed: %s" % (_CHECKS[0], msg))


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_check():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([sys.executable, SCRIPT, "check"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _dump(path, payload):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)


def main() -> int:
    for p in (OUT, PARENT):
        if not os.path.exists(p):
            print("NEGATIVE CONTROL cannot start: missing %s" % p)
            return 1

    out_sha = _sha(OUT)
    par_sha = _sha(PARENT)
    tmpdir = tempfile.mkdtemp(prefix="r2014bmc_")
    out_bak = os.path.join(tmpdir, "daycount.json")
    par_bak = os.path.join(tmpdir, "cash_leg.json")
    shutil.copy2(OUT, out_bak)
    shutil.copy2(PARENT, par_bak)
    k10 = str(10_000_000)

    try:
        # 1. untouched -> rc0
        rc, txt = _run_check()
        _ok(rc == 0, "clean face must be rc0, got %d\n%s" % (rc, txt[-800:]))
        _ok("CHECK ok" in txt, "clean face prints CHECK ok")

        # 2. panel moved -> rc3 and the word STALE
        face = _load(OUT)
        face["evidence_cutoff"] = "1999-01-01"
        _dump(OUT, face)
        rc, txt = _run_check()
        _ok(rc == 3, "moved cutoff -> rc3, got %d" % rc)
        _ok("STALE" in txt, "moved cutoff wears STALE")
        shutil.copy2(out_bak, OUT)

        # 3. the cash leg's own annualised number hand-edited -> rc3, NO STALE
        face = _load(OUT)
        face["cash_tape"]["calendar"]["annualized"] += 1e-6
        _dump(OUT, face)
        rc, txt = _run_check()
        _ok(rc == 3, "hand-edited cash_tape -> rc3, got %d" % rc)
        _ok("CHECK FAILED" in txt, "hand-edited cash_tape wears CHECK FAILED")
        _ok("STALE" not in txt, "hand-edited cash_tape must NOT wear STALE")
        shutil.copy2(out_bak, OUT)

        # 4. a net number hand-edited -> rc3, NO STALE
        face = _load(OUT)
        face["summary"]["A"]["by_capital"][k10]["net_calendar_per_period_mean"] += 1e-9
        _dump(OUT, face)
        rc, txt = _run_check()
        _ok(rc == 3, "hand-edited net_calendar -> rc3, got %d" % rc)
        _ok("CHECK FAILED" in txt, "hand-edited net_calendar wears CHECK FAILED")
        _ok("STALE" not in txt, "hand-edited net_calendar must NOT wear STALE")
        shutil.copy2(out_bak, OUT)

        # 5. ladder number hand-edited -> rc3, NO STALE
        face = _load(OUT)
        face["summary"]["B"]["by_capital"][k10]["net_ladder_per_period_mean"] -= 1e-9
        _dump(OUT, face)
        rc, txt = _run_check()
        _ok(rc == 3, "hand-edited net_ladder -> rc3, got %d" % rc)
        _ok("CHECK FAILED" in txt, "hand-edited net_ladder wears CHECK FAILED")
        _ok("STALE" not in txt, "hand-edited net_ladder must NOT wear STALE")
        shutil.copy2(out_bak, OUT)

        # 6. parent anchor broken -> rc3 and STALE
        par = _load(PARENT)
        par["summary"]["B"]["by_capital"][k10]["net_with_cash_per_period_mean"] += 1e-6
        _dump(PARENT, par)
        rc, txt = _run_check()
        _ok(rc == 3, "broken parent anchor -> rc3, got %d" % rc)
        _ok("STALE" in txt, "broken parent anchor wears STALE")
        shutil.copy2(par_bak, PARENT)

        # 7. missing face -> rc3, "face missing"
        os.remove(OUT)
        rc, txt = _run_check()
        _ok(rc == 3, "missing face -> rc3, got %d" % rc)
        _ok("face missing" in txt, "missing face says face missing")
        _ok("STALE" not in txt, "missing face is not STALE (it is gone, not moved)")
        shutil.copy2(out_bak, OUT)

        # 8. restored -> rc0 and byte-identical
        rc, txt = _run_check()
        _ok(rc == 0, "restored face -> rc0, got %d\n%s" % (rc, txt[-800:]))
        _ok(_sha(OUT) == out_sha, "face restored byte-for-byte")
        _ok(_sha(PARENT) == par_sha, "parent restored byte-for-byte")

    finally:
        shutil.copy2(out_bak, OUT)
        shutil.copy2(par_bak, PARENT)
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("negative control %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
