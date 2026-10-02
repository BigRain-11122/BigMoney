# -*- coding: utf-8 -*-
# r588 bm-a surgical wrap push (r523 law + r577 same-day twin face rule)
import subprocess, sys, os
REPO = os.getcwd()

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args[:3], (r.stderr or "")[-300:]); sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
myhead = git(["rev-parse", "HEAD"]).stdout.strip()

mine = [f for f in git(["diff", "--name-only", "-z", myhead + "^", myhead]).stdout.split("\0") if f]
theirs = [f for f in git(["diff", "--name-only", "-z", base + "~2", base]).stdout.split("\0") if f]
drop = set(f for f in mine if f in theirs)   # both-touched: take origin (r577 twin rule)
payload = [f for f in mine if f not in drop]
print("my commit files:", len(mine), "| both-touched (take origin):", len(drop), "| surgical payload:", len(payload))

TMP = os.path.join(REPO, "results", "_r588bma_tmp_idx2")
e = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", base], env=e)
for f in payload:
    sha = git(["hash-object", "-w", f]).stdout.strip()
    git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, f)], env=e)
tree = git(["write-tree"], env=e).stdout.strip()

# deletion-set assertion (empty vs base)
dels = git(["diff", "--name-status", "--no-renames", base, tree], env=e).stdout
del_rows = [l for l in dels.splitlines() if l.startswith("D")]
if del_rows:
    print("DELETION SET NOT EMPTY:", del_rows[:8]); sys.exit(1)
# tree-delta == payload assertion
delta = git(["diff", "--name-only", "--no-renames", base, tree], env=e).stdout
dset = set(l for l in delta.splitlines() if l)
if dset != set(payload):
    print("TREE DELTA != PAYLOAD", dset ^ set(payload)); sys.exit(1)

msg = git(["log", "-1", "--format=%B", myhead]).stdout
mp = os.path.join(REPO, ".codely-cli", "scratch", "r588bma_msg2.txt")
open(mp, "w", encoding="utf-8", newline="\n").write(msg)
newc = git(["commit-tree", tree, "-p", base, "-F", mp],
           env={"GIT_AUTHOR_NAME": "bm-a-loop", "GIT_AUTHOR_EMAIL": "bm-a@fleet.local",
                "GIT_COMMITTER_NAME": "bm-a-loop", "GIT_COMMITTER_EMAIL": "bm-a@fleet.local"}).stdout.strip()
r = git(["push", "origin", newc + ":main"], check=False)
print("push rc=", r.returncode, ((r.stdout or "") + (r.stderr or ""))[:200])
if r.returncode != 0:
    sys.exit(1)

# align local (r578 + M-face classifier lesson)
git(["update-ref", "refs/heads/main", newc, myhead])
git(["reset", "--mixed", newc])
old_base_blob = {}
for f in theirs + payload:
    # classify: worktree stale if it equals the OLD myhead blob but differs from new tree
    try:
        w = git(["hash-object", f]).stdout.strip()
        h = git(["rev-parse", newc + ":" + f]).stdout.strip()
        o = git(["rev-parse", myhead + ":" + f], check=False).stdout.strip()
    except Exception:
        continue
    if w != h:
        if w == o and o:
            git(["checkout", "--", f])   # stale worktree (old-base verbatim) -> restore HEAD
        # else: local live-write/new content -> keep, next round handles
rc, st = git(["status", "--porcelain"]).stdout, None
st = git(["status", "--porcelain"]).stdout
nd = sum(1 for l in st.splitlines() if l.startswith(" D") or l.startswith("D "))
print("new commit", newc[:9], "| remaining-D:", nd, "| remaining-M:", sum(1 for l in st.splitlines() if l.startswith(" M") or l.startswith("M ")))
git(["fetch", "origin"])
behind = git(["rev-list", "--count", "main..origin/main"]).stdout.strip()
ahead = git(["rev-list", "--count", "origin/main..main"]).stdout.strip()
print("behind=%s ahead=%s" % (behind, ahead))
