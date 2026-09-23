"""向量化技术指标。输入均为 date×code 的 DataFrame（列=标的），输出同形状。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.rolling(n, min_periods=n).mean()


def ema(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.ewm(span=n, adjust=False).mean()


def rsi(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """Wilder RSI（0-100），早期不足 n 日为 NaN（不产生信号）。"""
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    avg_up = up.ewm(alpha=1 / n, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / n, adjust=False).mean()
    rs = avg_up / avg_down.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    out = out.mask((avg_down == 0) & (avg_up > 0), 100.0)  # 无下跌=全强
    out = out.mask((avg_up == 0) & (avg_down > 0), 0.0)    # 无上涨=全弱
    return out


def roc(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """n 日收益率（动量）。"""
    return close / close.shift(n) - 1.0


def roll_max(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.rolling(n, min_periods=n).max()


def roll_min(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.rolling(n, min_periods=n).min()


def ann_vol(close: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """年化波动率。"""
    ret = close.pct_change()
    return ret.rolling(n, min_periods=n).std() * np.sqrt(252)


def zscore(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """滚动 z-score。"""
    mean = df.rolling(n, min_periods=n).mean()
    std = df.rolling(n, min_periods=n).std()
    return (df - mean) / std.replace(0.0, np.nan)


def universe_index(close: pd.DataFrame) -> pd.Series:
    """股票池等权指数（作市场过滤参考）。"""
    ret = close.pct_change()
    eq = (1.0 + ret.mean(axis=1, skipna=True).fillna(0.0)).cumprod()
    return eq


def macd(close: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD 公式：DIF = EMA(fast) - EMA(slow)；DEA = EMA(DIF, signal)；HIST = DIF - DEA。"""
    dif = ema(close, fast) - ema(close, slow)
    dea = ema(dif, signal)
    hist = dif - dea
    return dif, dea, hist


def kdj(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame,
        n: int = 9, k_n: int = 3, d_n: int = 3) -> pd.DataFrame:
    """KDJ 公式（中国市场经典指标）：
    RSV = (C - L_n) / (H_n - L_n) × 100；K = SMA(RSV, k_n, 1)；D = SMA(K, d_n, 1)；J = 3K - 2D。
    SMA(X, N, M) 为国内行情软件标准函数：Y_t = (M×X_t + (N-M)×Y_{t-1}) / N，即 ewm(alpha=M/N)。
    """
    hh = roll_max(high, n)
    ll = roll_min(low, n)
    rng_ = (hh - ll).replace(0.0, np.nan)
    rsv = (close - ll) / rng_ * 100.0
    rsv = rsv.fillna(50.0)
    k = rsv.ewm(alpha=1.0 / k_n, adjust=False).mean()
    d = k.ewm(alpha=1.0 / d_n, adjust=False).mean()
    return 3.0 * k - 2.0 * d


def rsrs_beta(high: pd.DataFrame, low: pd.DataFrame, window: int) -> pd.DataFrame:
    """RSRS 阻力支撑相对强度：N 日窗口内 high ~ low 滚动回归斜率 beta。

    出处：光大证券金融工程 2017《基于阻力支撑相对强度(RSRS)的市场择时》。
    向量化实现：beta = Cov(high,low) / Var(low)，用滚动矩计算。
    """
    mean_h = high.rolling(window, min_periods=window).mean()
    mean_l = low.rolling(window, min_periods=window).mean()
    mean_hl = (high * low).rolling(window, min_periods=window).mean()
    mean_ll = (low * low).rolling(window, min_periods=window).mean()
    var_l = (mean_ll - mean_l * mean_l).replace(0.0, np.nan)
    return (mean_hl - mean_h * mean_l) / var_l
