"""Extract the E415 smoke leg verbatim and run it standalone (the full suite is ~30 min).

Same workaround as ``scripts/run_e412_smoke_leg.py``: the exact leg text is pulled out of
``smoke_test.py`` and executed under a minimal ``check()`` harness, so the published leg is proven
against the published face rather than paraphrased into a second copy that can drift.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "smoke_test.py")
START = "# E415 (r1434 bm-b)"
END = 'if __name__ == "__main__":'

lines = io.open(SRC, encoding="utf-8").read().splitlines()
start = next(i for i, ln in enumerate(lines) if ln.startswith(START))
end = next(i for i, ln in enumerate(lines[start:], start) if ln.startswith(END))
body = lines[start:end]

harness = [
    "import json, os, sys",
    "RESULTS = []",
    "def check(name, ok, detail=''):",
    "    RESULTS.append((name, bool(ok), detail))",
    "    print(('PASS' if ok else 'FAIL') + ' :: ' + name, '' if ok else detail)",
    "",
]
# the leg reads faces and imports the study by repo-relative name, exactly as the suite does
os.chdir(ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
ns = {"__name__": "e415_leg"}
exec(compile("\n".join(harness + body), "e415_leg", "exec"), ns)
bad = [r for r in ns["RESULTS"] if not r[1]]
print("%d/%d legs passed" % (len(ns["RESULTS"]) - len(bad), len(ns["RESULTS"])))
sys.exit(1 if bad else 0)