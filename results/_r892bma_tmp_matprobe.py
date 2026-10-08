# -*- coding: utf-8 -*-
import io
import re
t = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
print("pf.N1_BANDS[188] count:", t.count("pf.N1_BANDS[188]"))
print("pf.N1_BANDS[189] count:", t.count("pf.N1_BANDS[189]"))
print("pf.N1_BANDS[187] count:", t.count("pf.N1_BANDS[187]"))
i = t.find("--- W189 materializer")
seg = t[i:i + 24000]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] == \{\"a\": \((\d+_\d+), (\d+_\d+)\)", seg)
print("W189 mat chain rows found:", len(rows))
for r in rows[-6:]:
    print(r)
stamps = re.findall(r"registered W(\d+) row parity drift \(r307; bm-a r(\d+)\)", seg)
print("stamps tail:", stamps[-6:])
mat = io.open(r"results\_r892bma_w190_probe_n1_mat.txt", encoding="utf-8", newline="").read()
rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] == \{\"a\": \((\d+_\d+), (\d+_\d+)\)", mat)
print("dump rows:", len(rows2), "tail:", rows2[-4:])
stamps2 = re.findall(r"registered W(\d+) row parity drift \(r307; bm-a r(\d+)\)", mat)
print("dump stamps tail:", stamps2[-6:])
