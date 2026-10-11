# -*- coding: utf-8 -*-
import sys, io, ast
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open(r"results\_r908bmc_w213_prereg_build.py", encoding="utf-8").read()
i = src.find('("5. **W213')
j = src.find('"', i+2)
old = ast.literal_eval(src[i+1:j+1])
t = open(r"research\PERPETUAL_N1_W212_PREREG.md", encoding="utf-8").read()
phys_i = t.find("5. **W213+")
phys = t[phys_i:phys_i+len(old)+80]
n = min(len(phys), len(old))
for k in range(n):
    if phys[k] != old[k]:
        print(f"divergence at {k}: phys={phys[max(0,k-25):k+25]!r}")
        print(f"                  old ={old[max(0,k-25):k+25]!r}")
        break
else:
    print("no divergence in compared range; phys len", len(phys), "old len", len(old))
print("count:", t.count(old))
