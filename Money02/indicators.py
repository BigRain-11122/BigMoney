"""Vectorized indicator helpers over (T, N) panels. NaN-safe via pandas rolling."""
import numpy as np
import pandas as pd


def sma(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.rolling(n, min_periods=n).mean()


def rmax(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.rolling(n, min_periods=n).max()


def pct_change(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df / df.shift(n) - 1.0


def rsi(close: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    d = close.diff()
    up = d.clip(lower=0).rolling(n, min_periods=n).mean()
    dn = (-d.clip(upper=0)).rolling(n, min_periods=n).mean()
    return 100.0 - 100.0 / (1.0 + up / (dn + 1e-12))


def shift1(arr: np.ndarray, fill: float = 0.0) -> np.ndarray:
    """Shift along axis 0 by 1 day (prior-day values), row 0 filled."""
    out = np.full_like(arr, fill, dtype=arr.dtype)
    if arr.shape[0] > 1:
        out[1:] = arr[:-1]
    return out
