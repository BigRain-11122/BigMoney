"""r583 bm-a surgical re-push #2: replay W96 closure commit (adds + one modify) onto 6b8c9fa7c (bm-b W100 seat)."""
import subprocess, sys, os

NO_WINDOW = 0x08000000

def git(args, env=None, timeout=120):
    return subprocess.run(["git"] + args, capture_output=True, timeout=timeout,
                          creationflags=NO_WINDOW, env=env)

def out(r):
    return r.stdout.decode("utf-8", errors="replace").strip()

base = out(git(["rev-parse", "origin/main"]))  # integration base = current origin tip BEFORE my commit's parent
# my unpushed: parent-of-main..main
parent = out(git(["rev-parse", "main^"]))
print("parent:", parent, "== origin tip?", parent == base)
r = git(["rev-list", "%s..main" % parent])
mine = out(r).splitlines()
assert mine == [out(git(["rev-parse", "main"]))], "unexpected range %r" % mine
myc = mine[0]

# my delta vs parent: adds + modifies, zero deletes
r = git(["diff-tree", "-r", "--no-renames", "--name-status", parent, myc])
delta = [l for l in out(r).splitlines() if l.strip()]
dels = [l.split("\t", 1)[1] for l in delta if l.startswith("D")]
assert not dels, "deletions in payload: %r" % dels
print("delta:", len(delta), "files (A/M)")

tmp_index = os.path.abspath("results/_r583bma_surgery_index2")
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
r = git(["read-tree", base], env=env)
assert r.returncode == 0, out(r)

r = git(["diff-tree", "-r", "--no-renames", parent, myc])
raw = r.stdout.decode("utf-8", errors="replace").splitlines()
n = 0
for line in raw:
    if not line.strip():
        continue
    meta, path = line.split("\t", 1)
    parts = meta.split(" ")
    newmode, newsha, status = parts[1], parts[3], parts[4]
    path = path.strip('"')
    if status in ("A", "M"):
        rr = git(["update-index", "--add", "--cacheinfo", "%s,%s,%s" % (newmode, newsha, path)], env=env)
        assert rr.returncode == 0, (path, out(rr))
        n += 1
print("update-index:", n)

tree = out(git(["write-tree"], env=env))
msg = out(git(["log", "-1", "--format=%B", myc]))
r = subprocess.run(["git", "commit-tree", tree, "-p", base, "-m", msg],
                   capture_output=True, creationflags=NO_WINDOW)
newc = out(r)
assert r.returncode == 0, r.stderr
print("surgical commit:", newc)

# assertions
r = git(["diff-tree", "-r", "--no-renames", "--diff-filter=D", "--name-only", base, newc])
dset = [l for l in out(r).splitlines() if l.strip()]
assert not dset, "deletion set: %r" % dset
r = git(["diff-tree", "-r", "--no-renames", "--name-only", base, newc])
nd = [l for l in out(r).splitlines() if l.strip()]
assert len(nd) == n, "tree-delta %d != payload %d" % (len(nd), n)
print("assertions OK: deletion-set empty, tree-delta == payload (%d)" % n)

r = git(["push", "origin", "%s:main" % newc], timeout=180)
print("push rc:", r.returncode)
print(out(r) or r.stderr.decode("utf-8", errors="replace")[:300])
sys.exit(r.returncode)
