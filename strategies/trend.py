"""Trend following schools: Donchian breakout, Turtle, MA cross."""
import numpy as np
import pandas as pd


def donchian_breakout(close: pd.Series, high: pd.Series, low: pd.Series,
                      entry_n: int = 20, exit_n: int = 10) -> pd.Series:
    """Turtle-style: buy at N-day high, exit at M-day low."""
    upper = high.rolling(entry_n).max()
    lower = low.rolling(exit_n).min()
    position = np.where(close >= upper, 1, np.where(close <= lower, -1, 0))
    pos = pd.Series(position, index=close.index).replace(0, np.nan).ffill().fillna(0)
    return pos


def dual_ma_cross(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    return (f > s).astype(int)


def triple_ma(close: pd.Series, n1: int = 5, n2: int = 20,
              n3: int = 60) -> pd.Series:
    """3 MA: long when all aligned bullish."""
    m1 = close.rolling(n1).mean()
    m2 = close.rolling(n2).mean()
    m3 = close.rolling(n3).mean()
    return ((m1 > m2) & (m2 > m3)).astype(int)


def parabolic_sar(close: pd.Series, af_start: float = 0.02,
                  af_inc: float = 0.02, af_max: float = 0.2) -> pd.Series:
    """Simplified PSAR: 1=long, 0=flat."""
    n = len(close)
    sar = np.zeros(n)
    pos = np.zeros(n)
    ep = close.iloc[0]
    af = af_start
    long = True
    sar[0] = close.iloc[0]
    for i in range(1, n):
        if long:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if close.iloc[i] < sar[i]:
                long = False
                sar[i] = ep
                ep = close.iloc[i]
                af = af_start
            else:
                if close.iloc[i] > ep:
                    ep = close.iloc[i]
                    af = min(af + af_inc, af_max)
        else:
            sar[i] = sar[i-1] + af * (ep - sar[i-1])
            if close.iloc[i] > sar[i]:
                long = True
                sar[i] = ep
                ep = close.iloc[i]
                af = af_start
            else:
                if close.iloc[i] < ep:
                    ep = close.iloc[i]
                    af = min(af + af_inc, af_max)
        pos[i] = 1 if long else 0
    return pd.Series(pos, index=close.index)


def supertrend(close: pd.Series, high: pd.Series, low: pd.Series,
               n: int = 10, mult: float = 3.0) -> pd.Series:
    """Supertrend indicator."""
    hl2 = (high + low) / 2
    atr = (high - low).rolling(n).mean()
    upper = hl2 + mult * atr
    lower = hl2 - mult * atr
    direction = pd.Series(1, index=close.index)
    for i in range(1, len(close)):
        prev_dir = direction.iloc[i-1]
        if close.iloc[i] > upper.iloc[i-1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = prev_dir
    return (direction > 0).astype(int)
