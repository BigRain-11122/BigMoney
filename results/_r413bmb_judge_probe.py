import json
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in d.get("entries", []):
    if e.get("id") in ("TRIAL-LABOR-W5-JUDGE", "TRIAL-LABOR-W6-JUDGE"):
        print("=====", e["id"])
        print(json.dumps(e, ensure_ascii=False, indent=1)[:3000])
