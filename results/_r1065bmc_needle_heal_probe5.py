# -*- coding: utf-8 -*-
# r1065 heal-5: lineage check -- W259 derive's own above-own-A asserts (the precedent face)
import io, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w259bmc_prereg_derive.py"
src = io.open(p, encoding="utf-8").read().splitlines()
print("--- W259 derive lines with 'above-own-A' count asserts/floors:")
for i, l in enumerate(src):
    s = l.strip()
    if "above-own-A" in s and ("assert" in s or "count" in s or "':" in s or '":' in s):
        print(i + 1, ":", s[:190])
print()
print("--- W259 derive: assert lines around ordinal gates (search 第八次/第九次):")
for i, l in enumerate(src):
    s = l.strip()
    if s.startswith("assert") and ("第八次" in s or "第九次" in s or "第七次" in s):
        print(i + 1, ":", s[:190])
