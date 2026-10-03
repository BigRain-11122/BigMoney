# r414 bm-c: pool ready-unclaimed identity probe v2 (schema: id/lane_owner/status/shards[].key)
import json

d = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/results/runnable_pool.json",
                   encoding="utf-8"))
flagged = 0
for e in d.get("entries", []):
    eid = str(e.get("id", ""))
    st = e.get("status")
    owner = e.get("owner") or e.get("claimed_by") or e.get("workers_plan")
    shards = e.get("shards") or []
    shard_info = []
    for s in shards:
        shard_info.append("%s:%s%s" % (
            s.get("key", "?"), s.get("status", "?"),
            "@" + str(s.get("owner")) if s.get("owner") else ""))
    if st == "ready" and not owner:
        print("ENTRY-READY-UNCLAIMED", eid, "| lane_owner:", e.get("lane_owner"),
              "| prio:", e.get("priority"), "| shards:", shard_info)
        flagged += 1
    elif st == "ready":
        print("ENTRY-READY-OWNED  ", eid, "| workers_plan:", str(owner)[:80],
              "| lane_owner:", e.get("lane_owner"))
print("total_ready_unclaimed:", flagged)
