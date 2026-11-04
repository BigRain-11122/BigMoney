"""Run the E403 smoke leg verbatim from smoke_test.py, without executing the rest of the suite."""
import io
import json
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

text = io.open("smoke_test.py", encoding="utf-8").read()
start = text.index("# E403: E398 stopped at")
marker = '# E414 (r1433 bm-b)'
end = text.index(marker, start)
block = text[start:end]
# the block ends with the leg's check(...) call, not with an "or _d403)" detail line
assert "check(_name403" in block, "the E403 leg block lost its check call"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


env = {"check": check, "json": json, "os": os, "sys": sys, "__name__": "e403_leg"}
exec(compile(block, "smoke_test.py:E403", "exec"), env)
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + str(detail))
print("legs %d/%d" % (sum(1 for r in results if r[1]), len(results)))
sys.exit(0 if all(r[1] for r in results) else 1)