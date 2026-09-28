import json
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
print("== non-done entries ==")
for e in d.get("entries", []):
    if e.get("status") not in ("done",):
        print(e.get("id"), "|", e.get("status"), "| lane:", e.get("lane_owner"),
              "|", str(e.get("ticket_ref", ""))[:110])
