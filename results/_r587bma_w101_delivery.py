import subprocess, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TMP = os.path.join(REPO, "results", "_r587bma_tmp_index3")

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr); sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
print("base:", base)

NEW = ["results/perpetual_faces/n1_w101_results.json",
       "results/_r587bma_w101_s78_backfill.py"]
MOD = ["research/PERPETUAL_N1_W101_PREREG.md"]

origin_set = set(git(["ls-tree", "-r", "--name-only", "origin/main"]).stdout.strip().splitlines())
for f in NEW:
    assert f not in origin_set, "already on origin: " + f
for f in MOD:
    assert f in origin_set, "mod target missing on origin: " + f

env = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", "origin/main"], env=env)
for f in NEW + MOD:
    sha = git(["hash-object", "-w", f]).stdout.strip()
    git(["update-index", "--add", "--cacheinfo", "100644", sha, f], env=env)
tree = git(["write-tree"], env=env).stdout.strip()
otree = git(["rev-parse", "origin/main^{tree}"]).stdout.strip()
delta = git(["diff-tree", "-r", "--name-status", otree, tree]).stdout.strip().splitlines()
changed = set(l.split("\t")[-1] for l in delta)
assert changed == set(NEW + MOD), changed
assert all(l.split("\t")[0].startswith(("A", "M")) for l in delta), delta
print("tree-delta PASS:", delta)

msg = os.path.join(REPO, "results", "_r587bma_msg3.txt")
with open(msg, "w", encoding="utf-8", newline="\n") as f:
    f.write("round 587 bm-a: W101 FINALIZE landed one-pass first-run (chain head 584,548 -> 586,748, "
            "K=217,920 -> 220,120; w101-only mu=-0.0950309 sigma=0.2408679; merged mu=-0.0928742 "
            "sigma=0.2447945; skill_line_v2 @n_eff 584,548: 1.1689 -> 1.1686, K-lift delta -0.0003; "
            "voids_applied LOWAMP-P1/P2; §5 four gates ALL PASS on the W96 freeze anchor "
            "(|dmu|=0.0022<0.02, sigma -0.02%<10%, A p95 diff 0.0230<0.05, K-lift -0.0003) "
            "+ prereg SS7/SS8 mechanical backfill (r307 two-state law; r538 first-run-only) "
            "-- downstream W102 bm-c finalize UNBLOCKED. [via bm-a r587]")
c = subprocess.run(["git", "commit-tree", tree, "-p", "origin/main", "-F", msg], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
if c.returncode != 0: print("CT FAIL:", c.stderr); sys.exit(1)
sha = c.stdout.strip(); print("commit:", sha)
p = subprocess.run(["git", "push", "origin", sha + ":main"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc:", p.returncode, p.stdout.strip(), p.stderr.strip())
if p.returncode != 0: sys.exit(1)
git(["fetch", "origin"])
bad = [f for f in NEW + MOD if len(subprocess.run(["git", "ls-tree", "origin/main", "--", f], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()) < 3]
print("delivery:", len(NEW + MOD) - len(bad), "ok,", len(bad), "bad")
os.remove(TMP); os.remove(msg)
