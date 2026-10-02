# r602 bm-b: probe CURRENT origin pool state (post bm-a harvest flip daad93d5e)
import subprocess, json

def blob(path):
    p = subprocess.run(["git", "show", "origin/main:" + path], capture_output=True)
    return p.stdout.decode("utf-8-sig", "replace")

d = json.loads(blob("results/runnable_pool.json"))
if isinstance(d, dict):
    for k in ("entries", "pool", "items", "runnable"):
        if isinstance(d.get(k), list):
            d = d[k]; break
for eid in ("FUND-VALUE-P1-CELL-VALUEPB-X2", "FUND-VALUE-P1-NULLS", "FUND-VALUE-P1-SENS"):
    e = next((x for x in d if x.get("id") == eid), None)
    sh = (e or {}).get("shards", [{}])[0]
    print(json.dumps({
        "id": eid, "entry": e.get("status") if e else None,
        "shard": sh.get("status"), "owner": sh.get("owner"),
        "owner_since": sh.get("owner_since"), "done_at": sh.get("done_at"),
        "done_by": e.get("done_by") if e else None,
        "harvested_by": sh.get("harvested_by"), "harvest_claim": sh.get("harvest_claim"),
    }, ensure_ascii=False))
print("total entries:", len(d))
