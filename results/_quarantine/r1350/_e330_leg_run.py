"""Run the E330 smoke leg standalone by exec-ing its own text out of smoke_test.py.

The suite is ~35 minutes; extracting the leg proves the shipped text, not a re-implementation.
"""
import io
import json
import os
import sys

src = io.open("smoke_test.py", encoding="utf-8").read()
start = src.index("# E330: a construct that picks between two references")
end = src.index("return _finish()", start)
block = src[start:end]
block = chr(10).join((l[4:] if l.startswith(chr(32)*4) else l) for l in block.split(chr(10)))

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))


ns = {"check": check, "json": json, "os": os, "sys": sys, "__name__": "e330_leg"}
exec(compile(block, "smoke_test.py:E330", "exec"), ns)
bad = [r for r in results if not r[1]]
print("\n%d/%d passed" % (len(results) - len(bad), len(results)))
sys.exit(0 if not bad else 1)