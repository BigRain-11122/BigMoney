import json
import subprocess


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


path = "results/compute_audit.json"
a = show("origin/main", path)   # bm-b side
b = show("beeb4bc66", path)     # my r433 side
ha, hb = a["history"], b["history"]
# union by content identity, preserve ts ordering
seen = {json.dumps(h, sort_keys=True) for h in hb}
merged = list(hb)
added = 0
for h in ha:
    k = json.dumps(h, sort_keys=True)
    if k not in seen:
        merged.append(h)
        seen.add(k)
        added += 1
merged.sort(key=lambda h: h.get("ts", ""))
out = {"history": merged, "latest": b["latest"]}  # latest = take-new (mine 14:50:08 > bm-b 14:29:48)
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"compute_audit union: history {len(hb)} + {added} origin-only = {len(merged)} rows; latest=mine ts={b['latest'].get('ts')}")
