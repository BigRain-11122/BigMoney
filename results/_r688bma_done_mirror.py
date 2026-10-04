"""r688 bm-a S3g: dump full done-state of SHARD-0 (bm-c's completed flip) as the mirror target."""
import json
import re

t = open("results/runnable_pool.json", encoding="utf-8").read()
m = re.search(r'\{\s*"id":\s*"MASS-TRIAL-W3-JUDGE-SHARD-0"', t)
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
keep = {k: e.get(k) for k in ("id", "status", "done_at", "result_ref", "lane_owner", "entered_at", "entered_by")}
print("ENTRY-LEVEL done-state:")
print(json.dumps(keep, ensure_ascii=False, indent=1))
print("\nSHARD[0] done-state:")
print(json.dumps(e["shards"][0], ensure_ascii=False, indent=1))
