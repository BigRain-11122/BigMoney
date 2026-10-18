# -*- coding: utf-8 -*-
import io, re
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
SRC = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
print("canon 39e1bb32f1 count:", SRC.count("39e1bb32f1"))
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~4.4GB", "gpu_face": "GPUSTUB"}
exec(B[i:j], ns)
txt = SRC
for n, (old, new) in enumerate(ns["NEEDLES"]):
    c0 = txt.count("39e1bb32f1")
    txt = txt.replace(old, new)
    c1 = txt.count("39e1bb32f1")
    if c0 != c1:
        print("needle %d %r -> count %d->%d" % (n, old[:50], c0, c1))
P1 = "\x01W\x01"
t2 = txt
for w in range(274, 258, -1):
    if w == 274:
        t2 = t2.replace("W274", P1)
    else:
        t2 = t2.replace("W%d" % w, "W%d" % (w + 1))
t2 = t2.replace(P1, "W275")
txt = t2
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w274", P2).replace("n1_w273", "n1_w274").replace("n1_w272", "n1_w273").replace("n1_w271", "n1_w272").replace(P2, "n1_w275")
txt = txt.replace("_w274bmc", P3).replace("_w273bmc", "_w274bmc").replace("_w272bmc", "_w273bmc").replace(P3, "_w275bmc")
print("final count:", txt.count("39e1bb32f1"))
for m in re.finditer("39e1bb32f1", txt):
    a, b = m.start(), m.end()
    print("  ctx:", repr(txt[max(0, a - 80):b + 40]))
