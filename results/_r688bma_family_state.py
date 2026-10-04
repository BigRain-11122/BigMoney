"""r688 bm-a S3l: check current local SHARD-0 face after mid-round merges."""
import json

t = open("results/runnable_pool.json", encoding="utf-8").read()
pool = json.loads(t)
for eid in ("MASS-TRIAL-W3-JUDGE-SHARD-0", "MASS-TRIAL-W3-JUDGE-SHARD-1",
            "MASS-TRIAL-W3-JUDGE-SHARD-2", "MASS-TRIAL-W3-JUDGE-SHARD-3"):
    e = [x for x in pool["entries"] if x.get("id") == eid][0]
    s0 = e["shards"][0]
    print(eid, "| entry:", e.get("status"), "| shard:", s0.get("status"),
          "| owner:", s0.get("owner"), "| since:", s0.get("owner_since"),
          "| done_at:", e.get("done_at"), "| shard.done_at:", s0.get("done_at"))
