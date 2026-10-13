import json
p = "results/runnable_pool.json"
d = json.load(open(p, encoding="utf-8"))
entries = d.get("entries", d if isinstance(d, list) else [])
if isinstance(d, dict) and "entries" in d:
    pass
else:
    entries = d if isinstance(d, list) else []
print("total entries:", len(entries))
waiting = []
for e in entries:
    st = e.get("status")
    if st in ("waiting", "ready"):
        waiting.append(e)
print("waiting/ready:", len(waiting))
for e in waiting[:15]:
    print("-", e.get("id") or e.get("name"), "| status=", st, "| lane_owner=", e.get("lane_owner"), "| priority=", e.get("priority"), "| machine=", e.get("machine") or e.get("audit", {}).get("machine") if isinstance(e.get("audit"), dict) else "")
