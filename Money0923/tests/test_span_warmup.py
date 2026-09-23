"""联赛窗口指标预热缓冲测试（2026-09-21 用户"历史数据下全"配套机制）。

对照实验：250日动量策略（dual_momentum mom_len=250）在252天硬切窗内
只有最后~2天有信号（98%时间持币=结构性失能，进化被迫只选短回看参数）；
带300日预热缓冲后评估窗内全程有持仓。无未来函数不变：指标只用≤当日
数据，预热段不计分。
运行: python tests/test_span_warmup.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import quant.arena as qar  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.data import PanelData  # noqa: E402
from quant.strategies import get_strategy as get_strat  # noqa: E402


def make_panel(n_days: int = 600, n_codes: int = 3) -> PanelData:
    dates = pd.bdate_range("2024-01-02", periods=n_days)
    codes = ["600000", "600519", "510300"][:n_codes]
    idx = np.arange(n_days)
    close = pd.DataFrame({c: 10.0 * (1.0 + 0.002 * idx) for c in codes}, index=dates)
    high = close * 1.01
    low = close * 0.99
    open_ = close * 0.999
    vol = pd.DataFrame({c: np.full(n_days, 1e9) for c in codes}, index=dates)
    amt = pd.DataFrame({c: np.full(n_days, 1e10) for c in codes}, index=dates)
    return PanelData(open=open_, high=high, low=low, close=close,
                     volume=vol, amount=amt, codes=codes, dates=dates)


PARAMS = {"mom_len": 250, "skip_days": 21, "top_k": 1, "abs_floor": 0.0}


def test_long_lookback_unbuffers():
    cfg = AppConfig()
    # 本测试对照"无缓冲=结构性空仓"：逆回购现金计息会给空仓组合+~1.2%/252天，
    # 撑爆"10倍碾压"相对断言——关闸恢复原意（现金收益口径由 test_repo 单独验证）
    cfg.risk.repo_enabled = False
    panel = make_panel()
    dates = panel.dates
    ev_start, ev_end = 348, 599  # 252天评估窗
    player = {"id": "P1", "strategy": "dual_momentum", "params": dict(PARAMS),
              "sizing": "equal", "sizing_params": {}, "capital": 1_000_000.0,
              "style": "均衡"}
    qar._ARENA_CTX["panel"] = panel
    qar._ARENA_CTX["cfg"] = cfg

    # 对照：硬切窗（无预热）——250日动量只在窗末~2天有信号（结构性失能实证）
    raw_win = panel.window(dates[ev_start], dates[ev_end])
    w_direct = get_strat("dual_momentum")().target_weights(raw_win, PARAMS)
    active_rows = int((w_direct.abs() > 1e-12).any(axis=1).sum())
    assert active_rows <= 3, f"无缓冲对照应在窗末才有信号，实际{active_rows}天有持仓"

    # 实验组：span 路径300日预热缓冲 → 评估窗内全程持仓、收益碾压无缓冲对照
    # （绝对值受 50% ETF 上限+15日超时换手×16轮+成本拖累≈8% 机械压制，
    #  故对照口径=倍数碾压，不断言绝对收益）
    res = qar._arena_run_player(player, span=(ev_start, ev_end))
    assert res.get("ok"), f"回测应成功: {res.get('error')}"
    ret = float(res["metrics"]["total_return"])
    from quant.backtest import run_backtest
    res_u = run_backtest(raw_win, w_direct, cfg, start_cash=1_000_000.0)
    ret_u = float(res_u.metrics["total_return"])
    assert ret > max(10.0 * max(ret_u, 0.0), 0.05), \
        f"缓冲收益应碾压无缓冲对照：{ret:+.2%} vs {ret_u:+.2%}"
    print(f"预热缓冲 OK: 无缓冲={active_rows}天持仓/收益{ret_u:+.2%} → "
          f"有缓冲=收益{ret:+.1%}（250日动量在1年窗内解封，全史长周期规律可入场竞争）")


if __name__ == "__main__":
    test_long_lookback_unbuffers()
    print("ALL PASS")
