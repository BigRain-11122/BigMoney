import json
d = json.load(open("results/token_usage.json", encoding="utf-8"))
h = d.get("history", [])
if isinstance(h, list) and h:
    print("history_len", len(h))
    for row in h[-2:]:
        print(json.dumps(row, ensure_ascii=False)[:300])
else:
    for k in list(d)[:10]:
        v = str(d[k])[:200]
        print(k, "=", v)
