# -*- coding: utf-8 -*-
import io

t = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", errors="replace", newline="").read().replace("\r\n", "\n")
i = t.find('    194: {"batch": "PERPETUAL-N1-W194"')
print("BEFORE194:", repr(t[i - 100:i + 60]))
j = t.find('    195: {"batch": "PERPETUAL-N1-W195"')
print("BEFORE195:", repr(t[j - 40:j + 40]))
k = t.find("\n" + " " * 19 + "    195")
print("IND19-prefixed 195:", k >= 0)
m = t.find("\n" + " " * 19 + "    194")
print("IND19-prefixed 194:", m >= 0)
