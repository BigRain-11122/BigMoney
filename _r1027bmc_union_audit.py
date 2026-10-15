# -*- coding: utf-8 -*-
# r1027 bm-c: compute_audit.json union-by-ts merge (rebase conflict resolution, r1000 precedent)
import json, subprocess, io

def load_ours():
    with io.open("results/compute_audit.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)

def load_mine():
    raw = subprocess.run(["git", "show", "d43b3917c:results/compute_audit.json"],
                          capture_output=True).stdout.decode("utf-8-sig")
    return json.loads(raw)

ours = load_ours()
mine = load_mine()

def ts_of(e):
    for k in ("ts", "time", "timestamp", "datetime", "asof"):
        if k in e:
            return str(e[k])
    return ""

merged = {}
for e in ours.get("history", []):
    merged[ts_of(e) + "|" + json.dumps(e, sort_keys=True)[:60]] = e
for e in mine.get("history", []):
    key = ts_of(e) + "|" + json.dumps(e, sort_keys=True)[:60]
    merged[key] = e  # mine wins on exact-shape collision (newer bm-c face)

history = sorted(merged.values(), key=ts_of)
latest = ours.get("latest", {})
if ts_of(mine.get("latest", {})) > ts_of(latest):
    latest = mine.get("latest", {})

out = {"history": history, "latest": latest}
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("AUDIT-UNION ours=%d mine=%d merged=%d" % (len(ours.get("history", [])), len(mine.get("history", [])), len(history)))
