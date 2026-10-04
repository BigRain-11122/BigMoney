"""r665: claim owners of standing-wave/fund tickets + runnable pool status summary."""
import json, io

for tid in ("T-2026-10-03-158", "T-2026-10-02-150-P1", "T-2026-10-04-166-P1", "T-2026-10-03-155-P1", "T-2026-10-03-153-P1"):
    p = f"fleet/tasks/{tid}.json"
    try:
        with io.open(p, "r", encoding="utf-8") as f:
            t = json.load(f)
        print(tid, "| status=", t.get("status"), "| claimed_by=", t.get("claimed_by"))
        prog = t.get("progress") or t.get("note") or ""
        if isinstance(prog, str):
            print("   prog:", prog[:300])
    except Exception as e:
        print(tid, "ERR", e)

with io.open("results/runnable_pool.json", "r", encoding="utf-8") as f:
    pool = json.load(f)
units = pool.get("units", pool if isinstance(pool, list) else [])
if isinstance(units, dict):
    units = list(units.values())
from collections import Counter
c = Counter(u.get("status") for u in units)
print("pool units:", len(units), dict(c))
for u in units:
    if u.get("status") in ("waiting", "ready", "running"):
        print("  ", u.get("batch_name", u.get("id", "?")), "|", u.get("status"), "| owner:", u.get("audit", {}).get("machine") if isinstance(u.get("audit"), dict) else u.get("lane_owner"))
