"""r243 pool flip bookkeeping: bump updated_at + validate JSON."""
import io
import json

P = "results/runnable_pool.json"
txt = io.open(P, encoding="utf-8").read()
d = json.loads(txt)  # validate pre-state
gpu = [e for e in d["entries"] if e["id"] == "GPU-FACTOR-LANE-PROOF"][0]
assert gpu["status"] == "ready", gpu["status"]
old = '"updated_at": "2026-09-26 06:55:17"'
new = '"updated_at": "2026-09-26 11:45:30"'
assert old in txt, "updated_at anchor not found"
io.open(P, "w", encoding="utf-8", newline="").write(txt.replace(old, new))
d2 = json.loads(io.open(P, encoding="utf-8").read())
print("json valid; updated_at =", d2["updated_at"])
print("gpu entry status =", gpu["status"])
print("shard status =", gpu["shards"][0]["status"])
