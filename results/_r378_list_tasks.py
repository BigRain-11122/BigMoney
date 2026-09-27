import json, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
rows = []
for f in glob.glob("fleet/tasks/*.json"):
    with open(f, encoding="utf-8-sig") as fh:
        j = json.load(fh)
    ts = j if isinstance(j, list) else [j]
    if isinstance(ts[0], dict) and "tasks" in ts[0] and isinstance(ts[0]["tasks"], list):
        ts = ts[0]["tasks"]
    for t in ts:
        if isinstance(t, dict):
            rows.append((t.get("id"), t.get("status"), t.get("claimed_by"), str(t.get("title", ""))[:100]))
act = [r for r in rows if r[1] in ("open", "claimed", "in_progress")]
print(f"total tickets={len(rows)} active={len(act)}")
for r in act:
    print(r)
