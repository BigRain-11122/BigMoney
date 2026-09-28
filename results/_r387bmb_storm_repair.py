# r387 bm-b storm-repair: autofill 14:33 stale claim-refresh reverted shard
# status done->waiting on BOTH judge entries (done_at/result_ref/notes
# survived = dict-merge not whole-file replace). Checkpoints complete =
# zero science damage (relaunch would be idempotent zero-cell no-op).
# Re-assert status=done with checkpoint evidence gates, then IMMEDIATE
# commit+push (next autofill tick ~14:43 window).
import json, os, datetime

POOL = "results/runnable_pool.json"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ckpt_rows(p):
    n = 0
    with open(p, encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                n += 1
    return n

n_w1 = ckpt_rows(r"results\trial_labor_w1\checkpoint\judge_shard_0of1.jsonl")
n_w2 = ckpt_rows(r"results\trial_labor_w2\checkpoint\judge_shard_0of1.jsonl")
assert n_w1 == 149, n_w1
assert n_w2 >= 404, n_w2
print("checkpoint evidence: W1 =", n_w1, "rows / W2 =", n_w2, "rows")

pool = json.load(open(POOL, encoding="utf-8-sig"))
for e in pool["entries"]:
    if e["id"] == "TRIAL-LABOR-W1-JUDGE":
        sh = e["shards"][0]
        assert sh["status"] == "waiting", sh["status"]
        assert sh.get("done_at") == "2026-09-28 14:27:53", sh.get("done_at")
        assert "149/149" in sh.get("result_ref", ""), str(sh.get("result_ref"))[:80]
        sh["status"] = "done"
        sh["storm_repair"] = (
            "r387 storm-repair: autofill 14:33:33 stale claim-refresh "
            "reverted status done->waiting (dict-merge kept done_at/"
            "result_ref); re-asserted done same round, checkpoint 149/149 "
            "re-verified"
        )
    elif e["id"] == "TRIAL-LABOR-W2-JUDGE":
        sh = e["shards"][0]
        assert sh["status"] == "waiting", sh["status"]
        assert sh.get("done_at"), sh
        assert "404/404" in sh.get("result_ref", ""), str(sh.get("result_ref"))[:80]
        sh["status"] = "done"
        sh["storm_repair"] = (
            "r387 storm-repair: same 14:33:10 stale claim-refresh revert; "
            "re-asserted done same round, checkpoint >=404 rows re-verified "
            "(r386-cont original flip evidence retained in done_at/"
            "result_ref)"
        )
pool["updated_at"] = now

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

pool2 = json.load(open(POOL, encoding="utf-8-sig"))
for eid in ("TRIAL-LABOR-W1-JUDGE", "TRIAL-LABOR-W2-JUDGE"):
    e2 = [x for x in pool2["entries"] if x["id"] == eid][0]
    sh = e2["shards"][0]
    assert sh["status"] == "done"
    print("repair OK", eid, "-> shard done, done_at", sh["done_at"])
