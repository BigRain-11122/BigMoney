# r357 bm-c S0 shard rescue: re-deliver W61 shard-9/10 to origin.
# Provenance: ba9c9d77c (engine appender, 2026-10-02 08:25:37) committed the
# last two W61 shards locally but the r356 session died pre-push -> never
# reached origin (W61 stuck 10/12 on origin, 12/12 on disk). r532 no-rebase
# surgical route (tracked live-write files in tree make rebase impossible);
# r530/r519 deletion-set assertion; r516 post-push ls-tree delivery check.
# Ownership: audit.machine=bm-c verified in _r357bmc_s0_checks.py (r525 gate).
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SHARDS = [
    "results/p2cal_ext/n1_w61/shard-9-of-12.json",
    "results/p2cal_ext/n1_w61/shard-10-of-12.json",
]

MSG = ("r357 bm-c S0 shard rescue: W61 shard-9/10 re-delivery (ba9c9d77c "
       "engine appender 08:25:37 committed locally, dead r356 session died "
       "pre-push, never reached origin; ownership audit.machine=bm-c "
       "verified, 182+184 cells, 8w ProcessPool O-2355; unblocks W61 "
       "12/12 r310 completeness gate for finalize) via surgical CAS "
       "[additions-only payload, deletion-set empty r530, r532 no-rebase "
       "route] [via bm-c r357]")


def git(args, env=None):
    r = subprocess.run(["git"] + args, cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


# 1) fresh fetch + parent rev-parse (r531: derive parent at push time)
rc, _, err = git(["fetch", "origin"])
assert rc == 0, "fetch failed: " + err
rc, parent, err = git(["rev-parse", "origin/main"])
assert rc == 0, err

# 2) pre-gate: origin has 10/12, missing exactly 9 and 10
rc, out, err = git(["ls-tree", "origin/main", "--name-only",
                    "results/p2cal_ext/n1_w61/"])
present = set(l.strip() for l in out.splitlines() if l.strip())
for s in SHARDS:
    assert s not in present, "already on origin: " + s
assert len(present) == 10, "expected 10/12 on origin, got %d" % len(present)

# 3) temp-index surgical tree (diff-based payload staging, r530 law)
env = os.environ.copy()
idx = os.path.join(ROOT, ".git", "r357bmc-rescue-index")
if os.path.exists(idx):
    os.remove(idx)
env["GIT_INDEX_FILE"] = idx


def giti(args):
    rc, o, e = git(args, env=env)
    assert rc == 0, " ".join(args) + " -> " + e
    return o


giti(["read-tree", parent])
for s in SHARDS:
    rc, blob, err = git(["hash-object", "-w", s])
    assert rc == 0, err
    giti(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, s)])
tree = giti(["write-tree"])

# 4) deletion-set + payload assertions vs parent (r530/r519 claw)
rc, diffout, err = git(["diff-tree", "-r", "--name-status", parent, tree])
assert rc == 0, err
lines = [l for l in diffout.splitlines() if l.strip()]
adds = [l for l in lines if l.startswith("A")]
dels = [l for l in lines if l.startswith("D")]
mods = [l for l in lines if l.startswith("M")]
assert len(adds) == 2 and not dels and not mods, "unexpected diff: " + diffout
for s in SHARDS:
    assert any(s in l for l in adds), "missing add: " + s

# 5) commit + CAS push (parent re-derived above; FF push, no force)
commit = giti(["commit-tree", tree, "-p", parent, "-m", MSG])
rc, out, err = git(["push", "origin", commit + ":main"])
if rc != 0:
    print("PUSH_REJECTED parent=%s err=%s" % (parent, err))
    sys.exit(2)
print("PUSHED commit=%s parent=%s" % (commit, parent))

# 6) delivery self-verify: fetch + ls-tree 12/12 + both shards present (r516)
rc, _, err = git(["fetch", "origin"])
assert rc == 0, err
rc, head2, err = git(["rev-parse", "origin/main"])
assert rc == 0, err
assert head2 == commit, "origin/main moved post-push: %s vs %s" % (head2, commit)
rc, out, err = git(["ls-tree", "origin/main", "--name-only",
                    "results/p2cal_ext/n1_w61/"])
final = set(l.strip() for l in out.splitlines() if l.strip())
assert len(final) == 12, "expected 12/12 post-push, got %d" % len(final)
for s in SHARDS:
    assert s in final, "delivery check failed: " + s
print("DELIVERED 12/12 W61 shards on origin; head=%s" % head2)
