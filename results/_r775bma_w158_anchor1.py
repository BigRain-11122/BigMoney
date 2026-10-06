# -*- coding: utf-8 -*-
src = open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
i = src.find('157: {"batch"')
print("W157 entry at", i)
seg = src[i - 80:i + 2600]
print(seg)
