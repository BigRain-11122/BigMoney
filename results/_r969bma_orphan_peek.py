import json
p = r"results/_orphan_face_probe.bm-a.json"
d = json.load(open(p, encoding="utf-8"))
print("keys:", sorted(d.keys()))
for k, v in d.items():
    if isinstance(v, (int, float, str)):
        print(k, "=", v)
    elif isinstance(v, list):
        print(k, "= list len", len(v))
        for item in v[:6]:
            print("   ", json.dumps(item, ensure_ascii=False)[:400])
    else:
        print(k, "= ", json.dumps(v, ensure_ascii=False)[:600])
