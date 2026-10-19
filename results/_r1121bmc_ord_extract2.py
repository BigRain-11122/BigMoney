# -*- coding: utf-8 -*-
# r1121 bm-c: extract new ORD rows between watermark blob ac5501f1-face and current 33abb57c
# (content-sha1 pinned probe method r977). Read-only judgment input.
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"

def show_at(sha1_of_blob_guess_commit):
    # find the commit whose docs/orders.md content-sha1 matches, walking recent commits
    r = subprocess.run(["git", "-C", GRP, "log", "-20", "--format=%H"], capture_output=True, text=True)
    return r.stdout.split()

def blob_bytes(ref):
    r = subprocess.run(["git", "-C", GRP, "show", ref], capture_output=True)
    return r.stdout

cur = blob_bytes("origin/main:docs/orders.md")
# walk history to find the commit matching the OLD watermark content
old_sha = "ac5501f1591bc038170c234f8313a2732c4d864e"
old_bytes = None
r = subprocess.run(["git", "-C", GRP, "log", "-30", "--format=%H", "origin/main", "--", "docs/orders.md"],
                   capture_output=True, text=True)
for c in [x for x in r.stdout.split() if x]:
    b = blob_bytes(c + ":docs/orders.md")
    import hashlib
    if hashlib.sha1(b).hexdigest() == old_sha:
        old_bytes = b
        print("old face found at commit", c)
        break
if old_bytes is None:
    raise SystemExit("old orders face not found in last 30 orders-touching commits")
old_lines = [l for l in old_bytes.decode("utf-8", "replace").splitlines()]
cur_lines = [l for l in cur.decode("utf-8", "replace").splitlines()]
old_set = set(l.strip() for l in old_lines)
print("=== NEW ORD ROWS (in cur, not in old) ===")
for l in cur_lines:
    if l.strip() and l.strip() not in old_set and ("2026-10-19" in l or "|" in l):
        print(l[:400])
