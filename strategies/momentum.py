"""Momentum & rotation schools: dual momentum, sector rotation."""
import numpy as np
import pandas as pd


def cross_sectional_momentum(close: pd.DataFrame, n: int = 120,
                             skip: int = 20,
                             top_k: int = 5) -> pd.DataFrame:
    """Select top_k by n-month momentum skipping last skip days.
    Returns DataFrame of weights (0 or 1) aligned to close index."""
    mom = close.shift(skip) / close.shift(n) - 1
    ranks = mom.rank(axis=1, ascending=False)
    return (ranks <= top_k).astype(int)


def dual_momentum(close: pd.DataFrame, bench: pd.Series,
                  n: int = 120, top_k: int = 5) -> pd.DataFrame:
    """Absolute + relative momentum: only hold if above cash-like benchmark."""
    rel = close.pct_change(n)
    abs_ = close.pct_change(n) > 0
    ranks = rel.rank(axis=1, ascending=False)
    rel_top = ranks <= top_k
    return (rel_top & abs_).astype(int)


def time_series_momentum(close: pd.Series, n: int = 200) -> pd.Series:
    """Absolute momentum: hold if price > MA(n)."""
    return (close > close.rolling(n).mean()).astype(int)


def relative_strength_rotation(close: pd.DataFrame, bench: pd.Series,
                                n: int = 20, top_k: int = 5) -> pd.DataFrame:
    """Hold top_k relative to benchmark over n days."""
    diff = close.pct_change(n).subtract(bench.pct_change(n), axis=0)
    ranks = diff.rank(axis=1, ascending=False)
    return (ranks <= top_k).astype(int)


def momentum_acceleration(close: pd.DataFrame,
                          fast: int = 20, slow: int = 120) -> pd.DataFrame:
    """Rising momentum: fast momentum > slow momentum."""
    f = close.pct_change(fast)
    s = close.pct_change(slow)
    return (f > s).astype(int)
