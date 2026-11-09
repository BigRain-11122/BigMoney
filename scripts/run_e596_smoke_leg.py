# -*- coding: utf-8 -*-
"""Run the E596 smoke block out of smoke_test.py, verbatim, without launching the suite.

``smoke_test.py`` has no leg filter (r1499: ``main()`` ignores argv, so any flag runs all ~350
legs), so a single leg is proved by extracting its own source out of the suite and exec'ing it
against the same ``check`` name the suite uses.  ``--doctor`` rewrites a copy of the published face
so one both-role face claims the two bars share a date, and requires the block to go red -- a leg
that cannot fail proves nothing.

  python scripts/run_e596_smoke_leg.py
  python scripts/run_e596_smoke_leg.py --doctor
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
MARK = "# E596:"
END_MARK = "check(_name596,"
FACE = os.path.join("results", "state_tilt", "VALUEJOINNAME.json")


def extract():
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    i = src.find(MARK)
    if i < 0:
        raise SystemExit("the E596 block is not in smoke_test.py")
    j = src.find(END_MARK, i)
    if j < 0:
        raise SystemExit("the E596 block has no closing check()")
    j = src.find("\n", j) + 1
    return src[i:j]


def run_block(block, cwd):
    results = []

    def check(name, ok, detail=""):
        results.append((bool(ok), name, detail))

    env = {"__name__": "e596_smoke_leg", "os": os, "json": json,
           "importlib": importlib, "check": check, "sys": sys}
    old = os.getcwd()
    old_path = list(sys.path)
    sys.path.insert(0, os.path.join(cwd, "scripts"))
    os.chdir(cwd)
    try:
        exec(compile(block, "<e596-smoke-leg>", "exec"), env)
    finally:
        os.chdir(old)
        sys.path[:] = old_path
    return results


def doctor(cwd):
    """Make one both-role face lie about its own dates, and require the leg to catch it."""
    path = os.path.join(cwd, FACE)
    face = json.load(io.open(path, encoding="utf-8"))
    for d in face.get("details") or []:
        if not (d.get("carries_pricing") and d.get("carries_decision")):
            continue
        decision_date = next((f["date"] for f in d["bar_fields"]
                              if "decision" in f["role"].split("+") and f["date"]), "")
        if not decision_date:
            continue
        # move every pricing-role date onto the decision date: the two roles now share one date,
        # so the published 'different dates' answer becomes a lie the leg must catch
        for f in d["bar_fields"]:
            if "pricing" in f["role"].split("+"):
                f["date"] = decision_date
        break
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False)


def main(argv):
    doctor_mode = "--doctor" in argv
    block = extract()
    tmp = tempfile.mkdtemp(prefix="e596leg-")
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
        print("\nDOCTOR: %d/%d red (expected: the lying face must be caught)"
              % (len(red), len(rows)))
        return 0 if len(red) == 1 else 1
    print("\n%d/%d PASS" % (len(rows) - len(red), len(rows)))
    return 0 if not red else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))