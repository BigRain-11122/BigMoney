# -*- coding: utf-8 -*-
"""r846 bm-a: heal MSG-0612 pool owner_since backward move (pre-push claw save).
Canon: S0 reland ring law / r835 -- per-face per-shard max-merge vs origin blob,
ts-like fields newer-wins (owner_since/cleared_ts). Origin bm-c claim-refresh
22:30:04 must survive my 22:20:04 stale absorb."""
import json, subprocess

FACES = ["results/runnable_pool.json", "results/runnable_pool.bm-a.json"]
TS_FIELDS = ("owner_since", "cleared_ts", "claimed_at", "done_at", "ts")

for path in FACES:
    org = json.loads(subprocess.run(["git", "show", "origin/main:" + path],
                                    capture_output=True).stdout.decode("utf-8"))
    mine = json.load(open(path, encoding="utf-8"))
    m_by = {e.get("id"): e for e in mine.get("entries", [])}
    o_by = {e.get("id"): e for e in org.get("entries", [])}
    changed = 0
    for eid, m in m_by.items():
        o = o_by.get(eid)
        if not o:
            continue
        ms = {s.get("key"): s for s in m.get("shards", [])}
        os_ = {s.get("key"): s for s in o.get("shards", [])}
        for k, mshard in ms.items():
            oshard = os_.get(k)
            if not oshard:
                continue
            for f in TS_FIELDS:
                ov, mv = oshard.get(f), mshard.get(f)
                if ov and mv and ov > mv:
                    mshard[f] = ov
                    # owner tied to newer claim: adopt whole shard ts/owner fields
                    for f2 in ("owner", "status"):
                        if f2 in oshard and ov == oshard.get("owner_since", ""):
                            mshard[f2] = oshard[f2]
                    changed += 1
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(mine, f, ensure_ascii=False, indent=1)
    print(path, "-> shard ts fields healed forward:", changed)
print("HEAL DONE")
