# -*- coding: utf-8 -*-
"""r771 bm-a: read the r769 W156 band-gate leg3 derivation code."""
import io, re

s = io.open(r"results/_r769bma_w156_band_gate.py", "r", encoding="utf-8", newline="").read()
i = s.find("leg3")
print(s[max(0, i - 200): i + 2600])
