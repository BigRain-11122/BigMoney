# r379 bm-c surgical reparent push (r523 law; bm-a r588 helper adapted):
#   payload = MY COMMIT blobs (ls-tree, never worktree hash-object -- r585 law)
#   deletion side handled via --force-remove (inbox move whitelist in assertion)
import subprocess, sys, os

REPO = os.getcwd()
CREATE_NO_WINDOW = 0x08000000

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=e, creationflags=CREATE_NO_WINDOW)
    if check and r.returncode != 0:
        print("GIT FAIL:", args[:3], (r.stderr or r.stdout)[-400:]); sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
myhead = git(["rev-parse", "HEAD"]).stdout.strip()
myparent = git(["rev-parse", "HEAD^"]).stdout.strip()
print("base(origin)=%s myhead=%s" % (base[:9], myhead[:9]))
if base == myparent:
    print("origin did NOT advance past my parent -- plain push should work; abort surgical"); sys.exit(2)

# payload from MY COMMIT diff vs its parent (name-status to know D/A sides)
ns = git(["diff", "--name-status", "--no-renames", "-z", myparent, myhead]).stdout
parts = [p for p in ns.split("\0") if p]
payload = []   # (status, path)
i = 0
while i < len(parts):
    st = parts[i]; path = parts[i + 1]; i += 2
    payload.append((st, path))
print("payload entries:", len(payload))

TMP = os.path.join(REPO, "results", "_r379bmc_tmp_idx")
e = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", base], env=e)
skipped = 0
eff = []
for st, f in payload:
    if st == "D":
        rb = git(["rev-parse", "--verify", "--quiet", "%s:%s" % (base, f)], check=False)
        if rb.returncode != 0:
            skipped += 1  # already absent in base -- no-op
            continue
        git(["update-index", "--force-remove", f], env=e)
        eff.append(f)
        continue
    sha = git(["rev-parse", "%s:%s" % (myhead, f)]).stdout.strip()
    rb = git(["rev-parse", "--verify", "--quiet", "%s:%s" % (base, f)], check=False)
    if rb.returncode == 0 and rb.stdout.strip() == sha:
        skipped += 1  # identical blob in base -- no-op entry, keep base side
        continue
    git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, f)], env=e)
    eff.append(f)
tree = git(["write-tree"], env=e).stdout.strip()
print("no-op payload entries skipped:", skipped, "effective:", len(eff))

# assertion 1: deletion set only via inbox-move whitelist pattern
dels = git(["diff", "--name-status", "--no-renames", base, tree]).stdout
bad = []
for l in dels.splitlines():
    if l.startswith("D"):
        p = l.split("\t", 1)[1]
        if p.startswith("fleet/inbox/") and not p.startswith("fleet/inbox/processed/"):
            moved = "fleet/inbox/processed/" + os.path.basename(p)
            if not any(x.startswith("A") and ("\t" + moved) in x for x in dels.splitlines()):
                bad.append(l)
        else:
            bad.append(l)
if bad:
    print("DELETION SET NOT EMPTY/WHITELISTED:", bad[:10]); sys.exit(1)
# assertion 2: tree-delta == effective payload paths
delta = git(["diff", "--name-only", "--no-renames", base, tree]).stdout
dset = set(x for x in delta.splitlines() if x)
pset = set(eff)
if dset != pset:
    print("TREE DELTA != PAYLOAD", dset ^ pset); sys.exit(1)

msg = git(["log", "-1", "--format=%B", myhead]).stdout
mp = os.path.join(REPO, "results", "_r379bmc_tmp_msg.txt")
open(mp, "w", encoding="utf-8", newline="\n").write(msg)
newc = git(["commit-tree", tree, "-p", base, "-F", mp]).stdout.strip()

r = git(["push", "origin", newc + ":main"], check=False)
print("push rc=", r.returncode)
if r.returncode != 0:
    print((r.stderr or "")[-400:]); sys.exit(1)

# align local: CAS update-ref (full 40-char old) + reset --mixed (r578 law)
git(["update-ref", "refs/heads/main", newc, myhead])
git(["reset", "--mixed", newc])
print("new commit", newc[:9], "parent", base[:9])
if os.path.exists(TMP): os.remove(TMP)
