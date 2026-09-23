import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

from quant.data import spot_quotes_light
from quant.decide import account_equity

s = json.load(open("state/state.json", encoding="utf-8"))
acc = s["account"]
pos = acc["positions"]
codes = sorted(pos)
q = spot_quotes_light(codes)
prices = {c: (q.get(c) or {}).get("price", 0.0) for c in codes}
eq = account_equity(s, prices)
print("=== 账户（收盘） ===")
print(f"现金 {acc['cash']:,.0f} | 权益 {eq:,.0f} | 本金 100,000")
print(f"当日浮动 {eq - 100000:+,.0f} ({(eq / 100000 - 1) * 100:+.2f}%)")
buy = {t["code"]: t for t in s.get("trade_log", [])
       if t.get("date") == "20260921" and t.get("side") == "buy"}
print("=== 持仓（今日 09:37 建仓，T+1）===")
deploy = 0.0
for c in codes:
    p = pos[c]
    price = prices[c] or p.get("cost", 0.0)
    pnl = (price - p.get("cost", 0.0)) * p.get("shares", 0)
    pct = ((price / p.get("cost", 1)) - 1) * 100 if p.get("cost") else 0.0
    b = buy.get(c, {})
    deploy += b.get("amount", 0)
    print(f"{c} {q.get(c, {}).get('name', '')}: {p['shares']}股 "
          f"买价{b.get('price')} 现价{price:.2f} 浮动{pnl:+,.0f}（{pct:+.2f}%）")
mv = sum(pos[c]["shares"] * (prices.get(c) or pos[c].get("cost", 0.0)) for c in codes)
print(f"投入 {deploy:,.0f} → 现市值 {mv:,.0f} | 部署仓浮动 {mv - deploy:+,.0f}（{(mv / deploy - 1) * 100 if deploy else 0:+.2f}%）")
print("=== 今日收盘轨道 ===")
for t in (s.get("paper_track") or [])[-3:]:
    print(f"{t.get('date')}: 权益 {float(t.get('equity', 0)):,.0f} | 市值 {float(t.get('market_value', 0)):,.0f} | 持仓 {t.get('n_positions')}")
evo = s.get("evolution", {})
a = s.get("arena", {})
risk = s.get("risk", {})
print("=== 系统 ===")
print(f"GA 第 {evo.get('generation')} 代 | 联赛 {a.get('round')} 局 | 认证 {len(a.get('qualified') or [])} 人")
print(f"团队: " + ", ".join(f"{m.get('strategy')}/{m.get('sizing')}" for m in (s.get("team") or [])))
print(f"风控: halt={risk.get('halt')} | 高水位 {acc.get('equity_high', 0):,.0f}")
