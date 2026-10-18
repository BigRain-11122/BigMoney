# -*- coding: utf-8 -*-
# r1107 diagnostic 2: roll the full needle chain, exec VMAP/FLOORS/POST_LEGS/NEW/BLOCKS + the
# generated post-gates MUST list, run blocks on T0', and report EVERY missing MUST face at once.
# NOTE: spans are NOT substituted in this probe -- faces living inside span-replaced regions
# (S1 header/S9 wave-list/S10 stamps etc.) may show false misses here; classify manually.
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
exec(seg(txt, "VMAP_FLOORS = {", "def xf(t):"), ns2)
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

# post-gates MUST list from the generated script
pg = seg(txt, "# ---------------- post gates ----------------", 'io.open(OUT, "w"')
ns3 = {"T2": T2, "re": re}
exec(seg(pg, "MUST = [", "for s in MUST:"), ns3)
MUST = ns3["MUST"]
print("generated post-gates MUST faces:", len(MUST))
miss = [s for s in MUST if s not in T2]
print("MISSING faces: %d" % len(miss))
for s in miss:
    print("  MISS %r" % s)
    k = T2.find(s[:14])
    if k >= 0:
        print("       nearest context: %r" % T2[max(0, k-60):k+90])
import re
face = "618_101..620_100"
print("probe-T2 count of %r: %d" % (face, T2.count(face)))
for m in re.finditer(re.escape(face), T2):
    a, b = m.start(), m.end()
    print("  ctx:", repr(T2[max(0, a - 90):b + 60]))
