# r588 bm-a surgical push (r523 law): my HEAD commit payload rebased onto fresh origin/main
import subprocess, sys, os
REPO = os.getcwd()

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args[:3], (r.stderr or r.stdout)[-300:]); sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
myhead = git(["rev-parse", "HEAD"]).stdout.strip()
myparent = git(["rev-parse", "HEAD^"]).stdout.strip()

# payload files = my commit diff vs its parent
names = git(["diff", "--name-only", "-z", myparent, myhead]).stdout
payload = [f for f in names.split("\0") if f]
print("payload files:", len(payload))

# build temp index from origin/main
TMP = os.path.join(REPO, "results", "_r588bma_tmp_idx")
e = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", base], env=e)
for f in payload:
    sha = git(["hash-object", "-w", f]).stdout.strip()
    git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, f)], env=e)
tree = git(["write-tree"], env=e).stdout.strip()

# deletion-set assertion: new tree must not delete anything origin has
dels = git(["diff", "--name-status", "--no-renames", base, tree]).stdout
del_rows = [l for l in dels.splitlines() if l.startswith("D")]
if del_rows:
    print("DELETION SET NOT EMPTY:", del_rows[:10]); sys.exit(1)

# tree-delta assertion == payload
delta = git(["diff", "--name-only", "--no-renames", base, tree]).stdout
dset = set(l for l in delta.splitlines() if l)
if dset != set(payload):
    print("TREE DELTA != PAYLOAD", dset ^ set(payload)); sys.exit(1)

msg = git(["log", "-1", "--format=%B", myhead]).stdout
mp = os.path.join(REPO, "results", "_r588bma_tmp_msg.txt")
open(mp, "w", encoding="utf-8", newline="\n").write(msg)
newc = git(["commit-tree", tree, "-p", base, "-F", mp],
           env={"GIT_AUTHOR_NAME": "bm-a-loop", "GIT_AUTHOR_EMAIL": "bm-a@fleet.local",
                "GIT_COMMITTER_NAME": "bm-a-loop", "GIT_COMMITTER_EMAIL": "bm-a@fleet.local"}).stdout.strip()

r = git(["push", "origin", newc + ":main"], check=False)
print("push rc=", r.returncode)
if r.returncode != 0:
    print((r.stderr or "")[-300:]); sys.exit(1)

# align local: update-ref CAS + reset --mixed (r578 law)
git(["update-ref", "refs/heads/main", newc, myhead])
git(["reset", "--mixed", newc])
print("new commit", newc[:9], "parent", base[:9])
fin = git(["status", "-sb"]).stdout
print(fin.splitlines()[0])
