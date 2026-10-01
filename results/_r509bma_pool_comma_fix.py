"""r509 bm-a: pool JSON comma repair after union splice (harvested_by tail key)."""
import json

PATH = "results/runnable_pool.json"
raw = open(PATH, encoding="utf-8", newline="").read()
bad = '"harvested_by": "bm-c"\r\n"claimed_since"'
good = '"harvested_by": "bm-c",\r\n"claimed_since"'
n = raw.count(bad)
assert n == 1, f"expected 1 occurrence, got {n}"
raw = raw.replace(bad, good)
open(PATH, "w", encoding="utf-8", newline="").write(raw)

p = json.loads(raw)
n3 = [e for e in p["entries"] if e["id"].startswith("PERPETUAL-N3-R1-")]
w5 = [e for e in p["entries"] if "N1-W5" in e["id"]]
sh11 = [e for e in w5 if "SHARD-11" in e["id"]][0]["shards"][0]
print("JSON VALID; N3 done", sum(e["status"] == "done" for e in n3),
      "/6; W5 done", sum(e["status"] == "done" for e in w5), "/12")
print("shard-11 keys:", sorted(sh11.keys()))
