"""Clean-room GTJA191 factor ops (vendor-semantic replica, no talib/qlib/cython).

Replicates research/shortline/external/gtja191_lib_factor_ops.py semantics in
pure pandas/numpy so external/gtja191_alpha191.py can run without TA-Lib or the
original project's private `factors.ops.rolling` cython modules (playbook §2.2:
"TA-Lib C 依赖不装", "缺则降级").

Deltas vs vendored file (documented, semantics-preserving):
- SMA/WMA/DECAYLINEAR/HIGHDAY/LOWDAY/RANK/IFELSE/COUNT/MAX/MIN/DELTA/DELAY/
  SUM/MEAN/CORR/COVARIANCE/TS_MAX/TS_MIN/TS_RANK/STD/REGBETA/REGRESI: direct
  pandas replicas of the vendored bodies.
- WMA/DECAYLINEAR/HIGHDAY/LOWDAY: cython `_wma/_max_distance/_min_distance`
  replaced by numpy sliding_window_view equivalents.
- HIGHDAY/LOWDAY semantic: distance in days to the rolling N-day extreme
  (0 = extreme is today); NaN rows preserved via na_map (same as vendor).
- rolling_slope: qlib's rolling linear-regression slope replaced by fixed
  linear weights on the window (verified vs np.polyfit in selftest).
- talib LINEARREG family: NOT ported (unused by alpha191 bodies; grep=0).
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view


def _roll_weight(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Rolling weighted sum: out[t] = sum(w[k] * values[t-K+1+k]). NaN-propagating."""
    T, C = values.shape
    K = len(weights)
    if T < K:
        return np.full((T, C), np.nan)
    win = sliding_window_view(values, K, axis=0)      # (T-K+1, C, K)
    res = np.full((T, C), np.nan)
    res[K - 1:] = win @ weights
    return res


def RANK(data: pd.DataFrame):
    return data.rank(axis=1, pct=True)


def IFELSE(condition: pd.DataFrame, A, B):
    if isinstance(A, pd.DataFrame):
        na_map = A.isna().astype(float).replace(1., np.nan)
        return A.where(condition, B) + na_map
    elif isinstance(B, pd.DataFrame):
        na_map = B.isna().astype(float).replace(1., np.nan)
        return B.where(~condition, A) + na_map
    raise ValueError("IFELSE: A or B must be a DataFrame")


def COUNT(condition: pd.DataFrame, n: int, na_map: pd.DataFrame = None):
    condition = condition.astype(int)
    if na_map is not None:
        condition = condition + na_map
    return condition.rolling(n).sum()


def SMA(data: pd.DataFrame, n: int, m: int, ignore_nan=True):
    assert n > m
    na_map = data.isna().astype(float).replace(1., np.nan)
    return data.ewm(alpha=m / n, ignore_na=ignore_nan).mean() + na_map


def WMA(data: pd.DataFrame, n: int):
    weight = (np.arange(n) + 1).astype(float)
    weight = weight / weight.sum()
    return pd.DataFrame(_roll_weight(data.values, weight),
                        index=data.index, columns=data.columns)


def DECAYLINEAR(data: pd.DataFrame, n: int):
    weight = np.array([2 * i / (n * (n + 1)) for i in range(1, n + 1)])
    return pd.DataFrame(_roll_weight(data.values, weight),
                        index=data.index, columns=data.columns)


def DELTA(A: pd.DataFrame, n: int):
    return A.diff(n)


def DELAY(A: pd.DataFrame, n: int):
    return A.shift(n)


def SUM(A: pd.DataFrame, n: int):
    return A.rolling(n).sum()


def MEAN(A: pd.DataFrame, N: int):
    return A.rolling(N).mean()


def CORR(A: pd.DataFrame, B: pd.DataFrame, n: int):
    return A.rolling(n).corr(B)


def COVARIANCE(A: pd.DataFrame, B: pd.DataFrame, n: int, sign=False):
    if sign:
        return np.sign(A.rolling(n).cov(B))
    return A.rolling(n).cov(B)


def MAX(A, B):
    return np.maximum(A, B)


def MIN(A, B):
    return np.minimum(A, B)


def HIGHDAY(A: pd.DataFrame, N: int, zero_diff=False):
    """Days since the rolling N-day max (0 = max is today); NaN rows kept NaN."""
    na_map = A.isna().astype(float).replace(1., np.nan)
    v = A.fillna(-np.inf).values
    T, C = v.shape
    res = np.full((T, C), np.nan)
    if T >= N:
        win = sliding_window_view(v, N, axis=0)      # (T-N+1, C, N)
        res[N - 1:] = (N - 1) - win.argmax(axis=2)
    return pd.DataFrame(res, index=A.index, columns=A.columns) - int(zero_diff) + na_map


def LOWDAY(A: pd.DataFrame, N: int, zero_diff=False):
    na_map = A.isna().astype(float).replace(1., np.nan)
    v = A.fillna(+np.inf).values
    T, C = v.shape
    res = np.full((T, C), np.nan)
    if T >= N:
        win = sliding_window_view(v, N, axis=0)
        res[N - 1:] = (N - 1) - win.argmin(axis=2)
    return pd.DataFrame(res, index=A.index, columns=A.columns) - int(zero_diff) + na_map


def TS_MAX(A: pd.DataFrame, N: int):
    return A.rolling(N).max()


def TS_MIN(A: pd.DataFrame, N: int):
    return A.rolling(N).min()


def TS_RANK(data: pd.DataFrame, N: int):
    return data.rolling(N).rank(pct=True)


def STD(price: pd.DataFrame, N: int):
    return price.rolling(N).std()


def REGBETA(X: pd.DataFrame, Y: pd.DataFrame, N: int):
    return X.rolling(N).cov(Y) / X.rolling(N).var()


def REGRESI(X: pd.DataFrame, Y: pd.DataFrame, N: int):
    return X.rolling(N).mean() - Y.rolling(N).mean() * REGBETA(X, Y, N)


def rolling_slope(X: pd.DataFrame, N: int):
    """qlib rolling_slope: OLS slope of X against time over N-window, vectorized.

    slope_t = sum_k w_k * x_{t-N+1+k},  w_k = (k - (N-1)/2) / sum((k-(N-1)/2)^2).
    """
    k = np.arange(N, dtype=float)
    denom = float(((k - (N - 1) / 2) ** 2).sum())
    weights = (k - (N - 1) / 2) / denom
    return pd.DataFrame(_roll_weight(X.values.astype(float), weights),
                        index=X.index, columns=X.columns)


def rolling_rsquare(X: pd.DataFrame, N: int):
    """qlib rolling_rsquare via R^2 = corr(x, t)^2 (unused by alpha191, provided for completeness)."""
    k = np.arange(N, dtype=float)
    corr = X.rolling(N).apply(lambda s: float(np.corrcoef(s, k)[0, 1]), raw=True)
    return corr ** 2
