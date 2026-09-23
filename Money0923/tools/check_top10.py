import json

s = json.load(open(r"C:\Users\sjs20\Desktop\Money\state\state.json", encoding="utf-8"))
t10 = s["evolution"].get("top10") or []
uniq = len({(t["strategy"], json.dumps(t["params"], sort_keys=True)) for t in t10})
print("当前代:", s["evolution"]["generation"])
print("top10条数:", len(t10), "唯一(策略+参数全值):", uniq)
print("最近一代时间:", s["evolution"]["history"][-1]["time"] if s["evolution"].get("history") else None)
