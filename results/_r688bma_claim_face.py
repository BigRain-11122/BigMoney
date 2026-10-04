"""r688 bm-a S3f: full shard sub-face dict from claim commit vs current (find owner fields)."""
import json
import re
import subprocess


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


blob = subprocess.run(
    ["git", "show", "03f7ac259:results/runnable_pool.json"], capture_output=True
).stdout.decode("utf-8")
e = entry_of(blob, "MASS-TRIAL-W3-JUDGE-SHARD-2")
print("CLAIM-COMMIT shard[0] FULL:")
print(json.dumps(e["shards"][0], ensure_ascii=False, indent=1))
print("CLAIM-COMMIT entry status/owner:", e.get("status"), e.get("owner"), e.get("owner_since"))
