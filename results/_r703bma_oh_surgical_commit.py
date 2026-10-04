# r703 bm-a: surgical commit of OH-20261005-bigmoney.md to group repo
# Law: 外科提交净路 (2026-09-30 19:01) -- temp index, zero worktree touch, pure FF push
import subprocess, os, sys

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
SRC = os.path.join(os.getcwd(), "results", "_r703bma_OH-20261005-bigmoney.md")
DST = "cph4/oss-harvest/OH-20261005-bigmoney.md"
IDX = os.path.join(GRP, ".git", "surgical_index_r703bma")

env = dict(os.environ)
env["GIT_INDEX_FILE"] = IDX
if os.path.exists(IDX):
    os.remove(IDX)

def g(args, inp=None):
    r = subprocess.run(["git", "-C", GRP] + args, capture_output=True, env=env, input=inp)
    if r.returncode != 0:
        print("FAIL:", args, r.stderr.decode("utf-8", errors="replace")[:400])
        sys.exit(1)
    return r.stdout.decode("utf-8", errors="replace").strip()

# 1. re-fetch to guarantee tip
subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
tip = subprocess.run(["git", "-C", GRP, "rev-parse", "origin/main"], capture_output=True, text=True).stdout.strip()
print("origin tip:", tip)

# 2. temp index from tip
g(["read-tree", tip])

# 3. hash the file (w writes blob into group odb)
sha = g(["hash-object", "-w", SRC])
print("blob:", sha)

# 4. stage at destination path (--add required for new path per git update-index contract)
g(["update-index", "--add", "--cacheinfo", f"100644,{sha},{DST}"])

# 5. tree + commit
tree = g(["write-tree"])
print("tree:", tree)
msg = ("OSS harvest slice OH-20261005-bigmoney (D-20261005-05(1) receipt window) -- "
       "bigmoney license-gate debt closure: polars MIT verified (39.9k stars, pushed 10-04) cleared-for-adoption; "
       "vectorbt Apache-2.0+Commons-Clause original-text verified (internal-use legal, no-sell clause not touched, "
       "dep stays parked); pandas-ta upstream 404-dead honest negative -> successor xgboosted/pandas-ta-classic MIT "
       "retarget for shortline research corpus. Anti-dup 3-face zero-hit. Real-search face 6 API reads. "
       "Zero new adoption (O-1750 needs-based). Receipt: D-20261005-05(1) [via bm-a r703]")
commit = subprocess.run(["git", "-C", GRP, "commit-tree", tree, "-p", tip],
                        capture_output=True, env=env, input=msg.encode("utf-8"))
csha = commit.stdout.decode("utf-8", errors="replace").strip()
if not csha:
    print("commit-tree FAIL:", commit.stderr.decode("utf-8", errors="replace")[:400])
    sys.exit(1)
print("commit:", csha)

# 6. push pure FF (remote name required -- bare refspec is parsed as host:path)
r = subprocess.run(["git", "-C", GRP, "push", "origin", f"{csha}:refs/heads/main"], capture_output=True, env=env)
print("push rc:", r.returncode)
print("push out:", (r.stdout + r.stderr).decode("utf-8", errors="replace")[:400])
sys.exit(0 if r.returncode == 0 else 2)
