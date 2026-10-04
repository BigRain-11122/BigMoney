"""r482 bm-c: origin pool W3 state probe (resolver assert face). Reads
origin/main pool blob, reports W3 shard + entry states + trio owner_since."""
import json
import subprocess

r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                   capture_output=True)
assert r.returncode == 0, "origin pool read fail"
pool = json.loads(r.stdout.decode("utf-8"))
out = []
for e in pool["entries"]:
    if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD"):
        s = e["shards"][0]
        out.append("ORIGIN %s entry=%s shard=%s owner=%s since=%s harvest=%s/%s" % (
            e["id"], e.get("status"), s.get("status"), s.get("owner"),
            s.get("owner_since"), s.get("harvested_by"), s.get("harvest_claim")))
    if str(e.get("id", "")).startswith("FUND-") and "NULLS" in str(e.get("id", "")):
        s = e["shards"][0]
        out.append("ORIGIN %s %s owner=%s since=%s" % (
            e["id"], s.get("status"), s.get("owner"), s.get("owner_since")))
out.append("ORIGIN total entries %d" % len(pool["entries"]))
open("results/_r482bmc_origin_pool_out.txt", "w",
     encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE")
