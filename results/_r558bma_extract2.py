# -*- coding: utf-8 -*-
"""Extract W48 prereg sections 0-4 and 6 for W52 copy-adapt."""
import re

t = open(r"research\PERPETUAL_N1_W48_PREREG.md", encoding="utf-8").read()
parts = re.split(r"(?m)^(## .+)$", t)
out = []
for i in range(1, len(parts), 2):
    head = parts[i]
    m = re.match(r"## .*(\d+(?:\.\d+)?)", head)
    if m and m.group(1) in ("0", "0.5", "1", "2", "3", "4", "6"):
        out.append(head + parts[i + 1])
open(r"research\_tmp_w48_sections.txt", "w", encoding="utf-8", newline="").write("\n".join(out))
print("ok", len(out))
