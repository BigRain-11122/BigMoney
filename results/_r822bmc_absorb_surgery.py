# r822 bm-c absorb-reconcile surgery (claim_lost_yield spiral root-fix)
# Pattern: r818 absorb + CAS direct-invest + local reset alignment.
# Shared append-only face pre-merged (post_review.jsonl origin-superset union done pre-run).
import subprocess, os, sys, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def git(*args, **kw):
    env = kw.pop("env", None)
    r = subprocess.run(["git"] + [str(a) for a in args], capture_output=True, env=env)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    return r.returncode, out, err

def log(*a):
    print(*a, flush=True)

# 1. fresh fetch + tip
rc, out, err = git("fetch", "origin")
log("fetch rc", rc, err.strip()[:120])
rc, tip, _ = git("rev-parse", "origin/main")
tip = tip.strip()
log("origin tip =", tip)

# 2. dirty inventory -> pathspec file
rc, st, _ = git("status", "--porcelain")
paths = []
for line in st.splitlines():
    if not line.strip():
        continue
    p = line[3:].strip()
    if "->" in p or not p:
        continue
    paths.append(p)
psf = os.path.join(ROOT, "results", "_r822bmc_absorb_pathspec.txt")
with open(psf, "w", encoding="utf-8") as f:
    f.write("\n".join(paths))
log("absorb faces:", len(paths))

# 3. temp index: base = origin tip tree, add all dirty faces
tmp_index = os.path.join(ROOT, ".git", "_r822bmc_tmp_index")
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = os.environ.copy()
env["GIT_INDEX_FILE"] = tmp_index
rc, out, err = git("read-tree", tip, env=env)
log("read-tree rc", rc)
rc, out, err = git("add", "-A", "--pathspec-from-file=" + psf, env=env)
if rc != 0:
    log("ADD FAILED:", err[:600])
    sys.exit(2)
rc, tree, err = git("write-tree", env=env)
tree = tree.strip()
log("tree =", tree)

# 4. commit-tree on origin tip
msg = ("r822 absorb-reconcile: 207-tick claim_lost_yield spiral face-union onto origin tip "
       "(S6 outputs + r820 estate + pit r822 surgery entry + daemon keepalive faces + "
       "post_review origin-superset union 9719 lines) [via bm-c r822]")
rc, commit, err = git("commit-tree", tree, "-p", tip, "-m", msg)
commit = commit.strip()
log("commit =", commit)

# 5. push (retry on tip-move, max 3)
pushed = False
for attempt in range(3):
    rc, out, err = git("push", "origin", commit + ":refs/heads/main")
    log("push attempt", attempt + 1, "rc", rc, (err.strip()[:200] if rc else "OK"))
    if rc == 0:
        pushed = True
        break
    # tip moved -> rebuild on new tip
    git("fetch", "origin")
    rc, tip2, _ = git("rev-parse", "origin/main")
    tip2 = tip2.strip()
    if tip2 == tip:
        log("push failed but tip unchanged -- abort for manual review")
        break
    tip = tip2
    rc, _, _ = git("read-tree", tip, env=env)
    rc, _, err2 = git("add", "-A", "--pathspec-from-file=" + psf, env=env)
    rc, tree, _ = git("write-tree", env=env)
    tree = tree.strip()
    rc, commit, err = git("commit-tree", tree, "-p", tip, "-m", msg)
    commit = commit.strip()
    log("rebuilt on new tip", tip, "commit", commit)

if not pushed:
    log("SURGERY PUSH FAILED -- no local state touched, abort")
    sys.exit(3)

# 6. verify remote tip
rc, out, _ = git("ls-remote", "origin", "refs/heads/main")
remote_tip = out.split()[0] if out else ""
log("remote main =", remote_tip, "match:", remote_tip == commit)

# 7. local alignment: backup branch (preserve 207 orphaned tick commits) + reset --mixed
if remote_tip == commit:
    rc, out, err = git("branch", "backup-r822-reconcile")
    log("backup branch rc", rc, err.strip()[:120])
    for attempt in range(8):
        rc, out, err = git("reset", "--mixed", commit)
        if rc == 0:
            log("reset OK on attempt", attempt + 1)
            break
        log("reset retry", attempt + 1, err.strip()[:120])
        time.sleep(3)
    rc, ahead, _ = git("rev-list", "--count", "origin/main..HEAD")
    rc2, behind, _ = git("rev-list", "--count", "HEAD..origin/main")
    log("post-reset ahead/behind:", ahead.strip(), "/", behind.strip())
    rc, st2, _ = git("status", "--porcelain")
    log("post-reset dirty lines:", len(st2.splitlines()))
else:
    log("REMOTE TIP MISMATCH -- skip reset, manual review")
    sys.exit(4)
log("SURGERY COMPLETE")
