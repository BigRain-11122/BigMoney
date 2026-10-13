# -*- coding: utf-8 -*-
# r980 L3 needle audit: run the generator with a collecting rep() (log-and-continue),
# report ALL failing needles in one pass. Derived verbatim from _r977bmc_r35gen.py.
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

src = open(r"results\_r977bmc_r35gen.py", encoding="utf-8").read()

# swap the rep() helper for a collecting version (same signature; on count!=n logs and continues)
old_rep = '''def rep(old, new, n=1):
    global t
    c = t.count(old)
    assert c == n, f"rep count {c} != {n}: {old[:80]!r}"
    t = t.replace(old, new)'''
new_rep = '''FAILS = []
def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        FAILS.append((c, n, old))
        return
    t = t.replace(old, new)'''
assert old_rep in src, "rep helper face drifted"
src = src.replace(old_rep, new_rep)

# strip the final verify block (module import checks would run on a partially-updated text)
marker = "# ---- dict rename + final writes ----"
head, tail = src.split(marker)
src = head + "print('AUDIT FAILS:', len(FAILS))\nfor c, n, old in FAILS:\n    print('FAIL count=%d want=%d' % (c, n), repr(old[:110]))\n"

g = {"__name__": "audit"}
exec(compile(src, "r35gen_audit", "exec"), g)
