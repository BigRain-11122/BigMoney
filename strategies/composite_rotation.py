"""J7 composite-factor Top-N rotation (BACKTEST_PLAN P1).

Signal = J6 composite factor (see scripts/composite_ic.py, same weights):
  0.3*(-z(vol_60)) + 0.3*(-z(intraday_range))
  + 0.2*z(mom_12_1)  + 0.2*z(price_position)

Top-N membership is recomputed every `rebal_days` (non-overlapping windows)
and held between rebalances. All inputs are backward-looking; the engine
executes queued entries at next-day open (no look-ahead). mom_12_1 needs a
240-day warmup, so live signals start ~1 year into the panel.
"""
import numpy as np
import pandas as pd

from engine.factors import FACTORS

WEIGHTS = {
    "vol_60": -0.3,
    "intraday_range": -0.3,
    "mom_12_1": +0.2,
    "price_position": +0.2,
}


def _xs_zscore(df: pd.DataFrame, min_n: int = 5) -> pd.DataFrame:
    """Cross-sectional z-score per date; dates with < min_n valid rows -> NaN."""
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=0)
    valid = df.notna().sum(axis=1) >= min_n
    z = df.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)
    z[~valid] = np.nan
    return z


def composite_score(high: pd.DataFrame, low: pd.DataFrame,
                    close: pd.DataFrame) -> pd.DataFrame:
    """Weighted sum of cross-sectionally z-scored components."""
    d = {"high": high, "low": low, "close": close}
    out = None
    for name, w in WEIGHTS.items():
        z = _xs_zscore(FACTORS[name](d))
        out = w * z if out is None else out + w * z
    return out


def top_n_rotation(high: pd.DataFrame, low: pd.DataFrame,
                   close: pd.DataFrame, top_n: int = 5,
                   rebal_days: int = 20) -> pd.DataFrame:
    """Hold the top_n composite-score ETFs, refreshed every rebal_days."""
    score = composite_score(high, low, close)
    ranks = score.rank(axis=1, ascending=False)
    in_set = ranks <= top_n
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)
