"""r558 bm-a S0 surgical delivery (r532/r530/r519 family law).

Base = origin/main (rev-parse at script time). Payload = ride-5 changed files
minus shared-regen BOTH-set (left to origin side, re-derived this round S6),
plus pool_core_samples.jsonl exact-string union (r294 domain law).
Assertions: deletion-set empty, payload count, post-push ls-tree delivery.
Retry: origin moved during push -> re-derive union vs new parent, blobs cheap.
"""
import subprocess, os, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
os.chdir(REPO)

BASE = "0584c3d18"  # ride-5 parent (my last pushed commit)
UNION_PATH = "results/pool_core_samples.jsonl"

def git(*args, **kw):
    r = subprocess.run(["git"] + list(args), capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:400]}")
    return r.stdout

def git_env(env_extra, *args, **kw):
    env = dict(os.environ); env.update(env_extra)
    r = subprocess.run(["git"] + list(args), capture_output=True, env=env, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:400]}")
    return r.stdout

def changed_files(a, b):
    out = git("diff", "--name-only", a, b).decode("utf-8", "replace")
    return [l for l in out.splitlines() if l.strip()]

for attempt in range(1, 4):
    git("fetch", "origin")
    parent = git("rev-parse", "origin/main").decode().strip()

    mine_changed = changed_files(BASE, "HEAD")          # ride-5 payload (parent..ride5)
    origin_changed = changed_files(BASE, parent)        # origin 7+ commits
    mine_only = [p for p in mine_changed if p not in origin_changed]
    both = [p for p in mine_changed if p in origin_changed]

    # sanity: W48 shards are the critical payload
    shards = [p for p in mine_only if "n1_w48" in p]
    assert len(shards) == 5, f"expected 5 W48 shard files, got {shards}"
    assert UNION_PATH in both, f"union path not in BOTH set: both={both}"

    # ---- union for pool_core_samples.jsonl (exact-string dedupe, r294 domain law)
    org_bytes = git("show", f"{parent}:{UNION_PATH}")
    eol = b"\r\n" if b"\r\n" in org_bytes else b"\n"
    org_lines = org_bytes.split(eol)
    trailing = org_bytes.endswith(eol)
    mine_bytes = open(UNION_PATH, "rb").read()
    mine_lines = mine_bytes.replace(b"\r\n", b"\n").split(b"\n")
    org_keys = [l for l in org_lines if l.strip()]
    seen = set(l.rstrip(b"\r") for l in org_lines if l.strip())
    extras = []
    for l in mine_lines:
        k = l.rstrip(b"\r")
        if k.strip() and k not in seen:
            seen.add(k); extras.append(k)
    merged = list(org_lines)  # preserve origin order verbatim (incl blanks)
    # drop trailing empty artifact if origin ends with eol
    if trailing and merged and merged[-1] == b"":
        merged = merged[:-1] + extras + ([b""] if trailing else [])
    else:
        merged = merged + extras
    union_bytes = eol.join(merged) + (eol if trailing else b"")
    print(f"[union] origin={len([l for l in org_lines if l.strip()])} extras={len(extras)} merged={len(merged)}")

    # ---- temp index staging (r530 diff-based payload)
    tmp_idx = os.path.join(tempfile.gettempdir(), f"r558_idx_{os.getpid()}")
    env_idx = {"GIT_INDEX_FILE": tmp_idx}
    git_env(env_idx, "read-tree", parent)
    staged = []
    for p in mine_only:
        blob = open(p, "rb").read()
        h = git("hash-object", "-w", "--stdin", input=blob).decode().strip()
        git_env(env_idx, "update-index", "--add", "--cacheinfo", f"100644,{h},{p}")
        staged.append(p)
    h = git("hash-object", "-w", "--stdin", input=union_bytes).decode().strip()
    git_env(env_idx, "update-index", "--add", "--cacheinfo", f"100644,{h},{UNION_PATH}")
    staged.append(UNION_PATH)
    tree = git_env(env_idx, "write-tree").decode().strip()
    os.remove(tmp_idx)

    # ---- assertions: deletion-set empty (r519/r530 law), payload count
    st = git("diff", "--name-status", parent, tree).decode("utf-8", "replace")
    lines = [l for l in st.splitlines() if l.strip()]
    dels = [l for l in lines if l.startswith("D")]
    assert not dels, f"DELETION SET NON-EMPTY: {dels}"
    assert len(lines) == len(staged), f"payload count mismatch: {len(lines)} vs staged {len(staged)}"
    print(f"[assert] {len(lines)} files, 0 deletions, all A/M: OK")

    msg_file = os.path.join(tempfile.gettempdir(), f"r558_msg_{os.getpid()}.txt")
    with open(msg_file, "w", encoding="utf-8", newline="\n") as f:
        f.write("r558 S0 surgical delivery: W48 12/12 product shards (7-11, burn complete on tick engine) "
                "+ bm-a engine lane faces (state/history/ledger/face, autofill/compute_audit.bm-a, update statuses, token_usage.bm-a) "
                "+ monthly regen faces (science_audit/briefings/self_review, mine-only) "
                f"+ pool_core_samples exact-string union (origin preserved + {len(extras)} mine-only lines, r294 domain law); "
                "shared regen faces (BOTH set, 18 files) left to origin side per bm-b r558 precedent, re-derived this round S6; "
                "stale-prev W48 first finalize product deleted pre-rerun per r538 law -- second finalize re-derive follows this round per r518 seat-loss law (W49 landed first, prev=470,148) [via bm-a r558]")
    commit_sha = git("commit-tree", tree, "-p", parent, "-F", msg_file).decode().strip()
    os.remove(msg_file)
    print(f"[commit-tree] {commit_sha} parent={parent[:9]}")

    # ---- push (CAS by construction: parent == origin/main rev-parse'd above)
    r = subprocess.run(["git", "push", "origin", f"{commit_sha}:main"], capture_output=True)
    if r.returncode == 0:
        print(f"[push] OK {commit_sha[:9]}")
        break
    print(f"[push] attempt {attempt} rejected: {r.stderr.decode(errors='replace')[:200]} -- rebuild on new parent")
else:
    sys.exit("push failed after 3 attempts")

git("fetch", "origin")
new_origin = git("rev-parse", "origin/main").decode().strip()
assert new_origin == commit_sha, f"origin/main {new_origin[:9]} != pushed {commit_sha[:9]}"
# delivery verification: ls-tree key payloads (r310 completeness face)
for p in [UNION_PATH, "results/p2cal_ext/n1_w48/shard-11-of-12.json",
          "results/perpetual_faces/n1_w47_results.json"]:
    out = git("ls-tree", "origin/main", p).decode()
    assert out.strip(), f"DELIVERY MISS: {p}"
    print(f"[ls-tree] {p}: delivered")
n = git("ls-tree", "--name-only", "origin/main", "results/p2cal_ext/n1_w48/").decode()
print(f"[W48 shards on origin] {len([l for l in n.splitlines() if l.strip()])} files")
print("SURGICAL_OK", commit_sha)
