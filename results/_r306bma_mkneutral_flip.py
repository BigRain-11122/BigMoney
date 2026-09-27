# r306 bm-a: done-flip CN-MKTNEUTRAL-P1 (r302 law: flip FIRST, before any
# artifact analysis -- next autofill tick would re-burn the completed batch
# since the runner never edits the pool; single-writer = control plane).
import json
import os

POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "results", "runnable_pool.json")
RESULT = "results/cn_mkneutral/p1_results.json"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

flipped = []
for e in pool.get("entries", []):
    if e.get("id") != "CN-MKTNEUTRAL-P1":
        continue
    assert e.get("status") == "ready", f"unexpected status {e.get('status')}"
    assert os.path.isfile(os.path.join(os.path.dirname(POOL), "..", RESULT)), \
        "terminal marker p1_results.json missing -- refuse flip"
    e["status"] = "done"
    e["result_ref"] = RESULT
    for sh in e.get("shards", []):
        sh["status"] = "done"
        sh["result_ref"] = RESULT
    flipped.append(e["id"])

assert flipped == ["CN-MKTNEUTRAL-P1"], f"flip target mismatch: {flipped}"
pool["updated_at"] = "2026-09-27 08:48:00"
tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(pool, fh, indent=1)
os.replace(tmp, POOL)

check = json.load(open(POOL, encoding="utf-8"))
e = [x for x in check["entries"] if x["id"] == "CN-MKTNEUTRAL-P1"][0]
print("FLIPPED", e["id"], "status:", e["status"],
      "shard:", e["shards"][0]["status"], "result_ref:", e["result_ref"])
