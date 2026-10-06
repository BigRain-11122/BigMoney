# -*- coding: utf-8 -*-
"""r795 bm-a session-attribution probe: count every 'r794'/'r793' session
narrative in the NEW W165 faces (pf block / n1 entry / n1 mat / n1 claim /
prereg md / verify asserts) to plan the honest-attribution surgical fix.
Read-only; dumps findings."""
import io
import re

PF = "scripts/perpetual_faces.py"
N1 = "scripts/perpetual_faces_n1.py"
PRE = "research/PERPETUAL_N1_W165_PREREG.md"
VER = "results/_r794bma_w165_freeze_verify.py"

pf = io.open(PF, encoding="utf-8", newline="").read()
n1 = io.open(N1, encoding="utf-8", newline="").read()
pre = io.open(PRE, encoding="utf-8", newline="").read()
ver = io.open(VER, encoding="utf-8", newline="").read()

EO = '"engine_owner": "bm-a"},'
# new W165 pf block
i2 = pf.find("    # W165 (bm-a r")
j2 = pf.find(EO, i2) + len(EO)
pfblk = pf[i2:j2]
# new W165 n1 entry
k2 = n1.find('165: {"batch"')
m2 = n1.find(EO, k2) + len(EO)
entry = n1[k2:m2]
# new W165 mat block
w2 = n1.find("# --- W165 materializer face")
t3 = n2end = n1.find("# --- T-141 s2 lane face", w2)
mat = n1[w2:t3]
# claim
cs2 = n1.find('"+ W165 materializer face')
ce2 = n1.find('"r794 bm-a] "', cs2) + len('"r794 bm-a] "')
claim = n1[cs2:ce2]

out = io.open("results/_r795bma_session_probe.txt", "w", encoding="utf-8")
for tag, seg in (("pf", pfblk), ("entry", entry), ("mat", mat), ("claim", claim),
                 ("prereg", pre), ("verify", ver)):
    out.write(f"===== {tag} ({len(seg)}B) =====\n")
    for m in re.finditer(r"r79[234]", seg):
        ln = seg[:m.start()].count("\n") + 1
        line = seg.splitlines()[ln - 1].strip()
        out.write(f"  {m.group()} L{ln}: {line[:150]}\n")
out.close()
print("probe dumped results/_r795bma_session_probe.txt")
print("pf r794:", pfblk.count("r794"), "pf r793:", pfblk.count("r793"))
print("entry r794:", entry.count("r794"), "entry r793:", entry.count("r793"))
print("mat r794:", mat.count("r794"), "mat r793:", mat.count("r793"))
print("claim r794:", claim.count("r794"), "claim r793:", claim.count("r793"))
print("prereg r794:", pre.count("r794"), "prereg r793:", pre.count("r793"))
print("verify r794:", ver.count("r794"), "verify r793:", ver.count("r793"))
