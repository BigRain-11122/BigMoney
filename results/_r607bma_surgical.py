"""r607 bm-a surgical re-land (r523/GM 净路): origin advanced (5d2fe405d->ac8519fd2+)
after my closeout commit 3ff0daa64; push was claw-blocked as r374 fork artifact.
Surgical path: temp index from origin/main -> apply my 56-file payload with
face-aware overrides (CODELY.md + pool_core_samples.jsonl = bytes-space union
onto NEW origin base; 18 shared host faces = my fresh blobs per r378 host right)
-> commit-tree -p <fresh origin/main> -> push sha:main -> CAS realign local.
Three assertions fail-fast (r523): deletion set / payload tree-delta / staging
identity. Zero working-tree touch during push.
"""
import subprocess, sys, os, json

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
MY_COMMIT = "3ff0daa64"   # unpushed local closeout commit
BASE = "5d2fe405d"        # merge-base (my commit's parent)
TMPIDX = os.path.join(REPO, "results", "_r607bma_tmpidx")

def git(*args, env=None, inp=None):
    e = dict(os.environ)
    if env: e.update(env)
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, env=e, input=inp)
    return r.returncode, r.stdout, r.stderr

def g(*args, env=None):
    rc, o, e = git(*args, env=env)
    if rc != 0:
        print("GIT FAIL:", args, e.decode("utf-8", "replace")); sys.exit(1)
    return o

# 0) execution-time fresh reads (r593 law)
ORIGIN = g("rev-parse", "origin/main").decode().strip()
HEAD_NOW = g("rev-parse", "HEAD").decode().strip()
assert HEAD_NOW.startswith(MY_COMMIT), f"HEAD moved: {HEAD_NOW} -- abort (daemon commit race)"
print(f"origin={ORIGIN} head={HEAD_NOW}")

# 1) my payload: (status, path) vs BASE
out = g("diff-tree", "--no-commit-id", "--no-renames", "--name-status", "-r", MY_COMMIT).decode()
payload = []
for ln in out.splitlines():
    if not ln.strip(): continue
    st, path = ln.split("\t")[0], ln.split("\t")[-1]
    payload.append((st, path))
print("payload files:", len(payload))

# 2) build union blobs (bytes-space, r600/r373)
def union_jsonl(origin_ref, path):
    ob = g("show", f"{origin_ref}:{path}")
    crlf = ob.count(b"\r\n"); lf = ob.count(b"\n")
    eol = b"\r\n" if crlf * 2 > lf else b"\n"
    ol = [l.rstrip(b"\r") for l in ob.split(b"\n") if l.strip()]
    with open(os.path.join(REPO, path), "rb") as f:
        disk = f.read()
    dl = [l.rstrip(b"\r") for l in disk.split(b"\n") if l.strip()]
    oset = set(ol)
    local_only = [l for l in dl if l not in oset]
    for l in ol + local_only:
        obj = json.loads(l.decode("utf-8", "replace"))
        assert isinstance(obj, dict), f"non-dict line in {path}"
    merged = eol.join(ol + local_only) + eol
    tmpf = os.path.join(REPO, "results", "_r607bma_unionblob.tmp")
    with open(tmpf, "wb") as f:
        f.write(merged)
    sha = g("hash-object", "-w", tmpf).decode().strip()
    os.remove(tmpf)
    return sha, len(ol), len(local_only), eol

pool_sha, pool_on, pool_mine, pool_eol = union_jsonl(ORIGIN, "results/pool_core_samples.jsonl")
print(f"pool union: origin={pool_on} local_only={pool_mine} eol={'CRLF' if pool_eol==b'\r\n' else 'LF'} sha={pool_sha[:10]}")

# CODELY union: origin verbatim + my line appended if absent
ob = g("show", f"{ORIGIN}:CODELY.md")
crlf = ob.count(b"\r\n") * 2 > ob.count(b"\n")
ceol = b"\r\n" if crlf else b"\n"
mine_line = None
with open(os.path.join(REPO, "CODELY.md"), "rb") as f:
    for l in f.read().split(b"\n"):
        if b"[2026-10-03 05:0x r607 bm-a] S0 " in l:
            mine_line = l.rstrip(b"\r"); break
assert mine_line, "my CODELY line not found on disk"
if mine_line in ob:
    codely_blob = g("rev-parse", f"{ORIGIN}:CODELY.md").decode().strip()
    print("CODELY: my line already in origin blob (no-op)")
else:
    merged = ob.rstrip(b"\n").rstrip(b"\r") + ceol + mine_line + ceol
    tmpf = os.path.join(REPO, "results", "_r607bma_codelyblob.tmp")
    with open(tmpf, "wb") as f: f.write(merged)
    codely_blob = g("hash-object", "-w", tmpf).decode().strip()
    os.remove(tmpf)
    print(f"CODELY union: origin + my r607 line, sha={codely_blob[:10]}")

# 3) temp index from origin tree
if os.path.exists(TMPIDX): os.remove(TMPIDX)
IDXENV = {"GIT_INDEX_FILE": TMPIDX}
g("read-tree", ORIGIN, env=IDXENV)

# 4) apply payload with overrides
for st, path in payload:
    if path == "results/pool_core_samples.jsonl":
        mode = g("ls-tree", MY_COMMIT, "--", path).decode().split()[0]
        g("update-index", "--add", "--cacheinfo", f"{mode},{pool_sha},{path}", env=IDXENV)
    elif path == "CODELY.md":
        mode = g("ls-tree", MY_COMMIT, "--", path).decode().split()[0]
        g("update-index", "--add", "--cacheinfo", f"{mode},{codely_blob},{path}", env=IDXENV)
    elif st == "D":
        g("update-index", "--force-remove", path, env=IDXENV)
    else:
        # take blob+mode from MY commit tree (host-fresh right for shared faces)
        row = g("ls-tree", MY_COMMIT, "--", path).decode()
        mode, bsha = row.split()[0], row.split()[2]
        g("update-index", "--add", "--cacheinfo", f"{mode},{bsha},{path}", env=IDXENV)
NEW_TREE = g("write-tree", env=IDXENV).decode().strip()
print("new tree:", NEW_TREE)

# 5) assertions
# 5a) deletion set: origin tree vs new tree
out = g("diff-tree", "--no-renames", "--name-status", "-r", ORIGIN, NEW_TREE).decode()
d_rows = [l.split("\t")[-1] for l in out.splitlines() if l.startswith("D")]
expected_d = ["fleet/inbox/MSG-2026-10-03-0410-bmc-bma.md"]  # my own move (whitelisted)
assert sorted(d_rows) == sorted(expected_d), f"deletion set mismatch: {d_rows}"
# 5b) payload tree-delta: M+A+D counts vs my 56-file payload
delta_rows = [l for l in out.splitlines() if l.strip()]
dm = [l for l in delta_rows if l.startswith("M")]
da = [l for l in delta_rows if l.startswith("A")]
my_m = [p for s, p in payload if s == "M"]
my_a = [p for s, p in payload if s == "A"]
# every my-M/A path must appear exactly once in new-tree delta (M or A)
delta_paths = set(l.split("\t")[-1] for l in delta_rows)
missing = [p for s, p in payload if s != "D" and p not in delta_paths]
assert not missing, f"payload paths missing in tree delta: {missing}"
print(f"assertions: D={d_rows} M={len(dm)} A={len(da)} payload ok")

# 6) commit-tree -p ORIGIN
msg_path = os.path.join(REPO, ".codely-cli", "scratch", "r607bma_msg.txt")
NEW_SHA = g("commit-tree", NEW_TREE, "-p", ORIGIN, "-F", msg_path).decode().strip()
print("new commit:", NEW_SHA)

# 7) push sha:main (claw runs: deletion set = inbox move only)
rc, o, e = git("push", "origin", f"{NEW_SHA}:refs/heads/main")
print("push rc:", rc)
if rc != 0:
    print("PUSH FAIL:", e.decode("utf-8", "replace")); sys.exit(1)

# 8) CAS realign local main: old = full 40-char current head (r569-3)
old_full = g("rev-parse", "HEAD").decode().strip()
g("update-ref", "refs/heads/main", NEW_SHA, old_full)
g("reset", "--mixed", NEW_SHA)
os.remove(TMPIDX)
print("REALIGNED: local main ->", NEW_SHA[:10], " (post-push faceted checkout = next step)")
