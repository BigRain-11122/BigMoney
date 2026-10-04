"""r688 bm-a S3k: who re-claimed SHARD-2? origin face + autofill state + local burn process."""
import json
import re
import subprocess

ob = subprocess.run(
    ["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True
).stdout.decode("utf-8")
opool = json.loads(ob)
e = [x for x in opool["entries"] if x.get("id") == "MASS-TRIAL-W3-JUDGE-SHARD-2"][0]
print("ORIGIN entry.status:", e["status"])
print("ORIGIN shard[0]:", json.dumps(e["shards"][0], ensure_ascii=False)[:500])

# origin lane mirrors for shard-2 ownership hints
for lane in ("results/runnable_pool.bm-a.json", "results/runnable_pool.bm-b.json", "results/runnable_pool.bm-c.json"):
    b = subprocess.run(["git", "show", "origin/main:" + lane], capture_output=True).stdout.decode("utf-8")
    if not b.strip():
        print(lane, ": absent at origin")
        continue
    d = json.loads(b)
    ent = [x for x in d["entries"] if x.get("id") == "MASS-TRIAL-W3-JUDGE-SHARD-2"]
    if ent:
        s0 = ent[0]["shards"][0]
        print(lane, "entry:", ent[0]["status"], "| shard:", s0.get("status"), "owner:", s0.get("owner"), "since:", s0.get("owner_since"))

# our autofill state
try:
    af = json.load(open("results/autofill_state.bm-a.json", encoding="utf-8-sig"))
    print("autofill_state.bm-a:", json.dumps(af, ensure_ascii=False)[:600])
except Exception as ex:
    print("autofill state read err:", ex)

# recent origin commits touching pool
out = subprocess.run(
    ["git", "log", "--oneline", "-8", "origin/main"], capture_output=True
).stdout.decode("utf-8")
print("origin log:", out)
