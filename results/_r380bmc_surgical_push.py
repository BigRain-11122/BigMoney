# -*- coding: utf-8 -*-
# r380 bm-c surgical CAS push (r523/r532 law: live-writer faces present -> no rebase; r585: payload blobs from MY COMMIT)
import subprocess, os

CWD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
MY = "1801e570c"
PAYLOAD = ["CODELY.md", "research/pit-data.md", "fleet/tasks/T-2026-10-02-144-P1.json"]

def git(*a, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(["git"] + list(a), cwd=CWD, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", creationflags=CNW, env=env)

def q(r, what):
    assert r.returncode == 0, f"{what} rc={r.returncode}: {r.stderr[:300]}"
    return r.stdout.strip()

base = q(git("rev-parse", "origin/main"), "resolve origin/main")
print("origin/main:", base)

# 1. my commit's blobs (r585 law: ls-tree from MY COMMIT, explicit column slicing per r366)
r = git("ls-tree", MY, "--", *PAYLOAD)
assert r.returncode == 0, r.stderr
entries = {}
for line in r.stdout.strip().splitlines():
    meta, path = line.split("\t", 1)
    parts = meta.split(" ")  # mode SP type SP sha
    assert len(parts) == 3, f"column parse: {line!r}"
    entries[path] = (parts[0], parts[2])
assert set(entries) == set(PAYLOAD), f"missing blobs: {set(PAYLOAD) ^ set(entries)}"
print("my blobs:", {p: s[:12] for p, (m, s) in entries.items()})

# 2. temp index from origin/main tree
idx = os.path.join(CWD, ".git", "surgindex_r380")
if os.path.exists(idx):
    os.remove(idx)
env = {"GIT_INDEX_FILE": idx}
q(git("read-tree", base, env_extra=env), "read-tree")
for p, (mode, sha) in entries.items():
    q(git("update-index", "--add", "--cacheinfo", f"{mode},{sha},{p}", env_extra=env), f"update-index {p}")
tree = q(git("write-tree", env_extra=env), "write-tree")
print("tree:", tree)

# 3. three assertions (r366/r374 law): deletion-set EMPTY x2 + tree-delta == payload
r = git("diff-tree", "--name-status", "-r", "--no-renames", base, tree)
assert r.returncode == 0
delta = [l for l in r.stdout.strip().splitlines() if l.strip()]
print("tree-delta vs origin:")
for l in delta:
    print("  ", l)
assert all(l.startswith("M\t") or l.startswith("A\t") for l in delta), f"non-M/A in delta: {delta}"
assert sorted(l.split("\t")[1] for l in delta) == sorted(PAYLOAD), f"delta != payload: {delta}"
r2 = git("diff-tree", "--diff-filter=D", "--name-only", "-r", base, tree)
assert r2.returncode == 0 and not r2.stdout.strip(), f"DELETION SET NON-EMPTY: {r2.stdout}"
print("deletion-set: EMPTY (x2 asserted)")

# 4. commit-tree on origin head + CAS push
commit = q(git("commit-tree", tree, "-p", base, "-F",
               r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\_r380bmc_msg.txt"), "commit-tree")
print("surgical commit:", commit)
r = git("push", "origin", f"{commit}:refs/heads/main")
print("push rc:", r.returncode)
print((r.stdout or "")[:300])
print((r.stderr or "")[:300])
if r.returncode == 0:
    # 5. local realign (r578: reset --mixed + faceted checkout; live-writer faces preserved)
    q(git("reset", "--mixed", commit), "reset --mixed")
    st = git("status", "--porcelain").stdout
    print("post-realign status:")
    print(st)
    os.remove(idx)
    print("SURGICAL PUSH OK:", commit)
