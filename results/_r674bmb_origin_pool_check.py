# -*- coding: utf-8 -*-
# r674 bm-b final: origin pool trio owner_since freshness (MSG-1332 closure criterion,
# bm-c: "origin trio owner_since back to fresh (<15min age) = self-heal proof")
import subprocess, json, datetime

r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True)
assert r.returncode == 0
pool = json.loads(r.stdout.decode("utf-8"))
now = datetime.datetime.now()
out = {}
for e in pool.get("entries", []):
    if str(e.get("id", "")).startswith("FUND") and str(e.get("id", "")).endswith("NULLS"):
        sh = e.get("shards", [{}])[0]
        os_ = sh.get("owner_since")
        age_min = None
        if os_:
            try:
                t = datetime.datetime.strptime(os_, "%Y-%m-%d %H:%M:%S")
                age_min = round((now - t).total_seconds() / 60, 1)
            except Exception:
                pass
        out[e["id"]] = {"owner": sh.get("owner"), "owner_since": os_, "age_min": age_min,
                        "fresh_lt15": (age_min is not None and age_min < 15)}
with open(r"results\_r674bmb_origin_pool_check.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
ok = all(v["fresh_lt15"] for v in out.values()) and len(out) == 3
print("trio fresh on origin:", "ALL-FRESH (MSG-1332 closure met)" if ok else "STALE")
for k, v in out.items():
    print(k, v["owner"], v["owner_since"], "age", v["age_min"], "min")
