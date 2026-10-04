"""r665: dump pool active entries full key view."""
import json, io

d = json.load(io.open("results/runnable_pool.json", encoding="utf-8"))
es = d["entries"]
act = [e for e in es if e.get("status") not in ("done", "cancelled")]
print("active:", len(act))
for e in act:
    print(json.dumps({k: e[k] for k in e if k in (
        "id", "name", "batch_name", "status", "priority", "lane", "lane_owner",
        "waiting_on", "ram_gate", "created_at", "updated_at", "shards", "shard_status",
        "claimed_by", "claim_ts", "audit", "note", "flip_gates", "deps", "family")},
        ensure_ascii=False, default=str)[:1400])
    print("---")
