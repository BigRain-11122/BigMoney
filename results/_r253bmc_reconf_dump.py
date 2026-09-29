#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c: dump origin CODELY.md full + my archive r252 section full."""
import subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

co = blob(2, "CODELY.md").decode("utf-8")
print("===== ORIGIN CODELY.md (%dB) =====" % len(co.encode("utf-8")))
for i, line in enumerate(co.splitlines()):
    print("%02d| %s" % (i, line[:120]))

at = blob(3, "research/memory-archive/202609.md").decode("utf-8")
lines = at.splitlines()
start = None
for i, l in enumerate(lines):
    if l.startswith("## ") and "r252 bm-c 窗批" in l:
        start = i; break
print("\n===== MY archive r252 section (from line %d) =====" % start)
for l in lines[start:start + 40]:
    print(l[:170])
print("... (section continues to line %d)" % (start + 40 if start + 40 < len(lines) else len(lines)))
# also show tail of origin archive to find append point
ao = blob(2, "research/memory-archive/202609.md").decode("utf-8")
ol = ao.splitlines()
print("\n===== ORIGIN archive tail (last 12 lines of %d) =====" % len(ol))
for l in ol[-12:]:
    print(l[:170])
