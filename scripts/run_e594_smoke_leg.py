# -*- coding: utf-8 -*-
"""Run the E594 smoke block out of smoke_test.py, verbatim, without launching the suite.

``smoke_test.py`` has no leg filter (r1499: ``main()`` ignores argv, so any flag runs all ~350
legs), so a single leg is proved by extracting its own source out of the suite and exec'ing it
against the same ``check`` name the suite uses.  ``--doctor`` copies the published face to a temp
directory, breaks one count in it, and requires the block to go red -- a leg that cannot fail
proves nothing.

  python scripts/run_e594_smoke_leg.py
  python scripts/run_e594_smoke_leg.py --doctor
"""
from __future__ import annotations

import importlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MARK = "# E594:"
END_MARK = "check(_name594,"


def extract():
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    i = src.find(MARK)
    if i < 0:
        raise SystemExit("the E594 block is not in smoke_test.py")
    j = src.find(END_MARK, i)
    if j < 0:
        raise SystemExit("the E594 block has no closing check()")
    j = src.find("\n", j) + 1
    return src[i:j]


def run_block(block, cwd):
    results = []

    def check(name, ok, detail=""):
        results.append((bool(ok), name, detail))

    env = {"__name__": "e594_smoke_leg", "os": os, "json": json,
           "importlib": importlib, "check": check, "sys": sys}
    old = os.getcwd()
    os.chdir(cwd)
    try:
        exec(compile(block, "<e594-smoke-leg>", "exec"), env)
    finally:
        os.chdir(old)
    return results


def main(argv):
    doctor = "--doctor" in argv
    block = extract()
    cwd = ROOT
    if doctor:
        tmp = tempfile.mkdtemp(prefix="e594doctor_")
        for sub in ("results/state_tilt", "scripts"):
            os.makedirs(os.path.join(tmp, sub), exist_ok=True)
        src_face = os.path.join(ROOT, "results", "state_tilt", "BARDIALECTJOIN.json")
        dst_face = os.path.join(tmp, "results", "state_tilt", "BARDIALECTJOIN.json")
        face = json.load(io.open(src_face, encoding="utf-8"))
        face["counts"]["pairs_joining_a_spelling_the_face_lacks"] = 0
        io.open(dst_face, "w", encoding="utf-8", newline="\n").write(
            json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True))
        shutil.copy(os.path.join(ROOT, "scripts", "e594_bar_dialect_join.py"),
                    os.path.join(tmp, "scripts", "e594_bar_dialect_join.py"))
        cwd = tmp
    res = run_block(block, cwd)
    bad = [r for r in res if not r[0]]
    for ok, name, detail in res:
        print(("PASS " if ok else "FAIL ") + name + (" | " + detail if not ok else ""))
    if doctor:
        print("\ndoctor: %s" % ("RED as required" if bad else "STILL GREEN -- the leg cannot fail"))
        return 0 if bad else 2
    print("\n%d/%d PASS" % (len(res) - len(bad), len(res)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))