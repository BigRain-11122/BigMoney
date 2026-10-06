# -*- coding: utf-8 -*-
"""r779 bm-a W159 pre-TOK probe leg-2: PASS-claim + materializer anchors."""
import io

n = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
cs = n.find('"+ W158 materializer face')
print("claim start found:", cs > 0)
print(repr(n[cs:cs+420]))
print("---materializer block boundaries---")
w = n.find("# --- W158 materializer face")
t2 = n.find("# --- T-141 s2 lane face", w)
blk = n[w:t2]
ci = blk.find("assert pf.N1_BANDS[138]")
cj = blk.find("# prior-wave disjointness")
print("ci,cj:", ci, cj)
import re
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", blk[ci:cj])
print("chain rows:", rows[0], "..", rows[-1], "n=", len(rows))
print("W158 row in chain:", "N1_BANDS[158]" in blk)
print("post head:", repr(blk[cj:cj+200]))
# claim tail: what follows the W158 claim
i = n.find("bm-a]", cs)
print("claim tail area:", repr(n[cs:cs+40]), "...", repr(n[i-80:i+40]))
