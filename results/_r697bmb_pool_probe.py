"""r697 bm-b: pool state probe (structure-first per r675bmb key-posit law)."""
import json

p = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in p.get("entries", []):
    k = e.get("key") or e.get("id") or "?"
    st = e.get("status")
    shards = e.get("shards", [])
    if not shards:
        print(f"{k} | {st} | (no shards)")
        continue
    row = ", ".join(
        "%s:%s:%s" % (s.get("shard_id") or s.get("key", "?"),
                      s.get("status"),
                      (s.get("owner") or "").strip() or "-")
        for s in shards)
    print(f"{k} | {st} | {row}")
