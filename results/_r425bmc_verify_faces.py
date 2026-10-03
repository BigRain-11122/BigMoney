import json
os_pool = "results/runnable_pool.json"
pool = json.load(open(os_pool, encoding="utf-8"))
ents = pool["entries"] if isinstance(pool, dict) else pool
for e in ents:
    if str(e.get("id", "")).startswith("MASS-TRIAL-W2-JUDGE-SHARD"):
        s = e["shards"][0]
        print("%s entry=%s done_by=%s done_at=%s | shard=%s owner=%s owner_since=%s done_at=%s harvested=%s"
              % (e["id"], e.get("status"), e.get("done_by"), e.get("done_at"),
                 s.get("status"), s.get("owner"), s.get("owner_since"), s.get("done_at"), s.get("harvested_by")))
print("total entries:", len(ents))
# ckpt1 progress
import os
f = "results/mass_trial/w2_judge_shard_1of4.jsonl"
if os.path.exists(f):
    n = sum(1 for _ in open(f, encoding="utf-8"))
    print("shard1 local ckpt rows:", n)
