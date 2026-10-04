"""r696 bm-b pool + lanes overview probe (shard-key path law r675bmb/r692: entries[].shards[])."""
import json, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pool = json.load(open(os.path.join(root, "results", "runnable_pool.json"), encoding="utf-8"))
rows = []
for e in pool.get("entries", []):
    st = e.get("status")
    for s in e.get("shards", []):
        rows.append({
            "id": e.get("id"), "shard": s.get("key"), "status": s.get("status"),
            "owner": s.get("owner"), "since": s.get("owner_since"),
            "gate": (s.get("gate") or "")[:40],
        })
    if not e.get("shards"):
        rows.append({"id": e.get("id"), "shard": "-", "status": st,
                     "owner": e.get("owner"), "since": e.get("owner_since"), "gate": ""})
for r in rows:
    print(json.dumps(r, ensure_ascii=False))
print("TOTAL entries:", len(pool.get("entries", [])))
