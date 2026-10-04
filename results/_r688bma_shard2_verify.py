"""r688 bm-a S3c: verify shard-2 output completeness (interleaved i%4==2, 194 cells) + origin pool face state.

Laws: r482/r685 (id-dup probe before finalize), r483 (fetch+origin check before flip),
r678 (pool json surgical line edit, no load-dump), r474 (no owner_since regression on push).
"""
import json
import subprocess

# --- 1. output completeness ---
lines = open("results/mass_trial/w3_judge_shard_2of4.jsonl", encoding="utf-8", errors="replace").read().strip().split("\n")
rows = [json.loads(l) for l in lines]
idx = sorted(r["i"] for r in rows)
uniq_i = sorted(set(idx))
expect = list(range(2, 777, 4))
print("rows:", len(rows), "unique-i:", len(uniq_i))
print("i-set == expected interleaved 2,6..774:", uniq_i == expect)
# dup id probe (r482): candidate_id uniqueness
cids = [r["candidate_id"] for r in rows]
print("candidate_id unique:", len(set(cids)) == len(cids), "n:", len(cids))
# judge completeness: key fields present and non-null on all rows
missing = []
for r in rows:
    for k in ("dual_nulls", "sample_sufficient", "legs", "n_eff_start_windows"):
        if k not in r:
            missing.append((r["candidate_id"], k))
print("rows missing key fields:", len(missing))
# dup full-row bytes (byte-identical duplicates)
seen = set()
dups = 0
for l in lines:
    if l in seen:
        dups += 1
    seen.add(l)
print("byte-dup rows:", dups)

# --- 2. origin pool face for the 4 shards (fresh fetch) ---
subprocess.run(["git", "fetch", "origin"], capture_output=True)
blob = subprocess.run(
    ["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True
).stdout
opool = json.loads(blob.decode("utf-8"))
for e in opool.get("entries", []):
    if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE-SHARD"):
        print(
            "ORIGIN:", e.get("id"), "| status:", e.get("status"),
            "| owner:", e.get("owner"), "| since:", e.get("owner_since"),
            "| done_at:", e.get("done_at"),
        )
