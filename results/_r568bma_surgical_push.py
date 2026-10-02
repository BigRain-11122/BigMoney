# r568 surgical push (r341 third-rejection escalation; r530 hardened template):
# diff-based payload staging onto latest origin/main + deletion-set assertion +
# payload-count assertion + post-push ls-tree delivery self-check.
import subprocess, sys, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TMP_IDX = os.path.join(REPO, r".git\_r568bma_tmp_index")

def git(args, extra_env=None, check=True):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        print("GIT FAIL:", args, r.stdout, r.stderr)
        sys.exit(1)
    return r

git(["fetch", "origin"])
base = git(["rev-parse", "origin/main"]).stdout.strip()
head = git(["rev-parse", "HEAD"]).stdout.strip()
print("base:", base, "head:", head)

# payload = full delta origin/main -> HEAD
ns = git(["diff", "--name-status", base, head]).stdout.strip().splitlines()
payload = {}
dels = []
for line in ns:
    st, path = line.split("\t", 1)
    if st.startswith("D"):
        dels.append(path)
    else:
        payload[path] = st
print("payload files:", len(payload), "deletions:", len(dels), dels[:5])

# deletion-set assertion: r525/r519 family guard -- D face must be empty here
# (yield closeout retained bm-b files; no deliberate deletions this window).
if dels:
    print("ABORT: unexpected deletion set:", dels)
    sys.exit(2)

# build surgical tree: read-tree base, overlay payload blobs from HEAD
env = {"GIT_INDEX_FILE": TMP_IDX}
git(["read-tree", base], extra_env=env)
# batch update-index via ls-tree piped: build cacheinfo lines from HEAD
ls = git(["ls-tree", "head", "-r", "--full-name", "--", *payload.keys()] if len(payload) < 200 else ["ls-tree", "head", "-r", "--full-name"])
entries = {}
for line in ls.stdout.strip().splitlines():
    meta, path = line.split("\t", 1)
    entries[path] = meta  # "mode type sha"

missing = [p for p in payload if p not in entries]
if missing:
    print("ABORT: payload paths not found in HEAD tree:", missing[:5])
    sys.exit(3)
print("payload coverage: all", len(payload), "paths resolved in HEAD tree")

update_input = "\n".join(f"{entries[p]}\t{p}" for p in payload)
r = subprocess.run(["git", "-C", REPO, "update-index", "--index-info"], input=update_input, capture_output=True, text=True,
                   env={**os.environ, "GIT_INDEX_FILE": TMP_IDX}, encoding="utf-8")
if r.returncode != 0:
    print("update-index FAIL:", r.stdout, r.stderr)
    sys.exit(4)

tree = git(["write-tree"], extra_env=env).stdout.strip()
msg = ("r568 surgical push: rebased r567 chain delivery (W64 shard-4..11 products + W65 yield closeout + "
       "r567/r568 rides + W64 finalize product pending separate closeout commit) onto " + base[:9])
new_sha = git(["commit-tree", tree, "-p", base, "-m", msg]).stdout.strip()
print("surgical commit:", new_sha)

# payload-count assertion on the surgical tree vs base (r343: index vs tree with --cached)
r = git(["diff-index", "--cached", "--name-only", base], extra_env=env)
n = len([l for l in r.stdout.strip().splitlines() if l.strip()])
print("surgical tree diff count:", n, "(payload", len(payload), ")")
if n != len(payload):
    print("ABORT: surgical tree payload count mismatch")
    sys.exit(5)

# push with explicit remote name (r559)
pr = git(["push", "origin", new_sha + ":main"], check=False)
print("push rc:", pr.returncode)
print(pr.stdout[-500:] if pr.stdout else "", pr.stderr[-500:] if pr.stderr else "")
