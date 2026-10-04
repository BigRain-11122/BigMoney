# -*- coding: utf-8 -*-
"""r499 bm-c: N2-W15 shard progress view (origin raw-blob, r675bmb key-position law:
shard truth = entries[].shards[].owner/status, NOT entry-level owner)."""
import json
import re
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                  capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
pool = json.loads(r.stdout.decode("utf-8"))
rows = []
for e in pool.get("entries", []):
    if "N2-W15" in str(e.get("key", e.get("id", ""))):
        for sh in e.get("shards", []):
            rows.append((sh.get("shard", "?"), sh.get("status", "?"),
                         sh.get("owner", "?"), sh.get("owner_since", "?")[:19]))
for row in sorted(rows):
    print("|".join(str(x) for x in row))
stat = {}
for row in rows:
    stat[row[1]] = stat.get(row[1], 0) + 1
print("STATUS-SUMMARY: " + json.dumps(stat, ensure_ascii=False))
