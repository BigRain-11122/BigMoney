# -*- coding: utf-8 -*-
# r1065 heal-2: locate the erroneous B-ordinal shift leg in the derive vmap
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w260bmc_prereg_derive.py", encoding="utf-8").read().splitlines()
print("--- lines containing 'above-own-A' with shift context (vmap/pairs/tuple):")
for i, l in enumerate(src):
    s = l.strip()
    if "above-own-A" in s:
        print(i + 1, ":", s[:200])
print()
print("--- lines containing vmap/PAIRS/SUBS definitions (first 40):")
n = 0
for i, l in enumerate(src):
    s = l.strip()
    if ("VMAP" in s or "PAIRS" in s.upper() or "SUBS" in s.upper() or "vmap" in s) and ("=" in s or "def" in s or "[" in s or "{" in s):
        print(i + 1, ":", s[:200])
        n += 1
        if n >= 40:
            break
