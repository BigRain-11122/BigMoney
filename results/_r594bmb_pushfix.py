# r594 bm-b push-recovery: restore bm-a session files my worktree never
# materialized (origin-tree adds absent on local disk -> git add -A staged
# them as deletions; pre-push claw caught it, D-20261002-04 working as
# designed). r580 python subprocess argv; r294 amend-safety check.
import subprocess
import sys

FILES = [
    "results/_r592bma_s6_stderr.txt",
    "results/_r592bma_s6_stdout.txt",
    "results/_r592bma_takeorigin.txt",
    "results/_r592bma_w114_anchor.py",
    "results/_r592bma_w114_band_gate.py",
    "results/_r592bma_w114_freeze_edits.py",
    "results/_r592bma_w114_prereg_gen.py",
    "results/_r592bma_w114_probe.py",
    "results/_r593bma_s6_chain.py",
]

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

# amend-safety: HEAD must be MY unpushed round commit (r294 hijack law)
rc, subj = git("log", "-1", "--format=%s")
print("HEAD subject:", subj[:80])
if not subj.startswith("round 594 (bm-b)"):
    print("FATAL: HEAD is not my r594 commit -- amend refused")
    sys.exit(1)
rc, out = git("rev-list", "--count", "origin/main..HEAD")
if out.strip() != "1":
    print("FATAL: unpushed count != 1 (got %s) -- amend refused" % out.strip())
    sys.exit(1)

# 1) restore the 9 origin-tree files into worktree+index
rc, out = git("checkout", "origin/main", "--", *FILES)
print("restore 9 files rc=%d" % rc)
if rc != 0:
    print(out)
    sys.exit(1)
# 2) stage everything (restoration + any probe-script fix)
rc, out = git("add", "-A")
print("add -A rc=%d" % rc)
# 3) deletion set must now be EMPTY vs origin
rc, out = git("diff", "--diff-filter=D", "--name-only", "origin/main", "HEAD")
dels = [l for l in out.splitlines() if l.strip()]
staged = subprocess.run(["git", "diff", "--diff-filter=D", "--name-only",
                         "--cached"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace").stdout
staged_dels = [l for l in staged.splitlines() if l.strip()]
print("deletions vs origin: %d | staged deletions: %d"
      % (len(dels), len(staged_dels)))
if dels or staged_dels:
    print("FATAL deletions remain:", dels, staged_dels)
    sys.exit(1)
print("PUSH_RECOVERY_OK")
