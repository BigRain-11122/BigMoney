# -*- coding: utf-8 -*-
"""r698 bm-a pool/queue state probe (read-only)."""
import json, io, sys

out = io.StringIO()
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    pool = json.load(fh)

entries = pool.get("entries", [])
ready, waiting, running, done = [], [], [], []
for e in entries:
    st = e.get("status")
    row = {"id": e.get("id"), "status": st, "priority": e.get("priority"),
           "lane_owner": e.get("lane_owner")}
    shards = e.get("shards", [])
    owners = {}
    for s in shards:
        owners[s.get("key")] = (s.get("owner"), s.get("status"))
    if st == "ready":
        ready.append((row, owners))
    elif st == "waiting":
        waiting.append((row, owners))
    elif st == "running":
        running.append((row, owners))
    elif st == "done":
        done.append(row["id"])

print("POOL: entries=%d ready=%d waiting=%d running=%d done=%d" % (
    len(entries), len(ready), len(waiting), len(running), len(done)), file=out)
for row, owners in ready:
    print("READY:", row, file=out)
    for k, v in owners.items():
        print("   shard", k, v, file=out)
for row, owners in running:
    print("RUNNING:", row, file=out)
    for k, v in owners.items():
        print("   shard", k, v, file=out)
for row, owners in waiting:
    print("WAITING:", row, file=out)
    for k, v in owners.items():
        print("   shard", k, v, file=out)

# not-done tail summary
print(file=out)
print("NOT-DONE ids:", [r["id"] for r, _ in ready] + [r["id"] for r, _ in waiting] + [r["id"] for r, _ in running], file=out)

with open("results/_r698bma_pool_probe.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
