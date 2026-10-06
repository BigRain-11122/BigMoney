# -*- coding: utf-8 -*-
"""r794 bm-a: enumerate the numeric landscape of the four W164 freeze tools to
adjudicate the uniform +2,200 regex advance safety (band dotted/undotted, K
comma, ledger comma, bare 6-digit, floats)."""
import collections
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOOLS = [
    r"results/_r792bma_w164_face_probe.py",
    r"results/_r792bma_w164_prereg_build.py",
    r"results/_r792bma_w164_freeze_edits.py",
    r"results/_r792bma_w164_freeze_verify.py",
]

dotted = collections.Counter()
undot6 = collections.Counter()
comma3 = collections.Counter()
floats = collections.Counter()

for p in TOOLS:
    s = io.open(p, encoding="utf-8").read()
    for m in re.finditer(r"\b3\d{2}_\d{3}\b", s):
        dotted[m.group(0)] += 1
    for m in re.finditer(r"\b\d{6}\b", s):
        undot6[m.group(0)] += 1
    for m in re.finditer(r"\b\d{3},\d{3}\b", s):
        comma3[m.group(0)] += 1
    for m in re.finditer(r"\b0\.0\d{3,}\b", s):
        floats[m.group(0)] += 1

print("== dotted 3xx_xxx ==")
for k, v in sorted(dotted.items()):
    print(f"  {k} x{v}  (+2200 -> {int(k.replace('_',''))+2200:,})")
print("== bare 6-digit ==")
for k, v in sorted(undot6.items()):
    print(f"  {k} x{v}")
print("== comma 3,3 ==")
for k, v in sorted(comma3.items()):
    print(f"  {k} x{v}  (+2200 -> {int(k.replace(',',''))+2200:,})")
print("== 0.0xxx floats ==")
for k, v in sorted(floats.items()):
    print(f"  {k} x{v}")
