# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
L = io.open("scripts/trial_labor_w12.py", encoding="utf-8").read().splitlines()
def show(a, b, tag):
    print("=====", tag)
    for i in range(a - 1, min(b, len(L))):
        print(i + 1, "|", L[i].rstrip()[:155])
show(2540, 2620, "prep gates G-MOM..G-RSQR")
show(3136, 3200, "dual nulls + judge cell head")
show(3200, 3368, "judge cell body")
show(3920, 4000, "judge finalize sums")
show(4063, 4172, "intake")
show(4330, 4370, "selftest L6")
show(4485, 4510, "selftest L7")
show(4848, 4914, "parser")
