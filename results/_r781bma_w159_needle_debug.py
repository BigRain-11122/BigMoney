# -*- coding: utf-8 -*-
"""needle-shape debug: dump the physical lines around the mat-block
delivery prose (post-vmap) to get the exact fragment shape."""
import io
import sys

sys.argv = ["x"]
exec(io.open(r"results\_r781bma_w159_freeze_edits.py", encoding="utf-8").read()
     .split("pfsrc = io.open")[0])  # definitions only

N1 = r"scripts/perpetual_faces_n1.py"
n1src = io.open(N1, encoding="utf-8", newline="").read()
w = n1src.find("# --- W158 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
block = n1src[w:t2]
ci = block.find("assert pf.N1_BANDS[138]")
pre = block[:ci]
post_v = vmap(pre)
i = post_v.find("direct fast-forward")
print(repr(post_v[i - 120:i + 400]))
