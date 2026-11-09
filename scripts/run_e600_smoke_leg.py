# -*- coding: utf-8 -*-
"""Run the E600 smoke block out of smoke_test.py, verbatim, without launching the suite.

``smoke_test.py`` has no leg filter (r1499), so a single leg is proved by extracting its own source
out of the suite and exec'ing it against the same ``check`` name the suite uses.  ``--doctor``
rewrites a copy of the published face so one date row claims a different face count than the index
does, and requires the block to go red -- a leg that cannot fail proves nothing.

  python scripts/run_e600_smoke_leg.py
  python scripts/run_e600_smoke_leg.py --doctor
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
MARK = "# E600:"
END_MARK = "check(_name600,"
FACE = os.path.join("results", "state_tilt", "DATEFACEUNIQUE.json")


def extract():
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    i = src.find(MARK)
    if i < 0:
        raise SystemExit("the E600 block is not in smoke_test.py")
    j = src.find(END_MARK, i)
    if j < 0:
        raise SystemExit("the E600 block has no closing check()")
    j = src.find("\n", j) + 1
    return src[i:j]


def run_block(block, cwd):
    results = []

    def check(name, ok, detail=""):
        results.append((bool(ok), name, detail))

    env = {"__name__": "e600_smoke_leg", "os": os, "json": json,
           "importlib": importlib, "check": check, "sys": sys}
    old = os.getcwd()
    old_path = list(sys.path)
    sys.path.insert(0, os.path.join(cwd, "scripts"))
    os.chdir(cwd)
    try:
        exec(compile(block, "<e600-smoke-leg>", "exec"), env)
    finally:
        os.chdir(old)
        sys.path[:] = old_path
    return results


def doctor(cwd):
    """Make one published date row disagree with its own index entry, and require the leg to catch it."""
    path = os.path.join(cwd, FACE)
    face = json.load(io.open(path, encoding="utf-8"))
    for row in face.get("date_rows") or []:
        if row["face_count"] <= 1:
            continue
        # strip one face from the row: the index still says the old count, so the published row no
        # longer re-derives the class it claims
        row["face_count"] -= 1
        row["sample_paths"] = row["sample_paths"][:-1]
        break
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False)


def main(argv):
    doctor_mode = "--doctor" in argv
    block = extract()
    tmp = tempfile.mkdtemp(prefix="e600leg-")
    try:
        work = tmp
        shutil.copytree(os.path.join(ROOT, "scripts"), os.path.join(work, "scripts"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        os.makedirs(os.path.join(work, "results", "state_tilt"), exist_ok=True)
        shutil.copy(os.path.join(ROOT, FACE), os.path.join(work, FACE))
        if doctor_mode:
            doctor(work)
        rows = run_block(block, work)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for ok, name, detail in rows:
        print(("PASS " if ok else "FAIL ") + name + ((" | " + detail) if detail else ""))
    red = [r for r in rows if not r[0]]
    if doctor_mode:
        print("\nDOCTOR: %d/%d red (expected: the lying row must be caught)"
              % (len(red), len(rows)))
        return 0 if len(red) == 1 else 1
    print("\n%d/%d PASS" % (len(rows) - len(red), len(rows)))
    return 0 if not red else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))