"""r688 bm-a debug: replicate flip_face gate-3 reads with debug output."""
import json

POOL = "results/runnable_pool.json"
text = open(POOL, encoding="utf-8", newline="").read()
pre = json.loads(text)
ents = pre["entries"]
print("entries:", len(ents))
fam = {e["id"]: e for e in ents if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE-SHARD")}
print("fam ids:", sorted(fam))
e0 = fam.get("MASS-TRIAL-W3-JUDGE-SHARD-0")
print("SHARD-0 type:", type(e0))
print("SHARD-0 status:", repr(e0.get("status")) if e0 else "MISSING")
# find ALL startswith matches including sub-ids
allm = [e.get("id") for e in ents if "W3-JUDGE" in str(e.get("id", ""))]
print("all W3-JUDGE ids:", allm)
