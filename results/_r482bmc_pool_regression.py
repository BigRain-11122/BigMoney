"""r482 bm-c post-push pool regression probe (r474 law): W3 shard states +
fund-trio owner_since regression check vs origin history + harvest-flip state."""
import json

pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
out = []

w3 = {}
for e in pool["entries"]:
    if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD"):
        s = e["shards"][0]
        w3[e["id"]] = {
            "entry_status": e.get("status"),
            "shard_status": s.get("status"),
            "owner": s.get("owner"),
            "owner_since": s.get("owner_since"),
            "harvested_by": s.get("harvested_by"),
            "harvest_claim": s.get("harvest_claim"),
        }
for k in sorted(w3):
    out.append("W3 %s %s" % (k, json.dumps(w3[k], ensure_ascii=False)))

# fund trio owner_since (r474 regression face: must not be < 13:04:19 family
# of 2026-10-04 -- current origin-newest wins)
trio = {}
for e in pool["entries"]:
    if str(e.get("id", "")).startswith("FUND-") and "NULLS" in str(e.get("id", "")):
        s = e["shards"][0]
        trio[e["id"]] = {"status": s.get("status"), "owner": s.get("owner"),
                         "owner_since": s.get("owner_since")}
for k in sorted(trio):
    out.append("TRIO %s %s" % (k, json.dumps(trio[k], ensure_ascii=False)))

# claims face
import os
for d in sorted(os.listdir("results/pool_claims")):
    if "MASS-TRIAL-W3" in d:
        for fn in sorted(os.listdir(os.path.join("results/pool_claims", d))):
            c = json.load(open(os.path.join("results/pool_claims", d, fn),
                                encoding="utf-8"))
            out.append("CLAIM %s/%s state=%s outcome=%s" %
                       (d, fn, c.get("state"), c.get("outcome")))

# entry layer counts
n_done = sum(1 for e in pool["entries"] if e.get("status") == "done")
n_total = len(pool["entries"])
out.append("POOL total=%d done=%d" % (n_total, n_done))

open("results/_r482bmc_pool_regression_out.txt", "w",
     encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE")
