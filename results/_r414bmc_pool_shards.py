# r414 bm-c: pool ready-face shard-owner pin (audit unclaimed=3 identity evidence)
import json

d = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/results/runnable_pool.json",
                   encoding="utf-8"))
for e in d.get("entries", []):
    if e.get("status") != "ready":
        continue
    print("== ", e.get("id"))
    for s in (e.get("shards") or []):
        print("   shard:", json.dumps(s, ensure_ascii=False)[:400])
