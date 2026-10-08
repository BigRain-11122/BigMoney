# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
j = t.find("NEW_PF")
if j < 0:
    j = t.find("pf_block = vmap")
if j < 0:
    j = t.find("vmap(pf_block")
if j < 0:
    j = t.find("vmap(")
print("at", j)
print(t[j:j+3000])
