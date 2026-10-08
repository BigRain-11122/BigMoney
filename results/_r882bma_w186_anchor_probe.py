# -*- coding: utf-8 -*-
# r882 bm-a: pre-freeze anchor verification probe (W186)
import io

NL = "\r\n"
pf = io.open("scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
n1 = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
EO = '"engine_owner": "bm-a"},'
print("pf EO+close count:", pf.count(EO + NL + "}"))
print("n1 EO+IND23+close count:", n1.count(EO + NL + " " * 23 + "}"))
print("n1 T141 anchor:", n1.count("    # --- T-141 s2 lane face"))
print("n1 claim anchor:", n1.count('"r878 bm-a] "' + NL + " " * 10 + '"+ T-141 s2 "'))
print("n1 mat W185 block:", n1.count("# --- W185 materializer face"))
print("pf W185 block:", pf.count("# W185 (bm-a r878 freeze"))
print("n1 185 batch entry:", n1.count('185: {"batch": "PERPETUAL-N1-W185",'))
print("pf N1_BANDS len check: has 185:", '"a": (421_804, 423_803)' in pf)
