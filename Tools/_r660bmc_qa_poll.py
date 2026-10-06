# -*- coding: utf-8 -*-
"""r660 bm-c QA runner poll: wait for terminal state in runner .out, print tail."""
import time
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r660bmc_qa_runner.out"
t = ""
for i in range(60):
    time.sleep(5)
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        t = ""
    low = t.lower()
    if ("summary" in low or "5/5" in t or "fail" in low) and len(t) > 200:
        break
print(t[-2500:] if t else "EMPTY")
