"""团队同资产类别约束测试（2026-09-21 全品种指令，CTA 自服务架构）。

Evolver._ind_asset_class 分类器 + 团队权重并集合并（fill_value=0）验证：
- cta_trend（通道开+窗口数据）→ 'fut'；通道关 → 空权重
- 纯股票权重 → 'stock'；混合权重 → 'mixed'（团队禁入）
- 股票成员+CTA 成员合成权重：F.* 列=CTA值/N（绝不能是 NaN）
运行: python tests/test_futures_teamclass.py
"""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

import quant.futures as qf  # noqa: E402
import quant.strategies as strat_lib  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.data import PanelData  # noqa: E402
from quant.decide import team_target_weights  # noqa: E402
from quant.evolve import Evolver  # noqa: E402


def make_panel(n: int = 260) -> PanelData:
    """纯股票面板（600000/600519）——CTA 自服务架构下面板永不含 F.* 列。"""
    dates = pd.date_range("2025-01-06", periods=n, freq="B")
    close = pd.DataFrame({"600000": np.full(n, 10.5),
                          "600519": 1600.0 * np.cumprod(1.0 + np.full(n, 0.002))},
                         index=dates)
    op = close.shift(1).fillna(close.iloc[0])
    high, low = close * 1.002, close * 0.998
    volume = pd.DataFrame({c: np.full(n, 1e7) for c in close.columns}, index=dates)
    amount = volume * close
    return PanelData(open=op, high=high, low=low, close=close, volume=volume,
                     amount=amount, codes=list(close.columns), dates=dates)


class _StockStub:
    def target_weights(self, panel, params):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.close.columns)
        w.iloc[-1] = [0.3, 0.15]
        return w


class _MixedStub:
    def target_weights(self, panel, params):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.close.columns)
        w.iloc[-1] = [0.3, 0.15]
        w["F.IF"] = 0.5
        return w


def classify(shim: object, ind: dict) -> str:
    return Evolver._ind_asset_class(shim, ind)  # duck-typed self 直调


def test_asset_class():
    panel = make_panel()
    shim = types.SimpleNamespace(train_panel=panel)
    orig = strat_lib.get_strategy
    orig_gate, orig_fw = qf.futures_enabled, qf.futures_window

    # 纯期货：cta_trend 真实策略 + 通道开 + 自服务窗口数据（F.IF 持续上行 → 末行持多）
    qf.futures_enabled = lambda cfg=None: True
    if_series = 3900.0 * np.cumprod(1.0 + np.full(len(panel.dates), 0.003))
    qf.futures_window = lambda dates: {"F.IF": pd.DataFrame(
        {"open": if_series, "high": if_series, "low": if_series, "close": if_series,
         "volume": np.full(len(dates), 1e5), "amount": 0.0}, index=pd.DatetimeIndex(dates))}
    cta_ind = {"strategy": "cta_trend", "params": {
        "trend_fast": 20, "trend_slow": 60, "entry_len": 20, "exit_len": 10,
        "top_k": 2, "rebal_days": 5, "allow_short": "both"}}
    cls = classify(shim, cta_ind)
    assert cls == "fut", f"cta_trend 应为 fut，实际 {cls}"
    print("cta_trend（自服务通道开）→ fut OK")

    # 通道关：cta_trend 返回空权重 → 股票类（零仓位无害成员）
    qf.futures_enabled = lambda cfg=None: False
    cls = classify(shim, cta_ind)
    assert cls == "stock", f"通道关应为 stock（空权重），实际 {cls}"
    qf.futures_enabled, qf.futures_window = orig_gate, orig_fw
    print("cta_trend（通道关）→ 空权重 OK")

    # 纯股票 / 混合
    strat_lib.get_strategy = lambda name: _StockStub
    assert classify(shim, {"strategy": "zzz", "params": {}}) == "stock"
    strat_lib.get_strategy = lambda name: _MixedStub
    assert classify(shim, {"strategy": "zzz", "params": {}}) == "mixed"
    strat_lib.get_strategy = orig
    print("纯股票 → stock / 混合 → mixed（团队禁入）OK")


def test_team_union_weights():
    """股票成员+CTA 成员合成：F.* 列必须是数值（fill_value=0 并集），绝不能 NaN。"""
    panel = make_panel()
    orig = strat_lib.get_strategy

    class _FutStub:
        def target_weights(self, panel, params):
            w = pd.DataFrame(0.0, index=panel.dates, columns=panel.close.columns)
            w["F.IF"] = 0.5
            return w

    strat_lib.get_strategy = lambda name: (_FutStub if name == "cta" else _StockStub)
    state = {"team": [
        {"strategy": "stk", "params": {}, "sizing": "equal", "sizing_params": {}},
        {"strategy": "cta", "params": {}, "sizing": "equal", "sizing_params": {}},
    ], "champion": None}
    w = team_target_weights(AppConfig(), state, panel)
    strat_lib.get_strategy = orig
    last = w.iloc[-1]
    assert "F.IF" in w.columns, "F.* 列必须在合成权重中"
    assert abs(float(last["F.IF"]) - 0.25) < 1e-9, f"F.IF 应=0.5/2=0.25，实际 {last['F.IF']}"
    assert abs(float(last["600000"]) - 0.15) < 1e-9, last["600000"]
    assert not w.isna().any().any(), "合成权重绝不允许 NaN"
    print("团队权重并集合并 OK: F.IF=0.25 / 600000=0.15（fill_value=0，无 NaN）")


if __name__ == "__main__":
    test_asset_class()
    test_team_union_weights()
    print("test_futures_teamclass 全部通过")
