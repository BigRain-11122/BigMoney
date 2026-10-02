# -*- coding: utf-8 -*-
# _r374bmc_coda_push.py -- coda surgical push (2-file payload; same paradigm
# as _r374bmc_push.py). CODELY union re-derived against the FRESH origin blob.
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
IDX = os.path.join(ROOT, ".git", "_r374bmc_coda_index")
BASE = "a0d9cabd3"                      # my pushed surgical commit (coda's parent)
MY_PIT_KEY = "pre-push 爪删除集"
PAYLOAD = ["CODELY.md", "results/_r374bmc_push.py"]


def git(args, env=None, check=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CNW, env=e)
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:4],
                   r.stderr.decode("utf-8", "replace")[:400]))
    return r


git(["fetch", "origin"])
origin_tip = git(["rev-parse", "origin/main"]).stdout.decode().strip()
print("origin tip: " + origin_tip[:12])

their = git(["diff", "--name-status", "--no-renames", BASE, origin_tip]).stdout.decode()
print("their delta vs my pushed base:\n" + their)

# CODELY union: fresh origin blob + my push-saga pit line
SRC = os.path.join(ROOT, "CODELY.md")
origin_lf = git(["show", "origin/main:CODELY.md"]).stdout
assert origin_lf.count(b"\r") == 0
local_lf = open(SRC, "rb").read().replace(b"\r\n", b"\n")
o_lines = origin_lf.decode("utf-8").split("\n")
l_lines = local_lf.decode("utf-8").split("\n")
pit_line = next(ln for ln in l_lines if MY_PIT_KEY in ln)
assert pit_line not in o_lines, "coda pit line already on origin"
assert o_lines.count("### Reference") == 1
assert any("带闸 leg0c" in x for x in o_lines), "leg0c line missing from origin CODELY"
ref_i = o_lines.index("### Reference")
union = o_lines[:ref_i] + [pit_line] + o_lines[ref_i:]
union_lf = "\n".join(union).encode("utf-8")
assert len(union_lf) == len(origin_lf) + len(pit_line.encode("utf-8")) + 1
open(SRC, "wb").write(union_lf.replace(b"\n", b"\r\n"))
print("CODELY union: origin %dB + coda pit %dB" % (len(origin_lf), len(pit_line.encode("utf-8")) + 1))

env_idx = {"GIT_INDEX_FILE": IDX}
if os.path.exists(IDX):
    os.remove(IDX)
git(["read-tree", origin_tip], env=env_idx)
git(["add", "--"] + PAYLOAD, env=env_idx)
tree = git(["write-tree"], env=env_idx).stdout.decode().strip()

delA = git(["diff-tree", "-r", "--diff-filter=D", "--name-only", origin_tip, tree],
           env=env_idx).stdout.decode().strip()
assert delA == "", "deletion set non-empty: " + delA[:300]
dset = set(git(["diff-tree", "-r", "--name-only", origin_tip, tree],
               env=env_idx).stdout.decode().strip().splitlines())
assert dset <= set(PAYLOAD), ("tree-delta not subset of payload", sorted(dset))
print("assertions PASS: deletion-set empty, tree-delta(%d) == payload(2)" % len(dset))

msg = ("r374 bm-c coda: push-saga pit line (pre-push claw deletion-set false positive on "
       "diverged base x2; surgical path immune; r305/r501 commit -C net-path rerun; "
       "r366 column-parse + stale-face lessons) + push tool receipt archived [via bm-c r374]")
new_sha = git(["commit-tree", tree, "-p", origin_tip, "-m", msg]).stdout.decode().strip()
r = git(["push", "origin", new_sha + ":main"], check=False)
if r.returncode != 0:
    print("PUSH REJECTED (origin moved again): " + r.stderr.decode("utf-8", "replace")[:300])
    sys.exit(3)
print("PUSH OK: %s -> origin/main (parent %s)" % (new_sha[:12], origin_tip[:12]))

old_local = git(["rev-parse", "main"]).stdout.decode().strip()
git(["update-ref", "refs/heads/main", new_sha, old_local])
git(["reset", "--mixed", new_sha])
st2 = git(["status", "--porcelain"]).stdout.decode("utf-8")
restore = [ln[3:].strip().strip('"') for ln in st2.splitlines()
           if ln.startswith(" D") or ln.startswith("D ")]
if restore:
    git(["checkout", "--"] + restore)
    print("restored %d origin-side files (D face)" % len(restore))
git(["fetch", "origin"])
ahead = git(["rev-list", "--count", "origin/main..main"]).stdout.decode().strip()
behind = git(["rev-list", "--count", "main..origin/main"]).stdout.decode().strip()
print("delivery proof: ahead=%s behind=%s" % (ahead, behind))
print("CODA PUSH COMPLETE")
