# -*- coding: utf-8 -*-
"""r779 bm-a W159 pre-TOK probe leg-3: materializer pre/post exact faces."""
import io
import re

n = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
w = n.find("# --- W158 materializer face")
t2 = n.find("# --- T-141 s2 lane face", w)
blk = n[w:t2]
ci = blk.find("assert pf.N1_BANDS[138]")
cj = blk.find("# prior-wave disjointness")
pre, chain, post = blk[:ci], blk[ci:cj], blk[cj:]
io.open(r"results/_r779bma_w159_mat_pre.txt", "w", encoding="utf-8", newline="").write(pre)
io.open(r"results/_r779bma_w159_mat_chain.txt", "w", encoding="utf-8", newline="").write(chain)
io.open(r"results/_r779bma_w159_mat_post.txt", "w", encoding="utf-8", newline="").write(post)
print("=== PRE (", len(pre), "bytes) ===")
print(pre)
print("=== CHAIN head 400 ===")
print(chain[:400])
print("=== CHAIN tail 700 ===")
print(chain[-700:])
print("=== POST (", len(post), "bytes) ===")
print(post)
