# -*- coding: utf-8 -*-
"""r698 bm-a: which pool entries does bm-a own in the local (dirty) tree."""
import json, io

out = io.StringIO()
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    pool = json.load(fh)

for e in pool.get("entries", []):
    for s in e.get("shards", []):
        if s.get("owner") == "bm-a":
            print("entry=%s status=%s | shard=%s status=%s owner_since=%s done_at=%s" % (
                e.get("id"), e.get("status"), s.get("key"), s.get("status"),
                s.get("owner_since"), s.get("done_at")), file=out)

with open("results/_r698bma_my_shards.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
