# -*- coding: utf-8 -*-
# r1107 diagnostic 4: which generated VMAP needle eats the paradigm face?
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
face = "bm-c r1102 W273 §7 范式"
print("T0 raw count:", T0.count(face))
t = T0
for k, (o, n) in enumerate(VMAP):
    c = t.count(o)
    if c and (face in o or o in face or "范式" in o or "bm-c r11" in o):
        print("VMAP[%d] old=%r" % (k, o[:110]))
        print("         new=%r  count=%d" % (n[:110], c))
    t2 = t.replace(o, n)
    if t2.count(face) != t.count(face):
        print(">>> VMAP[%d] CHANGED paradigm-face count %d -> %d" % (k, t.count(face), t2.count(face)))
        print("    old=%r" % o[:130])
        print("    new=%r" % n[:130])
    t = t2
print("post-VMAP count:", t.count(face))
