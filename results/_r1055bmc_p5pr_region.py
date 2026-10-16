# -*- coding: utf-8 -*-
"""r1055 absorb: dump the ACTUAL source region containing the P5e-pr needle text."""
import io

SRC = r"results\_w253bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()

j = t.find("A=1-HOP STAIRCASE-AFFECTS-A walk")
print("=== region around 'A=1-HOP STAIRCASE-AFFECTS-A walk' (j=%d) ===" % j)
print(t[max(0, j - 200):j + 800])
