"""r457 bm-c pool probe2: status histogram + all non-done entries with shard ownership."""
import json

with open(r"results\runnable_pool.json", encoding="utf-8-sig") as fh:
    d = json.load(fh)
hist = {}
for e in d["entries"]:
    hist[e.get("status", "?")] = hist.get(e.get("status", "?"), 0) + 1
print("STATUS-HIST", json.dumps(hist, ensure_ascii=False))
print("POOL-UPDATED", d.get("updated_at"))
for e in d["entries"]:
    if e.get("status") in ("ready", "waiting", "running"):
        print("== %s status=%s lane=%s wc=%s" % (e.get("id"), e.get("status"),
              e.get("lane_owner", "?"), e.get("worker_class", "?")))
        for sh in e.get("shards", [])[:40]:
            print("   shard %s st=%s owner=%s since=%s" % (
                sh.get("key"), sh.get("status"), sh.get("owner"), sh.get("owner_since")))
