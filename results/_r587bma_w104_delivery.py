import subprocess, os, json, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TMP = os.path.join(REPO, "results", "_r587bma_tmp_index2")

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr); sys.exit(1)
    return r

# 0. fresh fetch (r570 law)
git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
print("base:", base)

# 1. payload: 12 W104 shards + 3 r587 receipts (new files, hash-object)
new_files = []
for i in range(12):
    new_files.append("results/p2cal_ext/n1_w104/shard-%d-of-12.json" % i)
new_files += ["results/_r587bma_s0_surgery.py", "results/_r587bma_realign.py",
              "results/_r587bma_w104_delivery.py"]

# 2. pool_core_samples.jsonl: re-union onto CURRENT origin blob (idempotent, r570/r580 law)
p = "results/pool_core_samples.jsonl"
oblob = git(["show", "origin/main:" + p]).stdout.replace("\r\n", "\n")
olines = [l for l in oblob.split("\n") if l.strip()]
lbytes = open(os.path.join(REPO, p), "rb").read().decode("utf-8", errors="replace").replace("\r\n", "\n")
llines = [l for l in lbytes.split("\n") if l.strip()]
oset = set(olines)
extra = [l for l in llines if l not in oset]
for l in extra:
    assert isinstance(json.loads(l), dict), "non-dict extra row"
merged = olines + extra
for l in merged:
    assert isinstance(json.loads(l), dict)
work = "\n".join(merged) + "\n"
open(os.path.join(REPO, p), "wb").write(work.encode("utf-8"))
print("pool union: origin", len(olines), "+ local extra", len(extra), "=", len(merged))

# 3. temp index from origin/main
env = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", "origin/main"], env=env)

# 4. deletion-set assertion: no payload file already exists in origin (all new/append)
origin_ls = set(git(["ls-tree", "-r", "--name-only", "origin/main"]).stdout.strip().splitlines())
for f in new_files:
    if f in origin_ls:
        print("UNEXPECTED: new file already in origin:", f); sys.exit(1)

# 5. hash-object new files + update-index
for f in new_files:
    sha = git(["hash-object", "-w", f]).stdout.strip()
    git(["update-index", "--add", "--cacheinfo", "100644", sha, f], env=env)
# pool file: hash the unioned worktree content
sha_p = git(["hash-object", "-w", p]).stdout.strip()
git(["update-index", "--cacheinfo", "100644", sha_p, p], env=env)
payload = set(new_files) | {p}

tree = git(["write-tree"], env=env).stdout.strip()
otree = git(["rev-parse", "origin/main^{tree}"]).stdout.strip()
delta = git(["diff-tree", "-r", "--name-status", otree, tree]).stdout.strip().splitlines()
changed = set()
for line in delta:
    cols = line.split("\t")
    changed.add(cols[1] if len(cols) < 3 else cols[2])
if changed != payload:
    print("TREE-DELTA MISMATCH:", changed - payload, payload - changed); sys.exit(1)
for line in delta:
    cols = line.split("\t")
    st = cols[0][0] if cols else "?"
    tgt = cols[1] if len(cols) < 3 else cols[2]
    if tgt == p and st in ("M", "A"): continue
    if st != "A":
        print("NON-ADD ENTRY IN DELTA:", line[:100]); sys.exit(1)
print("tree-delta == payload assertion PASS,", len(delta), "(adds + 1 pool mod)")

# 6. commit-tree
msg_path = os.path.join(REPO, "results", "_r587bma_msg2.txt")
with open(msg_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("round 587 bm-a: W104 burn products 12/12 delivered to origin (engine burn complete 17:26-17:38, "
            "K=2,200 = A 0..2000 + B 0..200 grid, machine=bm-a provenance, workers=8 multicore, "
            "prereg=PERPETUAL_N1_W104_PREREG frozen r586, bands A 251_004..253_003 / B 59_601..59_800; "
            "session-delivery precedent r583 W98) + pool_core_samples union row (r570/r580 law, dict-gated) "
            "+ r587 S0 receipts (r586-wrap surgical delivery + face-wise realign). "
            "All-add payload, deletion-set empty vs origin. [via bm-a r587]")
cmt = subprocess.run(["git", "commit-tree", tree, "-p", "origin/main", "-F", msg_path], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
if cmt.returncode != 0:
    print("COMMIT-TREE FAIL:", cmt.stderr); sys.exit(1)
sha = cmt.stdout.strip()
print("commit:", sha)

# 7. push
push = subprocess.run(["git", "push", "origin", sha + ":main"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc:", push.returncode, push.stdout.strip(), push.stderr.strip())
if push.returncode != 0: sys.exit(1)

# 8. delivery verify
git(["fetch", "origin"])
bad = []
for f in new_files + [p]:
    r = subprocess.run(["git", "ls-tree", "origin/main", "--", f], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
    if not (r and len(r) > 2): bad.append(f)
print("delivery verify:", len(new_files) + 1 - len(bad), "ok,", len(bad), "bad", bad[:3])
os.remove(TMP); os.remove(msg_path)
