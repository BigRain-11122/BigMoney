"""r558 bm-a surgical push of the W48 finalize commit (origin hot-window CAS retry).

Payload = my commit's changed files (vs HEAD^) staged onto freshest origin/main
tree. Deletion-set empty by construction; payload count asserted; retry loop
rebuilds parent each fetch (blobs immutable, rebuild ~1s).
"""
import subprocess, os, tempfile, sys

def git(*a, **kw):
    r = subprocess.run(["git"] + list(a), capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {a[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:200]}")
    return r.stdout

def genv(env, *a, **kw):
    e = dict(os.environ); e.update(env)
    r = subprocess.run(["git"] + list(a), capture_output=True, env=e, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"git {a[:3]} rc={r.returncode}: {r.stderr.decode(errors='replace')[:200]}")
    return r.stdout

mine_head = git("rev-parse", "HEAD").decode().strip()
base = git("rev-parse", "HEAD^").decode().strip()
files = [l for l in git("diff", "--name-only", base, mine_head).decode().splitlines() if l.strip()]
print(f"[payload] {len(files)} files from {mine_head[:9]}")
blobs = {p: git("show", f"{mine_head}:{p}") for p in files}

for attempt in range(1, 8):
    git("fetch", "origin")
    parent = git("rev-parse", "origin/main").decode().strip()
    idx = os.path.join(tempfile.gettempdir(), f"r558cas_idx_{os.getpid()}")
    env = {"GIT_INDEX_FILE": idx}
    genv(env, "read-tree", parent)
    for p, b in blobs.items():
        h = git("hash-object", "-w", "--stdin", input=b).decode().strip()
        genv(env, "update-index", "--add", "--cacheinfo", f"100644,{h},{p}")
    tree = genv(env, "write-tree").decode().strip()
    os.remove(idx)
    st = git("diff", "--name-status", parent, tree).decode()
    lines = [l for l in st.splitlines() if l.strip()]
    assert len(lines) == len(files) and not any(l.startswith("D") for l in lines), f"assert: {lines}"
    msg = os.path.join(tempfile.gettempdir(), f"r558cas_{os.getpid()}.txt")
    with open(msg, "w", encoding="utf-8", newline="\n") as f:
        f.write(git("log", "--format=%B", "-1", mine_head).decode())
    sha = git("commit-tree", tree, "-p", parent, "-F", msg).decode().strip()
    os.remove(msg)
    r = subprocess.run(["git", "push", "origin", f"{sha}:main"], capture_output=True)
    print(f"[attempt {attempt}] parent={parent[:9]} -> {sha[:9]}: {'OK' if r.returncode==0 else r.stderr.decode(errors='replace')[:90]}")
    if r.returncode == 0:
        git("fetch", "origin")
        o = git("rev-parse", "origin/main").decode().strip()
        assert o == sha
        for p in files:
            assert git("ls-tree", "origin/main", p).decode().strip(), f"DELIVERY MISS {p}"
        print("CAS_PUSH_OK", sha)
        print("LOCAL_RESYNC_NEEDED from", mine_head[:9])
        sys.exit(0)
sys.exit("CAS push failed 7 attempts")
