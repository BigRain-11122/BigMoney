"""r696 bm-b: stage0 pool JSON parse (SHARD-3/4 + trio since)."""
import json
import subprocess

r = subprocess.run(["git", "show", ":0:results/runnable_pool.json"],
                   capture_output=True)
doc = json.loads(r.stdout.decode("utf-8"))
for eid in ("PERPETUAL-N2-W15-SHARD-3", "PERPETUAL-N2-W15-SHARD-4",
            "FUND-VALUE-P1-NULLS", "CONTEST-YTD-P1-RC-0OF1"):
    e = [x for x in doc["entries"] if x.get("id") == eid]
    if e:
        s = e[0].get("shards", [{}])[0]
        print(eid, "| status=", s.get("status"), "| owner=", s.get("owner"),
              "| since=", s.get("owner_since"))
    else:
        print(eid, "| MISSING")
print("stage0 bytes:", len(r.stdout))
