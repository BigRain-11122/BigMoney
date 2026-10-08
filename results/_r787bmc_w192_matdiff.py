# -*- coding: utf-8 -*-
"""r787 bm-c W192 roll-semantics prober: extract the W190-era MAT block (from
the r892 freeze commit 0cce3c47e) and diff it against the live W191 MAT block
to derive the exact per-freeze MAT roll transformation (extraction-from-
emission law). Zero writes; prints a unified-ish line diff with counts."""
import difflib
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREAT = 0x08000000

n1_live = io.open(ROOT + r"\scripts\perpetual_faces_n1.py", encoding="utf-8",
                  newline="").read()
mi = n1_live.find("# --- W191 materializer face")
tj = n1_live.find("    # --- T-141 s2 lane face", mi)
w191_mat = n1_live[mi:tj]
if w191_mat.endswith("\r\n"):
    w191_mat = w191_mat[:-2]

old_n1 = subprocess.check_output(
    ["git", "show", "0cce3c47e:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
mi0 = old_n1.find("# --- W190 materializer face")
tj0 = old_n1.find("    # --- T-141 s2 lane face", mi0)
w190_mat = old_n1[mi0:tj0]
if w190_mat.endswith("\r\n"):
    w190_mat = w190_mat[:-2]
elif w190_mat.endswith("\n"):
    w190_mat = w190_mat[:-1]

print(f"W190 mat bytes={len(w190_mat)} lines={w190_mat.count(chr(10))+1}")
print(f"W191 mat bytes={len(w191_mat)} lines={w191_mat.count(chr(10))+1}")

a = w190_mat.splitlines()
b = w191_mat.splitlines()
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
n_eq = n_del = n_ins = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        n_eq += i2 - i1
        continue
    print(f"== {tag} [{i1}:{i2}] -> [{j1}:{j2}] ==")
    for ln in a[i1:i2]:
        print("  - " + ln)
    for ln in b[j1:j2]:
        print("  + " + ln)
    n_del += i2 - i1
    n_ins += j2 - j1
print(f"summary: equal={n_eq} del={n_del} ins={n_ins}")
