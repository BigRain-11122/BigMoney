import json
import subprocess

r = subprocess.run(
    ["git", "show", "origin/main:results/runnable_pool.json"],
    capture_output=True, timeout=30)
pool = json.loads(r.stdout.decode("utf-8"))
for e in pool.get("entries", []):
    eid = e.get("id", "")
    if eid in ("PERPETUAL-N2-W15-SHARD-2", "PERPETUAL-N2-W15-SHARD-10",
               "CONTEST-YTD-P1-RC-0OF1"):
        print("entry:", eid, "status=", e.get("status"))
        for s in e.get("shards", []):
            print("  ", s.get("key"), "status=", s.get("status"),
                  "owner=", s.get("owner"),
                  "owner_since=", s.get("owner_since"),
                  "done_at=", s.get("done_at"),
                  "harvested_by=", s.get("harvested_by"))
