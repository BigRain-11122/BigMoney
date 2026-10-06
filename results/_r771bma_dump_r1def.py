# -*- coding: utf-8 -*-
"""r771 bm-a: dump W155 template lines 35-80 (r1 construction)."""
import io

s = io.open(r"results/_r768bma_w155_freeze_edits.py", encoding="utf-8", newline="").read()
lines = s.splitlines()
for i in range(35, 81):
    print(f"{i:4d} {lines[i][:150]}")
