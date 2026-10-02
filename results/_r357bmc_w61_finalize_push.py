# r357 bm-c W61 finalize surgical CAS push (r532 no-rebase route: tracked
# live-write lane files in tree make rebase impossible; r530 diff-based payload
# staging + deletion-set assertion; r531 parent rev-parse at push time; r516
# post-push ls-tree delivery self-verify).
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PAYLOAD_ADD = ["results/perpetual_faces/n1_w61_results.json"]
PAYLOAD_MOD = ["research/PERPETUAL_N1_W61_PREREG.md"]
ALL = PAYLOAD_ADD + PAYLOAD_MOD

MSG = ("r357 bm-c W61 FINALIZE one-pass: K=132,120 == sec.0 projection "
       "bitwise (129,920+2,200), ledger prev=496,548 (live-head derive, "
       "zero hand-copy) + 2,200 = 498,748 NET CHAIN HEAD (voids_applied "
       "LOWAMP-P1/P2); S5 4/4 PASS (W61-only mu -0.094806 vs anchor "
       "-0.092367 |d|=0.0024<0.02 / sigma 0.248458 vs 0.248885 = -0.17% "
       "<10% / A p95 0.3163 vs 0.3099 d=+0.0064<0.05 / K-lift +0.0003 "
       "<=0.02 skill_line 1.1618->1.1621 @n_eff_held 496,548); se_mu "
       "0.000679->0.000674 narrowing; burned by bm-c resident engine 12/12 "
       "(cross-machine burn on bm-b-owned wave per lane contract, honest "
       "note), last-2 shard rescue self-healed by engine appender 92671123d "
       "after dead r356 session pre-push death (ba9c9d77c orphan); prereg "
       "s7/s8 mechanical backfill same-window (r307 law); default-wave "
       "selftest PASS full chain W2..W62 [via bm-c r357]")


def git(args, env=None):
    r = subprocess.run(["git"] + args, cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


rc, _, err = git(["fetch", "origin"])
assert rc == 0, "fetch failed: " + err
rc, parent, err = git(["rev-parse", "origin/main"])
assert rc == 0, err

# pre-gate: results file NOT on origin yet; prereg IS (frozen bm-b commit)
rc, out, err = git(["cat-file", "-e", "origin/main:"
                    "results/perpetual_faces/n1_w61_results.json"])
assert rc != 0, "n1_w61_results.json already on origin -- peer finalize?"
rc, out, err = git(["cat-file", "-e", "origin/main:"
                    "research/PERPETUAL_N1_W61_PREREG.md"])
assert rc == 0, "W61 prereg missing on origin: " + err

env = os.environ.copy()
idx = os.path.join(ROOT, ".git", "r357bmc-finalize-index")
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

# payload + deletion-set assertions (r530/r519 claw)
rc, diffout, err = git(["diff-tree", "-r", "--name-status", parent, tree])
assert rc == 0, err
lines = [l for l in diffout.splitlines() if l.strip()]
adds = [l for l in lines if l.startswith("A")]
mods = [l for l in lines if l.startswith("M")]
dels = [l for l in lines if l.startswith("D")]
assert not dels, "DELETION SET NON-EMPTY -- ABORT (r530 law): " + diffout
assert sorted(l.split("\t", 1)[1] for l in adds) == sorted(PAYLOAD_ADD), \
    "unexpected adds: " + diffout
assert sorted(l.split("\t", 1)[1] for l in mods) == sorted(PAYLOAD_MOD), \
    "unexpected mods: " + diffout

commit = giti(["commit-tree", tree, "-p", parent, "-m", MSG])
rc, out, err = git(["push", "origin", commit + ":main"])
if rc != 0:
    print("PUSH_REJECTED parent=%s err=%s" % (parent, err))
    sys.exit(2)
print("PUSHED commit=%s parent=%s" % (commit, parent))

# delivery self-verify (r516)
rc, _, err = git(["fetch", "origin"])
assert rc == 0, err
rc, head2, err = git(["rev-parse", "origin/main"])
assert rc == 0, err
assert head2 == commit, "origin moved post-push: %s vs %s" % (head2, commit)
rc, out, err = git(["cat-file", "-e",
                    "origin/main:results/perpetual_faces/n1_w61_results.json"])
assert rc == 0, "delivery check failed for results file"
print("DELIVERED n1_w61_results.json + prereg s7/s8 backfill on origin")
print("LEDGER HEAD 498,748 (W61 landed, chain W1..W61 complete)")
