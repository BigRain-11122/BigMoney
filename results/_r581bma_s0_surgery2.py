"""r581 bm-a S0 surgery round 2: align onto origin 70b32c101 (bm-b W95 freeze
+ bm-c bookkeeping window). Same law path as round-1 surgery: r532/r578 CAS +
reset --mixed + face checkout; r570 pool_core dict-only union; shared derive
faces take origin (r513/r505); bm-a live-write faces untouched (not in diff).
"""
import json
import os
import subprocess
import sys

OLD = "e0da19f87d430aab10c5c028f99fb231bf5a3af9"
NEW = sys.argv[1] if len(sys.argv) > 1 else None
assert NEW, "usage: surgery2.py <full-new-sha>"
POOL = "results/pool_core_samples.jsonl"


def g(*args):
    r = subprocess.run(list(args), capture_output=True)
    if r.returncode != 0:
        sys.exit(f"GIT FAIL {args}: {r.stderr.decode('utf-8', 'replace')[:400]}")
    return r.stdout


# pre: local-only pool_core rows (dict-only assert, cap 20)
origin_pool = g("git", "show", f"origin/main:{POOL}")
local_pool = open(POOL, "rb").read()
oset = {x.rstrip(b"\r") for x in origin_pool.split(b"\n") if x.strip()}
loconly = [x for x in local_pool.split(b"\n") if x.strip() and x.rstrip(b"\r") not in oset]
for row in loconly:
    assert isinstance(json.loads(row.rstrip(b"\r")), dict), "non-dict local row"
assert len(loconly) <= 20, f"unexpected local-only face {len(loconly)}"
print(f"pool_core local-only rows: {len(loconly)}")

out = g("git", "diff", "--name-status", "-z", OLD, "origin/main").decode("utf-8")
items = [x for x in out.split("\0") if x]
changed = []
i = 0
while i < len(items):
    st = items[i]
    if st[0] == "R":
        changed.append(items[i + 2])
        i += 3
    else:
        changed.append(items[i + 1])
        i += 2
checkout = [p for p in changed if p != POOL]
print(f"diff face: {len(changed)}; checkout: {len(checkout)}")

cur = g("git", "rev-parse", "main").decode().strip()
assert cur == OLD, f"main moved: {cur}"
g("git", "update-ref", "refs/heads/main", NEW, OLD)
g("git", "reset", "--mixed", NEW)
if checkout:
    g("git", "checkout", "--", *checkout)

body = origin_pool if origin_pool.endswith(b"\n") else origin_pool + b"\n"
for row in loconly:
    body += row.rstrip(b"\r") + b"\n"
open(POOL, "wb").write(body)
n = len([x for x in body.split(b"\n") if x.strip()])
o = len([x for x in origin_pool.split(b"\n") if x.strip()])
assert n == o + len(loconly), f"pool union {n} != {o}+{len(loconly)}"

# stale inbox dupes from the origin-side renames (publisher archived)
for f in ["fleet/inbox/MSG-20261002-1510-bmb-w92-yield-w93-seat.md",
          "fleet/inbox/MSG-20261002-1514-bma-w93-yield-w94-seat.md"]:
    if os.path.exists(f):
        ob = g("git", "show", f"origin/main:fleet/inbox/processed/{os.path.basename(f)}")
        lb = open(f, "rb").read()
        assert ob.replace(b"\r\n", b"\n") == lb.replace(b"\r\n", b"\n"), f"dup drift {f}"
        os.remove(f)
        print("removed stale inbox dupe:", f)

st = g("git", "status", "--porcelain").decode("utf-8", "replace")
print("--- status after surgery2 ---")
print(st)
print(f"pool_core union: {o}+{len(loconly)}={n} OK")
print("SURGERY2 OK")
