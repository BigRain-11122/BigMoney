"""r558 bm-a FIX v2: pool_core_samples.jsonl exact-dup removal from polluted blob.

Polluted origin blob (1059 lines) = canonical 557 (byte-verbatim prefix, mixed
line endings) + 501 appended lines (495 exact dups + 6 genuinely-new W48 lines).
Repair = line-level exact-string dedupe keeping first occurrence. Safety proof:
result must start with the canonical blob (git cat-file a9cd7e07) verbatim.
"""
import subprocess, os, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
P = "results/pool_core_samples.jsonl"
CANON_BLOB = "a9cd7e07052337101c0bd78afd8ff669e23c9cd4"  # 557-line canonical (e488e8008==a6fcc95f5)

def git(*args, **kw):
    r = subprocess.run(["git"] + list(args), capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:300]}")
    return r.stdout

def git_env(env_extra, *args, **kw):
    env = dict(os.environ); env.update(env_extra)
    r = subprocess.run(["git"] + list(args), capture_output=True, env=env, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:300]}")
    return r.stdout

canon_bytes = git("cat-file", "blob", CANON_BLOB)
canon_n = len(canon_bytes.splitlines())
print(f"[canon] {canon_n} lines, {len(canon_bytes)} bytes")

git("fetch", "origin")
parent = git("rev-parse", "origin/main").decode().strip()
org = git("show", f"{parent}:{P}")
org_kept = org.splitlines(keepends=True)
assert org.startswith(canon_bytes), f"origin blob is NOT canon-prefixed! manual review (parent={parent[:9]})"
print(f"[polluted] {len(org_kept)} lines starts with canon {canon_n} -- pollution region = {len(org_kept)-canon_n} lines")

seen = set()
kept = []
removed = 0
for l in org_kept:
    k = l.rstrip(b"\r\n")
    if k.strip() and k in seen:
        removed += 1
        continue
    if k.strip():
        seen.add(k)
    kept.append(l)
merged = b"".join(kept)
n = len(merged.splitlines())
print(f"[dedupe] kept={n} removed_dups={removed}")
assert merged.startswith(canon_bytes), "dedupe damaged canonical prefix"
assert n == canon_n + (len(org_kept) - canon_n - removed), "line count math mismatch"
# genuinely-new lines must all be W48 engine samples (my only legitimate additions)
new_lines = [l for l in merged[len(canon_bytes):].splitlines() if l.strip()]
for l in new_lines:
    assert b"PERPETUAL-N1-W48" in l, f"non-W48 line in new region: {l[:120]}"
print(f"[new-region] {len(new_lines)} lines, all W48 samples: OK")

for attempt in range(1, 4):
    idx = os.path.join(tempfile.gettempdir(), f"r558fix2_idx_{os.getpid()}")
    env = {"GIT_INDEX_FILE": idx}
    git_env(env, "read-tree", parent)
    h = git("hash-object", "-w", "--stdin", input=merged).decode().strip()
    git_env(env, "update-index", "--add", "--cacheinfo", f"100644,{h},{P}")
    tree = git_env(env, "write-tree").decode().strip()
    os.remove(idx)
    st = git("diff", "--name-status", parent, tree).decode()
    assert len([l for l in st.splitlines() if l.strip()]) == 1, f"payload not surgical: {st}"
    msg = os.path.join(tempfile.gettempdir(), f"r558fix2_msg_{os.getpid()}.txt")
    with open(msg, "w", encoding="utf-8", newline="\n") as f:
        f.write("r558 S0 repair v2: pool_core_samples.jsonl exact-duplicate removal (prior surgical commit appended 501 "
                f"lines due to mixed-eol split bug: 495 byte-identical dups removed line-level, canonical 557-line blob "
                f"byte-verbatim prefix asserted + {len(new_lines)} genuinely-new W48 sample lines kept; deletion set = "
                "own-pollution region only, canon-prefix ownership proof in script results/_r558bma_union_repair.py) [via bm-a r558]")
    sha = git("commit-tree", tree, "-p", parent, "-F", msg).decode().strip()
    os.remove(msg)
    r = subprocess.run(["git", "push", "origin", f"{sha}:main"], capture_output=True)
    if r.returncode == 0:
        print(f"[push] OK {sha[:9]}")
        break
    print(f"[push] attempt {attempt} rejected: {r.stderr.decode(errors='replace')[:160]}")
    git("fetch", "origin")
    parent = git("rev-parse", "origin/main").decode().strip()
    org = git("show", f"{parent}:{P}")
    if not org.startswith(canon_bytes):
        raise SystemExit("origin changed shape mid-repair -- manual review")
    seen = set(); kept = []; removed = 0
    for l in org.splitlines(keepends=True):
        k = l.rstrip(b"\r\n")
        if k.strip() and k in seen:
            removed += 1; continue
        if k.strip(): seen.add(k)
        kept.append(l)
    merged = b"".join(kept)
else:
    raise SystemExit("push failed 3x")

git("fetch", "origin")
o = git("rev-parse", "origin/main").decode().strip()
assert o == sha
b = git("show", f"origin/main:{P}")
assert b.startswith(canon_bytes) and len(b.splitlines()) == n
print(f"[verify] origin pool_core_samples = {len(b.splitlines())} lines, canon-prefix verbatim")
print("REPAIR_V2_OK", sha)
