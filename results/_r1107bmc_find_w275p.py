# -*- coding: utf-8 -*-
# r1107 diagnostic 6: locate the surviving W275+ 投影 in rolled T2.
import io, re
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
exec(seg(txt, "VMAP_POST_LEGS = [", "for o, n, f in VMAP_POST_LEGS:"), ns2)
exec(seg(txt, "NEW = {", "# marker pairs:"), ns2)
exec(seg(txt, "BLOCKS = [", "T2 = T1"), ns2)
VMAP, POST_LEGS, NEW, BLOCKS = ns2["VMAP"], ns2["VMAP_POST_LEGS"], ns2["NEW"], ns2["BLOCKS"]

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t
T1 = xf(T0)
for o, n, f in POST_LEGS:
    T1 = T1.replace(o, n)
T2 = T1
for name, sm, em in BLOCKS:
    a = T2.index(sm)
    b = T2.find(em, a) + len(em)
    T2 = T2[:a] + NEW[name].replace("@@SPLICE_T@@", "03:0x") + T2[b:]
face = "W275+ 投影"
print("T2 count:", T2.count(face))
for m in re.finditer(re.escape(face), T2):
    a, b = m.start(), m.end()
    print("  ctx:", repr(T2[max(0, a - 100):b + 80]))
# also: which BLOCK NEW or live region?
for name in NEW:
    if face in NEW[name]:
        print("in NEW[%s] count=%d" % (name, NEW[name].count(face)))
