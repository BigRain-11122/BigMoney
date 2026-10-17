# -*- coding: utf-8 -*-
# r1065 heal-3: dump template contexts of the 3 "第九次连续 above-own-A" instances to mirror into NEW blocks
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T1 = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w260bmc_w259_frozen_face.txt", encoding="utf-8").read()
n = "第九次连续 above-own-A"
pos = 0
k = 0
while True:
    i = T1.find(n, pos)
    if i < 0:
        break
    k += 1
    print("=== instance %d at byte %d ===" % (k, i))
    print(T1[max(0, i - 260):i + 200].replace("\n", " | "))
    print()
    pos = i + len(n)
