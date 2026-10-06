# -*- coding: utf-8 -*-
src = open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()

# 1) W157 entry tail
i = src.find('157: {"batch"')
j = src.find('"engine_owner": "bm-a"},', i)
print("=== W157 entry tail (last 700 chars) ===")
print(src[j - 500:j + 40])

# 2) materializer chain region
w = src.find("# --- W157 materializer face")
if w < 0:
    w = src.find("# --- W156 materializer face")
print("=== materializer anchor at", w, "===")
t2 = src.find("# --- T-141 s2 lane face", w)
print("t2 =", t2)
block = src[w:t2]
print("block len =", len(block))
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
print("ci =", ci, "cj =", cj)
import re
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", block[ci:cj])
print("chain rows:", rows[0], "..", rows[-1], "n=", len(rows))

# 3) PASS snippet claim area
cs = src.find('"+ W157 materializer face')
if cs < 0:
    cs = src.find('"+ W156 materializer face')
print("=== claim area at", cs, "===")
print(src[cs - 200:cs + 900])
