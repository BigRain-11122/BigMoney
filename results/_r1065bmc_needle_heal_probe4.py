# -*- coding: utf-8 -*-
# r1065 heal-4: check needle probe's simulated block content for the ninth above-own-A phrasing
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w260bmc_needle_probe.py", encoding="utf-8").read()
n = "第九次连续 above-own-A"
pos = 0
k = 0
while True:
    i = src.find(n, pos)
    if i < 0:
        break
    k += 1
    print("=== probe-script instance %d at byte %d ===" % (k, i))
    print(src[max(0, i - 300):i + 150].replace("\n", " | "))
    print()
    pos = i + len(n)
print("probe script total instances:", k)
