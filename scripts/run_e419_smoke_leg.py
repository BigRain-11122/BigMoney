"""Run the E419 smoke leg verbatim from smoke_test.py, without executing the rest of the suite."""
import io
import json
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

text = io.open("smoke_test.py", encoding="utf-8").read()
start = text.index("# E419 (r1437 bm-b)")
end = text.index("or _d419)\n", start) + len("or _d419)\n")
block = text[start:end]

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


env = {"check": check, "json": json, "os": os, "__name__": "e419_leg"}
exec(compile(block, "smoke_test.py:E419", "exec"), env)
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + detail)
print("legs %d/%d" % (sum(1 for r in results if r[1]), len(results)))
sys.exit(0 if all(r[1] for r in results) else 1)