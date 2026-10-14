# -*- coding: utf-8 -*-
# r1007 bm-a: structural map of the committed W243 freeze editor (727L)
import io, re
t = io.open(r"results/_w243bma_freeze_edits.py", encoding="utf-8").read()
lines = t.split("\n")
print("total lines", len(lines))
for i, l in enumerate(lines, 1):
    s = l.strip()
    hit = False
    if s.startswith("def ") or s.startswith("class "):
        hit = True
    if s.startswith("#") and ("FACE" in s or "STAGE" in s.upper() or "leg" in s.lower()[:8]):
        hit = True
    if re.match(r"^[A-Z][A-Z0-9_]* ?= ?['\"]", s):
        hit = True
    if s.startswith("# ---"):
        hit = True
    if hit:
        print("%4d %s" % (i, l[:132]))
