"""Extract the E463 smoke leg verbatim and run it standalone (the full suite is ~40 min).

Same workaround as ``scripts/run_e461_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face instead of being paraphrased into a second copy that can drift.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
START = "# E463 (r1486 bm-b)"
END = 'if __name__ == "__main__":'


def run_leg(quiet=False):
    import io
    lines = io.open(SRC, encoding="utf-8").read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
    end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
    body = lines[start:end]
    harness = [
        "import json, os, sys",
        "RESULTS = []",
        "def check(name, ok, detail=''):",
        "    RESULTS.append((name, bool(ok), detail))",
        "    if not %r:" % quiet,
        "        print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
        "",
    ]
    os.chdir(ROOT)
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    scope = {"__name__": "E463_leg"}
    exec(compile("\n".join(harness + body), "<E463-leg>", "exec"), scope)
    return scope["RESULTS"]


def main(argv):
    results = run_leg()
    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(("PASS" if ok else "FAIL"), "::", name)
        if not ok:
            print("   ", detail)
    print("%d/%d" % (len(results) - len(failed), len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
