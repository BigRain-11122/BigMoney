"""Calendar & seasonal schools."""
import numpy as np
import pandas as pd


def month_seasonality(close: pd.DataFrame, month: int) -> pd.Series:
    """Hold in specific month (e.g. 'January effect')."""
    return pd.Series(close.index.month == month, index=close.index,
                     dtype=int)


def month_end_effect(close: pd.DataFrame, window: int = 3) -> pd.Series:
    """Hold on last N trading days of month."""
    idx = close.index
    m = pd.Series(idx.month, index=idx)
    boundary = (m != m.shift(-1)).fillna(True)  # True on each month's last bar
    grp = boundary.cumsum()
    pos = pd.Series(range(len(idx)), index=idx).groupby(grp.values).cumcount()
    size = pos.groupby(grp.values).transform("max")
    days_to_end = size - pos
    return (days_to_end <= window - 1).astype(int)


def weekday_effect(close: pd.DataFrame, weekday: int = 4) -> pd.Series:
    """Hold on specific weekday (e.g. Friday effect)."""
    return pd.Series(close.index.weekday == weekday, index=close.index,
                     dtype=int)


def holiday_effect(close: pd.Series, pre_days: int = 3) -> pd.Series:
    """Buy N days before major holidays (CNY, National Day).
    Approximation: Nov-Feb window (holiday season)."""
    month = close.index.month
    return ((month == 1) | (month == 2) | (month == 10) |
            (month == 11)).astype(int)


def trend_by_season(close: pd.Series, month: int,
                    ma_n: int = 200) -> pd.Series:
    """Seasonal filter: only take trend signals in specified month."""
    trend = (close > close.rolling(ma_n).mean()).astype(int)
    in_month = pd.Series(close.index.month == month, index=close.index,
                         dtype=int)
    return trend & in_month
