# -*- coding: utf-8 -*-
"""r771 bm-a: dump the W155 editor LEG list content (lines 163-377)."""
import io

s = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()
lines = s.splitlines()
for i in range(163, 378):
    print(f"{i:4d} {lines[i][:165]}")
