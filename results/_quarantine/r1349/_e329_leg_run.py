"""Execute the E329 leg text out of smoke_test.py, standalone (a re-implementation would only
prove the copy).  Prints PASS/FAIL for the leg only."""
import io
import json
import os
import sys

src = io.open("smoke_test.py", encoding="utf-8").read()
start = src.index("# E329: a source that names two vintages")
end = src.index("    return _finish()", start)
body = "\n".join(l[4:] if l.startswith("    ") else l for l in src[start:end].splitlines())

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))


ns = {"os": os, "sys": sys, "json": json, "check": check}
exec(compile(body, "smoke_test.py:E329", "exec"), ns)
print("\n%d/%d legs passed" % (sum(1 for r in results if r[1]), len(results)))
sys.exit(0 if all(r[1] for r in results) else 1)
