# -*- coding: utf-8 -*-
import io
C = io.open(r"results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
old = "estate chain r1102 W273 同窗全周期（r1102-continuation absorb-healed）839441a547+04f2127db+6659a0e362"
print("needle-old count:", C.count(old))
k = C.find("estate chain r1102")
print(repr(C[k:k+160]))
