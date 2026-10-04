"""r458 bm-c S2 fleet-task board scan (regenerable, read-only).

Scan all fleet/tasks/*.json for status=open tickets; report id/title/claimed_by.
Working tree == origin/main tip (pushed this round); tasks dir is not a daemon face.
"""
import glob
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
open_tickets = []
counts = {}
for p in sorted(glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json"))):
    name = os.path.basename(p)
    try:
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
    except Exception as e:
        print("READ_FAIL", name, repr(e))
        continue
    st = t.get("status", "?")
    counts[st] = counts.get(st, 0) + 1
    if st == "open":
        open_tickets.append((name, t.get("title", "")[:80], t.get("claimed_by")))
print("STATUS_COUNTS", json.dumps(counts, ensure_ascii=False))
if open_tickets:
    for n, ttl, cb in open_tickets:
        print("OPEN", n, "|", ttl, "| claimed_by:", cb)
else:
    print("OPEN_ZERO")
