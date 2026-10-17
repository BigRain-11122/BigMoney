# -*- coding: utf-8 -*-
# r1065 needle-heal probe: count ordinal needles in frozen W259 template + dump vmap legs from derive script
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T1 = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w260bmc_w259_frozen_face.txt", encoding="utf-8").read()
needles = [
    "第七次连续 above-own-A",
    "第八次连续 above-own-A",
    "第九次连续 above-own-A",
    "第十次连续 above-own-A",
    "第七次连续 A-hop",
    "第八次连续 A-hop",
    "第九次连续 A-hop",
    "第十次连续 A-hop",
    "连续八波",
    "连续九波",
    "〔第九次连续〕",
    "〔第十次连续〕",
    "〔第八次连续〕",
]
for n in needles:
    print("T1 %-28r -> %d" % (n, T1.count(n)))
print()
src = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w260bmc_prereg_derive.py", encoding="utf-8").read().splitlines()
print("--- derive lines containing ordinal-shift legs (第八/第九/第十 with replace context):")
for i, l in enumerate(src):
    s = l.strip()
    if ("第八次" in s or "第九次" in s or "第十次" in s) and ("replace(" in s or "\"VMOVERALL" in s or "VMAP" in s or ".replace" in s or "SUBS" in s or "PAIRS" in s or "->" in s):
        print(i + 1, ":", s[:160])
print()
print("--- all lines with .replace( containing 次 (first 30):")
n = 0
for i, l in enumerate(src):
    if ".replace(" in l and "次" in l:
        print(i + 1, ":", l.strip()[:160])
        n += 1
        if n >= 30:
            break
