# -*- coding: utf-8 -*-
"""r1055 absorb: stage the W254 editor up to (excluding) P5e-pr, dump staged t."""
import io

ED = r"results\_w254bmc_derive_editor.py"
OUT = r"results\_r1055bmc_editor_staged.py"

t = io.open(ED, encoding="utf-8").read()

# cut everything from the P5e-pr chunk call onward
i = t.find('chunk(\'\'\'\n\'          "A=1-HOP STAIRCASE-AFFECTS-A walk')
assert i > 0, "P5e-pr chunk call not found"
staged = t[:i]

# append instrumentation: dump staged t + the P5e-pr needle (pre-xf and post-xf)
tail = '''

# --- r1055 absorb instrumentation: dump staged state ---
with io.open(r"results/_r1055bmc_staged_t.txt", "w", encoding="utf-8", newline="") as f:
    f.write(t)
_i1 = t.find('"P5e-pr")')
print("staged t len", len(t))
print("A=1-HOP count in staged t:", t.count("A=1-HOP STAIRCASE-AFFECTS-A walk"))
print("chain-order splice count:", t.count("chain-order splice from the "))
print("STAGE DUMP OK")
'''
io.open(OUT, "w", encoding="utf-8", newline="").write(staged + tail)
print("staged editor written:", OUT, "staged len", len(staged))
