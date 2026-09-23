"""市场风格引擎 + 模型近期验证（学习"现在的市场"，每晚备单前自动运行）。

风格识别（近 regime_lookback 日，默认60）：
- trend: 等权指数 vs MA20/MA60 → 趋势上行 / 趋势下行 / 震荡
- vol:   实现波动率在近一年分位 → 高波 / 低波
- breadth: 股票池站上MA20比例 → 市场宽度
- size_style: 510300 vs 510500/512100 相对强弱 → 大盘占优 / 小盘占优
- factor_style: 近20日横截面动量IC（5日动量对后续5日收益的Spearman秩相关）
  → 动量有效 / 反转有效 / 中性（纯历史计算，无未来函数）

模型验证（每晚）：
- 冠军近 recent_days（默认40）交易日的滚动表现（holdout 内最新段，样本外性质）
- 11个经典策略族在同一窗口的适配度排名 → "当前什么有效"的学习结论
- 错配（冠军明显跑输最适族）→ 置曝光系数 + GA移民偏向最适族
- 敌对风格（震荡+高波+冠军近期亏损）→ 曝光系数减半

风格只调节"暴露意愿"与"进化方向"，永不越过用户风控红线（仓位15%/ETF50%/2周/熔断照常生效）。
"""
from __future__ import annotations

import datetime as dt
import logging

import numpy as np
import pandas as pd

from . import indicators as ind
from . import strategies as strat_lib
from .backtest import run_backtest
from .config import AppConfig
from .evolve import GA_SEEDS
from .state import save_state

log = logging.getLogger("quant.regime")


def _rowwise_rank_corr(a: pd.DataFrame, b: pd.DataFrame) -> pd.Series:
    """逐行 Spearman 秩相关（横截面因子 IC 用的向量化实现）。"""
    ra = a.rank(axis=1)
    rb = b.rank(axis=1)
    za = ra.sub(ra.mean(axis=1), axis=0)
    zb = rb.sub(rb.mean(axis=1), axis=0)
    denom = np.sqrt((za ** 2).sum(axis=1) * (zb ** 2).sum(axis=1))
    return ((za * zb).sum(axis=1) / denom.replace(0.0, np.nan)).fillna(0.0)


def detect_regime(panel, cfg: AppConfig) -> dict:
    """识别当前市场风格快照。"""
    lookback = getattr(cfg.meta, "regime_lookback", 60)
    close = panel.close
    idx = ind.universe_index(close)
    if len(idx) < 120:
        raise ValueError("数据不足以做风格识别（需≥120个交易日）")
    lb = min(lookback, len(idx) - 1)

    # —— 趋势：等权指数 vs MA20/MA60 ——
    ma20 = idx.rolling(20).mean()
    ma60 = idx.rolling(60).mean()
    last, m20, m60 = idx.iloc[-1], ma20.iloc[-1], ma60.iloc[-1]
    m20_slope = m20 / ma20.iloc[-21] - 1.0 if len(ma20.dropna()) > 21 else 0.0
    if last > m20 and m20_slope > 0.01:
        trend = "趋势上行"
    elif last < m20 and m20_slope < -0.01:
        trend = "趋势下行"
    else:
        trend = "震荡"

    # —— 波动率分位（实现波动 vs 近252日）——
    ret = idx.pct_change().fillna(0.0)
    vol = ret.rolling(20).std() * np.sqrt(252)
    vol_now = float(vol.iloc[-1])
    vol_pct = float(vol.iloc[-252:].rank(pct=True).iloc[-1]) if vol.notna().sum() > 30 else 0.5

    # —— 市场宽度：站上MA20比例 ——
    ma20x = close.rolling(20, min_periods=20).mean()
    breadth = float((close > ma20x).sum(axis=1).iloc[-1] / close.notna().sum(axis=1).iloc[-1])

    # —— 大小盘风格：510300 vs 510500/512100 相对强弱 ——
    size_style = None
    big = "510300" if "510300" in panel.codes else None
    small = next((c for c in ("510500", "512100", "560010") if c in panel.codes), None)
    if big and small:
        rel = close[small] / close[big]
        rel_ret = float(rel.iloc[-1] / rel.iloc[-21] - 1.0) if len(rel.dropna()) > 21 else 0.0
        size_style = "小盘占优" if rel_ret > 0.02 else ("大盘占优" if rel_ret < -0.02 else "均衡")

    # —— 因子有效性：近20日横截面动量IC（t-5 的5日动量 → t-5→t 收益的已实现秩相关）——
    mom5 = ind.roc(close, 5)
    ic_series = _rowwise_rank_corr(mom5.shift(5), mom5)
    mom_ic = float(ic_series.iloc[-20:].mean())
    factor_style = "动量有效" if mom_ic > 0.05 else ("反转有效" if mom_ic < -0.05 else "因子中性")

    return {
        "date": dt.date.today().isoformat(),
        "trend": trend, "vol_pct": round(vol_pct, 3), "vol_high": vol_pct > 0.7,
        "vol_now": round(vol_now, 3), "breadth": round(breadth, 3),
        "size_style": size_style, "mom_ic": round(mom_ic, 3), "factor_style": factor_style,
    }


def regime_step(cfg: AppConfig, state: dict, panel) -> dict:
    """每晚模型验证闭环：风格识别 → 冠军近段验证 → 族适配度 → 曝光系数/进化提示。

    写 state["regime"]，返回快照。错配只降"暴露意愿"并给进化指路，
    用户风控红线（15%/ETF50%/2周/熔断）照常硬性生效。
    """
    snap = detect_regime(panel, cfg)
    mc = cfg.meta
    recent_n = int(getattr(mc, "recent_days", 40))
    recent_n = min(recent_n, len(panel.dates) - 10)

    champ = state.get("champion")
    champ_recent: dict | None = None
    best_seed: dict | None = None

    if recent_n >= 20:
        sub = panel.window(panel.dates[-recent_n], panel.dates[-1])

        def _recent_perf(ind):
            strat = strat_lib.get_strategy(ind["strategy"])()
            w = strat.target_weights(panel, ind["params"])
            res = run_backtest(sub, w, cfg)
            return {"family": ind["strategy"],
                    "sharpe": round(float(res.metrics["sharpe"]), 3),
                    "ret": round(float(res.metrics["total_return"]), 4)}

        # ① 冠军近段验证（holdout 内最新段）
        if champ:
            champ_recent = _recent_perf({"strategy": champ["strategy"], "params": champ["params"]})
        # ② 经典族适配度排名（学习"现在什么有效"）
        perfs = [_recent_perf(s) for s in GA_SEEDS]
        perfs.sort(key=lambda x: x["sharpe"], reverse=True)
        best_seed = perfs[0]

    # ③ 错配与敌对判定
    mismatch = False
    hostile = False
    if champ_recent and best_seed:
        mismatch = (champ_recent["sharpe"] < best_seed["sharpe"] - 0.3
                    and best_seed["family"] != champ["strategy"])
        hostile = (snap["trend"] == "震荡" and snap["vol_high"] and champ_recent["sharpe"] < 0)

    scale = 1.0
    if hostile:
        scale = float(getattr(mc, "hostile_scale", 0.5))
    elif mismatch:
        scale = float(getattr(mc, "mismatch_scale", 0.6))
    # 随机取点体检防御态（每日体检置位）：无论风格如何判定，曝光不高于0.5，
    # 直至体检通过或新冠军上位（清除标志）。体检结论优先级高于风格引擎。
    if state.get("meta", {}).get("stress_defense"):
        scale = min(scale, 0.5)

    st_regime = state.setdefault("regime", {})
    st_regime["snapshot"] = {**snap, "champion_recent": champ_recent,
                             "best_family_now": best_seed, "exposure_scale": scale,
                             "mismatch": mismatch, "hostile": hostile,
                             "checked_at": dt.datetime.now().isoformat(timespec="seconds")}
    st_regime["exposure_scale"] = scale
    st_regime["hint_family"] = best_seed["family"] if (mismatch and best_seed) else None
    st_regime.setdefault("history", []).append({
        "date": snap["date"], "trend": snap["trend"], "factor_style": snap["factor_style"],
        "champion_recent": champ_recent, "best_family_now": best_seed,
        "scale": scale, "mismatch": mismatch,
    })
    st_regime["history"] = st_regime["history"][-250:]
    save_state(state)

    log.info("【风格快照】%s | %s | 波动分位%.0f%% | %s | %s%s",
             snap["trend"], snap["factor_style"], snap["vol_pct"] * 100,
             f"{snap['size_style'] or '大小盘均衡'}",
             f"冠军近{recent_n}日 夏普{champ_recent['sharpe'] if champ_recent else '-'}",
             f" | 当前最适族: {best_seed['family']}(夏普{best_seed['sharpe']})" if best_seed else "")
    if mismatch:
        log.warning("【风格错配】冠军近段跑输 %s → 曝光×%.1f，GA移民偏向该族加速换血",
                    best_seed["family"], scale)
    if hostile:
        log.warning("【敌对风格】震荡+高波+冠军近段亏损 → 曝光×%.1f（防御态）", scale)
    return st_regime["snapshot"]
