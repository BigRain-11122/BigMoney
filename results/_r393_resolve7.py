"""r393 resolve #7: third-rebase stop #2 (commit af141b76, my round-391) -- 3 files.

  CODELY.md        memory-union (R208/r212): byte-prefix assert + concat.
  T-107 ticket     no claim collision (both=bm-c r174 16:33:39) -> plain
                   dict union: keep both progress keys (origin
                   progress_r391b + mine progress_r175_bmc).
  token_usage.json snapshot take-new by top-level 'generated' (R216).
"""
import json
import subprocess


def blob_bytes(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout


# ---- CODELY.md memory-union ----
P = "CODELY.md"
base, a, b = blob_bytes(1, P), blob_bytes(2, P), blob_bytes(3, P)
assert a.startswith(base), "CODELY ours not base+append"
assert b.startswith(base), "CODELY theirs not base+append"
merged = base + a[len(base):] + b[len(base):]
open(P, "wb").write(merged)
print(f"CODELY.md: {len(base)}+{len(a)-len(base)}+{len(b)-len(base)}"
      f" -> {len(merged)}B")

# ---- T-107 ticket dict union ----
P = "fleet/tasks/T-2026-09-28-107-P0.json"
A, B = json.loads(blob_bytes(2, P)), json.loads(blob_bytes(3, P))
assert A.get("claimed_by") == B.get("claimed_by"), "claim drift!"
merged_t = dict(A)
for k, v in B.items():
    if k not in merged_t:
        merged_t[k] = v
json.loads(json.dumps(merged_t))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged_t, ensure_ascii=False, indent=2))
print("T-107: dict union keys:", sorted(k for k in merged_t if k.startswith("progress")))

# ---- token_usage take-new ----
P = "results/token_usage.json"
A, B = json.loads(blob_bytes(2, P)), json.loads(blob_bytes(3, P))
ga, gb = A.get("generated", ""), B.get("generated", "")
newer = A if gb <= ga else B
open(P, "w", encoding="utf-8").write(json.dumps(
    newer, ensure_ascii=False, indent=1))
print(f"token_usage: take-new {'ours' if newer is A else 'theirs'}"
      f" ({ga} vs {gb})")
print("resolve7 done")
