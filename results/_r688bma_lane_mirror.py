"""r688 bm-a S3h: lane mirror runnable_pool.bm-a.json shard-2 state (pre-flip reconciliation)."""
import json
import re

for path in ("results/runnable_pool.bm-a.json",):
    t = open(path, encoding="utf-8").read()
    eid = "MASS-TRIAL-W3-JUDGE-SHARD-2"
    m = re.search(r'\{\s*"id":\s*"' + eid + '"', t)
    if not m:
        print(path, ": SHARD-2 entry NOT FOUND")
        continue
    start = m.start()
    depth = 0
    i = start
    while True:
        c = t[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    e = json.loads(t[start:i + 1])
    print(path, "entry.status:", e.get("status"))
    print("shard[0]:", json.dumps(e.get("shards", [{}])[0], ensure_ascii=False)[:500])
