# -*- coding: utf-8 -*-
"""r698 bm-a W14 entry detail probe (read-only)."""
import json, io

out = io.StringIO()
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    pool = json.load(fh)

for e in pool.get("entries", []):
    if e.get("id") in ("TRIAL-LABOR-W14-GENERATE", "FUND-VALUE-P1-NULLS", "CONTEST-YTD-P1-RC-0OF1"):
        print("=== ENTRY", e.get("id"), "===", file=out)
        for k, v in e.items():
            if k == "shards":
                for s in v:
                    print("  shard:", json.dumps(s, ensure_ascii=False)[:400], file=out)
            else:
                print("  %s: %s" % (k, str(v)[:400]), file=out)

with open("results/_r698bma_w14_detail.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
