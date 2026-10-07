# -*- coding: utf-8 -*-
import io
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
k = n1.find('169: {"batch"')
EO = '"engine_owner": "bm-a"},'
m = n1.find(EO, k) + len(EO)
print("after-entry 60 chars:", repr(n1[m:m + 60]))
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
i1 = pf.find("    # W169 (bm-a r811 freeze")
r1 = pf.find('169: {"a": (386_604', i1)
j1 = pf.find(EO, r1) + len(EO)
print("after-pf-row 40 chars:", repr(pf[j1:j1 + 40]))
