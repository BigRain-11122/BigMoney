# -*- coding: utf-8 -*-
import re
t = open(r"research\PERPETUAL_FACES.md", encoding="utf-8").read()
i = t.find("- N1 波51")
nxt = t.find("\n- ", i + 10)
row = t[i:nxt]
open(r"research\_tmp_w51_row.txt", "w", encoding="utf-8", newline="").write(row)
print("row len:", len(row), "| next block:", t[nxt:nxt+40])
