# -*- coding: utf-8 -*-
"""Extract W51 WAVE_CONFIGS entry + selftest leg for W52 copy-adapt."""
import os, sys

src = open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
T = os.environ["TEMP"]

i = src.find('    51: {"batch"')
assert i > 0
# entry ends where the dict literal closes: find the line starting with '    }' at same depth
j = src.find("\n    }", i)
seg = src[i:j + len("\n    }")]
open(os.path.join(T, "w51_entry.txt"), "w", encoding="utf-8", newline="").write(seg)
print("entry len:", len(seg))

m = src.find("W51 materializer face")
s2 = src.rfind("\n    # ---", 0, m)
e2 = src.find("\n    # ---", m)
leg = src[s2:e2]
open(os.path.join(T, "w51_leg.txt"), "w", encoding="utf-8", newline="").write(leg)
print("leg len:", len(leg))
print("next block head:", repr(src[e2:e2+180]))
