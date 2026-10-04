import json
import subprocess


def pool_of(rev):
    r = subprocess.run(["git", "show", f"{rev}:results/runnable_pool.json"],
                       capture_output=True, timeout=30)
    return json.loads(r.stdout.decode("utf-8"))


for rev in ("HEAD", "MERGE_HEAD"):
    p = pool_of(rev)
    print("===", rev)
    for e in p.get("entries", []):
        eid = e.get("id", "")
        if eid in ("CONTEST-YTD-P1-RC-0OF1", "PERPETUAL-N2-W15-SHARD-10",
                   "PERPETUAL-N2-W15-SHARD-2", "PERPETUAL-N2-W15-SHARD-11"):
            print(" entry:", eid, "status=", e.get("status"),
                  "done_by=", e.get("done_by"), "done_at=", e.get("done_at"))
            for s in e.get("shards", []):
                print("   ", s.get("key"), s.get("status"),
                      "owner=", s.get("owner"),
                      "owner_since=", s.get("owner_since"),
                      "done_at=", s.get("done_at"),
                      "harvested_by=", s.get("harvested_by"))
