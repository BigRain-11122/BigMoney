"""r688 bm-a S3i: raw line dump of SHARD-2 entry block (pool + lane mirror) for surgical planning."""
import re

t = open("results/runnable_pool.json", encoding="utf-8").read()
m = re.search(r'\{\s*"id":\s*"MASS-TRIAL-W3-JUDGE-SHARD-2"', t)
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
block = t[start:i + 1]
lines = block.split("\r\n")
print("pool file shard-2 entry: %d lines" % len(lines))
for j, l in enumerate(lines):
    s = l.strip()
    if s.startswith('"id"') or s.startswith('"status"') or s.startswith('"note"') or s.startswith('"checkpoint"') or s.startswith('"entered_at"') or s.startswith('"lane_owner"') or s.startswith('"key"') or s in ("},", "}") or s == "{":
        print(j, repr(l[:130]))
