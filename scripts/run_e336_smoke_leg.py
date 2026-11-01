"""Extract the E336 smoke leg verbatim and run it standalone (r1356 wall-budget workaround).

The full suite is ~35 min; this pulls the exact leg text out of smoke_test.py and executes it under a
minimal check() harness so the published leg is proven against the published face, not paraphrased.
"""
import io
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smoke_test.py")
START = "# E336:"
END = "    return _finish()"

lines = io.open(SRC, encoding="utf-8").read().splitlines()
start = next(i for i, ln in enumerate(lines) if ln.strip().startswith(START))
end = next(i for i, ln in enumerate(lines[start:], start) if ln == END)
body = []
for ln in lines[start:end]:
    body.append(ln[4:] if ln.startswith("    ") else ln)

harness = [
    "import json, os, sys",
    "RESULTS = []",
    "def check(name, ok, detail=''):",
    "    RESULTS.append((name, bool(ok), detail))",
    "    print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
    "",
]
ns = {"__name__": "e336_leg"}
exec(compile("\n".join(harness + body), "e336_leg", "exec"), ns)
bad = [r for r in ns["RESULTS"] if not r[1]]
print("%d/%d legs passed" % (len(ns["RESULTS"]) - len(bad), len(ns["RESULTS"])))
sys.exit(1 if bad else 0)