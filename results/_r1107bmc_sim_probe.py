# -*- coding: utf-8 -*-
# r1107 diagnostic: replicate builder needle chain + W-chain, exec generated VMAP/FLOORS/
# POST_LEGS/BLOCKS, run them on the frozen T0' and report every BLOCKS marker count.
import io, re
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
SRC = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
T0 = io.open(REPO + r"\results\_w275bmc_w274_frozen_face.txt", encoding="utf-8", newline="").read()

# needles
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~4.4GB", "gpu_face": "GPUSTUB"}
exec(B[i:j], ns)
NEEDLES = ns["NEEDLES"]
txt = SRC
for old, new in NEEDLES:
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

ns2 = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01", "SPLICE_T": "03:0x"}
exec(seg(txt, "VMAP = [", "VMAP_FLOORS = {"), ns2)
exec(seg(txt, "VMAP_FLOORS = {", "def xf(t):"), ns2)
exec(seg(txt, "VMAP_POST_LEGS = [", "for o, n, f in VMAP_POST_LEGS:"), ns2)
exec(seg(txt, "BLOCKS = [", "T2 = T1"), ns2)
VMAP, FLOORS, POST_LEGS, BLOCKS = ns2["VMAP"], ns2["VMAP_FLOORS"], ns2["VMAP_POST_LEGS"], ns2["BLOCKS"]

# report floors status on raw T0
print("== FLOORS on raw T0 (f>0, count mismatch) ==")
for o, f in FLOORS.items():
    if f:
        c = T0.count(o)
        if c != f:
            print("  floor %-60r f=%d c=%d" % (o[:58], f, c))
print("== zero-floors violated on raw T0 ==")
for o, f in FLOORS.items():
    if f == 0 and T0.count(o):
        print("  zero %r count=%d" % (o[:58], T0.count(o)))

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t
T1 = xf(T0)
for o, n, f in POST_LEGS:
    c = T1.count(o)
    if c < f:
        print("POST LEG FLOOR FAIL %r count=%d floor=%d" % (o[:58], c, f))
    T1 = T1.replace(o, n)
print("== BLOCKS marker counts on post-roll T1 ==")
for name, sm, em in BLOCKS:
    print("  %-14s start count=%d  %r" % (name, T1.count(sm), sm[:70]))
# show the actual b5 header region in T1
k = T1.find("投影（probe")
print("== '投影（probe' context in T1 ==")
print(repr(T1[k-120:k+240]))
