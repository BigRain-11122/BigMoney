import json, datetime

p = r"C:\Users\Administrator\.codely-cli\sentinel\bmb-idleguard-state.json"
d = json.load(open(p, encoding="utf-8"))
iso = d.get("idle_since")
if isinstance(iso, str):
    try:
        d["idle_since"] = datetime.datetime.fromisoformat(iso).timestamp()
    except Exception:
        d["idle_since"] = None
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state migrated:", json.dumps(d, ensure_ascii=False))
