"""仓位控制策略层（可进化基因）。

分工：策略层决定"买什么"（选择权重），仓位控制层决定"买多少"（缩放权重）。
个体基因 = {strategy, params, sizing, sizing_params}，两层一起被 GA 进化。
执行顺序：策略权重 → 仓位控制缩放 → 引擎层资产上限截断（用户红线优先于任何仓位意图）。
全部只用 ≤t 日数据（滚动计算，无未来函数）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import indicators as ind
from .data import PanelData

SIZING: dict[str, type["SizingPolicy"]] = {}


def register_sizing(cls):
    SIZING[cls.name] = cls
    return cls


def get_sizing(name: str) -> "type[SizingPolicy]":
    name = name or "equal"
    if name not in SIZING:
        raise KeyError(f"未知仓位策略 {name}，可选: {list(SIZING)}")
    return SIZING[name]


class SizingPolicy:
    name: str = "base"
    param_space: dict[str, tuple] = {}

    def apply(self, w: pd.DataFrame, panel: PanelData, p: dict) -> pd.DataFrame:
        raise NotImplementedError


@register_sizing
class EqualSizing(SizingPolicy):
    """等权：不缩放（基线，各选中标的均分）。"""
    name = "equal"
    param_space = {}

    def apply(self, w, panel, p):
        return w


@register_sizing
class InvVol(SizingPolicy):
    """波动率倒数（风险平价式）：选中标的中低波者配更多，总暴露不变。"""
    name = "inv_vol"
    param_space = {"vol_win": ("int", 10, 60)}

    def apply(self, w, panel, p):
        vol = ind.ann_vol(panel.close, int(p["vol_win"]))
        inv = 1.0 / vol.replace(0.0, np.nan)
        sel = w > 0
        tilted = inv.where(sel)
        ssum = tilted.sum(axis=1)
        norm = tilted.div(ssum.where(ssum > 0), axis=0)
        out = norm.mul(w.sum(axis=1), axis=0)
        return out.fillna(0.0)


@register_sizing
class VolTarget(SizingPolicy):
    """组合波动率目标（择时性仓位控制）：总暴露 = clip(目标波动 / 市场近端年化波动, 下限, 1.0)，
    等比缩放全部选中权重——市场越动荡仓位越轻，波动回落仓位回升。"""
    name = "vol_target"
    param_space = {"target_vol": ("float", 0.05, 0.35), "vol_win": ("int", 10, 60),
                   "min_exp": ("choice", [0.0, 0.2, 0.4])}

    def apply(self, w, panel, p):
        mkt = ind.universe_index(panel.close)
        mkt_vol = mkt.pct_change().rolling(int(p["vol_win"]), min_periods=int(p["vol_win"])).std() * np.sqrt(252)
        exposure = (float(p["target_vol"]) / mkt_vol.replace(0.0, np.nan)).clip(float(p["min_exp"]), 1.0)
        exposure = exposure.fillna(0.0)  # 波动未知的早期保守空仓
        total = w.sum(axis=1)
        ratio = (exposure / total.where(total > 0)).fillna(0.0)
        return w.mul(ratio, axis=0).clip(lower=0.0)


@register_sizing
class MaRisk(SizingPolicy):
    """市场状态仓位：等权指数站上均线→满配（×1.0），跌破→缩至 risk_off 比例。"""
    name = "ma_risk"
    param_space = {"ma_len": ("int", 20, 250), "risk_off": ("choice", [0.0, 0.2, 0.4, 0.6])}

    def apply(self, w, panel, p):
        mkt = ind.universe_index(panel.close)
        ma = mkt.rolling(int(p["ma_len"]), min_periods=1).mean()
        scale = pd.Series(np.where(mkt >= ma, 1.0, float(p["risk_off"])), index=w.index)
        return w.mul(scale, axis=0)
