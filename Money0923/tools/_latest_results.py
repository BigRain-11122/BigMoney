import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
s = json.load(open("state/state.json", encoding="utf-8"))
a = s["arena"]
q = a.get("qualified") or []
new = [x for x in q if (x.get("qualified_at") or "") >= "2026-09-21T17:00"]
print(f"今晚 17:00 后新认证 {len(new)} 人:")
for x in new:
    print(f"  {x['id']} {x['strategy']}/{x.get('sizing')} "
          f"score={x.get('score')} @{(x.get('qualified_at') or '')[:16]}")
tr = s.get("trade_log") or []
acc = s["account"]
print(f"账户: 现金 {acc['cash']:.0f} | 持仓 {len(acc['positions'])} 只 | "
      f"今日成交 {len([t for t in tr if t.get('date') == '20260921'])} 笔")
