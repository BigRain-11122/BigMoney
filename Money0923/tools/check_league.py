import json
from collections import Counter

with open(r"C:\Users\sjs20\Desktop\Money\state\state.json", encoding="utf-8") as f:
    s = json.load(f)
a = s.get("arena", {})
ps = a.get("players", [])
sc = Counter(p.get("style", "?") for p in ps)
caps = {p["capital"] for p in ps}
rh = a.get("round_history", [])[-2:]
print("阵容:", len(ps), "支 | 资金:", caps, "| 赛制版本:", a.get("roster_version"))
print("风格席位:", dict(sc))
for r in rh:
    b = r["best"]
    print(f"第{r['round']}局 {r['window']} 均分{r['mean_score']} | "
          f"最佳 {b['id']}({b['strategy']}/{b.get('style')}) {b['score']}")
if rh:
    print("top10 风格分布(最近一局):", dict(Counter(t.get("style") for t in rh[-1]["top10"])))
