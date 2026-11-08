"""Extract and execute exactly one leg from smoke_test.py (r1559 bm-b).

The legs in smoke_test.py are top-level statements that call ``check(name, cond, detail)``.
This runner slices the source between a start anchor and its closing ``check(...)`` line and
execs it in a namespace that supplies ``check``, ``json`` and ``os``, so the leg under test is
the one on disk, verbatim -- not a re-typed copy.

    python scripts/run_e527_smoke_leg.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "# E527: which of E521's undecidable arms becomes decidable"
END = "check(_name527, not _bad527,"


def main():
    path = os.path.join(ROOT, "smoke_test.py")
    with io.open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(START))
    except StopIteration:
        print("the E527 leg is not in smoke_test.py")
        return 1
    stop = None
    for i in range(start, len(lines)):
        if lines[i].startswith(END):
            stop = i
            break
    if stop is None:
        print("the E527 leg has no closing check()")
        return 1
    source = "\n".join(lines[start:stop + 1])

    results = []

    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    os.chdir(ROOT)
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    namespace = {"check": check, "json": json, "os": os}
    exec(compile(source, path, "exec"), namespace)
    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            print("     %s" % detail)
    print("leg527: %d/%d passed" % (len(results) - len(failed), len(results)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())