"""Macro & regime filters (apply on top of any strategy)."""
import numpy as np
import pandas as pd


def csi300_trend_filter(close: pd.Series, bench: pd.Series,
                        ma_n: int = 200) -> pd.Series:
    """1 if benchmark above MA200 (risk-on), else 0 (risk-off)."""
    bench = bench.reindex(close.index).ffill()
    return (bench > bench.rolling(ma_n).mean()).astype(int)


def csi300_momentum_filter(close: pd.Series, bench: pd.Series,
                           n: int = 60) -> pd.Series:
    """1 if benchmark has positive n-month momentum."""
    bench = bench.reindex(close.index).ffill()
    return (bench.pct_change(n) > 0).astype(int)


def volatility_regime_filter(bench: pd.Series, n: int = 60) -> pd.Series:
    """1 if market vol below median (calm regime)."""
    rv = bench.pct_change().rolling(n).std()
    return (rv < rv.rolling(252).median()).astype(int)


def drawdown_filter(bench: pd.Series, max_dd: float = -0.15) -> pd.Series:
    """1 if benchmark not in >15% drawdown."""
    hh = bench.cummax()
    dd = bench / hh - 1
    return (dd > max_dd).astype(int)
