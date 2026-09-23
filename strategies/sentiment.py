"""Sentiment & money-flow schools (proxy, no social data)."""
import numpy as np
import pandas as pd


def turnover_surge(volume: pd.DataFrame, n: int = 20,
                   threshold: float = 2.0) -> pd.DataFrame:
    """Volume > threshold * MA(n) -> interest spike."""
    ma = volume.rolling(n).mean()
    return (volume > threshold * ma).astype(int)


def amount_rank(amount: pd.DataFrame, n: int = 20,
                top_k: int = 10) -> pd.DataFrame:
    """Hold top_k by recent amount (institutional interest)."""
    avg = amount.rolling(n).mean()
    ranks = avg.rank(axis=1, ascending=False)
    return (ranks <= top_k).astype(int)


def price_volume_trend(close: pd.DataFrame, volume: pd.DataFrame,
                       n: int = 20) -> pd.DataFrame:
    """Rising price + rising volume = confirmed trend."""
    price_up = close.pct_change(n) > 0
    vol_up = volume.rolling(n).mean() > volume.rolling(n).mean().shift(n)
    return (price_up & vol_up).astype(int)


def intraday_momentum(open_: pd.DataFrame, close: pd.DataFrame,
                      n: int = 10) -> pd.DataFrame:
    """Intraday return persistence."""
    intraday = close / open_ - 1
    return (intraday.rolling(n).mean() > 0).astype(int)


def overnight_drift(open_: pd.DataFrame, close: pd.DataFrame,
                    n: int = 10) -> pd.DataFrame:
    """Overnight return drift (US-style anomaly)."""
    overnight = open_ / close.shift(1) - 1
    return (overnight.rolling(n).mean() > 0).astype(int)
