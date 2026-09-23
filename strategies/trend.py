"""Trend following schools: Donchian breakout, Turtle, MA cross.

Warmup semantics (T-03-F7, audit P1-5, now on record): every rolling window
uses min_periods == window, so the first n-1 rows are NaN. Downstream boolean
comparisons with NaN evaluate to False silently — the engine treats NaN/False
as flat. This is intended warmup behavior, not a signal.
"""
import numpy as np
import pandas as pd


def donchian_breakout(close: pd.Series, high: pd.Series, low: pd.Series,
                      entry_n: int = 20, exit_n: int = 10) -> pd.Series:
    """Turtle-style: buy at N-day high, exit at M-day low.

    v2 (T-03-F7, audit P1-4) — BREAKING output change: long-only 0/1 contract,
    was {-1, 0, 1} three-state. No unmasked consumer exists today (the LFC
    batch consumed with a (pos>0) mask — masked outputs are identical);
    version-noted in strategies/README.md. A breakdown now sets flat (0)
    instead of a short state (-1).
    """
    upper = high.rolling(entry_n, min_periods=entry_n).max()
    lower = low.rolling(exit_n, min_periods=exit_n).min()
    state = pd.Series(np.nan, index=close.index)
    state[close <= lower] = 0          # breakdown -> flat (precedence: breakout wins on conflict, mirrors old np.where order)
    state[close >= upper] = 1          # breakout -> long
    return state.ffill().fillna(0).astype(int)


def dual_ma_cross(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast, min_periods=fast).mean()
    s = close.rolling(slow, min_periods=slow).mean()
    return (f > s).astype(int)


def triple_ma(close: pd.Series, n1: int = 5, n2: int = 20,
              n3: int = 60) -> pd.Series:
    """3 MA: long when all aligned bullish."""
    m1 = close.rolling(n1, min_periods=n1).mean()
    m2 = close.rolling(n2, min_periods=n2).mean()
    m3 = close.rolling(n3, min_periods=n3).mean()
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
    """Supertrend indicator.

    NaN safety note (T-03-F7, audit P1-5): during the ATR warmup window
    upper/lower are NaN; NaN comparisons in the loop below evaluate False,
    so direction simply carries the previous state (flat start) — no NaN
    can leak into the returned 0/1 signal.
    """
    hl2 = (high + low) / 2
    atr = (high - low).rolling(n, min_periods=n).mean()
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
