"""真实 state 隔离试运行：分仓制备单全链 dry-run（deepcopy，零落盘）。"""
import copy
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

import quant.decide as decide_mod
import quant.state as state_mod

decide_mod.save_state = lambda s: None  # 隔离：绝不落盘
state_mod.save_state = lambda s: None

from quant.config import load_config
from quant.state import load_state
from quant import sleeves as qsl

cfg = load_config()
state = load_state()
state = copy.deepcopy(state)  # 双保险：深拷贝

print("=== 迁移前 ===")
print(f"现金 {state['account']['cash']:,.0f} | 持仓 {len(state['account']['positions'])} 只 | "
      f"团队 {[m['strategy'] for m in state.get('team') or []]}")

svs = qsl.ensure_sleeves(state, cfg)
print("=== 迁移后三仓 ===")
for sv in svs:
    ms = [m.get("strategy") for m in (sv.get("members") or [])]
    print(f"{sv['id']} {sv['label']}: 成员 {ms} | 现金 {sv['cash']:,.0f} | "
          f"起点 {sv['capital_start']:,.0f}")
print(f"仓现金合计 {sum(sv['cash'] for sv in svs):,.0f} vs 总现金 {state['account']['cash']:,.0f}")
tags = {c: p.get("sleeve") for c, p in state["account"]["positions"].items()}
print(f"持仓仓标: {tags}")

print("=== 备单 dry-run（真实面板+真实认证池成员，约1-2分钟）===")
orders, info = decide_mod.prepare_orders(cfg, state)
print(f"生成订单 {len(orders)} 笔")
by_sleeve: dict = {}
for o in orders:
    by_sleeve.setdefault(o.get("sleeve"), []).append(o)
for sid, os_ in sorted(by_sleeve.items()):
    print(f"{sid}: {len(os_)} 笔")
    for o in os_[:6]:
        print(f"   {o['side']:4s} {o['code']} {o['shares']} 股 ({o.get('reason')})")
    if len(os_) > 6:
        print(f"   … 其余 {len(os_) - 6} 笔")
print("=== 校验 ===")
s1 = [o for o in orders if o.get("sleeve") == "S1"]
s1_buys = sum(o["shares"] for o in s1 if o["side"] == "buy")
print(f"S1 买单总股数 {s1_buys}（应为0：现有5持仓=目标，T+1锁定）")
codes = [o["code"] for o in orders]
print(f"订单标的唯一性: {len(codes) == len(set(codes))}")
print("DRY-RUN 完成（无落盘）")
