# 一次性只读：大样本Top10策略提炼 v2（字段修正：sum/n=均值；键=基因JSON自带全部信息）
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
s = json.load(open("state/state.json", encoding="utf-8"))
ps = (s["arena"].get("pstats") or {})

rows = []
for k, st in ps.items():
    n = int(st.get("n") or 0)
    if n < 300:
        continue
    rows.append({
        "id": st.get("id", "?"), "strategy": st.get("strategy", "?"),
        "style": st.get("style", "?"), "sizing": st.get("sizing", "equal"),
        "n": n,
        "ps": float(st.get("ps_sum", 0)) / n,          # 平均盈稳分（用户口径）
        "ret": float(st.get("ret_sum", 0)) / n,         # 平均局收益
        "dd": float(st.get("dd_sum", 0)) / n,          # 平均最大回撤
        "pos": float(st.get("win_rounds", 0)) / n,     # 正收益局占比
        "worst": float(st.get("worst", 0)),
        "top10": int(st.get("top10", 0)),
        "halt_ok": float(st.get("halt_ok", 0)) / n,
        "gene": json.loads(k) if isinstance(k, str) else {},
    })

rows.sort(key=lambda x: x["ps"], reverse=True)
print(f"== 大样本选手 n>=300：{len(rows)} 人（pstats 共 {len(ps)} 条）==\n")
print("== 最终Top10（平均盈稳分 = 局收益 - 1.5×|局回撤|，样本全部>=300局）==\n")
for i, r in enumerate(rows[:10], 1):
    print(f"#{i} {r['id']} {r['strategy']}·{r['style']} | 盈稳分 {r['ps']:+.2f}pt"
          f" | 收益 {r['ret']:+.1%}/局 | 回撤 {r['dd']:.1%} | 正收益局 {r['pos']:.0%}"
          f" | 最差局 {r['worst']:+.1%} | 停机线存活 {r['halt_ok']:.0%}"
          f" | 晋级 {r['top10']}次 | 样本 {r['n']:,}局")
    g = r["gene"]
    print(f"    策略参数: {json.dumps(g.get('params', g), ensure_ascii=False)}"
          f"  仓位: {g.get('sizing', r['sizing'])}")
print()

# 家族聚合
fam = {}
for r in rows:
    f = fam.setdefault(r["strategy"], [])
    f.append(r)
print("== 家族聚合（大样本内，按平均盈稳分排序） ==")
for k, lst in sorted(fam.items(), key=lambda kv: -sum(x["ps"] for x in kv[1]) / len(kv[1])):
    m = lambda key: sum(x[key] for x in lst) / len(lst)
    print(f"  {k:16s} {len(lst):2d}人 | 盈稳分 {m('ps'):+.2f}pt | 收益 {m('ret'):+.1%}/局"
          f" | 回撤 {m('dd'):.1%} | 正收益 {m('pos'):.0%} | 最大样本 {max(x['n'] for x in lst):,}局")
