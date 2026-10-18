# -*- coding: utf-8 -*-
# r1107 diagnostic: audit every builder needle old-face count in the W274 canon SRC.
# Zero-hit needles are suspects (some intentional consumed faces, some wrong-gen bugs).
import io, re, sys
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
SRC = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
seg = B[i:j]
ns = {"ram_face": "~DIAGGB", "gpu_face": "DIAG_GPU"}
exec(seg, ns)
needles = ns["NEEDLES"]
zero, hits = [], {}
for old, new in needles:
    c = SRC.count(old)
    hits[old] = c
    if c == 0:
        zero.append((old, new))
print("total needles:", len(needles))
print("zero-hit needles:", len(zero))
for o, n in zero:
    print("  ZERO old=%r" % o[:110])
    print("       new=%r" % n[:110])
