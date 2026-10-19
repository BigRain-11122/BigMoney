# -*- coding: utf-8 -*-
# r1121 bm-c: extract rows between the 33abb57c face and the d85679de face (mid-advance delta).
import subprocess, hashlib, sys
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"

def blob(ref):
    return subprocess.run(["git", "-C", GRP, "show", ref], capture_output=True).stdout

cur = blob("origin/main:docs/orders.md")
print("cur sha:", hashlib.sha1(cur).hexdigest())
old_sha = "33abb57c532ab837a00176af8025df9277c76654"
old_bytes = None
r = subprocess.run(["git", "-C", GRP, "log", "-15", "--format=%H", "origin/main", "--", "docs/orders.md"],
                   capture_output=True, text=True)
for c in [x for x in r.stdout.split() if x]:
    b = blob(c + ":docs/orders.md")
    if hashlib.sha1(b).hexdigest() == old_sha:
        old_bytes = b
        print("old face at", c)
        break
if old_bytes is None:
    print("OLD FACE NOT FOUND (already rolled past) -- dumping rows newer than 16:2x from cur instead:")
    for l in cur.decode("utf-8", "replace").splitlines():
        if l.strip().startswith("|") and any(k in l for k in ["16:3x", "16:4x", "16:5x", "17:0x", "2026-10-19 16:3", "2026-10-19 16:4", "2026-10-19 16:5", "2026-10-19 17:"]):
            print(l[:300])
    sys.exit(0)
old_set = set(l.strip() for l in old_bytes.decode("utf-8", "replace").splitlines())
print("=== DELTA ROWS ===")
for l in cur.decode("utf-8", "replace").splitlines():
    if l.strip() and l.strip() not in old_set and l.strip().startswith("|"):
        print(l[:350])
        print("---")
