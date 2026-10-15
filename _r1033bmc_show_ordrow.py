# -*- coding: utf-8 -*-
import io

REC = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_RECOVERED.py"
t = io.open(REC, encoding="utf-8").read()
i = t.find("ord_row_c = (")
j = t.find("\n", t.find("in-flight", i))
seg = t[i:j]
io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\_r1033bmc_ordrow_exact.txt", "w", encoding="utf-8").write(seg)
print("segment bytes:", len(seg.encode("utf-8")))
# print python-escaped form for patch construction
print(repr(seg[-400:]))
