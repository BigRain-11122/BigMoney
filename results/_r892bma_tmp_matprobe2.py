# -*- coding: utf-8 -*-
import io
t = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
import re
for m in re.finditer(r"pf\.N1_BANDS\[188\]", t):
    k = m.start()
    # which materializer block is this in?
    blk = t.rfind("# --- W18", 0, k)
    blk2 = t.rfind("# --- W19", 0, k)
    b = max(blk, blk2)
    print("at", k, "in block starting", t[b:b+40].split("\r\n")[0])
    print("   context:", repr(t[k-60:k+140]))
    print()
# also count total mat blocks
print("W187 mat:", t.count("# --- W187 materializer face"))
print("W188 mat:", t.count("# --- W188 materializer face"))
print("W189 mat:", t.count("# --- W189 materializer face"))
