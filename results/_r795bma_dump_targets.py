# -*- coding: utf-8 -*-
"""r795 bm-a: dump exact full lines of every session-attribution target
before the surgical fix. Read-only."""
import io

PF = "scripts/perpetual_faces.py"
N1 = "scripts/perpetual_faces_n1.py"
PRE = "research/PERPETUAL_N1_W165_PREREG.md"

pf = io.open(PF, encoding="utf-8", newline="").read()
n1 = io.open(N1, encoding="utf-8", newline="").read()
pre = io.open(PRE, encoding="utf-8", newline="").read()

EO = '"engine_owner": "bm-a"},'
i2 = pf.find("    # W165 (bm-a r")
j2 = pf.find(EO, i2) + len(EO)
pfblk = pf[i2:j2]
k2 = n1.find('165: {"batch"')
m2 = n1.find(EO, k2) + len(EO)
entry = n1[k2:m2]
w2 = n1.find("# --- W165 materializer face")
t3 = n1.find("# --- T-141 s2 lane face", w2)
mat = n1[w2:t3]
cs2 = n1.find('"+ W165 materializer face')
ce2 = n1.find('"r794 bm-a] "', cs2) + len('"r794 bm-a] "')
claim = n1[cs2:ce2]

out = io.open("results/_r795bma_session_targets.txt", "w", encoding="utf-8")
out.write("########## pf block full ##########\n" + pfblk)
out.write("\n########## entry r794 lines ##########\n")
for ln in entry.splitlines():
    if "r794" in ln:
        out.write("ENTRY| " + ln + "\n")
out.write("\n########## mat r794 lines ##########\n")
for ln in mat.splitlines():
    if "r794" in ln:
        out.write("MAT| " + ln + "\n")
out.write("\n########## claim full ##########\n" + claim)
out.write("\n########## prereg r794 lines ##########\n")
for ln in pre.splitlines():
    if "r794" in ln:
        out.write("PRE| " + ln + "\n")
out.close()
print("dumped results/_r795bma_session_targets.txt")
