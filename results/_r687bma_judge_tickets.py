# -*- coding: utf-8 -*-
"""r687 bm-a: W3 judge shard ticket states in local (daemon-synced) pool."""
import json, io

d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
rows = []
for e in d.get("entries", []):
    if "W3-JUDGE" in str(e.get("id", "")):
        rows.append((e.get("id"), e.get("status"), e.get("owner"),
                     e.get("owner_since"), str(e.get("cmd") or
                     e.get("command"))[:100]))
with io.open("results/_r687bma_judge_tickets.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(" | ".join(str(x) for x in r) + "\n")
    f.write("COUNT %d\n" % len(rows))
print("WROTE judge ticket states, count", len(rows))
