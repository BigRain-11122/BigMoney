# -*- coding: utf-8 -*-
import io
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
SRC = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
T0 = io.open(REPO + r"\results\_w275bmc_w274_frozen_face.txt", encoding="utf-8", newline="").read()
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~4.4GB", "gpu_face": "GPUSTUB"}
exec(B[i:j], ns)
txt = SRC
for old, new in ns["NEEDLES"]:
    txt = txt.replace(old, new)
P1 = "\x01W\x01"
txt2 = txt
for w in range(274, 258, -1):
    if w == 274:
        txt2 = txt2.replace("W274", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W275")
txt = txt2
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w274", P2).replace("n1_w273", "n1_w274").replace("n1_w272", "n1_w273").replace("n1_w271", "n1_w272").replace(P2, "n1_w275")
txt = txt.replace("_w274bmc", P3).replace("_w273bmc", "_w274bmc").replace("_w272bmc", "_w273bmc").replace(P3, "_w275bmc")

def seg(t, start, end):
    a = t.index(start)
    b = t.index(end, a)
    return t[a:b]

ns2 = {"P1": P1, "P2": P2, "P3": P3, "SPLICE_T": "03:0x"}
exec(seg(txt, "VMAP = [", "VMAP_FLOORS = {"), ns2)
VMAP = ns2["VMAP"]
print("VMAP needle count:", len(VMAP))
for o, n in VMAP:
    if "A-ext" in o or "A-ext" in n:
        print("  old=%r" % o[:70])
        print("  new=%r" % n[:70])
        print("  T0 count old:", T0.count(o))
# where in the canon script does the A-ext pair def sit?
k = txt.find("A-ext seed=")
print("first A-ext in rolled script:", repr(txt[k-40:k+80]))
# check the canon's original pair
c = SRC.find("A-ext seed=")
print("canon original:", repr(SRC[c-40:c+80]))
