"""r688 bm-a S3b: w3-judge pool ticket detail + shard-2 output completion state."""
import json

pool = json.load(open("results/runnable_pool.json", encoding="utf-8-sig"))
entries = pool.get("entries", [])
print("pool entries total:", len(entries))
w3j = [e for e in entries if "W3" in json.dumps(e) and "JUDGE" in json.dumps(e).upper()]
for e in w3j:
    keys = {k: e.get(k) for k in ("id", "shard", "status", "owner", "owner_since",
                                   "progress", "notes", "result_ref", "done_at") if k in e}
    print("ENTRY:", json.dumps(keys, ensure_ascii=False)[:400])

# shard-2 output tail
lines = open("results/mass_trial/w3_judge_shard_2of4.jsonl", encoding="utf-8", errors="replace").read().strip().split("\n")
print("\nshard-2 lines:", len(lines))
last = json.loads(lines[-1])
print("last line keys:", sorted(last.keys())[:15])
print("last line sample:", json.dumps({k: last[k] for k in list(last)[:8]}, ensure_ascii=False)[:300])
# check expected: 777 cells? count unique cell ids
try:
    ids = set()
    for l in lines:
        d = json.loads(l)
        cid = d.get("cand_id") or d.get("id") or d.get("cell") or d.get("k")
        ids.add(str(cid))
    print("unique ids in output:", len(ids))
except Exception as ex:
    print("id-count err:", ex)
