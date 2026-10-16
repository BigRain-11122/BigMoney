# -*- coding: utf-8 -*-
"""r1055 absorb: dump P5e-pr chunk src/dst + the actual source block around it."""
import io

ED = r"results\_w254bmc_derive_editor.py"
SRC = r"results\_w253bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8").read()
ed = io.open(ED, encoding="utf-8").read()

i1 = ed.find('"P5e-pr")')
i0 = ed.rfind("chunk('''", 0, i1)
region = ed[i0:i1 + len('"P5e-pr")')]
parts = region.split("'''")
src, dst = parts[1], parts[3]
print("=== P5e-pr SRC (needle pre-xf) ===")
print(src)
print("=== P5e-pr DST ===")
print(dst)
print("=== source block containing 'staircase-affects-A walk SECOND' ===")
j = t.find("W253 A staircase-affects-A walk SECOND consecutive A-hop")
print(repr(t[max(0, j - 300):j + 700]))
