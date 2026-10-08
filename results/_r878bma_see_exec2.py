# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
j = t.find("pf_block = vmap")
if j < 0:
    j = t.find("vmap(")
print("vmap calls at", j)
print(t[j-200:j+2600])
