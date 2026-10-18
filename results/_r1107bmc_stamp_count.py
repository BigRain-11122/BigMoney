# -*- coding: utf-8 -*-
import io
C = io.open(r"results\_w274bmc_prereg_derive.py", encoding="utf-8").read()
Q = chr(34)
for stamp in ["00:3x", "00:2x", "01:0x", "20:4x", "20:2x", "18:4x"]:
    f = Q + stamp + Q + ","
    print(repr(f), "->", C.count(f))
