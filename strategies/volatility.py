"""Volatility schools: low-vol anomaly, vol targeting, vol breakout."""
import numpy as np
import pandas as pd


def low_vol_long(close: pd.DataFrame, n: int = 60, top_k: int = 5,
                 rebal_days: int | None = None) -> pd.DataFrame:
    """Hold the top_k lowest-vol ETFs.

    rebal_days=None -> daily membership refresh (P1/G2 behavior, unchanged
    expression); int -> membership frozen between non-overlapping rebalances
    (J14 low-churn variant, same convention as composite_rotation.top_n_rotation).
    """
    vol = close.pct_change().rolling(n).std()
    ranks = vol.rank(axis=1, ascending=True)
    in_set = ranks <= top_k
    if rebal_days is None:
        return in_set.astype(int)
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def vol_target(close: pd.Series, target_vol: float = 0.15,
               n: int = 20) -> pd.Series:
    """Scale position by inverse vol.

    T-03-F7 (audit P1-5): zero realized vol now maps to NaN (was division by
    zero -> inf, then clip -> dirty 1.0/-inf targets). NaN signal = flat in
    the engine (truthy mask). Output differs from legacy ONLY on rv==0 cells,
    which previously produced non-finite targets.
    """
    rv = close.pct_change().rolling(n, min_periods=n).std() * np.sqrt(252)
    rv = rv.replace(0, np.nan)
    return (target_vol / rv).clip(upper=1.0)


def vol_breakout(close: pd.Series, n: int = 20) -> pd.Series:
    """Buy when realized vol expands from low base (start of trend)."""
    rv = close.pct_change().rolling(n).std()
    rv_pct = rv / rv.rolling(60).mean()
    return (rv_pct > 1.5).astype(int)


def vol_regime_switch(close: pd.Series, n: int = 20,
                      ma_n: int = 200) -> pd.Series:
    """In low-vol regime hold trend, in high-vol hold cash."""
    rv = close.pct_change().rolling(n).std()
    rv_median = rv.rolling(252).median()
    low_vol = rv < rv_median
    trend_up = close > close.rolling(ma_n).mean()
    return (low_vol & trend_up).astype(int)
