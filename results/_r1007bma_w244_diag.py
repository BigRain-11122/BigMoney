# -*- coding: utf-8 -*-
# r1007: diagnose B_A7/B_A8 block mismatches vs template bytes
import io, difflib
R = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
tpl = io.open(R + r"\results\_w243bma_freeze_edits.py", encoding="utf-8").read()
ns = {}
exec(compile(io.open(R + r"\results\_r1007bma_w244_gen_b2.py", encoding="utf-8").read(), "b2", "exec"), ns)
ns3 = {}
exec(compile(io.open(R + r"\results\_r1007bma_w244_gen_b3.py", encoding="utf-8").read(), "b3", "exec"), ns3)

for tag, old in [("B_A7_OLD", ns["B_A7_OLD"]), ("B_A8_OLD", ns3["B_A8_OLD"]),
                 ("B_A6_OLD", ns["B_A6_OLD"]), ("B_A5_OLD", ns["B_A5_OLD"]),
                 ("B_A9A_OLD", ns3["B_A9A_OLD"]), ("B_A9B_OLD", ns3["B_A9B_OLD"])]:
    c = tpl.count(old)
    print("=== %s count=%d ===" % (tag, c))
    if c == 0:
        # find the first line of the block and locate the real region
        first = old.split("\n")[0]
        idx = tpl.find(first)
        print("first-line find idx:", idx)
        if idx >= 0:
            real = tpl[idx:idx + len(old) + 400]
            print("--- REAL BYTES ---")
            print(real[:len(old) + 120])
            print("--- GEN OLD ---")
            print(old[:len(old) + 120])
