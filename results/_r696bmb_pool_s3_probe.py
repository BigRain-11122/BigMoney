"""r696 bm-b: pool SHARD-3 truth probe (working tree + origin tip + history)."""
import json
import subprocess

doc = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for eid in ("PERPETUAL-N2-W15-SHARD-3", "PERPETUAL-N2-W15-SHARD-4"):
    e = [x for x in doc["entries"] if x.get("id") == eid]
    if e:
        print(eid, "->", json.dumps(e[0].get("shards"), ensure_ascii=False)[:400])
    else:
        print(eid, "-> MISSING entry")

r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                   capture_output=True)
odoc = json.loads(r.stdout.decode("utf-8"))
e3 = [x for x in odoc["entries"] if x.get("id") == "PERPETUAL-N2-W15-SHARD-3"]
print("ORIGIN SHARD-3:", json.dumps(e3[0].get("shards"), ensure_ascii=False)[:400] if e3 else "MISSING")

h = subprocess.run(["git", "log", "--oneline", "-8", "--", "results/runnable_pool.json"],
                   capture_output=True)
print("POOL HISTORY (top8):")
print(h.stdout.decode("utf-8", "replace"))
