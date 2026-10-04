# -*- coding: utf-8 -*-
"""r698 bm-a: compare local-dirty vs origin pool rows for the 5 touched faces
(subprocess raw bytes per r660; owner_since newer-wins per r474)."""
import json, subprocess, io

CREATE_NO_WINDOW = 0x08000000
r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                   capture_output=True, creationflags=CREATE_NO_WINDOW)
origin = json.loads(r.stdout.decode("utf-8-sig"))
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    local = json.load(fh)

def faces(pool, eid):
    for e in pool.get("entries", []):
        if e.get("id") == eid:
            row = {"entry_status": e.get("status"),
                   "done_by": e.get("done_by"), "entry_done_at": e.get("done_at")}
            for s in e.get("shards", []):
                row[s.get("key")] = {"owner": s.get("owner"),
                                     "owner_since": s.get("owner_since"),
                                     "status": s.get("status"),
                                     "done_at": s.get("done_at"),
                                     "harvested_by": s.get("harvested_by")}
            return row
    return None

out = io.StringIO()
for eid in ["FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS",
            "CONTEST-YTD-P1-RC-0OF1", "PERPETUAL-N2-W15-SHARD-1", "PERPETUAL-N2-W15-SHARD-2"]:
    print("===", eid, file=out)
    print("  LOCAL :", json.dumps(faces(local, eid), ensure_ascii=False, sort_keys=True), file=out)
    print("  ORIGIN:", json.dumps(faces(origin, eid), ensure_ascii=False, sort_keys=True), file=out)

with open("results/_r698bma_facecmp.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
