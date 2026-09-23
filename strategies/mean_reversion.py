"""Mean reversion schools: Bollinger, RSI, oversold bounce."""
import numpy as np
import pandas as pd


def bollinger_breakout(close: pd.Series, n: int = 20,
                       k: float = 2.0) -> pd.Series:
    """Return position: 1=long (price below lower band = buy),
    -1=short (above upper band). For ETFs we only go long."""
    ma = close.rolling(n).mean()
    sd = close.rolling(n).std()
    lower = ma - k * sd
    upper = ma + k * sd
    pos = np.where(close < lower, 1, np.where(close > upper, 0, np.nan))
    return pd.Series(pos, index=close.index).ffill().fillna(0)


def rsi_revert(close: pd.Series, n: int = 14,
               oversold: float = 30, overbought: float = 70) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    pos = np.where(rsi < oversold, 1, np.where(rsi > overbought, 0, np.nan))
    return pd.Series(pos, index=close.index).ffill().fillna(0)


def zscore_revert(close: pd.Series, n: int = 20,
                  entry: float = -2.0) -> pd.Series:
    """Buy when z-score drops below entry, hold until mean."""
    ma = close.rolling(n).mean()
    sd = close.rolling(n).std()
    z = (close - ma) / sd
    pos = np.where(z < entry, 1, np.where(z > 0, 0, np.nan))
    return pd.Series(pos, index=close.index).ffill().fillna(0)


def pullback_bounce(close: pd.Series, trend_n: int = 60,
                    pullback_n: int = 10) -> pd.Series:
    """In uptrend, buy short-term pullback."""
    trend_up = close > close.rolling(trend_n).mean()
    recent_down = close.pct_change(pullback_n) < -0.05
    return ((trend_up) & (recent_down)).astype(int)


def rsi2(close: pd.Series, n: int = 2) -> pd.Series:
    """Larry Connors RSI-2: very short-term oversold."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    return (rsi < 10).astype(int)
