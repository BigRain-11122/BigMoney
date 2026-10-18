# -*- coding: utf-8 -*-
import io, re
C = io.open(r"results\_w274bmc_prereg_derive.py", encoding="utf-8").read()
f = "r1101 席位窗实跑"
for m in re.finditer(re.escape(f), C):
    a, b = m.start(), m.end()
    print(repr(C[max(0, a - 60):b + 70]))
    print("----")
