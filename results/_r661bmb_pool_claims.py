# Read pool claim rows for trio NULLS (structure-adaptive)
import json

pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
print("top keys:", list(pool.keys())[:10] if isinstance(pool, dict) else "LIST len=%d" % len(pool))

def walk(obj, path=""):
    if isinstance(obj, dict):
        key = str(obj.get("entry", obj.get("key", obj.get("id", ""))))
        if "nulls" in key and "fund" in key:
            print("POOL:", key, "| owner=", obj.get("owner"), "| owner_since=", obj.get("owner_since"))
        for k, v in obj.items():
            if k in ("shards", "entries", "items", "batches"):
                walk(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for it in obj:
            walk(it, path)

walk(pool)
