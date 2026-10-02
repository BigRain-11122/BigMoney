import subprocess, sys, os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TMP = os.path.join(REPO, "results", "_r587bma_tmp_index")

def git(args, env=None, check=True):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=e)
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr); sys.exit(1)
    return r

# 1. payload = staged diff vs HEAD (renames: delete old + add new)
st = git(["diff", "--cached", "--name-status", "HEAD"]).stdout.strip().splitlines()
payload_add = {}   # path -> staged blob sha
payload_del = []
for line in st:
    parts = line.split("\t")
    if parts[0].startswith("R"):
        payload_del.append(parts[1]); payload_add[parts[2]] = None
    elif parts[0].startswith("D"):
        payload_del.append(parts[1])
    elif parts[0].startswith("A") or parts[0].startswith("M"):
        payload_add[parts[1]] = None
    else:
        print("UNEXPECTED STATUS:", line); sys.exit(1)

# get staged blob shas
ls = git(["ls-files", "-s"] + list(payload_add.keys())).stdout.strip().splitlines()
for line in ls:
    cols = line.split()
    payload_add[cols[3]] = cols[1]  # path -> blob sha

print("payload_add:", len(payload_add), "payload_del:", len(payload_del))

# 2. temp index = origin/main
env = {"GIT_INDEX_FILE": TMP}
if os.path.exists(TMP): os.remove(TMP)
git(["read-tree", "origin/main"], env=env)

# 3. deletion-set assertion (vs origin/main): each payload_del must already be absent in origin/main
origin_ls = git(["ls-tree", "-r", "--name-only", "origin/main"]).stdout.strip().splitlines()
origin_set = set(origin_ls)
real_del = [p for p in payload_del if p in origin_set]
if real_del:
    print("DELETION SET NON-EMPTY vs origin:", real_del); sys.exit(1)
print("deletion-set assertion PASS (empty vs origin)")

# 4. apply adds with staged blobs
for path, sha in payload_add.items():
    if path in origin_set:
        osha = subprocess.run(["git", "ls-tree", "origin/main", "--", path], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
        if osha and osha[2] == sha:
            continue  # identical to origin, skip
    git(["update-index", "--add", "--cacheinfo", "100644", sha, path], env=env)

tree = git(["write-tree"], env=env).stdout.strip()
print("tree:", tree)

# 5. tree-delta assertion: origin_tree -> new_tree must equal payload set only
otree = git(["rev-parse", "origin/main^{tree}"]).stdout.strip()
delta = git(["diff-tree", "-r", "--name-status", otree, tree]).stdout.strip().splitlines()
changed_paths = set()
for line in delta:
    cols = line.split("\t")
    changed_paths.add(cols[1] if len(cols) < 3 else cols[2])
expected = set(payload_add.keys())
unexpected = changed_paths - expected
if unexpected:
    print("UNEXPECTED TREE DELTA:", unexpected); sys.exit(1)
print("tree-delta == payload set assertion PASS,", len(delta), "entries")

# 6. commit-tree on origin/main parent
msg_path = os.path.join(REPO, "results", "_r587bma_msg.txt")
with open(msg_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("round 586 bm-a wrap delivery (r586 session died post-heartbeat pre-commit; r587 adopts staged payload per r471 law): "
            "S6 chain outputs (36 legs), W104/W105 seat inbox moves to processed (blobs identical to origin moves, zero conflict), "
            "T-126 progress note, heartbeat+state 586, round report line, attrition scan CLEAN. "
            "Surgical payload onto origin/main base per r532/r523 law (live-write telemetry tree, rebase blocked). "
            "Deletion-set empty vs origin, tree-delta == payload set. [via bm-a r587]")
cmt = subprocess.run(["git", "commit-tree", tree, "-p", "origin/main", "-F", msg_path], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
if cmt.returncode != 0:
    print("COMMIT-TREE FAIL:", cmt.stderr); sys.exit(1)
sha = cmt.stdout.strip()
print("commit:", sha)

# 7. push (fast-forward from origin/main must succeed)
push = subprocess.run(["git", "push", "origin", sha + ":main"], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("push rc:", push.returncode, push.stdout.strip(), push.stderr.strip())
if push.returncode != 0: sys.exit(1)

# 8. delivery self-verify: ls-tree origin/main for payload files
git(["fetch", "origin"])
ok, bad = 0, []
for path, bsha in payload_add.items():
    r = subprocess.run(["git", "ls-tree", "origin/main", "--", path], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
    if r and r[2] == bsha: ok += 1
    else: bad.append(path)
print("delivery verify:", ok, "ok,", len(bad), "bad", bad[:5])
