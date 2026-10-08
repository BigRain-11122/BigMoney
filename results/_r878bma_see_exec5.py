# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
i = t.find("CL_PAIRS = [")
j = t.find("]", t.find("]", i) + 1)
# after all PAIRS defs, find the assembly section
k = t.find("pf_block_new")
if k < 0:
    k = t.find("vmap(pf_block")
if k < 0:
    k = t.find("vmap(pf")
print("assembly at", k)
print(t[k-400:k+3400])
