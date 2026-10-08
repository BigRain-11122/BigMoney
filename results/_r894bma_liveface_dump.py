# -*- coding: utf-8 -*-
import io
src = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
i = src.find('190: {"batch"')
j = src.find("    },", i)
print(repr(src[i:j + 7]))
print("---LEN---", j - i)
mat_i = src.find("# --- W190 materializer face")
mat_j = src.find("_set_wave(190)", mat_i)
seg = src[mat_i:mat_j + 14]
print("---MAT HEAD---")
print(repr(seg[:400]))
print("---MAT TAIL---")
print(repr(seg[-400:]))
print("---MAT LEN---", len(seg))
k = src.find('"r892 bm-a] "', mat_i)
print("---CLAIM CONTEXT---")
print(repr(src[k - 300:k + 120]))
