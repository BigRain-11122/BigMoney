# -*- coding: utf-8 -*-
"""R263 bm-a: dump full CN-CORE-DDCTL-P1 pool entry (harvest criterion read)."""
import io
import json

pool = json.load(io.open("results/runnable_pool.json", encoding="utf-8"))
items = pool if isinstance(pool, list) else pool.get("entries", [])
e = next(x for x in items if x.get("id") == "CN-CORE-DDCTL-P1")
print(json.dumps(e, ensure_ascii=False, indent=1)[:4000])
