"""r318 bm-c pool truth probe (r513 stale-view law: read ORIGIN side, not local lane view).
Faces: O-1332 sec.2 W9 supply acceptance, P2->T-140 finalize readiness, claimable truth
(r309/r489: shard layer is the truth, entry layer can ghost), park_note blindspot (r497).
"""
import json
import subprocess

RAW = subprocess.check_output(
    ["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney", "show", "origin/main:results/runnable_pool.json"]
)
pool = json.loads(RAW.decode("utf-8"))
entries = pool if isinstance(pool, list) else pool.get("entries", pool.get("pool", []))
print(f"ORIGIN_POOL entries={len(entries)}")
ready = unclaimed = 0
for e in entries:
    eid = e.get("id", "?")
    est = e.get("status", "?")
    shards = e.get("shards", []) or []
    sdone = sum(1 for s in shards if s.get("status") == "done")
    park = " park_note" if "park_note" in eid or e.get("park_note") else ""
    claimable = [s for s in shards if s.get("status") == "ready"]
    if est == "ready":
        ready += 1
        if claimable:
            unclaimed += 1
    print(f"  {eid}: entry={est} shards={sdone}/{len(shards)} ready_left={len(claimable)}{park}")
print(f"ENTRY_READY={ready} UNCLAIMED_WITH_READY_SHARDS={unclaimed}")

# W9 / P2(W8) / T-139 face lines
for e in entries:
    eid = str(e.get("id", ""))
    if "W9" in eid or "W8" in eid or "T-139" in eid.upper() or "REV" in eid.upper():
        shards = e.get("shards", []) or []
        sdone = sum(1 for s in shards if s.get("status") == "done")
        print(f"FACE {eid}: entry={e.get('status')} shards_done={sdone}/{len(shards)}")
