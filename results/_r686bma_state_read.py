import json
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
with open(repo + r"\state-bm-a.json", "rb") as f:
    d = json.loads(f.read().decode('utf-8'))
print("round_no:", d.get("round_no"))
nxt = d.get("next")
print("next:", json.dumps(nxt, ensure_ascii=True)[:800] if nxt else None)
for k in sorted(d.keys()):
    if k in ("round_no", "next"):
        continue
    v = json.dumps(d[k], ensure_ascii=True)
    print(k, "=", v[:200])
