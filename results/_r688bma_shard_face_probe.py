"""r688 bm-a S3e: SHARD-2 entry shards sub-face + crash-fuse scan + claim-commit provenance."""
import json
import re
import subprocess

t = open("results/runnable_pool.json", encoding="utf-8").read()


def entry_of(text, eid):
    m = re.search(r'\{\s*"id":\s*"' + eid + '"', text)
    start = m.start()
    depth = 0
    i = start
    while True:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return json.loads(text[start:i + 1])


for eid in ["MASS-TRIAL-W3-JUDGE-SHARD-1", "MASS-TRIAL-W3-JUDGE-SHARD-2", "MASS-TRIAL-W3-JUDGE-SHARD-3"]:
    e = entry_of(t, eid)
    print(eid, "entry.status:", e.get("status"), "| shards:", json.dumps(e.get("shards", []), ensure_ascii=False)[:360])

# claim commit's pool face for SHARD-2 (provenance: owner/owner_since that were lost)
blob = subprocess.run(
    ["git", "show", "03f7ac259:results/runnable_pool.json"], capture_output=True
).stdout.decode("utf-8")
e = entry_of(blob, "MASS-TRIAL-W3-JUDGE-SHARD-2")
print("CLAIM-COMMIT face: entry.status:", e.get("status"), "| shards:", json.dumps(e.get("shards", []), ensure_ascii=False)[:360])

# crash fuse scan
for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-a.json"):
    try:
        d = open(cf, encoding="utf-8").read()
    except FileNotFoundError:
        print("fuse missing:", cf)
        continue
    hits = d.count("w3-judge-2of4")
    print("fuse", cf, "| w3-judge-2of4 hits:", hits)
    if hits:
        idx = d.find("w3-judge-2of4")
        print("  window:", d[max(0, idx - 200):idx + 300].replace("\n", " ")[:400])
