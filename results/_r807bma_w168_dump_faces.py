# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
N1 = r"scripts/perpetual_faces_n1.py"
PF = r"scripts/perpetual_faces.py"
n1 = io.open(N1, encoding="utf-8", newline="").read()
pf = io.open(PF, encoding="utf-8", newline="").read()

EO = '"engine_owner": "bm-a"},'
k = n1.find('167: {"batch"')
assert k > 0
m = n1.find(EO, k) + len(EO)
print("===== n1 WAVE_CONFIGS[167] entry =====")
print(n1[k:m])
print()
w = n1.find("# --- W167 materializer face")
t2 = n1.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2
blk = n1[w:t2]
print("===== W167 mat block len:", len(blk), "=====")
print(blk)
print()
i1 = pf.find("    # W167 (bm-a r805 freeze")
assert i1 > 0, "pf W167 comment block not found"
r1 = pf.find('167: {"a": (', i1)
assert r1 > i1
j1 = pf.find(EO, r1) + len(EO)
blkpf = pf[i1:j1]
print("===== pf W167 comment+row block len:", len(blkpf), "=====")
print(blkpf)
