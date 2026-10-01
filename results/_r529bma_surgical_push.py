"""r529 bm-a surgical push (r486/r523 law): build tree = origin/main + my
47-file delta, commit-tree -p origin/main, push <sha>:main. Zero work-tree
touch, zero stash, zero rebase. My delta (7e03101fb..HEAD) is disjoint from
origin's new commit 47a96d504 (6 bm-c W17 shard files) -- verified.
"""
import subprocess
import sys

BASE = "7e03101fb"
IDX = ".git/_r529bma_surgidx"


def run(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, check=True, **kw)


import os

env = dict(os.environ, GIT_INDEX_FILE=IDX)
if os.path.exists(IDX):
    os.remove(IDX)

# 0. tight-window fetch (r505 law: fetch->build->push minimized race window)
run("git", "fetch", "origin")

# 1. temp index seeded from origin/main
run("git", "read-tree", "origin/main", env=env)

# 2. my delta paths with status
st = run("git", "diff", "--name-status", BASE, "HEAD").stdout.splitlines()
adds, dels = [], []
for line in st:
    parts = line.split("\t")
    tag = parts[0]
    if tag.startswith("R"):
        # rename: delete old, add new
        dels.append(parts[1])
        adds.append(parts[2])
    elif tag == "D":
        dels.append(parts[1])
    else:  # A / M
        adds.append(parts[1])
print(f"delta: {len(adds)} add/modify, {len(dels)} delete (renames flattened)")

# 3. apply: add my blob versions, remove deleted paths
for p in adds:
    blob = run("git", "rev-parse", f"HEAD:{p}").stdout.strip()
    run("git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{p}",
        env=env)
for p in dels:
    run("git", "update-index", "--force-remove", p, env=env)

# 4. write tree
tree = run("git", "write-tree", env=env).stdout.strip()

# 5. deletion-face assertion (r516 law): deleted paths absent from new tree
for p in dels:
    r = subprocess.run(["git", "ls-tree", tree, "--", p],
                       capture_output=True, text=True)
    assert r.stdout.strip() == "", f"deletion face leaked: {p}"

# 6. payload-count assertion: tree diff vs origin/main == my add set ONLY
#    (bm-c's 6 shards are IN origin/main already, so they appear in no diff --
#    instead assert they are PRESENT in the tree: provenance face)
new_files = run("git", "diff", "--name-only", "origin/main", tree).stdout.split()
assert set(new_files) == set(adds), \
    f"payload mismatch: extra={set(new_files)-set(adds)} missing={set(adds)-set(new_files)}"
for p in ("results/p2cal_ext/n1_w17/shard-0-of-12.json",
          "results/p2cal_ext/n1_w17/shard-5-of-12.json",
          "results/p2cal_ext/n1_w17/shard-11-of-12.json"):
    r = subprocess.run(["git", "ls-tree", tree, "--", p],
                       capture_output=True, text=True)
    assert r.stdout.strip() != "", f"bm-c shard dropped from tree: {p}"
print(f"tree {tree}: payload == my {len(adds)} files; deletions {len(dels)} "
      f"clean; bm-c shards present (provenance ok)")

# 7. commit-tree on origin/main
msg = ("round 529 [via bm-a]: N3-R1xW13 seed-domain overlap adjudicated "
       "(canon row + S6b two-state leg + MSG-183x) + W18 gate projection "
       "CLEAN pending-W17 + S6 33 legs rc0 + rides "
       "(surgical rebroadcast onto 47a96d504)")
sha = run("git", "commit-tree", tree, "-p", "origin/main", "-m", msg,
          env=env).stdout.strip()
print("commit:", sha)

# 8. push fast-forward
r = subprocess.run(["git", "push", "origin", f"{sha}:main"],
                   capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
sys.exit(r.returncode)
