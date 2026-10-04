# r683 (bm-b) pre-push pool semantic verify: W3-JUDGE 4/4 done after three-way merge
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"), encoding="utf-8"))
w3 = {e["id"]: e for e in pool["entries"] if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
assert set(w3) == {"MASS-TRIAL-W3-JUDGE-SHARD-%d" % i for i in range(4)}, sorted(w3)
for i in range(4):
    e = w3["MASS-TRIAL-W3-JUDGE-SHARD-%d" % i]
    s = e["shards"][0]
    assert e["status"] == "done", (e["id"], e["status"])
    assert s["status"] == "done", (e["id"], s["status"])
    assert s.get("done_at"), (e["id"], "no done_at")
    print("SHARD-%d done owner=%s done_at=%s" % (i, s.get("owner"), s.get("done_at")))
# our flip semantics preserved (r474 pusher-side re-check)
s1 = w3["MASS-TRIAL-W3-JUDGE-SHARD-1"]["shards"][0]
assert s1["owner"] == "bm-b" and s1.get("harvested_by") == "bm-b", s1
print("shard-1 bm-b flip semantics preserved")
print("POOL_VERIFY_PASS")
