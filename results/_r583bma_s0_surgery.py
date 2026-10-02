"""r583 bm-a surgical S0 re-push: replay my pure-addition commit onto the new origin/main tip.

Context: origin moved +3 (bm-c W99 seat+freeze fed0b4054/f2191688c, bm-b r582
W95 finalize 1ffa07210) after my 16:09 sync. My commit (W98 shard delivery)
is pure additions; tracked live-writer dirty tree forbids rebase (r532 law).
Path: temp-index read-tree origin/main + update-index my added blobs +
commit-tree -p origin/main + push <sha>:main (fast-forward guaranteed).
Assertions: my delta deletion-set empty x2 + payload count + tree-delta match.
"""
import subprocess, sys, os

NO_WINDOW = 0x08000000

def git(args, env=None, timeout=120):
    r = subprocess.run(["git"] + args, capture_output=True, timeout=timeout,
                       creationflags=NO_WINDOW, env=env)
    return r

def out(r):
    return r.stdout.decode("utf-8", errors="replace").strip()

# 1. locate my unpushed commit(s): 5125dc25d..main
r = git(["rev-list", "5125dc25d..main"])
mine = out(r).splitlines()
print("my unpushed commits:", mine)
assert len(mine) == 1, "expected exactly 1 unpushed commit, got %r" % mine
myc = mine[0]

# 2. my delta: must be pure additions (deletion-set empty, r519 claw law)
r = git(["diff-tree", "-r", "--no-renames", "--name-status", "5125dc25d", myc])
delta = [l for l in out(r).splitlines() if l.strip()]
adds = [l.split("\t", 1)[1] for l in delta if l.startswith("A")]
dels = [l.split("\t", 1)[1] for l in delta if l.startswith("D")]
print("delta lines:", len(delta), "adds:", len(adds), "dels:", len(dels))
assert not dels, "my commit carries deletions: %r" % dels

# 3. temp index: read-tree origin/main, then add my blobs
tmp_index = os.path.abspath("results/_r583bma_surgery_index")
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
r = git(["read-tree", "origin/main"], env=env)
assert r.returncode == 0, out(r)

r = git(["diff-tree", "-r", "--no-renames", "5125dc25d", myc])
raw = r.stdout.decode("utf-8", errors="replace").splitlines()
added = 0
for line in raw:
    if not line.strip():
        continue
    # format: :<oldmode> <newmode> <oldsha> <newsha> <status>\t<path>
    meta, path = line.split("\t", 1)
    parts = meta.split(" ")
    oldmode, newmode, oldsha, newsha, status = parts[0], parts[1], parts[2], parts[3], parts[4]
    path = path.strip('"')
    if status == "A":
        rr = git(["update-index", "--add", "--cacheinfo", "%s,%s,%s" % (newmode, newsha, path)], env=env)
        assert rr.returncode == 0, (path, out(rr))
        added += 1
print("update-index added:", added, "== delta adds:", len(adds))
assert added == len(adds)

# 4. write-tree + commit-tree on top of origin/main
r = git(["write-tree"], env=env)
tree = out(r)
assert r.returncode == 0

msg = out(git(["log", "-1", "--format=%B", myc]))
parent = out(git(["rev-parse", "origin/main"]))
r = subprocess.run(["git", "commit-tree", tree, "-p", parent, "-m", msg],
                   capture_output=True, creationflags=NO_WINDOW)
newc = out(r)
assert r.returncode == 0, (r.stderr, newc)
print("surgical commit:", newc, "parent:", parent)

# 5. assertions: deletion-set origin->newc empty; tree-delta == payload
r = git(["diff-tree", "-r", "--no-renames", "--diff-filter=D", "--name-only", parent, newc])
dset = [l for l in out(r).splitlines() if l.strip()]
assert not dset, "deletion set non-empty: %r" % dset
r = git(["diff-tree", "-r", "--no-renames", "--name-only", parent, newc])
ndelta = [l for l in out(r).splitlines() if l.strip()]
assert len(ndelta) == len(adds), "tree-delta %d != payload %d" % (len(ndelta), len(adds))
print("assertions OK: deletion-set empty x2, tree-delta == payload (%d files)" % len(ndelta))

# 6. push fast-forward
r = git(["push", "origin", "%s:main" % newc], timeout=180)
print("push rc:", r.returncode)
print(out(r) or r.stderr.decode("utf-8", errors="replace")[:400])
sys.exit(r.returncode)
