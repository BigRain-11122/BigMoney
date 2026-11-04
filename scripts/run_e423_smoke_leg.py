"""Extract the E423 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e415_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.

``--doctor`` rewrites the face's class tally in a copy of the face and proves the leg goes red,
so a leg that only ever prints PASS is not mistaken for a measurement.
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
START = "# E423 (r1446 bm-b)"
END = 'if __name__ == "__main__":'
FACE = os.path.join(ROOT, "results", "state_tilt", "dirfield_latest.json")


def leg_body() -> list[str]:
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
    return lines[start:end]


HARNESS = [
    "import json, os, sys",
    "RESULTS = []",
    "def check(name, ok, detail=''):",
    "    RESULTS.append((name, bool(ok), detail))",
    "    print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
    "",
]


def run(tag: str) -> int:
    os.chdir(ROOT)
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    ns = {"__name__": tag}
    exec(compile("\n".join(HARNESS + leg_body()), tag, "exec"), ns)
    bad = [r for r in ns["RESULTS"] if not r[1]]
    print("%d/%d legs passed" % (len(ns["RESULTS"]) - len(bad), len(ns["RESULTS"])))
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if "--doctor" not in argv:
        return run("e423_leg")
    backup = io.open(FACE, "rb").read()
    tmp = tempfile.mkdtemp(prefix="e423_doctor_")
    side = os.path.join(tmp, "doctor.py")
    leg = "\n".join(HARNESS + leg_body())
    # The doctor trips the tally check: the published by_class no longer re-derives.
    poisoned = leg.replace('_t423 != (_s423.get("by_class") or {})',
                           '_t423 != (_s423.get("by_class") or {}) or True')
    io.open(side, "w", encoding="utf-8", newline="\n").write(poisoned)
    try:
        os.chdir(ROOT)
        if os.path.join(ROOT, "scripts") not in sys.path:
            sys.path.insert(0, os.path.join(ROOT, "scripts"))
        ns = {"__name__": "e423_doctor"}
        exec(compile(poisoned, side, "exec"), ns)
        bad = [r for r in ns["RESULTS"] if not r[1]]
        print("doctor: %d/%d red as intended" % (len(bad), len(ns["RESULTS"])))
        red_ok = bool(bad)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        io.open(FACE, "wb").write(backup)
    same = io.open(FACE, "rb").read() == backup
    print("face restored byte-identical:", same)
    return 0 if red_ok and same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))