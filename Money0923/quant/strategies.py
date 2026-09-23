"""策略库：策略 = 信号逻辑 + 可进化参数空间，供遗传算法搜索。

统一接口：target_weights(panel, params) -> DataFrame(dates×codes)
- 值为该日收盘决策出的目标权重（[0,1]），回测/实盘在次日开盘执行
- 第 t 行只允许使用 ≤t 的数据（严禁未来函数）
- 权重执行时被风控分资产截断（股票15%/ETF 50%）

顶层：Evolved 进化策略（GP-lite）——入场/离场结构的基因组本身参与遗传进化，
策略空间不再局限于固定模板。
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from . import indicators as ind
from .data import PanelData, is_etf

STRATEGIES: dict[str, type["Strategy"]] = {}


def register(cls):
    STRATEGIES[cls.name] = cls
    return cls


def get_strategy(name: str) -> "type[Strategy]":
    if name not in STRATEGIES:
        raise KeyError(f"未知策略 {name}，可选: {list(STRATEGIES)}")
    return STRATEGIES[name]


class Strategy:
    name: str = "base"
    param_space: dict[str, tuple] = {}  # {"参数": ("int", lo, hi) | ("float", lo, hi) | ("choice", [...])}

    def target_weights(self, panel: PanelData, params: dict) -> pd.DataFrame:
        raise NotImplementedError


# ---------------------------------------------------------------- 辅助函数

def _assemble(hold: pd.DataFrame, score: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """hold 为 True 的标的中按 score 降序选 top_k 只，等权各 1/top_k（不满员则留现金）。"""
    masked = score.where(hold)
    ranks = masked.rank(axis=1, ascending=False)
    sel = ranks.notna() & ranks.le(top_k)
    w = sel.astype(float) / float(max(1, top_k))
    return w.fillna(0.0)


def _state_hold(entry: pd.DataFrame, exit_cond: pd.DataFrame, score: pd.DataFrame,
                top_k: int, max_hold: int | None = None) -> pd.DataFrame:
    """状态机持仓：entry 触发（按 score 选 top_k），exit 平仓，max_hold 为最长持有信号日数。

    entry/exit 均为收盘信号；实际成交由回测引擎在次日开盘完成。
    当日刚触发离场信号的标的当日不得再入场（防滞回消失，因子专家审查#7）。
    """
    E = entry.fillna(False).to_numpy(dtype=bool)
    X = exit_cond.fillna(False).to_numpy(dtype=bool)
    S = score.to_numpy(dtype=float)
    n, m = E.shape
    hold = np.zeros((n, m), dtype=bool)
    days = np.zeros((n, m), dtype=np.int32)
    for i in range(1, n):
        keep = hold[i - 1] & ~X[i]
        if max_hold is not None:
            keep &= days[i - 1] + 1 <= max_hold
        new = np.zeros(m, dtype=bool)
        slots = top_k - int(keep.sum())
        if slots > 0:
            cand = E[i] & ~keep & ~X[i]  # 当日退出者不得当日再入场
            if cand.any():
                s = np.where(cand, S[i], np.nan)
                finite = int(np.isfinite(s).sum())
                if slots >= finite:
                    new = cand
                else:
                    order = np.argsort(np.nan_to_num(s, nan=-1e18))[::-1][:slots]
                    new[order] = True
        hold[i] = keep | new
        days[i] = np.where(keep, days[i - 1] + 1, 0)
    return pd.DataFrame(hold, index=entry.index, columns=entry.columns)


def _rebalance_series(dates: pd.DatetimeIndex, step: int) -> pd.Series:
    """重平衡日历：锚定绝对 ISO 周（每 N 周的第一个交易日调仓，N=max(1, round(step/5))）。

    不能用"日历ordinal取模"——余数0可能恰好永远落在周末导致永不触发（实测发现）。
    ISO 周锚定保证训练/回放/实盘口径一致且必然触发。
    """
    iso = pd.Index(dates).isocalendar()
    wk = np.asarray(iso.week, dtype=np.int64)
    weeks = max(1, int(round(step / 5.0)))
    first_of_week = np.r_[True, np.diff(wk) != 0]
    return pd.Series(first_of_week & (wk % weeks == 0), index=dates)


def sanitize_params(name: str, params: dict) -> dict:
    """参数依赖约束（防病态区，因子专家审查#7）：采样/交叉/变异后统一过滤。

    dual_ma: 快线必须低于慢线5日以上（防反向假趋势）
    rsrs: 离场阈值必须低于买入阈值0.3以上（保滞回）
    """
    if name == "dual_ma":
        params["slow_ma"] = max(int(params["slow_ma"]), int(params["fast_ma"]) + 5)
    elif name == "rsrs":
        params["exit_z"] = round(min(float(params["exit_z"]), float(params["buy_z"]) - 0.3), 4)
    return params


# ---------------------------------------------------------------- 策略实现

@register
class DualMA(Strategy):
    """双均线趋势：快线在慢线上方持有，按60日动量取优。"""
    name = "dual_ma"
    param_space = {"fast_ma": ("int", 5, 30), "slow_ma": ("int", 20, 120), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        hold = ind.sma(panel.close, p["fast_ma"]) > ind.sma(panel.close, p["slow_ma"])
        return _assemble(hold, ind.roc(panel.close, 60), p["top_k"])


@register
class Momentum(Strategy):
    """动量轮动：每 rebal_days 日重选前 top_k 强者，skip_days 跳过近段（Jegadeesh-Titman 12-1 式），
    可选等权指数均线过滤。"""
    name = "momentum"
    param_space = {"lookback": ("int", 20, 250), "skip_days": ("int", 0, 20),
                   "top_k": ("int", 2, 10),
                   "rebal_days": ("int", 3, 10), "ma_filter_len": ("int", 0, 250)}

    def target_weights(self, panel, p):
        close = panel.close
        skip = int(p.get("skip_days", 0))
        if skip > 0:
            mom = close.shift(skip) / close.shift(skip + int(p["lookback"])) - 1.0
        else:
            mom = ind.roc(close, p["lookback"])
        ranks = mom.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(p["top_k"]) & ranks.notna()).where(rebal).ffill().fillna(False)
        w = sel.astype(float) / float(p["top_k"])
        if p["ma_filter_len"] > 0:
            mkt = ind.universe_index(panel.close)
            ma = mkt.rolling(p["ma_filter_len"], min_periods=1).mean()
            w = w.mul((mkt > ma).astype(float), axis=0)
        return w.where(panel.close.notna(), 0.0)


@register
class MeanRev(Strategy):
    """RSI 均值回归：趋势上方超卖入场，RSI 回升或超时离场，最超卖者优先。"""
    name = "mean_rev"
    param_space = {"rsi_len": ("int", 2, 10), "entry_th": ("int", 5, 35), "exit_th": ("int", 45, 90),
                   "trend_ma": ("int", 50, 250), "max_hold": ("int", 3, 10), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        r = ind.rsi(close, p["rsi_len"])
        entry = (close > ind.sma(close, p["trend_ma"])) & (r < p["entry_th"])
        exit_cond = r > p["exit_th"]
        hold = _state_hold(entry, exit_cond, -r, p["top_k"], max_hold=p["max_hold"])
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class Donchian(Strategy):
    """唐奇安通道突破：收盘创 entry_len 日新高入场，跌破 exit_len 日新低离场。"""
    name = "donchian"
    param_space = {"entry_len": ("int", 20, 80), "exit_len": ("int", 5, 40), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close, high, low = panel.close, panel.high, panel.low
        entry = close > ind.roll_max(high, p["entry_len"]).shift(1)
        exit_cond = close < ind.roll_min(low, p["exit_len"]).shift(1)
        hold = _state_hold(entry, exit_cond, ind.roc(close, 20), p["top_k"])
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class EtfTrend(Strategy):
    """ETF 轮动：只交易 ETF 列，动量为正且站上均线者中取前 top_k。"""
    name = "etf_trend"
    param_space = {"mom_len": ("int", 20, 120), "top_k": ("int", 2, 5), "ma_len": ("int", 20, 250)}

    def target_weights(self, panel, p):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        etf_cols = [c for c in panel.codes if is_etf(c)]
        if not etf_cols:
            return w
        sub = panel.close[etf_cols]
        mom = ind.roc(sub, p["mom_len"])
        hold = (mom > 0) & (sub > ind.sma(sub, p["ma_len"]))
        w[etf_cols] = _assemble(hold, mom, p["top_k"])
        return w


@register
class MultiFactor(Strategy):
    """多因子打分：动量 + 短期反转 + 低波动 + 趋势，横截面排名加权后轮动。"""
    name = "multifactor"
    param_space = {"w_mom": ("float", 0.0, 1.0), "w_rev": ("float", 0.0, 1.0),
                   "w_lowvol": ("float", 0.0, 1.0), "w_trend": ("float", 0.0, 1.0),
                   "lookback": ("int", 20, 120), "top_k": ("int", 3, 10),
                   "rebal_days": ("int", 5, 10)}

    def target_weights(self, panel, p):
        close = panel.close

        def cs(df):  # 横截面百分位排名
            return df.rank(axis=1, pct=True)

        composite = (p["w_mom"] * cs(ind.roc(close, p["lookback"]))
                     + p["w_rev"] * cs(-ind.roc(close, 5))
                     + p["w_lowvol"] * cs(-ind.ann_vol(close, 60))
                     + p["w_trend"] * cs((close > ind.sma(close, 120)).astype(float)))
        ranks = composite.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(p["top_k"]) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


# ================ 经典公开模型策略（"拿别人成功的模型去推论"） ================

def _first_col(panel: PanelData, candidates: list[str]) -> str | None:
    """按候选顺序取面板中第一个存在的列（如沪深300类ETF）。"""
    for c in candidates:
        if c in panel.codes:
            return c
    return None


@register
class Rotation28(Strategy):
    """二八轮动（A股经典公开轮动框架，短线20日版）：
    比较沪深300类ETF与中证500类ETF动量，持强弃弱，双弱持币。
    出处：国内量化社区广泛流传的大小盘轮动模型。"""
    name = "rotation_28"
    param_space = {"lookback": ("int", 5, 60), "cash_mom": ("choice", [-0.02, 0.0, 0.02])}

    def target_weights(self, panel, p):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        hs = _first_col(panel, ["510300", "510310", "159919"])   # 沪深300类
        zz = _first_col(panel, ["510500", "512500", "159619", "560010"])  # 中证500/1000类
        if not hs or not zz:
            return w
        close = panel.close[[hs, zz]]
        mom = ind.roc(close, p["lookback"])
        m_h, m_z = mom[hs], mom[zz]
        w[hs] = ((m_h >= m_z) & (m_h > p["cash_mom"])).astype(float)
        w[zz] = ((m_z > m_h) & (m_z > p["cash_mom"])).astype(float)
        return w.where(panel.close.notna(), 0.0)


@register
class DualMomentum(Strategy):
    """双动量（Gary Antonacci《Dual Momentum Investing》2014）：
    ETF池内相对动量选最强 top_k，绝对动量过滤（动量低于阈值不持）。"""
    name = "dual_momentum"
    param_space = {"mom_len": ("int", 20, 250), "skip_days": ("int", 0, 21),
                   "top_k": ("int", 2, 4), "abs_floor": ("choice", [-0.05, -0.02, 0.0, 0.02])}

    def target_weights(self, panel, p):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        etf_cols = [c for c in panel.codes if is_etf(c)]
        if not etf_cols:
            return w
        sub = panel.close[etf_cols]
        skip = int(p.get("skip_days", 0))
        mom = sub.shift(skip) / sub.shift(skip + int(p["mom_len"])) - 1.0 if skip > 0 \
            else ind.roc(sub, p["mom_len"])
        hold = mom.gt(p["abs_floor"])
        w[etf_cols] = _assemble(hold, mom, p["top_k"])
        return w


@register
class RsrsTiming(Strategy):
    """RSRS 阻力支撑相对强度择时（出处：光大证券金融工程 2017 公开研报）：
    目标ETF的 N 日 high~low 回归斜率 z-score 上穿买入阈值持有，下穿离场阈值清仓。"""
    name = "rsrs"
    param_space = {"window": ("int", 10, 40), "zscore_win": ("int", 200, 300),
                   "buy_z": ("float", 0.3, 1.5), "exit_z": ("float", -1.0, 0.5),
                   "target": ("choice", ["510300", "510310", "159919", "510500", "512100"])}

    def target_weights(self, panel, p):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        target = p.get("target", "510300")
        if target not in panel.codes:
            return w
        beta = ind.rsrs_beta(panel.high[[target]], panel.low[[target]], p["window"])[target]
        z = ind.zscore(beta, p["zscore_win"])
        entry = (z > p["buy_z"]).to_frame(target)
        exit_cond = (z < p["exit_z"]).to_frame(target)
        hold = _state_hold(entry, exit_cond, entry.astype(float), top_k=1)
        w[target] = hold[target].astype(float)
        return w.where(panel.close.notna(), 0.0)


@register
class LowVol(Strategy):
    """低波动异象（Baker & Haugen 2012；学术长验证的 BAB 系因子）：
    持有 vol_win 日年化波动最低的前 top_k，每 rebal_days 日轮动。"""
    name = "low_vol"
    param_space = {"vol_win": ("int", 20, 120), "top_k": ("int", 2, 10),
                   "rebal_days": ("int", 3, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        score = -ind.ann_vol(close, p["vol_win"])  # 波动越低分越高
        ranks = score.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(p["top_k"]) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class SmallReversal(Strategy):
    """小市值反转（A股最著名的公开策略族：小市值+短期反转效应）。
    全池按 rev_len 日跌幅最深者取前 top_k（反转在中小票最强），
    mom_filter 为要求近 mom_win 日动量不低于阈值（0=关）。小票端由
    universe 的中证1000尾部池提供，滑点分档×2 已在撮合层诚实计费。"""
    name = "small_reversal"
    param_space = {"rev_len": ("int", 3, 20), "top_k": ("int", 2, 10),
                   "rebal_days": ("int", 3, 10), "mom_win": ("int", 0, 60),
                   "mom_filter": ("float", -0.1, 0.1)}

    def target_weights(self, panel, p):
        close = panel.close
        rev = -ind.roc(close, p["rev_len"])  # 近期跌得越深分越高
        if int(p.get("mom_win", 0)) > 0:
            rev = rev.where(ind.roc(close, int(p["mom_win"])) >= float(p["mom_filter"]))
        ranks = rev.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(p["top_k"]) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class SectorMomentum(Strategy):
    """行业ETF动量轮动（机构常用行业轮动框架）：ETF池（行业/主题/宽基/商品）
    按 mom_len 日动量取前 top_k，每 rebal_days 日轮动，可选动量阈值过滤。"""
    name = "sector_momentum"
    param_space = {"mom_len": ("int", 10, 120), "top_k": ("int", 2, 4),
                   "rebal_days": ("int", 3, 10), "mom_floor": ("choice", [-0.05, -0.02, 0.0, 0.02])}

    def target_weights(self, panel, p):
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        etf_cols = [c for c in panel.codes if is_etf(c)]
        if not etf_cols:
            return w
        sub = panel.close[etf_cols]
        mom = ind.roc(sub, p["mom_len"])
        ranks = mom.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(p["top_k"]) & ranks.notna() & mom.gt(p["mom_floor"])) \
            .where(rebal).ffill().fillna(False)
        w[etf_cols] = (sel.astype(float) / float(p["top_k"]))
        return w.where(panel.close.notna(), 0.0)


# ================ 量价短线族（因子专家审查#9：短线约束下A股实证信息量最高的模式） ================

def _vol_ratio(volume: pd.DataFrame) -> pd.DataFrame:
    """量比：当日成交量 / 前20日均量（不含当日，无未来函数）。"""
    return volume / volume.rolling(20, min_periods=5).mean().shift(1)


@register
class LimitUpMomentum(Strategy):
    """涨停/大阳线次日动量（A股短线实证：强势K线隔日延续效应）。

    当日涨幅≥chg_th 且 量比≥vol_ratio 且 非一字板（一字买不到）触发，
    固定持有 hold_days 日离场。次日开盘若已一字涨停，引擎会真实拒单——
    这正是该效应在实盘的可执行边界。
    """
    name = "limitup_mom"
    param_space = {"chg_th": ("float", 0.04, 0.099), "hold_days": ("int", 2, 8),
                   "top_k": ("int", 7, 8), "vol_ratio": ("float", 1.0, 3.0)}

    def target_weights(self, panel, p):
        close = panel.close
        chg = close / close.shift(1) - 1.0
        vr = _vol_ratio(panel.volume)
        not_sealed = panel.high != panel.low  # 一字板买不进
        entry = (chg >= p["chg_th"]) & (vr >= p["vol_ratio"]) & not_sealed
        exit_cond = pd.DataFrame(False, index=panel.dates, columns=panel.codes)
        hold = _state_hold(entry, exit_cond, chg, p["top_k"], max_hold=int(p["hold_days"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class GapMomentum(Strategy):
    """隔夜跳空延续（短线量价模式）：高开 gap_th 以上、收盘守住开盘、量比确认，
    固定持有 hold_days 日。"""
    name = "gap_mom"
    param_space = {"gap_th": ("float", 0.01, 0.05), "hold_days": ("int", 2, 8),
                   "top_k": ("int", 7, 8), "vol_ratio": ("float", 0.5, 2.5)}

    def target_weights(self, panel, p):
        close = panel.close
        gap = panel.open / close.shift(1) - 1.0
        vr = _vol_ratio(panel.volume)
        entry = (gap >= p["gap_th"]) & (panel.close >= panel.open) & (vr >= p["vol_ratio"])
        exit_cond = pd.DataFrame(False, index=panel.dates, columns=panel.codes)
        hold = _state_hold(entry, exit_cond, gap, p["top_k"], max_hold=int(p["hold_days"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


# ================ 经典公式族（显式数学公式驱动 + 理性仓位，2026-09-19 增量会话） ================

def _apply_weighting(sel: pd.DataFrame, close: pd.DataFrame, vol_win: int,
                     mode: str, top_k: int) -> pd.DataFrame:
    """权重公式（理性仓位）：equal=等权1/N；inv_vol=反波动率加权 w_i ∝ 1/σ_i
    （风险平价思想，高波动标的自动降权）。单票上限由引擎/风控层统一截断。"""
    if str(mode) == "inv_vol":
        vol = ind.ann_vol(close, vol_win)
        inv = (1.0 / vol.replace(0.0, np.nan)).where(sel)
        total = inv.sum(axis=1).replace(0.0, np.nan)
        return inv.div(total, axis=0).fillna(0.0).clip(upper=1.0)
    return sel.astype(float) / float(max(1, top_k))


@register
class MacdTrend(Strategy):
    """MACD 公式趋势（经典）：DIF = EMA(fast) - EMA(slow)；DEA = EMA(DIF, signal)。
    DIF>DEA 金叉态持有，可选 DIF>0 零轴确认；按20日动量取优。"""
    name = "macd_trend"
    param_space = {"fast": ("int", 8, 16), "slow": ("int", 20, 32), "signal": ("int", 5, 12),
                   "need_positive": ("choice", [0, 1]), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        dif, dea, _ = ind.macd(panel.close, p["fast"], p["slow"], p["signal"])
        hold = dif > dea
        if p.get("need_positive", 1):
            hold = hold & (dif > 0)
        return _assemble(hold, ind.roc(panel.close, 20), p["top_k"])


@register
class KdjReversal(Strategy):
    """KDJ 公式超卖回归（中国市场经典指标）：
    RSV=(C-Ln)/(Hn-Ln)×100；K=SMA(RSV,3,1)；D=SMA(K,3,1)；J=3K-2D。
    J<entry_j 超卖触发、J>exit_j 离场，趋势均线过滤，最长持有 max_hold 日。"""
    name = "kdj_rev"
    param_space = {"kdj_n": ("int", 5, 20), "entry_j": ("float", -10.0, 25.0),
                   "exit_j": ("float", 40.0, 100.0), "trend_ma": ("int", 50, 250),
                   "max_hold": ("int", 3, 10), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        j = ind.kdj(panel.high, panel.low, close, int(p["kdj_n"]))
        entry = (close > ind.sma(close, p["trend_ma"])) & (j < p["entry_j"])
        exit_cond = j > p["exit_j"]
        hold = _state_hold(entry, exit_cond, -j, p["top_k"], max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class BollingerRev(Strategy):
    """布林带 Z 分数回归（公式）：z = (C - SMA(n)) / σ(n)。
    z < -entry_z 统计性偏离触发，z 回升过 exit_z 离场；趋势过滤 + 最长持有。"""
    name = "boll_rev"
    param_space = {"n": ("int", 10, 60), "entry_z": ("float", 1.0, 3.0),
                   "exit_z": ("float", 0.0, 1.0), "trend_ma": ("int", 50, 250),
                   "max_hold": ("int", 3, 10), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        z = ind.zscore(close, int(p["n"]))
        entry = (close > ind.sma(close, p["trend_ma"])) & (z < -p["entry_z"])
        exit_cond = z > p["exit_z"]
        hold = _state_hold(entry, exit_cond, -z, p["top_k"], max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class VolAdjMomentum(Strategy):
    """波动率调整动量（夏普式公式）：score = R(lookback) / σ_ann(vol_win)，
    单位风险收益排序的理性动量；权重模式可进化（等权 / 反波动率）。"""
    name = "vol_mom"
    param_space = {"lookback": ("int", 20, 120), "vol_win": ("int", 20, 90),
                   "top_k": ("int", 2, 10), "rebal_days": ("int", 3, 10),
                   "weighting": ("choice", ["equal", "inv_vol"])}

    def target_weights(self, panel, p):
        close = panel.close
        mom = ind.roc(close, int(p["lookback"]))
        vol = ind.ann_vol(close, int(p["vol_win"]))
        score = (mom / vol.replace(0.0, np.nan)).where(close.notna())
        ranks = score.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, int(p["rebal_days"]))
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        return _apply_weighting(sel, close, int(p["vol_win"]),
                                p.get("weighting", "equal"), int(p["top_k"]))


@register
class CtaTrend(Strategy):
    """CTA 期货趋势（用户指令2026-09-21"期货/基金/股票全品种"）：
    自服务数据通道（futures.futures_window 按窗口对齐，面板永不并入 F.* 列——
    防股票策略把期货当"低波股"选）；通道闸 cfg.universe.enable_futures 关闭=空仓。
    多空双向——趋势过滤（快/慢均线）+ 通道突破入场 + 反向通道离场；方向=趋势向上
    做多/向下做空，截面取动量最强的 top_k 品种。负权重=空头（期货分支保证金撮合）。"""
    name = "cta_trend"
    param_space = {"trend_fast": ("int", 5, 40), "trend_slow": ("int", 30, 200),
                   "entry_len": ("int", 10, 60), "exit_len": ("int", 5, 30),
                   "top_k": ("int", 1, 4), "rebal_days": ("int", 3, 10),
                   "allow_short": ("choice", ["long", "both"])}

    def target_weights(self, panel, p):
        from .futures import futures_enabled, futures_window
        empty_cols = list(panel.close.columns)
        if not futures_enabled():
            return pd.DataFrame(0.0, index=panel.dates, columns=empty_cols)
        fut = futures_window(panel.dates)
        fut_cols = [c for c in fut if c not in empty_cols]
        if not fut_cols:
            return pd.DataFrame(0.0, index=panel.dates, columns=empty_cols)
        close = pd.DataFrame({c: fut[c]["close"] for c in fut_cols})
        fast = ind.sma(close, int(p["trend_fast"]))
        slow = ind.sma(close, int(p["trend_slow"]))
        up_trend = (fast > slow).fillna(False)
        dn_trend = (fast < slow).fillna(False)
        hi = close.rolling(int(p["entry_len"])).max().shift(1)
        lo = close.rolling(int(p["entry_len"])).min().shift(1)
        x_hi = close.rolling(int(p["exit_len"])).max().shift(1)
        x_lo = close.rolling(int(p["exit_len"])).min().shift(1)
        long_entry = up_trend & (close > hi)
        long_exit = close < x_lo
        short_entry = dn_trend & (close < lo)
        short_exit = close > x_hi
        mom = ind.roc(close, max(10, int(p["exit_len"])))
        allow_short = (p.get("allow_short", "both") == "both")
        k = int(p["top_k"])
        rebal = _rebalance_series(panel.dates, int(p["rebal_days"]))
        # 状态机各自维护多/空持仓（防当日回场），方向信号在重平衡日对齐
        long_hold = _state_hold(long_entry, long_exit, mom, k)
        short_hold = _state_hold(short_entry, short_exit, -mom, k if allow_short else 0)
        w = long_hold.astype(float) / max(1, k) - short_hold.astype(float) / max(1, k)
        w = w.where(rebal).ffill().fillna(0.0)
        # 归一回全列矩阵（股票/ETF列=0 + F.*列=信号；联合回测分流层按权重路由）
        out = pd.DataFrame(0.0, index=panel.dates, columns=empty_cols + fut_cols)
        out[fut_cols] = w
        return out


# ================ 细分风格谱系（用户指令"非常细分和差异化"，2026-09-21） ================
# 九族九象：每族锚定一个独立的市场现象/学术异象，机制互不重叠：
# 网格收割（震荡结构）/ 月末效应（日历）/ 残差动量（学术风控）/
# 52周高点锚（行为金融）/ 连阳接力（价格模式）/ 放量突破（量价确认）/
# 非流动性溢价（微观结构）/ 相关补涨（相对价值）/ 波动率政权（择时防御）。

@register
class GridTrade(Strategy):
    """网格收割：价格在通道内位置越低权重越高（分档网格，逐格补仓/逐格减仓）——
    只在全池最低波动 n_targets 只标的上开网格（网格属震荡稳态标的的武器，
    全池撒网=伪网格，实测权重爆炸被此修复）；赚"位置回归"的钱，与趋势/反转正交。"""
    name = "grid_trade"
    param_space = {"channel_len": ("int", 20, 120), "n_grids": ("int", 3, 12),
                   "n_targets": ("int", 6, 24), "target_exp": ("float", 0.3, 1.0),
                   "rebal_days": ("int", 3, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        cl = int(p["channel_len"])
        hi = close.rolling(cl, min_periods=cl).max()
        lo = close.rolling(cl, min_periods=cl).min()
        rng = (hi - lo).replace(0.0, np.nan)
        pct = ((close - lo) / rng).clip(0.0, 1.0)          # 通道内位置 0=底 1=顶
        g = float(p["n_grids"])
        lvl = np.floor(pct * g) / g                          # 分档量化
        raw = (1.0 - lvl)                                    # 底=1 顶=0
        # 网格池：最低波动 n_targets 只（用短窗波动近似通道期波动）
        vol = ind.ann_vol(close, max(20, cl // 2))
        pool = vol.rank(axis=1, ascending=True).le(int(p["n_targets"]))
        raw = raw.where(pool).fillna(0.0)   # 出池即归零：防 ffill 复活陈旧权重（实测69只/370%堆叠）
        # 归一到目标总暴露（分母=池内权重和；空池=持币）
        denom = raw.sum(axis=1)
        w = raw.div(denom.where(denom > 0), axis=0).mul(float(p["target_exp"]), axis=0)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        w = w.where(rebal).ffill().fillna(0.0)
        return w.where(close.notna(), 0.0)


@register
class MonthEnd(Strategy):
    """月末效应（A股日历异象）：只在月末前 N 日~次月初 M 日的窗口内持有
    窗口外全现金——纯日历驱动，与其他任何信号族零重叠。"""
    name = "month_end"
    param_space = {"pre_days": ("int", 1, 5), "post_days": ("int", 1, 5),
                   "mom_len": ("int", 20, 120), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        d = pd.Index(panel.dates)
        # 每个交易月的组号 + 组内序号 → 月末/月初窗口掩码
        ym = d.to_period("M")
        grp_change = pd.Series(np.r_[True, (ym[1:] != ym[:-1])], index=d)
        grp_id = grp_change.cumsum()
        days_in = grp_id.groupby(grp_id).cumcount() + 1        # 月内第几个交易日
        total = grp_id.map(grp_id.value_counts())               # 该月交易日总数
        pre = (total - days_in) < int(p["pre_days"])            # 月末段
        post = days_in <= int(p["post_days"])                    # 月初段
        window = pd.Series(pre.values | post.values, index=d)
        mom = ind.roc(close, int(p["mom_len"]))
        ranks = mom.rank(axis=1, ascending=False)
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).astype(float) / float(p["top_k"])
        w = sel.mul(window.astype(float), axis=0)
        return w.where(close.notna(), 0.0)


@register
class ResidMom(Strategy):
    """残差动量（Blitz et al.）：先剔除市场β，只对市场外残差排序——
    学术实证比原始动量回撤更浅（行业/市场暴雷不背锅）。"""
    name = "resid_mom"
    param_space = {"lookback": ("int", 20, 120), "top_k": ("int", 2, 10),
                   "rebal_days": ("int", 5, 10), "ma_filter_len": ("int", 0, 250)}

    def target_weights(self, panel, p):
        close = panel.close
        ret = close.pct_change()
        mkt = ret.mean(axis=1, skipna=True)                    # 等权市场收益
        resid = ret.sub(mkt, axis=0)
        mom = (1.0 + resid).rolling(int(p["lookback"]), min_periods=int(p["lookback"])).apply(
            np.prod, raw=True) - 1.0
        ranks = mom.rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        w = sel.astype(float) / float(p["top_k"])
        if int(p["ma_filter_len"]) > 0:
            mi = ind.universe_index(close)
            ma = mi.rolling(int(p["ma_filter_len"]), min_periods=1).mean()
            w = w.mul((mi > ma).astype(float), axis=0)
        return w.where(close.notna(), 0.0)


@register
class High52(Strategy):
    """52周高点锚定（George-Hwang）：距 52 周高点越近动量越强（行为锚定效应），
    买入"接近新高"者——与累计收益动量不同的度量（100元涨到99.9 也算强）。"""
    name = "high_52"
    param_space = {"win_len": ("int", 120, 260), "min_dist": ("float", 0.05, 0.45),
                   "mom_len": ("int", 10, 60), "top_k": ("int", 2, 10),
                   "rebal_days": ("int", 5, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        hh = close.rolling(int(p["win_len"]), min_periods=int(p["win_len"])).max()
        dist = (hh / close - 1.0)                              # 距高点距离（0=新高）
        near = dist <= float(p["min_dist"])
        score = ind.roc(close, int(p["mom_len"]))
        ranks = score.where(near).rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class Streak(Strategy):
    """连阳接力：连续 N 日收阳的"连胜"延续（短期价格模式，与累计动量不同维度：
    3 连阳 +5% ≠ 1 天 +5%），最长持有 max_hold，断阳或超时离场。"""
    name = "streak"
    param_space = {"streak_n": ("int", 2, 6), "max_hold": ("int", 3, 8),
                   "min_up": ("float", 0.0, 0.02), "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        up = (close > close.shift(1)) & (close.pct_change() >= float(p["min_up"]) - 1e-9)
        cnt = up.astype(int)
        for k in range(2, int(p["streak_n"]) + 1):             # 连阳计数（滚动积攒）
            cnt = np.where(up.shift(k - 1).fillna(False), cnt + 1, 0)
        cnt = pd.DataFrame(np.asarray(cnt), index=close.index, columns=close.columns)
        entry = cnt >= int(p["streak_n"])
        exit_cond = ~up
        score = ind.roc(close, 5)
        hold = _state_hold(entry, exit_cond, score, int(p["top_k"]), max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class VolBreak(Strategy):
    """放量突破：创 N 日新高且成交量 ≥ 均量 × 倍数（量价确认）——
    无量突破是假突破常客，量能是多数现有族忽略的维度。"""
    name = "vol_break"
    param_space = {"brk_len": ("int", 20, 80), "vol_mult": ("float", 1.2, 3.0),
                   "vol_avg_len": ("int", 10, 40), "exit_len": ("int", 5, 30),
                   "top_k": ("int", 2, 10)}

    def target_weights(self, panel, p):
        close, high, vol = panel.close, panel.high, panel.volume
        brk = close > ind.roll_max(high, int(p["brk_len"])).shift(1)
        vavg = vol.rolling(int(p["vol_avg_len"]), min_periods=int(p["vol_avg_len"])).mean()
        surge = vol >= vavg * float(p["vol_mult"])
        entry = brk & surge & (vavg > 0)
        exit_cond = close < ind.roll_min(panel.low, int(p["exit_len"])).shift(1)
        hold = _state_hold(entry, exit_cond, ind.roc(close, 20), int(p["top_k"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class Amihud(Strategy):
    """非流动性溢价（Amihud |r|/成交额）：买"单位成交额撬动收益大"的滞涨股——
    微观结构因子，与市值/动量低相关的第四维度。"""
    name = "amihud"
    param_space = {"illiq_len": ("int", 20, 60), "mom_len": ("int", 5, 60),
                   "top_k": ("int", 2, 10), "rebal_days": ("int", 5, 10)}

    def target_weights(self, panel, p):
        close, amount = panel.close, panel.amount
        illiq = (close.pct_change().abs() / amount.replace(0.0, np.nan)).rolling(
            int(p["illiq_len"]), min_periods=int(p["illiq_len"])).mean()
        # 非流动性高 × 近段不亏（滞涨的非流动股，防接到下跌刀）
        ok = (illiq > 0) & (ind.roc(close, int(p["mom_len"])) > -0.05)
        ranks = illiq.where(ok).rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class PairLag(Strategy):
    """相关补涨（相对价值散户版）：60日高相关对子中买"近5日跑输同伴"的滞涨腿——
    相关劈叉是临时错杀的概率大于基本面劈叉（A股月度频率实证友好）。"""
    name = "pair_lag"
    param_space = {"corr_len": ("int", 40, 90), "corr_min": ("float", 0.6, 0.95),
                   "lag_len": ("int", 3, 10), "top_k": ("int", 2, 8),
                   "rebal_days": ("int", 5, 10)}

    def target_weights(self, panel, p):
        close = panel.close
        ret = close.pct_change()
        cl = int(p["corr_len"])
        # 成对高相关：与市场中位相关度最高的股票（近似配对，全对扫描代价高）
        mkt = ret.mean(axis=1, skipna=True)
        corr = ret.rolling(cl, min_periods=cl).corr(mkt)
        # 滞后腿：与市场同步度高但近 lag_len 日跑输市场的"补涨候选"
        lag = ret.rolling(int(p["lag_len"]), min_periods=int(p["lag_len"])).sum()
        mlag = mkt.rolling(int(p["lag_len"]), min_periods=int(p["lag_len"])).sum()
        cand = (corr >= float(p["corr_min"])) & lag.lt(mlag, axis=0) \
            & (ind.roc(close, int(p["lag_len"])) > -0.10)
        score = lag.rsub(mlag, axis=0)                         # 跑输越多，补涨空间分越高
        ranks = score.where(cand).rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class VolRegime(Strategy):
    """波动率政权（择时防御）：市场实现波动低于阈值 → 持动量强者；
    高波政权 → 撤入全宇宙最低波 ETF（股债切换，全市场防御）。"""
    name = "vol_regime"
    param_space = {"vol_len": ("int", 10, 40), "vol_th": ("float", 0.10, 0.35),
                   "mom_len": ("int", 20, 120), "top_k": ("int", 2, 10),
                   "def_top": ("int", 1, 3)}

    def target_weights(self, panel, p):
        close = panel.close
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        mi = ind.universe_index(close)
        mvol = mi.pct_change().rolling(int(p["vol_len"]), min_periods=int(p["vol_len"])).std() \
            * np.sqrt(252.0)
        risk_on = (mvol < float(p["vol_th"])).reindex(panel.dates).fillna(False)
        mom = ind.roc(close, int(p["mom_len"]))
        ranks = mom.rank(axis=1, ascending=False)
        sel = (ranks.le(int(p["top_k"])) & ranks.notna())
        w = sel.astype(float).mul(risk_on.astype(float), axis=0) / float(p["top_k"])
        # 防御腿：高波政权持最低波动标的（ETF优先，债/货基天然低波）
        etf_cols = [c for c in panel.codes if is_etf(c)]
        pool = close[etf_cols] if etf_cols else close
        dvol = ind.ann_vol(pool, 20)
        drank = dvol.rank(axis=1, ascending=True)
        dsel = drank.le(int(p["def_top"])) & drank.notna()
        w_def = dsel.reindex(columns=panel.codes, fill_value=False).astype(float) \
            .mul((~risk_on).astype(float), axis=0) / float(max(1, int(p["def_top"])))
        return ((w + w_def).clip(upper=0.5)).where(close.notna(), 0.0)


# ================ 游资/极端风格 + 科学对照组（参照外部系统谱系，2026-09-21） ================
# 六族六型：龙头战法/跌停反核/炸板回封/尾盘强势/次新波动/随机对照。
# 日频 OHLCV 近似披露：无分时数据，"涨停"用涨幅≥9.5%近似（创业板/ETF 20% 板
# 的大阳日同样计入=强势日口径）；尾盘强度用收盘位置(close-low)/(high-low)。

@register
class DragonHead(Strategy):
    """龙头战法：近 N 日"近似涨停日"（涨幅≥board_pct）计数≥min_boards 的
    连板高度者——游资跟随：只买有"板性"的强者，断板即走。
    与 limitup_mom（单板动量）的差异：要求连板≥2（真龙头）+ 高度优先。"""
    name = "dragon_head"
    param_space = {"count_len": ("int", 3, 8), "min_boards": ("int", 2, 4),
                   "board_pct": ("float", 0.05, 0.095), "max_hold": ("int", 3, 8),
                   "top_k": ("int", 2, 8)}

    def target_weights(self, panel, p):
        close = panel.close
        ret = close.pct_change()
        board = ret >= float(p["board_pct"]) - 1e-9       # 近似涨停/大阳日
        boards = board.rolling(int(p["count_len"]), min_periods=1).sum()
        entry = boards >= int(p["min_boards"])
        exit_cond = ret < 0
        score = boards * 10.0 + ind.roc(close, 3)          # 高度优先
        hold = _state_hold(entry, exit_cond, score, int(p["top_k"]),
                           max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class LimitDownBuy(Strategy):
    """跌停反核：前一日恐慌 flush（日跌 ≤ min_drop）后买入博超跌反弹——
    极端逆向（别人割肉我接刀），持有 max_hold 日，反弹即走/续崩即走。"""
    name = "limit_down_buy"
    param_space = {"min_drop": ("float", -0.105, -0.05), "max_hold": ("int", 2, 6),
                   "trend_ok": ("choice", ["any", "up"]), "top_k": ("int", 2, 8)}

    def target_weights(self, panel, p):
        close = panel.close
        ret = close.pct_change()
        panic = ret.shift(1) <= float(p["min_drop"]) + 1e-9
        if p.get("trend_ok", "any") == "up":
            panic &= close > ind.sma(close, 60)
        entry = panic & (ret > -0.02)                       # 恐慌次日不再续崩
        exit_cond = (ind.roc(close, 2) > 0.03) | (ret < -0.04)
        score = ret.shift(1)                                # 跌得越深分越高
        hold = _state_hold(entry, exit_cond, score, int(p["top_k"]),
                           max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class BanOpen(Strategy):
    """炸板回封：昨日冲板（high 日涨幅≥board_pct）但收盘回落≥2% =炸板；
    今日再度收强（≥+3%）=回封买点。游资"反包"模式的日频近似。"""
    name = "ban_open"
    param_space = {"board_pct": ("float", 0.07, 0.095), "max_hold": ("int", 3, 8),
                   "top_k": ("int", 2, 8)}

    def target_weights(self, panel, p):
        close, high = panel.close, panel.high
        ret = close.pct_change()
        hi_ret = high / close.shift(1) - 1.0
        broke = (hi_ret.shift(1) >= float(p["board_pct"])) \
            & (ret.shift(1) <= hi_ret.shift(1) - 0.02)
        entry = broke & (ret >= 0.03)
        exit_cond = ret < 0
        hold = _state_hold(entry, exit_cond, ind.roc(close, 3), int(p["top_k"]),
                           max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class StrongClose(Strategy):
    """尾盘强势：收盘位于日内区间顶部（(close-low)/(high-low)≥pos）+ 放量
    ——尾盘资金抢筹的日频指纹（无分时数据的诚实近似），博次日惯性。"""
    name = "strong_close"
    param_space = {"pos": ("float", 0.75, 0.98), "vol_mult": ("float", 1.1, 2.5),
                   "vol_len": ("int", 10, 40), "max_hold": ("int", 2, 8),
                   "top_k": ("int", 2, 8)}

    def target_weights(self, panel, p):
        close, high, low, vol = panel.close, panel.high, panel.low, panel.volume
        rng = (high - low).replace(0.0, np.nan)
        pos = (close - low) / rng
        vavg = vol.rolling(int(p["vol_len"]), min_periods=int(p["vol_len"])).mean()
        entry = (pos >= float(p["pos"])) & (vol >= vavg * float(p["vol_mult"])) \
            & (close.pct_change() > 0) & (vavg > 0)
        exit_cond = pos < 0.5
        hold = _state_hold(entry, exit_cond, pos, int(p["top_k"]),
                           max_hold=int(p["max_hold"]))
        return (hold.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class SubNew(Strategy):
    """次新股：面板历史 < new_bars 根（≈上市一年内）中的最强动量者——
    次新=无历史包袱+高波动+高换手（激进族），涨得最猛的优先。"""
    name = "sub_new"
    param_space = {"new_bars": ("int", 120, 300), "mom_len": ("int", 5, 30),
                   "rebal_days": ("int", 3, 10), "top_k": ("int", 2, 8)}

    def target_weights(self, panel, p):
        close = panel.close
        bars_so_far = close.notna().cumsum()                # 上市以来有效K线数
        is_new = (bars_so_far <= int(p["new_bars"])) & (bars_so_far >= 20)
        mom = ind.roc(close, int(p["mom_len"]))
        ranks = mom.where(is_new).rank(axis=1, ascending=False)
        rebal = _rebalance_series(panel.dates, p["rebal_days"])
        sel = (ranks.le(int(p["top_k"])) & ranks.notna()).where(rebal).ffill().fillna(False)
        return (sel.astype(float) / float(p["top_k"])).where(close.notna(), 0.0)


@register
class Gamble(Strategy):
    """随机对照组（科学对照）：按（代码,ISO周）哈希伪随机选股——每周一批
    "纯随机"持仓。用途：全场对照组——若真策略跑不赢 gamble，信号无效；
    若 gamble 被碾压，进化选择的超额收益为真。参照外部系统 gamble 设计。"""
    name = "gamble"
    param_space = {"top_k": ("int", 2, 10), "rebal_weeks": ("int", 1, 4)}

    def target_weights(self, panel, p):
        import hashlib
        close = panel.close
        iso = pd.Index(panel.dates).isocalendar()
        wk = np.asarray(iso.week, dtype=np.int64)
        codes = list(panel.codes)
        # 确定性哈希（Python 内建 hash 对字符串按进程加盐随机——跨进程不可复现，
        # 会破坏评估缓存/复算审计；用 md5 前8位做种子）
        seed_arr = np.array(
            [int(hashlib.md5(str(c).encode()).hexdigest()[:8], 16) % 10_000
             for c in codes], dtype=np.int64)
        period = max(1, int(p["rebal_weeks"]))
        first_of_week = np.r_[True, np.diff(wk) != 0]
        anchor = first_of_week & (wk % period == 0)
        n = len(panel.dates)
        k = int(p["top_k"])
        w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        pick_idx = np.argsort((seed_arr * 7919) % 100_007)[:k]
        for i in range(n):
            if i == 0 or anchor[i]:
                pick_idx = np.argsort(((seed_arr + wk[i]) * 7919) % 100_007)[:k]
            w.iloc[i, pick_idx] = 1.0 / k
        return w.where(close.notna(), 0.0)


# ================ GP 基因组策略：策略结构本身参与进化（进化金字塔顶层） ================
# 18个固定模板之上的缺失层：入场/离场的"逻辑组合结构"由遗传算子生成/突变/淘汰，
# 系统可以发现今天不存在的策略，而非只在已知模板内调参。
# 基因组 JSON 可序列化（state持久化/竞技场/评估缓存全兼容）。

_GENOME_PRIMS = {
    # kind: (n_lo, n_hi, th_lo, th_hi)  n=回看窗口；th=阈值（trend_up 的 th=慢均线周期）
    "cross_up":  (5, 200, 0.0, 0.0),
    "osc_low":   (2, 14, 5.0, 35.0),
    "osc_high":  (2, 14, 55.0, 90.0),
    "mom_pos":   (5, 120, -0.05, 0.10),
    "mom_neg":   (5, 120, -0.10, 0.05),
    "breakout":  (10, 80, 0.0, 0.0),
    "breakdown": (5, 60, 0.0, 0.0),
    "zlow":      (10, 120, -3.0, -0.5),
    "zhigh":     (10, 120, 0.5, 3.0),
    "vol_low":   (10, 120, 0.05, 0.60),
    "trend_up":  (3, 30, 40.0, 200.0),
}
_GENOME_EXIT_KINDS = ("osc_high", "breakdown", "mom_neg", "zhigh")
_GENOME_SCORES = ("roc_20", "roc_60", "low_vol", "rev_5")


def _rand_prim(rng, kinds=None):
    kind = rng.choice(kinds or list(_GENOME_PRIMS))
    nlo, nhi, tlo, thi = _GENOME_PRIMS[kind]
    prim = {"kind": kind, "n": int(rng.randint(nlo, nhi))}
    if tlo != thi:
        prim["th"] = round(float(rng.uniform(tlo, thi)), 3)
    return prim


def _gauss_i(rng, cur, lo, hi, sigma=0.2):
    return int(max(lo, min(hi, round(cur + rng.gauss(0, sigma * (hi - lo))))))


def _gauss_f(rng, cur, lo, hi, sigma=0.2):
    return round(float(max(lo, min(hi, cur + rng.gauss(0, sigma * (hi - lo))))), 4)


@register
class Evolved(Strategy):
    """GP 进化策略（基因组）：入场=1~4个原语的 all/any 组合，离场=0~2个原语，
    排序因子/持仓数/调仓周期/市场过滤/最长持有/加权模式全部进化的基因。

    结构+参数同时被 GA/Arena/联赛进化——策略空间的边界由算法定义，不由模板清单定义。
    有离场原语→状态机持有；无离场原语→ISO周锚定轮动（2周~15日硬上限照常兜底）。
    """
    name = "evolved"
    param_space = {}  # 基因组由专用遗传算子操作（见 random_genome/crossover_genomes/mutate_genome）

    # ------------------------------------------------ 基因组算子（evolve.py 分发调用）

    @staticmethod
    def random_genome(rng):
        genome = {
            "entry": [_rand_prim(rng) for _ in range(rng.randint(1, 4))],
            "logic": rng.choice(["all", "any"]),
            "exit": [_rand_prim(rng, _GENOME_EXIT_KINDS) for _ in range(rng.randint(0, 2))],
            "score": rng.choice(_GENOME_SCORES),
            "top_k": int(rng.randint(2, 8)),
            "rebal_days": int(rng.randint(3, 10)),
            "ma_filter": int(rng.choice([0, 0, 50, 100, 150, 200, 250])),
            "max_hold": int(rng.choice([0, 3, 5, 8, 10, 15])),
            "weighting": rng.choice(["equal", "inv_vol"]),
        }
        return Evolved.sanitize(genome)

    @staticmethod
    def crossover_genomes(a, b, rng):
        child = {}
        for key in ("logic", "score", "top_k", "rebal_days", "ma_filter", "max_hold", "weighting"):
            child[key] = a.get(key, b.get(key)) if rng.random() < 0.5 else b.get(key, a.get(key))
        for key, lim in (("entry", 4), ("exit", 2)):
            la, lb = list(a.get(key) or []), list(b.get(key) or [])
            cut = rng.randint(0, len(la))
            child[key] = copy.deepcopy((la[:cut] + lb[cut:])[:lim])
        return Evolved.sanitize(child)

    @staticmethod
    def mutate_genome(g, rng, rate):
        out = copy.deepcopy(g)
        for key, kinds, lim in (("entry", None, 4), ("exit", _GENOME_EXIT_KINDS, 2)):
            prims = out.get(key) or []
            if prims and rng.random() < rate:
                prims[rng.randrange(len(prims))] = _rand_prim(rng, kinds)
            if len(prims) > 1 and rng.random() < rate * 0.5:
                prims.pop(rng.randrange(len(prims)))
            if len(prims) < lim and rng.random() < rate * 0.5:
                prims.append(_rand_prim(rng, kinds))
        for prim in out.get("entry", []) + out.get("exit", []):
            nlo, nhi, _, _ = _GENOME_PRIMS.get(prim.get("kind", "cross_up"), (5, 200, 0, 0))
            if rng.random() < rate:
                prim["n"] = _gauss_i(rng, int(prim.get("n", nlo)), nlo, nhi)
            tlo, thi = _GENOME_PRIMS[prim["kind"]][2], _GENOME_PRIMS[prim["kind"]][3]
            if tlo != thi and "th" in prim and rng.random() < rate:
                prim["th"] = _gauss_f(rng, float(prim["th"]), tlo, thi)
        if rng.random() < rate:
            out["logic"] = rng.choice(["all", "any"])
        if rng.random() < rate:
            out["score"] = rng.choice(_GENOME_SCORES)
        if rng.random() < rate:
            out["top_k"] = _gauss_i(rng, int(out.get("top_k", 5)), 2, 8)
        if rng.random() < rate:
            out["rebal_days"] = _gauss_i(rng, int(out.get("rebal_days", 5)), 3, 10)
        if rng.random() < rate:
            out["ma_filter"] = rng.choice([0, 50, 100, 150, 200, 250])
        if rng.random() < rate:
            out["max_hold"] = rng.choice([0, 3, 5, 8, 10, 15])
        if rng.random() < rate:
            out["weighting"] = rng.choice(["equal", "inv_vol"])
        return Evolved.sanitize(out)

    @staticmethod
    def sanitize(genome: dict) -> dict:
        """基因组合法化：尺寸/范围/字段校验（采样/交叉/变异/持久化恢复统一过闸）。"""
        out = dict(genome)
        entry = [p for p in (out.get("entry") or []) if p.get("kind") in _GENOME_PRIMS][:4]
        if not entry:
            entry = [{"kind": "cross_up", "n": 50}]
        out["entry"] = entry
        out["exit"] = [p for p in (out.get("exit") or []) if p.get("kind") in _GENOME_PRIMS][:2]
        out["logic"] = out.get("logic") if out.get("logic") in ("all", "any") else "all"
        out["score"] = out.get("score") if out.get("score") in _GENOME_SCORES else "roc_60"
        out["top_k"] = int(max(2, min(8, out.get("top_k", 5))))
        out["rebal_days"] = int(max(3, min(10, out.get("rebal_days", 5))))
        out["ma_filter"] = int(out.get("ma_filter", 0))
        out["max_hold"] = int(out.get("max_hold", 0))
        out["weighting"] = out.get("weighting") if out.get("weighting") in ("equal", "inv_vol") else "equal"
        for prim in out["entry"] + out["exit"]:
            nlo, nhi, tlo, thi = _GENOME_PRIMS[prim["kind"]]
            prim["n"] = int(max(nlo, min(nhi, int(prim.get("n", nlo)))))
            if tlo != thi:
                prim["th"] = float(max(tlo, min(thi, float(prim.get("th", tlo)))))
        return out

    # ------------------------------------------------ 信号求值

    @staticmethod
    def _eval_prim(panel, prim):
        k = prim["kind"]
        n = max(2, int(prim.get("n", 20)))
        th = float(prim.get("th", 0.0))
        close, high, low = panel.close, panel.high, panel.low
        if k == "cross_up":
            return close > ind.sma(close, n)
        if k == "osc_low":
            return ind.rsi(close, n) < th
        if k == "osc_high":
            return ind.rsi(close, n) > th
        if k == "mom_pos":
            return ind.roc(close, n) > th
        if k == "mom_neg":
            return ind.roc(close, n) < th
        if k == "breakout":
            return close > ind.roll_max(high, n).shift(1)
        if k == "breakdown":
            return close < ind.roll_min(low, n).shift(1)
        if k == "zlow":
            return ind.zscore(close, n) < th
        if k == "zhigh":
            return ind.zscore(close, n) > th
        if k == "vol_low":
            return ind.ann_vol(close, n) < th
        if k == "trend_up":
            return ind.sma(close, n) > ind.sma(close, max(n + 1, int(round(th))))
        raise ValueError(f"未知原语 {k}")

    @staticmethod
    def _score_df(panel, name):
        close = panel.close
        if name == "roc_20":
            return ind.roc(close, 20)
        if name == "roc_60":
            return ind.roc(close, 60)
        if name == "low_vol":
            return -ind.ann_vol(close, 60)
        if name == "rev_5":
            return -ind.roc(close, 5)
        raise ValueError(name)

    def target_weights(self, panel, p):
        close = panel.close
        g = Evolved.sanitize(p)
        entry = None
        for prim in g["entry"]:
            m = self._eval_prim(panel, prim).fillna(False)
            entry = m if entry is None else (entry & m if g["logic"] == "all" else entry | m)
        if entry is None:
            return pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
        score = self._score_df(panel, g["score"])
        exits = g.get("exit") or []
        if exits:
            exit_mask = None
            for prim in exits:
                m = self._eval_prim(panel, prim).fillna(False)
                exit_mask = m if exit_mask is None else exit_mask | m
            hold = _state_hold(entry, exit_mask, score, g["top_k"],
                               max_hold=(g["max_hold"] or None))
            sel = hold
        else:
            ranks = score.where(entry).rank(axis=1, ascending=False)
            rebal = _rebalance_series(panel.dates, g["rebal_days"])
            sel = (ranks.le(g["top_k"]) & ranks.notna()).where(rebal).ffill().fillna(False)
        w = _apply_weighting(sel, close, 60, g["weighting"], g["top_k"])
        if g["ma_filter"] > 0:
            mkt = ind.universe_index(close)
            w = w.mul((mkt > mkt.rolling(g["ma_filter"], min_periods=1).mean()).astype(float), axis=0)
        return w.where(close.notna(), 0.0).fillna(0.0)
