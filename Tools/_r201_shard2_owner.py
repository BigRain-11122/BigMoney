# r201: SHARD-2 shard-level owner claim (r199 two-line law: owner+owner_since real clock)
# context: 20:00:01 tick launched WILD-S1-SHARD-2 (pid 14112 live) during the mid-rebase
# window without pool owner-write; bm-a launched same shard 19:40:02 with claim also not
# landed in origin (rebase race) -> write bm-b owner now, fresh owner_since, push-first.
import json, time

p = "results/runnable_pool.json"
with open(p, encoding="utf-8") as f:
    pool = json.load(f)

now = time.strftime("%Y-%m-%d %H:%M:%S")
hit = 0
for e in pool.get("entries", []):
    if e.get("id") == "WILD-S1-SHARD-2":
        s = e["shards"][0]
        assert s["key"] == "wr-2of8"
        s["owner"] = "bm-b"
        s["owner_since"] = now
        hit += 1
assert hit == 1, f"expected exactly 1 WILD-S1-SHARD-2 entry, hit={hit}"
pool["updated_at"] = now

out = json.dumps(pool, ensure_ascii=False, indent=1)
json.loads(out)  # validate before write (r185)
with open(p, "w", encoding="utf-8") as f:
    f.write(out)
print("owner claim:", now, "wr-2of8 -> bm-b (runner pid 14112 live)")
