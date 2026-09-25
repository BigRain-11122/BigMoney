# SHARD-2 done-flip (r180 dual-flip) + three-way verification, r201 bm-b
# runner pid 14112 (tick 20:00:01 launch) exited observed ~20:09; ckpt 196/196 done
import json, os, datetime

POOL = "results/runnable_pool.json"
pool = json.load(open(POOL, encoding="utf-8-sig"))
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
art_ts = datetime.datetime.fromtimestamp(
    os.path.getmtime("results/wild_route/checkpoint-2of8.jsonl")).strftime("%Y-%m-%d %H:%M:%S")

# three-way verification first
keys = set()
for line in open("results/wild_route/checkpoint-2of8.jsonl", encoding="utf-8"):
    line = line.strip()
    if line:
        r = json.loads(line)
        assert r["done"] is True
        keys.add(r["key"])
files = set(f[:-5] for f in os.listdir("results/wild_route/cells") if f.endswith(".json"))
expect = {k.replace("|", "_") for k in keys}
assert expect <= files, sorted(expect - files)[:3]
assert len(keys) == 196, len(keys)
print("three-way OK: 196 ckpt keys all done:true, all files present; ckpt mtime", art_ts)

for e in pool["entries"]:
    if e["id"] == "WILD-S1-SHARD-2":
        assert e["status"] == "ready", e["status"]
        e["status"] = "done"
        e["done_at"] = now
        e["done_note"] = ("196/196 cells complete: ckpt-2of8 196 unique keys all done:true, "
                          "196 cell files on disk (three-way verified r201); runner pid 14112 "
                          "(tick 20:00:01 launch) exited by 20:09, ~8min burn; ckpt artifact "
                          "mtime " + art_ts +
                          " (r62 law); dual-burn disclosure: bm-a launched same shard 19:30:02/"
                          "19:40:02 during my mid-rebase no-push window (r159 pull-lag face), "
                          "deterministic recompute zero scientific impact")
        for sh in e["shards"]:
            assert sh["key"] == "wr-2of8"
            assert sh["owner"] == "bm-b"
            sh["status"] = "done"
        break
else:
    raise SystemExit("SHARD-2 entry not found")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "WILD-S1-SHARD-2"][0]
print("flip OK:", e2["status"], e2["done_at"], "| shard:", e2["shards"][0]["status"])
