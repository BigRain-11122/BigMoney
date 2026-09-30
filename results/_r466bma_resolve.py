"""r466 bm-a rebase conflict resolver (append-log union, r188/r244 blob-rebuild law).

Conflict: results/paper/marks/marks-20260930.jsonl UU during S0 pull --rebase
(origin=3cc1267be bm-c r262 chain vs local sidecar f68414785).
Recipe: append-log (*.jsonl) -> line-level union zero-loss.
Stages per r351 directional law: :2: = origin side, :3: = local side.
"""
import subprocess, sys, json

PATH = "results/paper/marks/marks-20260930.jsonl"

def blob(stage: str) -> bytes:
    out = subprocess.run(
        ["git", "show", f":{stage}:{PATH}"],
        capture_output=True,
    )
    if out.returncode != 0:
        sys.exit(f"git show :{stage}: failed: {out.stderr!r}")
    return out.stdout

origin_lines = blob(2).splitlines()
local_lines = blob(3).splitlines()

# line-level union, order-preserving: origin first, then local-only additions
seen = set()
union = []
dup_content = 0
for ln in origin_lines + local_lines:
    if ln in seen:
        dup_content += 1
        continue
    seen.add(ln)
    union.append(ln)

# parse-verify every line before writeback (r185 law)
for ln in union:
    json.loads(ln)

with open(PATH, "wb") as f:
    f.write(b"\n".join(union) + b"\n")

print(f"origin={len(origin_lines)} local={len(local_lines)} union={len(union)} dup_exact_lines={dup_content}")
assert len(union) == len(set(origin_lines + local_lines)), "union zero-loss assertion failed"
print("RESOLVED zero-loss, all lines json-valid")
