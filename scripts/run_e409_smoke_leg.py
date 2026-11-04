"""Run the E409 smoke leg verbatim, without paying for the other 300 legs.

The leg was appended to smoke_test.py; this extracts its own block from that file and execs
it against a collector, so what is exercised is the code the suite will run -- not a
re-implementation of it.  A drift between the block's text and this extractor's anchors is
reported as a failure rather than skipped.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "smoke_test.py")
START = "# E409: E408 named the two writers"
END = '\nif __name__ == "__main__":'


def main():
    if not os.path.exists(SMOKE):
        print("FAIL: smoke_test.py not found")
        return 1
    text = open(SMOKE, encoding="utf-8", errors="replace").read()
    if START not in text:
        print("FAIL: the E409 leg is not in smoke_test.py")
        return 1
    head = text.index(START)
    tail = text.index(END, head) if END in text[head:] else len(text)
    block = text[head:tail]
    # exec the leg itself, not just the study: the exec'd block is the assertion
    results = []

    def check(name, ok, detail=""):
        results.append((bool(ok), name, detail))

    ns = {"os": os, "sys": sys, "json": json, "check": check, "__name__": "_e409_leg"}
    cwd = os.getcwd()
    try:
        os.chdir(ROOT)
        exec(compile(block, "smoke_test.py:E409", "exec"), ns)  # noqa: S102 - the leg is our own code
    finally:
        os.chdir(cwd)
    if not results:
        print("FAIL: the leg registered no check() -- it did not run")
        return 1
    for ok, name, detail in results:
        print(("PASS " if ok else "FAIL ") + name[:160])
        if not ok:
            print("      " + str(detail)[:280])
    return 0 if all(r[0] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())