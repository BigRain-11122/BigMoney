# 一次性：盘中实时成绩面板（腾讯轻量源，只读）
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from quant.data import spot_quotes_light

s = json.load(open("state/state.json", encoding="utf-8"))
acc = s["account"]

print("== 今日成交（分仓标签）==")
for t in s.get("trade_log", []):
    if t.get("date") == "20260922":
        print(f"  {t.get('sleeve','?')} {t.get('code')} {t.get('side')} {t.get('shares')} @ {t.get('price')}")

ch = s["champion"]
print(f"\n== 现任冠军 ==\n  {ch['strategy']}/{ch.get('sizing')} 样本外分 {ch['holdout']['score']} "
      f"(总收益 {ch['holdout']['metrics']['total_return']*100:+.1f}% 回撤 {ch['holdout']['metrics']['max_dd']*100:.1f}% "
      f"夏普 {ch['holdout']['metrics']['sharpe']:.2f}) 上任 {ch.get('promoted_at')}")
print("  退休冠军:", [f"{r.get('strategy')}({r.get('score')})" for r in s.get("champion_retired", [])])

codes = list(acc["positions"].keys())
q = spot_quotes_light(codes)
if not q:
    print("!! 行情获取失败"); sys.exit(1)
print(f"\n== 实时持仓（{len(q)}/{len(codes)} 只有行情）==")
tot_mv = 0.0
for code, p in acc["positions"].items():
    d = q.get(code)
    if not d:
        print(f"  {code} 无行情"); continue
    px = d["price"]; mv = px * p["shares"]; tot_mv += mv
    pnl = (px - p["cost"]) * p["shares"]; pct = (px / p["cost"] - 1) * 100
    print(f"  {code} {d.get('name','')} 现价{px} 成本{p['cost']:.3f} ×{p['shares']} "
          f"市值{mv:,.0f} 浮动{pnl:+,.0f} ({pct:+.2f}%)")

eq = tot_mv + acc["cash"]
print(f"\n总市值 {tot_mv:,.0f} | 现金 {acc['cash']:,.2f}")
print(f"实时权益 {eq:,.2f} | 今日开盘基线 {acc['day_start_equity']:,.2f} "
      f"→ 盘中 {(eq/acc['day_start_equity']-1)*100:+.2f}% | 累计 vs 10万本金 {(eq/100000-1)*100:+.2f}%")

# 分仓浮盈：今日带 sleeve 标签的成交归各仓；存量持仓（昨夜迁移）归 S1
sl = s.get("sleeves", [])
if sl:
    print("\n== 分仓实况 ==")
    own = {}
    for t in s.get("trade_log", []):
        if t.get("side") == "buy" and t.get("sleeve"):
            k = (t["sleeve"], t["code"])
            own[k] = own.get(k, 0) + t.get("shares", 0)
    tagged = {c for (_sid, c) in own}
    for sv in sl:
        mv = 0.0
        for (sid, code), sh in own.items():
            if sid == sv["id"] and code in q:
                mv += q[code]["price"] * sh
        if sv["id"] == "S1":  # 存量迁移持仓（未被其他仓今日买入的）归 S1
            for code, p in acc["positions"].items():
                if code not in tagged and code in q:
                    mv += q[code]["price"] * p["shares"]
        s_eq = mv + sv.get("cash", 0)
        base = sv.get("capital_start", s_eq)
        line = sv.get("halt_line")
        line_txt = f"停机线-{int(line*100)}%" if line is not None else "无停机线（亏80%退役）"
        print(f"  {sv['id']} {sv['label']} [{sv['members'][0]['strategy']}] "
              f"权益 {s_eq:,.0f}（起点 {base:,.0f}，{(s_eq/base-1)*100:+.2f}%）{line_txt}")

ar = s["arena"]
print(f"\n== 联赛 ==\n  累计 {ar.get('round')} 局 | 认证池 {len(ar.get('qualified', []))}★ | "
      f"阵容 {len(ar.get('players', []))}人")
