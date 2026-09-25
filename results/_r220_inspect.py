import json, os
def rd(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

wr = "results/watermark_red.json"
if os.path.exists(wr):
    d = rd(wr)
    print("watermark_red: red =", d.get("red"), "| reason =", str(d.get("reason"))[:200])
else:
    print("watermark_red.json ABSENT")

pool = rd("results/runnable_pool.json")
print("pool updated_at:", pool.get("updated_at"), "| schema:", pool.get("schema"))
for e in pool.get("entries", []):
    print("-", e.get("id"), "|", e.get("status"), "| shards:",
          len(e.get("shards", [])) if isinstance(e.get("shards"), list) else e.get("shards"),
          "|", str(e.get("title") or e.get("desc") or "")[:100])
