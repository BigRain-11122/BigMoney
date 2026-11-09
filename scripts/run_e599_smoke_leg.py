# -*- coding: utf-8 -*-
"""Run the E599 smoke block out of smoke_test.py, verbatim, without launching the suite.

``smoke_test.py`` has no leg filter (r1499: ``main()`` ignores argv, so any flag runs all ~350
legs), so a single leg is proved by extracting its own source out of the suite and exec'ing it
against the same ``check`` name the suite uses.  ``--doctor`` copies the published face to a temp
directory and grades a row across fields while leaving its two ends on ONE field name -- the exact
shape the leg refuses -- and requires the block to go red.  A leg that cannot fail proves nothing.

  python scripts/run_e599_smoke_leg.py
  python scripts/run_e599_smoke_leg.py --doctor
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MARK = "# E599:"
END_MARK = "check(_name599,"


def extract():
    src = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read()
    i = src.find(MARK)
    if i < 0:
        raise SystemExit("the E599 block is not in smoke_test.py")
    j = src.find(END_MARK, i)
    if j < 0:
        raise SystemExit("the E599 block has no closing check()")
    j = src.find("\n", j) + 1
    return src[i:j]


def run_block(block, cwd):
    results = []

    def check(name, ok, detail=""):
        results.append((bool(ok), name, detail))

    env = {"__name__": "e599_smoke_leg", "os": os, "json": json,
           "importlib": importlib, "check": check, "sys": sys}
    old = os.getcwd()
    os.chdir(cwd)
    try:
        exec(compile(block, "<e599-smoke-leg>", "exec"), env)
    finally:
        os.chdir(old)
    return results


def main(argv):
    doctor = "--doctor" in argv
    block = extract()
    if not doctor:
        res = run_block(block, ROOT)
        for ok, name, detail in res:
            print(("PASS " if ok else "FAIL ") + name + ("" if ok else " | " + str(detail)))
        return 0 if all(r[0] for r in res) else 2

    face_rel = os.path.join("results", "state_tilt", "POINTERREDIRECTBAR.json")
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "results", "state_tilt"), exist_ok=True)
        with io.open(os.path.join(ROOT, face_rel), encoding="utf-8") as f:
            face = json.load(f)
        # make the claim false: an across-field row is restated on ONE field name while its two
        # dates still differ, which is the mis-grading the leg exists to refuse
        flipped = False
        for r in face.get("pairs") or []:
            if r.get("class") == "the_two_ends_state_their_bar_in_different_fields":
                r["target_bar_field"] = r.get("pointer_bar_field")
                flipped = True
                break
        if not flipped:
            raise SystemExit("no across-field row on the face to flip")
        with io.open(os.path.join(td, face_rel), "w", encoding="utf-8") as f:
            f.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
        sys.path.insert(0, HERE)
        res = run_block(block, td)
    red = [r for r in res if not r[0]]
    for ok, name, detail in res:
        print(("PASS " if ok else "RED  ") + name + ("" if ok else " | " + str(detail)))
    print("\ndoctor: %d/%d red (1 expected)" % (len(red), len(res)))
    return 0 if len(red) == 1 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))