# -*- coding: utf-8 -*-
"""r771 bm-a: extract leg3 code block from the r769 W156 gate."""
import io

s = io.open(r"results/_r769bma_w156_band_gate.py", "r", encoding="utf-8", newline="").read()
i = s.find("# --- leg 3")
if i < 0:
    i = s.find("leg 3")
print(s[i:i + 3000])
