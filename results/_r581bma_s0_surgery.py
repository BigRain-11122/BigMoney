"""r581 bm-a S0 surgical integration onto origin e0da19f87.

Blocked rebase face: tracked live-write files (engine/autofill/marks/pool_core).
Law path: r532/r578 (CAS update-ref + reset --mixed + face checkout), r570
(pool_core dict-only union, origin base + local-only rows), r505/r499 (marks
settle twin -> origin wall-clock-newer side), r516 (stale inbox dup cleanup),
r580 (git batch ops via python argv only). Bytes in / bytes out per r568.
"""
import json
import os
import subprocess
import sys

OLD = "6bd40b6e4b7cf60e80ede3e97386cd720d9a90db"
NEW = "e0da19f87d430aab10c5c028f99fb231bf5a3af9"
POOL = "results/pool_core_samples.jsonl"


def g(*args, **kw):
    r = subprocess.run(list(args), capture_output=True, **kw)
    if r.returncode != 0:
        sys.exit(f"GIT FAIL {args}: {r.stderr.decode('utf-8', 'replace')[:400]}")
    return r.stdout


# --- pre: local-only pool_core row (dict-only assert) ---
origin_pool = g("git", "show", f"origin/main:{POOL}")
local_pool = open(POOL, "rb").read()
oset = {x.rstrip(b"\r") for x in origin_pool.split(b"\n") if x.strip()}
loconly = [x for x in local_pool.split(b"\n") if x.strip() and x.rstrip(b"\r") not in oset]
for row in loconly:
    assert isinstance(json.loads(row.rstrip(b"\r")), dict), "non-dict local row"
assert len(loconly) <= 3, f"unexpected local-only face {len(loconly)}"

# --- face list: everything origin changed vs old HEAD ---
out = g("git", "diff", "--name-status", "-z", OLD, NEW).decode("utf-8")
items = [x for x in out.split("\0") if x]
changed = []
i = 0
while i < len(items):
    st = items[i]
    path = items[i + 1] if st[0] in "AM" else None
    if st[0] == "R":
        path = items[i + 2]
        i += 3
    else:
        i += 2
    if path:
        changed.append(path)
assert changed, "empty payload face"
checkout = [p for p in changed if p != POOL]
print(f"diff face: {len(changed)} files; checkout: {len(checkout)}; union-write: pool_core")

# --- CAS move ref + reset mixed ---
cur = g("git", "rev-parse", "main").decode().strip()
assert cur == OLD, f"main moved: {cur}"
g("git", "update-ref", "refs/heads/main", NEW, OLD)
g("git", "reset", "--mixed", NEW)

# --- restore worktree faces from index (= origin) ---
if checkout:
    g("git", "checkout", "--", *checkout)

# --- pool_core union write: origin bytes + local-only rows (LF form) ---
body = origin_pool if origin_pool.endswith(b"\n") else origin_pool + b"\n"
for row in loconly:
    body += row.rstrip(b"\r") + b"\n"
open(POOL, "wb").write(body)

# --- stale inbox dup cleanup (canonical at processed/, eol-only diff) ---
dups = [
    "fleet/inbox/MSG-20261002-1415-bma-w90-seat.md",
    "fleet/inbox/MSG-20261002-1425-bmb-w91-seat.md",
    "fleet/inbox/MSG-20261002-1447-bmc-w92-seat.md",
]
for f in dups:
    ob = g("git", "show", f"origin/main:fleet/inbox/processed/{os.path.basename(f)}")
    lb = open(f, "rb").read()
    assert ob.replace(b"\r\n", b"\n") == lb.replace(b"\r\n", b"\n"), f"dup content drift {f}"
    os.remove(f)

# --- verify ---
st = g("git", "status", "--porcelain").decode("utf-8", "replace")
print("--- status after surgery ---")
print(st)
n_pool = len([x for x in open(POOL, "rb").read().split(b"\n") if x.strip()])
o_pool = len([x for x in origin_pool.split(b"\n") if x.strip()])
assert n_pool == o_pool + len(loconly), f"pool union count {n_pool} != {o_pool}+{len(loconly)}"
print(f"pool_core union: origin {o_pool} + local-only {len(loconly)} = {n_pool} OK")
print("SURGERY OK")
