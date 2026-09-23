"""Event & gap schools."""
import numpy as np
import pandas as pd


def gap_fill(open_: pd.Series, close: pd.Series,
             n: int = 5) -> pd.Series:
    """Buy if overnight gap down but price recovers by close."""
    gap = open_ / close.shift(1) - 1
    recovery = close > open_
    return ((gap < -0.01) & recovery).astype(int)


def breakout_confirm(close: pd.Series, volume: pd.Series,
                     n: int = 20, vol_mult: float = 1.5) -> pd.Series:
    """Breakout with volume confirmation."""
    hh = close.rolling(n).max().shift(1)
    vol_ma = volume.rolling(n).mean()
    breakout = close > hh
    confirm = volume > vol_mult * vol_ma
    return (breakout & confirm).astype(int)


def double_bottom(close: pd.Series, n: int = 20,
                  tolerance: float = 0.03) -> pd.Series:
    """Crude double bottom detection."""
    min1 = close.rolling(n).min()
    min2 = close.shift(n).rolling(n).min()
    return ((close > min1 * (1 + tolerance)) &
            (abs(min1 - min2) / min2 < tolerance)).astype(int)
