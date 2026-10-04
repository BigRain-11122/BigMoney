# -*- coding: utf-8 -*-
# r666 bm-b pool ready-face probe: shard owners + owner_since recency (in-flight burn detection)
import json

d = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
e = [i for i in d.get("entries", []) if i.get("status") in ("ready", "waiting")]
out = []
for i in e:
    shards = [(s.get("key"), s.get("status"), s.get("owner"), s.get("owner_since"))
              for s in i.get("shards", [])][:8]
    out.append({"id": i.get("id"), "status": i.get("status"),
                "runner": i.get("runner"), "prereg": i.get("prereg"), "shards": shards})
print(json.dumps(out, ensure_ascii=False, indent=1))
