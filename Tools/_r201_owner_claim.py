# r201: generic shard owner claim (r199 two-line law: owner+owner_since real clock)
# usage: python Tools/_r201_owner_claim.py <ENTRY_ID> <SHARD_KEY>
import json, sys, time

eid, skey = sys.argv[1], sys.argv[2]
p = "results/runnable_pool.json"
pool = json.load(open(p, encoding="utf-8"))
now = time.strftime("%Y-%m-%d %H:%M:%S")
hit = 0
for e in pool.get("entries", []):
    if e.get("id") == eid:
        for s in e["shards"]:
            if s["key"] == skey:
                s["owner"] = "bm-b"
                s["owner_since"] = now
                hit += 1
assert hit == 1, f"expected exactly 1 shard, hit={hit}"
pool["updated_at"] = now
out = json.dumps(pool, ensure_ascii=False, indent=1)
json.loads(out)  # validate before write (r185)
open(p, "w", encoding="utf-8").write(out)
print("owner claim:", now, skey, "-> bm-b")
