# -*- coding: utf-8 -*-
# _r997bmc_softcommit.py -- soft-copyright 18-model commit prep (group-tree surgical add)
# Laws: 95MB hard line (U187) per-file check BEFORE add; pathspec surgical commit only.
import os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = r"K:\Fluxgroup\FluxGroup"
D = os.path.join(G, "软著申请材料")

def git(*args, **kw):
    r = subprocess.run(["git", "-C", G] + list(args), capture_output=True)
    return r.stdout.decode("utf-8", "replace"), r.returncode

out, rc = git("status", "--porcelain", "--", "软著申请材料")
lines = [ln for ln in out.splitlines() if ln.strip()]
print("changed entries:", len(lines))
big, added, modified = [], [], []
for ln in lines:
    st, path = ln[:2], ln[3:].strip('"')
    fp = os.path.join(G, path.replace("/", "\\"))
    sz = os.path.getsize(fp) if os.path.isfile(fp) else 0
    if sz > 95 * 1024 * 1024:
        big.append((path, sz))
    if st.strip() == "A" or st == "??":
        added.append(path)
    else:
        modified.append(path)
print("MOD/M entries:", len(modified), " NEW/?? entries:", len(added))
print("BIG >95MB:", big if big else "NONE")
for p in modified[:25]:
    print("  M", p)
for p in added[:40]:
    print("  +", p)
if len(added) > 40:
    print("   ... +%d more" % (len(added) - 40))
# B-model src-txt census (disclosure face)
import glob
b_models = ["G04_ScrewOut", "G05_ReelRiot", "G07_MobTide", "G08_CrazyCampus",
            "G13_我想有个农场", "G14_大不了开饭馆", "G20_MonsterInn", "G23", "G26_归园田居", "G28_ArrowOut"]
print("--- B-model src-txt presence (bm-b lane disclosure) ---")
for m in b_models:
    pats = glob.glob(os.path.join(D, m + "*", "*源程序.txt")) + glob.glob(os.path.join(D, m + "*\\*源程序.txt"))
    print(" ", m, "->", [os.path.basename(x) for x in pats] if pats else "NO-SRC-TXT (bm-b lane)")
