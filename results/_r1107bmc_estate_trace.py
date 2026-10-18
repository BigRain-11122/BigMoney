# -*- coding: utf-8 -*-
import io, re
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
SRC = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~4.4GB", "gpu_face": "GPUSTUB"}
exec(B[i:j], ns)
txt = SRC
for n, (old, new) in enumerate(ns["NEEDLES"]):
    before = txt.count("estate chain")
    txt = txt.replace(old, new)
    after = txt.count("estate chain")
    if before != after:
        print("needle %d old=%r changed estate-count %d->%d" % (n, old[:60], before, after))
for m in re.finditer("estate chain", txt):
    print(repr(txt[m.start():m.start()+90]))
P1 = "\x01W\x01"
t2 = txt
for w in range(274, 258, -1):
    if w == 274:
        t2 = t2.replace("W274", P1)
    else:
        t2 = t2.replace("W%d" % w, "W%d" % (w + 1))
t2 = t2.replace(P1, "W275")
print("after chain:")
for m in re.finditer("estate chain", t2):
    print(repr(t2[m.start():m.start()+90]))
