"""Standalone runner for the E294 smoke leg: extract it verbatim from smoke_test.py and execute it."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    lines = io.open(os.path.join(ROOT, "smoke_test.py"), encoding="utf-8").read().splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# E294 (r1322 bm-b)"):
            start = i
            break
    if start is None:
        print("FAIL leg not found in smoke_test.py")
        return 1
    end = None
    for j in range(start, len(lines)):
        if lines[j].strip() == "return _finish()":
            end = j
            break
    body = "\n".join(lines[start:end])
    results = []

    def check(name, cond, detail=""):
        results.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name[:90])
        print("     " + str(detail)[:300])

    def _finish():
        return 0

    namespace = {"io": io, "os": os, "sys": sys, "json": __import__("json"),
                "check": check, "_finish": _finish}
    src = "\n".join(["    " + l if l.strip() else l for l in body.splitlines()])
    exec("def _leg():\n" + src + "\n", namespace)
    try:
        namespace["_leg"]()
    except Exception as exc:
        print("FAIL leg raised %r" % (exc,))
        return 1
    print("legs=%d pass=%d" % (len(results), sum(results)))
    return 0 if results and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())