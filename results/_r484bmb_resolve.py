"""r484 bm-b rebase conflict resolver: results/crash_fuse.json (UU).

Both sides are machine-written fuse ledgers (bm-a origin sweep vs bm-b
local sweep). Structure = {"sigs": {runner_key: fuse_row}, "cleared": {...}}.
Canonical zero-loss resolution per bigmoney-conflict-resolve SKILL
(rolling-ledger family): NESTED FULL UNION -- merged.sigs keeps every
runner key of both stage blobs; provably-dead rows (stale code_sha /
completed burns) are left for the machinery's own stale-sha sweeper,
zero semantic judgment here. Same-key collisions keep the newer ts.
"""
import json
import subprocess
import sys

PATH = "results/crash_fuse.json"


def _stage(n: int) -> dict:
    b = subprocess.check_output(["git", "show", f":{n}:{PATH}"])
    return json.loads(b.decode("utf-8"))


def _ts(row: dict) -> str:
    return str(row.get("last_crash_ts", "")) + str(row.get("last_refusal_ts", ""))


ours = _stage(2)      # HEAD (origin main latest)
theirs = _stage(3)    # f1f473f91 (bm-b runtime sync)
merged = {}
for top in set(ours) | set(theirs):
    a, b = ours.get(top, {}), theirs.get(top, {})
    if not isinstance(a, dict) or not isinstance(b, dict):
        merged[top] = b if top not in ours else a
        continue
    m = dict(a)
    for k, v in b.items():
        if k in m:
            if m[k] != v:
                print(f"key collision {top}.{k!r}: keep "
                      f"{'theirs' if _ts(v) > _ts(m[k]) else 'ours'}")
                if _ts(v) > _ts(m[k]):
                    m[k] = v
        else:
            m[k] = v
    merged[top] = m
na = sum(len(v) for v in ours.values() if isinstance(v, dict))
nb = sum(len(v) for v in theirs.values() if isinstance(v, dict))
nm = sum(len(v) for v in merged.values() if isinstance(v, dict))
print(f"union: ours_rows={na} theirs_rows={nb} merged_rows={nm}")
assert nm >= max(na, nb), "zero-loss union contract"
for src in (ours, theirs):
    for top, d in src.items():
        if isinstance(d, dict):
            for k in d:
                assert k in merged[top], f"lost {top}.{k}"
raw = json.dumps(merged, ensure_ascii=False, indent=1)
if "\r\n" in subprocess.check_output(["git", "show", f":2:{PATH}"]).decode("utf-8", "replace"):
    raw = raw.replace("\n", "\r\n")
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(raw)
json.load(open(PATH, encoding="utf-8"))
print("resolved + parse-verified")
sys.exit(0)
