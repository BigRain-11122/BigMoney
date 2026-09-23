"""当前认证分最高策略的今日目标持仓（只读）。"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, ".")

from quant import data as qdata
from quant import strategies as strat_lib
from quant.sizing import get_sizing
from quant.config import load_config

s = json.load(open("state/state.json", encoding="utf-8"))
q = (s.get("arena") or {}).get("qualified") or []
top = sorted(q, key=lambda x: -float(x.get("score") or 0))[:3]
cfg = load_config()
_, panel = qdata.full_panel(cfg)
uni = qdata.load_universe()
names = dict(zip(uni["code"].astype(str), uni["name"].astype(str)))

for x in top:
    strat = strat_lib.get_strategy(x["strategy"])()
    w = strat.target_weights(panel, x["params"]).astype(float)
    sizer = get_sizing(x.get("sizing") or "equal")()
    w = sizer.apply(w, panel, x.get("sizing_params") or {})
    last = w.iloc[-1]
    picks = {c: round(float(v), 3) for c, v in last.items() if float(v) > 1e-9}
    print(f"\n=== {x['id']} {x['strategy']}/{x.get('sizing')} 认证分 {x.get('score')} ===")
    if picks:
        for c, v in sorted(picks.items(), key=lambda kv: -kv[1]):
            print(f"  {c} {names.get(c, '')} 权重 {v:.1%}")
    else:
        print("  （当前信号：持币空仓）")
