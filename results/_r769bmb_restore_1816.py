# _r769bmb_restore_1816.py -- restore 3ed8cb8cc's null|1816 row into fund_value nulls
# (rebase replay reset the worktree to pick-1 lineage which lacked it; daemon appended 1817+ after,
#  leaving a permanent key gap unless restored; row bytes = authentic committed burn result, zero re-burn cost)
import subprocess, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "results/fund_value_p1/nulls.jsonl"

b = subprocess.run(["git", "show", "stash@{0}:" + P], capture_output=True, cwd=REPO).stdout
rows1816 = [l for l in b.decode("utf-8").splitlines() if '"null|1816"' in l]
assert len(rows1816) == 1, f"expected exactly one null|1816 row in stash tree, got {len(rows1816)}"
row = json.loads(rows1816[0])
assert row["key"] == "null|1816" and row["k"] == 1816

disk_b = open(os.path.join(REPO, P), "rb").read()
lines = [l for l in disk_b.decode("utf-8").split("\n") if l.strip()]
keys = [json.loads(l)["k"] for l in lines]
if 1816 in keys:
    print("null|1816 already present; no-op")
    sys.exit(0)
assert 1816 not in keys, "invariant"
# insert k-sorted (append-only ledger, k monotone in file order)
idx = len(lines)
for i, k in enumerate(keys):
    if k > 1816:
        idx = i
        break
lines.insert(idx, json.dumps(row, sort_keys=True, ensure_ascii=False))
open(os.path.join(REPO, P), "wb").write(("\n".join(lines) + "\n").encode("utf-8"))

# post-verify (daemon may append concurrently; only assert our key landed and count grew)
after = open(os.path.join(REPO, P), "rb").read().decode("utf-8")
ak = [json.loads(l)["k"] for l in after.split("\n") if l.strip()]
assert 1816 in ak, "restore failed"
assert len(ak) >= len(keys) + 1, "row-count regression"
print(json.dumps({"restored": "null|1816", "k_pos": ak.index(1816), "rows_after": len(ak),
                  "row": rows1816[0][:160]}))
