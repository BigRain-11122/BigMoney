"""Negative control for results/astock_veto_hedgeable_beta.json (r2022 bm-c).

A face is only as good as its ability to say no.  This script poisons the published
face one field at a time and requires the face's own `check` to refuse each poison --
and refuses to be fooled by its own repairs: every poison is restored from a byte
copy and the restored file must come back byte-identical before the next leg runs.

Legs
----
 1  untouched face                                  -> check rc0
 2  another evidence_cutoff (parent moved)          -> rc3, says STALE
 3  another hedge return on one period              -> rc3, CHECK FAILED
 4  another book return on one period               -> rc3, CHECK FAILED
 5  another in-sample beta                          -> rc3, CHECK FAILED
 6  another out-of-sample Sharpe on one arm          -> rc3, CHECK FAILED
 7  verdict flipped by hand                          -> rc3, CHECK FAILED
 8  variance share nudged                            -> rc3, CHECK FAILED
 9  rows truncated                                   -> rc3, no crash
10  face deleted                                     -> rc3, says "face missing"
11  hedge leg's last bar moved in the face          -> rc3, says STALE
12  restored file is byte-identical and still green

Usage: python results/_r2022bmc_hedge_negative.py
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
FACE = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
SCRIPT = os.path.join(ROOT, "scripts", "astock_veto_hedgeable_beta.py")

ok, fail = 0, 0


def _ok(cond, msg):
    global ok, fail
    if cond:
        ok += 1
        print("PASS  %s" % msg)
    else:
        fail += 1
        print("FAIL  %s" % msg)


def _run_check() -> tuple:
    proc = subprocess.run([sys.executable, SCRIPT, "check"], cwd=ROOT,
                          capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _sha(path) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _poison(mutate, expect_word, label):
    """Mutate the face, require rc3 + the expected word, then restore exactly."""
    original = _sha(FACE)
    face = json.load(open(FACE, encoding="utf-8"))
    mutate(face)
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    rc, out = _run_check()
    _ok(rc == 3 and expect_word in out, "%s -> rc3 + %r" % (label, expect_word))
    shutil.copyfile(BACKUP, FACE)
    _ok(_sha(FACE) == original, "%s -> restored byte-identical" % label)


def main() -> int:
    global BACKUP
    if not os.path.exists(FACE):
        print("face missing: %s -- run the face first" % FACE)
        return 2
    BACKUP = os.path.join(tempfile.mkdtemp(prefix="r2022bmc_"), "face.json")
    shutil.copyfile(FACE, BACKUP)

    rc, out = _run_check()
    _ok(rc == 0 and "CHECK OK" in out, "untouched face -> check rc0")

    _poison(lambda f: f.__setitem__("evidence_cutoff", "2026-10-01"),
            "STALE", "another evidence_cutoff")

    def poison_hedge(f):
        for r in f["rows"]:
            if r["hedge_etf"] is not None:
                r["hedge_etf"] = r["hedge_etf"] + 0.001
                return
    _poison(poison_hedge, "CHECK FAILED", "one hedge return moved")

    def poison_book(f):
        f["rows"][3]["book_net"] = f["rows"][3]["book_net"] + 0.002
    _poison(poison_book, "CHECK FAILED", "one book return moved")

    _poison(lambda f: f["beta"]["etf_in_sample"].__setitem__("beta", 0.75),
            "CHECK FAILED", "in-sample beta rewritten")

    _poison(lambda f: f["arms_etf"]["1.00"]["out_of_sample"].__setitem__(
        "sharpe_excess_0", 1.44), "CHECK FAILED", "one arm's out-of-sample Sharpe rewritten")

    _poison(lambda f: f.__setitem__("verdict", "HEDGE_PAYS_OUT_OF_SAMPLE"),
            "CHECK FAILED", "verdict flipped by hand")

    def poison_share(f):
        f["variance"]["share_removable"] = float(f["variance"]["share_removable"]) + 0.05
    _poison(poison_share, "CHECK FAILED", "variance share nudged")

    _poison(lambda f: f.__setitem__("rows", f["rows"][:40]),
            "CHECK FAILED", "rows truncated (shape problem, not a crash)")

    def poison_last_bar(f):
        f["data"]["etf"]["last"] = "2026-11-13"
    _poison(poison_last_bar, "STALE", "hedge leg's last bar moved")

    # 10. a deleted face is a named absence, not a traceback
    os.remove(FACE)
    rc, out = _run_check()
    _ok(rc == 3 and "face missing" in out, "deleted face -> rc3 + 'face missing'")
    shutil.copyfile(BACKUP, FACE)

    # 12. the restored face is the one we started with, and it is still green
    rc, out = _run_check()
    _ok(rc == 0 and "CHECK OK" in out, "restored face -> still green")
    _ok(_sha(FACE) == _sha(BACKUP), "restored face is byte-identical to the backup")

    print("\nnegative control %d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
