# r491 bm-a surgical lane-only push (clean-path recipe, zero worktree touch).
# Overlay = D (this round's committed files) + (O \ R) (my-5 ahead lane files
# remote never touched). Intersection faces not regenerated this round keep
# the remote version. Temp index -> read-tree origin/main -> update-index from
# worktree -> write-tree -> commit-tree -p origin/main -> push (fast-forward).
import subprocess, sys, os

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"GIT FAIL: git {' '.join(args)}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()

git("fetch", "origin")
OM = git("rev-parse", "origin/main")

# D = files changed in the r491 local commit (HEAD vs HEAD~1)
D = set(git("diff-tree", "--no-commit-id", "--name-only", "-r",
            "HEAD~1", "HEAD").splitlines())
# O = my side since divergence (merge-base -> HEAD)
O = set(git("diff", f"{OM}...HEAD", "--name-only").splitlines())
# R = remote side since divergence (merge-base -> origin/main)
R = set(git("diff", f"HEAD...{OM}", "--name-only").splitlines())
overlay = D | (O - R)
print(f"OM={OM[:9]} D={len(D)} O={len(O)} R={len(R)} overlay={len(overlay)}")

idx = os.path.abspath(".git/r491_surg_index")
env = dict(os.environ, GIT_INDEX_FILE=idx)
def gidx(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        print(f"GIT FAIL: git {' '.join(args)}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()

gidx("read-tree", OM)
files = sorted(overlay)
for i in range(0, len(files), 200):
    gidx("update-index", "--add", "--", *files[i:i + 200])
tree = gidx("write-tree")
msg = ("round 491 surgical lane push: stranded-window closeout (r484-490 watch "
       "ended) + banned-gate LANDED (T-129 D-41 sec.1.2: Tools/banned_direction_gate.py "
       "fail-closed admission gate + BANNED_DIRECTIONS registry + PREREG_TEMPLATE s0.5, "
       "selftest 8/8, realfire 3 CJK fire) + PROSPECT 22-member anchor refreeze same-cutoff "
       "2026-09-22 (RW-1 exit-T+1-open aftermath: r475 legacy pin cannot reproduce pre-RW-1 "
       "evidence, 22/22 drift on first new-bar window, fixed per r472 precedent, 6 sign-flips "
       "disclosed in results/RW1_PROSPECT_REFREEZE_2026-09-30.md; t24paper 22/22 PASS + "
       "09-30 accrual, promotion 0/22 honest) + 09-30 bar landed (36 rows) + S6 37 legs rc0 "
       "+ CODELY 3-way union + hot-cold 5970B + smoke 47/47; state 490->491 "
       "[via bm-a]")
with open(".git/r491_surg_msg.txt", "w", encoding="utf-8") as f:
    f.write(msg)
commit = git("commit-tree", tree, "-p", OM, "-F", ".git/r491_surg_msg.txt")
print(f"tree={tree[:9]} commit={commit[:9]}")
git("push", "origin", f"{commit}:refs/heads/main")
print(f"PUSHED {commit[:9]} -> main (parent {OM[:9]})")
for p in (idx, ".git/r491_surg_msg.txt"):
    try:
        os.remove(p)
    except OSError:
        pass
