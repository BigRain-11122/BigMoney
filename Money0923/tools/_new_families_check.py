"""新策略族真实数据健全性检查：末行信号 + 全历史回测指标（防退化族入进化）。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

from quant import data as qdata
from quant import strategies as strat_lib
from quant.backtest import run_backtest
from quant.config import load_config

NEW = ["dragon_head", "limit_down_buy", "ban_open", "strong_close",
       "sub_new", "gamble"]


def mid(spec):
    if spec[0] == "int":
        return (spec[1] + spec[2]) // 2
    if spec[0] == "float":
        return round((spec[1] + spec[2]) / 2, 4)
    return list(spec[1])[0]


cfg = load_config()
_, panel = qdata.full_panel(cfg)
print(f"面板: {len(panel.dates)} 日 × {len(panel.codes)} 标的")
print(f"{'族':12s} {'末行持仓':6s} {'近20日均暴露':10s} {'全史收益':9s} {'回撤':7s} {'夏普':6s} {'成交':5s}")
for name in NEW:
    strat = strat_lib.get_strategy(name)()
    params = {k: mid(v) for k, v in strat.param_space.items()}
    w = strat.target_weights(panel, params)
    last_nz = int((w.iloc[-1] != 0).sum())
    expo = float(w.sum(axis=1).tail(20).mean())
    res = run_backtest(panel, w, cfg)
    m = res.metrics
    print(f"{name:12s} {last_nz:6d} {expo:10.1%} {m['total_return']:9.1%} "
          f"{m['max_dd']:7.1%} {m['sharpe']:6.2f} {m['n_trades']:5d}")
