# r357 bm-c W62 finalize surgical CAS push (r532/r530/r531/r516 laws -- same
# route as _r357bmc_w61_finalize_push.py, W62 payload).
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PAYLOAD_ADD = ["results/perpetual_faces/n1_w62_results.json"]
PAYLOAD_MOD = ["research/PERPETUAL_N1_W62_PREREG.md"]
ALL = PAYLOAD_ADD + PAYLOAD_MOD

MSG = ("r357 bm-c W62 FINALIZE one-pass (bm-a-owned wave cross-machine "
       "closeout, three-machine relay first full-lifecycle: yield->seat->"
       "freeze 381d85208 bm-a ->tick self-burn 12/12 bm-a ->finalize bm-c): "
       "K=134,320 == sec.0 projection bitwise (132,120+2,200), ledger "
       "prev=498,748 (live-head derive) + 2,200 = 500,948 NET CHAIN HEAD "
       "(voids_applied LOWAMP-P1/P2); S5 4/4 PASS (W62-only mu -0.100936 "
       "vs anchor -0.092367 |d|=0.0086<0.02 / sigma 0.239601 vs 0.248885 "
       "= -3.73%<10% / A p95 0.3037 vs 0.3099 d=-0.0062<0.05 / K-lift "
       "-0.0006<=0.02 skill_line 1.1623->1.1617 @n_eff_held 498,748); "
       "se_mu 0.000674->0.000668; prereg s7/s8 mechanical backfill "
       "same-window (r307 law); chain order honored: W61 landed first "
       "same-window 2eb556a8f; default-wave selftest PASS W2..W62 "
       "[via bm-c r357]")


def git(args, env=None):
    r = subprocess.run(["git"] + args, cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


rc, _, err = git(["fetch", "origin"])
assert rc == 0, "fetch failed: " + err
rc, parent, err = git(["rev-parse", "origin/main"])
assert rc == 0, err

rc, out, err = git(["cat-file", "-e", "origin/main:"
                    "results/perpetual_faces/n1_w62_results.json"])
assert rc != 0, "n1_w62_results.json already on origin -- peer finalize won"
rc, out, err = git(["cat-file", "-e", "origin/main:"
                    "research/PERPETUAL_N1_W62_PREREG.md"])
assert rc == 0, "W62 prereg missing on origin: " + err

env = os.environ.copy()
idx = os.path.join(ROOT, ".git", "r357bmc-w62f-index")
if os.path.exists(idx):
    os.remove(idx)
env["GIT_INDEX_FILE"] = idx


def giti(args):
    rc, o, e = git(args, env=env)
    assert rc == 0, " ".join(args) + " -> " + e
    return o


giti(["read-tree", parent])
for p in ALL:
    rc, blob, err = git(["hash-object", "-w", p])
    assert rc == 0, err
    giti(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, p)])
tree = giti(["write-tree"])

rc, diffout, err = git(["diff-tree", "-r", "--name-status", parent, tree])
assert rc == 0, err
lines = [l for l in diffout.splitlines() if l.strip()]
adds = [l for l in lines if l.startswith("A")]
mods = [l for l in lines if l.startswith("M")]
dels = [l for l in lines if l.startswith("D")]
assert not dels, "DELETION SET NON-EMPTY -- ABORT (r530): " + diffout
assert sorted(l.split("\t", 1)[1] for l in adds) == sorted(PAYLOAD_ADD), diffout
assert sorted(l.split("\t", 1)[1] for l in mods) == sorted(PAYLOAD_MOD), diffout

commit = giti(["commit-tree", tree, "-p", parent, "-m", MSG])
rc, out, err = git(["push", "origin", commit + ":main"])
if rc != 0:
    print("PUSH_REJECTED parent=%s err=%s" % (parent, err))
    sys.exit(2)
print("PUSHED commit=%s parent=%s" % (commit, parent))

rc, _, err = git(["fetch", "origin"])
assert rc == 0, err
rc, head2, err = git(["rev-parse", "origin/main"])
assert rc == 0, err
assert head2 == commit, "origin moved post-push: %s vs %s" % (head2, commit)
rc, out, err = git(["cat-file", "-e",
                    "origin/main:results/perpetual_faces/n1_w62_results.json"])
assert rc == 0, "delivery check failed"
print("DELIVERED n1_w62_results.json + prereg s7/s8 backfill on origin")
print("LEDGER HEAD 500,948 (W62 landed, chain W1..W62 complete)")
