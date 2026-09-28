import json, os
print("== watermark_red.json ==")
p = "results/watermark_red.json"
if os.path.exists(p):
    d = json.load(open(p, encoding="utf-8"))
    print(json.dumps(d, ensure_ascii=False)[:600])
else:
    print("ABSENT")
print("== pool key entries ==")
d = json.load(open("results/runnable_pool.json", encoding="utf-8"))
for e in d.get("entries", []):
    eid = str(e.get("entry_id", ""))
    if any(k in eid for k in ("W6", "V3", "T-105")):
        print(json.dumps({k: e.get(k) for k in ("entry_id", "status", "worker", "shards", "note")}, ensure_ascii=False)[:500])
