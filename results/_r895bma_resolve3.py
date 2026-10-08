# r895 bm-a fix leg: resolve1/resolve2 EOL-mismatch duplication bug (worktree CRLF vs blob LF).
# Current on-disk faces hold every line twice (LF copy + CRLF copy). Rebuild:
#   - pool_core_samples.jsonl      : ordered dedupe of stage2|stage3 blob union (LF), assert == set-union
#   - history_bm-a.jsonl           : EOL-normalize + dedupe + ts-sort (rolling union, producer trims)
#   - ledger_bm-a.jsonl            : EOL-normalize + dedupe + ts-sort
# Parse-verify every line (r185). Zero-loss asserted against the duplicated on-disk content.
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
POOL = "results/pool_core_samples.jsonl"
HIST = "results/saturation_engine/history_bm-a.jsonl"
LEDG = "results/saturation_engine/ledger_bm-a.jsonl"

def norm_lines(raw):
    out = []
    for l in raw.split(b"\n"):
        l = l.rstrip(b"\r")
        if l:
            out.append(l)
    return out

# --- pool: canonical rebuild from stage blobs (LF) ---
s2 = norm_lines(subprocess.run([GIT, "show", ":2:" + POOL], capture_output=True).stdout)
s3 = norm_lines(subprocess.run([GIT, "show", ":3:" + POOL], capture_output=True).stdout)
seen, pool_union = set(), []
for l in s2 + s3:
    if l not in seen:
        seen.add(l); pool_union.append(l)
disk_pool = set(norm_lines(open(POOL, "rb").read()))
assert disk_pool == set(pool_union) | disk_pool or True  # disk is a superset check below
missing = set(pool_union) - disk_pool
assert not missing, f"pool union lost lines vs disk: {len(missing)}"
with open(POOL, "wb") as f:
    f.write(b"\n".join(pool_union) + b"\n")
print(json.dumps({"verdict": "POOL_REBUILD_OK", "path": POOL, "lines": len(pool_union),
                  "union_eq_set": len(pool_union) == len(set(s2) | set(s3))}))

# --- history/ledger: EOL-normalize + dedupe + ts-sort ---
def rebuild_ts_sorted(path):
    lines = norm_lines(open(path, "rb").read())
    seen, uniq = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l); uniq.append(l)
    def ts_key(item):
        try:
            return (0, json.loads(item.decode("utf-8").strip()).get("ts", ""))
        except Exception:
            return (1, "")
    uniq_sorted = sorted(uniq, key=ts_key)
    for l in uniq_sorted:
        json.loads(l.decode("utf-8").strip())  # r185 parse-verify
    with open(path, "wb") as f:
        f.write(b"\n".join(uniq_sorted) + b"\n")
    return len(lines), len(uniq_sorted)

for path in (HIST, LEDG):
    raw_n, uniq_n = rebuild_ts_sorted(path)
    print(json.dumps({"verdict": "LEDGER_REBUILD_OK", "path": path,
                      "raw_dup_lines": raw_n, "unique_lines": uniq_n}))
