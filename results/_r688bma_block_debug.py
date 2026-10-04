"""r688 bm-a S3i-debug: find why block walk yields 1 line."""
import re

t = open("results/runnable_pool.json", encoding="utf-8").read()
m = re.search(r'\{\s*"id":\s*"MASS-TRIAL-W3-JUDGE-SHARD-2"', t)
print("match start:", m.start(), "end:", m.end())
print("context:", repr(t[m.start() - 60:m.end() + 40]))
