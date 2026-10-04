# r669 pool status probe (utf-8 safe, ascii output)
import json
d = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
rows = []
for e in d.get("entries", []):
    rows.append((e.get("id", "?"), e.get("status", "?"), e.get("owner", "?"), str(e.get("updated_at", ""))[:19]))
counts = {}
for r in rows:
    counts[r[1]] = counts.get(r[1], 0) + 1
with open(r"results\_r669bmb_pool_status_out.txt", "wb") as f:
    f.write(("counts=" + json.dumps(counts, ensure_ascii=True) + "\n").encode("ascii"))
    for r in rows:
        f.write((" | ".join(r) + "\n").encode("ascii"))
print("POOL-PROBE-DONE", counts)
