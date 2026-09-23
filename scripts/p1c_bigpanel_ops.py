"""P-1c stock-pool big-panel factor ops (P1C_STOCK_IC.md SS5 scale layer).

Net-room semantics (research/shortline/screening/gtja191_ops.py is the
canonical reference) with streaming internals for the (8792, 5222) panel:

Replaced (memory/time bombs at panel scale, each equivalence-gated vs the
net-room reference in selftest, real cache slice incl. 688 cols + synthetic
NaN-hole panel):
  _roll_weight family -> scipy lfilter FIR stream  (WMA / DECAYLINEAR /
                         rolling_slope; sliding_window_view+matmul would
                         materialize (T-n+1, C, n) ~= 44 GB at n=120)
  HIGHDAY / LOWDAY    -> column-blocked sliding argmax / argmin
  SUM / MEAN / STD    -> prefix-sum stream (pandas min_periods=n default =
                         any-NaN-in-window -> NaN)
  CORR / COVARIANCE / REGBETA / REGRESI -> prefix-sum stream
                         (joint-pair rule, pandas min_periods=n default)
  TS_RANK             -> comparison-broadcast rank (method=average, pct)

Re-exported verbatim from the net-room layer (zero drift by construction,
no gate needed): RANK IFELSE COUNT SMA MAX MIN DELTA DELAY TS_MAX TS_MIN.

All ASCII output (PS console safety). Ledger note: pure operator layer.
"""
import glob
import importlib.util
import json
import os

import numpy as np
import pandas as pd

try:
    from scipy.signal import lfilter
    HAVE_SCIPY = True
except ImportError:                                    # pragma: no cover
    HAVE_SCIPY = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
NETROOM_PATH = os.path.join(ROOT, "research", "shortline", "screening",
                            "gtja191_ops.py")

TOL = 1e-8          # gate tolerance: max(|a-b|) <= TOL * max(1, |ref|)
HD_BLOCK = 256      # HIGHDAY/LOWDAY column block


def _netroom():
    spec = importlib.util.spec_from_file_location("p1c_netroom_ops",
                                                  NETROOM_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------ streaming core

def _prefix(X):
    cs = np.cumsum(X, axis=0)
    head = np.zeros((1, X.shape[1]), dtype=X.dtype)
    return np.vstack([head, cs])


def _any_nan_out(X, n):
    """out rows t>=n-1: NaN iff any NaN inside the window, else the stat."""
    fin = np.isfinite(X)
    k = _prefix((~fin).astype(np.float64))
    kc = k[n:] - k[:-n]           # NaN count per window, shape (T-n+1, C)
    return kc == 0                # True = clean window


def roll_mean_stream(X, n):
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    Xf = np.where(np.isfinite(X), X, 0.0)
    s = _prefix(Xf)
    sa = s[n:] - s[:-n]
    out[n - 1:] = np.where(_any_nan_out(X, n)[:, :], sa / n, np.nan)
    return out


def roll_sum_stream(X, n):
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    Xf = np.where(np.isfinite(X), X, 0.0)
    s = _prefix(Xf)
    sa = s[n:] - s[:-n]
    out[n - 1:] = np.where(_any_nan_out(X, n), sa, np.nan)
    return out


def roll_std_stream(X, n):
    """Rolling std, ddof=1, min_periods=n (any-NaN-in-window -> NaN)."""
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    fin = np.isfinite(X)
    Xf = np.where(fin, X, 0.0)
    s1 = _prefix(Xf)
    s2 = _prefix(Xf * Xf)
    m1 = (s1[n:] - s1[:-n]) / n
    m2 = (s2[n:] - s2[:-n]) / n
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (m2 - m1 * m1) * n / (n - 1.0)
        sd = np.sqrt(np.maximum(var, 0.0))
    out[n - 1:] = np.where(_any_nan_out(X, n), sd, np.nan)
    return out


def _pair_stats(A, B, n):
    """Joint-pair prefix stats; returns None if T < n."""
    T = A.shape[0]
    if T < n:
        return None
    ok = np.isfinite(A) & np.isfinite(B)
    Af = np.where(ok, A, 0.0)
    Bf = np.where(ok, B, 0.0)
    sA, sB = _prefix(Af), _prefix(Bf)
    sAB, sAA, sBB = _prefix(Af * Bf), _prefix(Af * Af), _prefix(Bf * Bf)
    cnt = _prefix(ok.astype(np.float64))

    def d(S):
        return S[n:] - S[:-n]

    k = d(cnt)
    clean = (k == n)
    return clean, d(sA), d(sB), d(sAB), d(sAA), d(sBB)


def roll_corr_stream(A, B, n):
    T, C = A.shape
    out = np.full((T, C), np.nan)
    st = _pair_stats(A, B, n)
    if st is None:
        return out
    clean, sa, sb, sab, saa, sbb = st
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sab - sa * sb / n
        va = saa - sa * sa / n
        vb = sbb - sb * sb / n
        r = cov / np.sqrt(va * vb)
    out[n - 1:] = np.where(clean, r, np.nan)
    return out


def roll_cov_stream(A, B, n):
    """Sample covariance, ddof=1 (pandas Rolling.cov default)."""
    T, C = A.shape
    out = np.full((T, C), np.nan)
    st = _pair_stats(A, B, n)
    if st is None:
        return out
    clean, sa, sb, sab, _, _ = st
    with np.errstate(invalid="ignore", divide="ignore"):
        # sum(xy) - sum(x)sum(y)/n == n * pop_cov -> / (n-1) for ddof=1
        cov = (sab - sa * sb / n) / (n - 1.0)
    out[n - 1:] = np.where(clean, cov, np.nan)
    return out


def roll_wma_stream(X, n, weights):
    """out[t] = sum_k w[k] * X[t-n+1+k], NaN-propagating (net-room _roll_weight).

    FIR: b[m] = w[n-1-m], a=1; lfilter carries NaN in state for exactly n-1
    steps == sliding-window NaN propagation. Head rows t < n-1 -> NaN.
    """
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    if HAVE_SCIPY:
        y = lfilter(np.asarray(weights[::-1], float), [1.0], X, axis=0)
        out[n - 1:] = y[n - 1:]
        return out
    # fallback: chunked sliding-window matmul (bounded memory, no big view)
    from numpy.lib.stride_tricks import sliding_window_view
    step = 128
    for c0 in range(0, C, step):
        c1 = min(c0 + step, C)
        win = sliding_window_view(X[:, c0:c1], n, axis=0)
        out[n - 1:, c0:c1] = win @ weights
    return out


def roll_highday_stream(X, n, block=HD_BLOCK):
    """Days since rolling n-day max (0 = max today); current-NaN rows NaN."""
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    for c0 in range(0, C, block):
        c1 = min(c0 + block, C)
        v = X[:, c0:c1]
        na = ~np.isfinite(v)
        vf = np.where(na, -np.inf, v)
        win = sliding_window_view_(vf, n)
        res = ((n - 1) - win.argmax(axis=2)).astype(np.float64)
        res[na[n - 1:]] = np.nan
        out[n - 1:, c0:c1] = res
    return out


def roll_lowday_stream(X, n, block=HD_BLOCK):
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    for c0 in range(0, C, block):
        c1 = min(c0 + block, C)
        v = X[:, c0:c1]
        na = ~np.isfinite(v)
        vf = np.where(na, +np.inf, v)
        win = sliding_window_view_(vf, n)
        res = ((n - 1) - win.argmin(axis=2)).astype(np.float64)
        res[na[n - 1:]] = np.nan
        out[n - 1:, c0:c1] = res
    return out


def sliding_window_view_(X, n):
    from numpy.lib.stride_tricks import sliding_window_view
    return sliding_window_view(X, n, axis=0)


def ts_rank_stream(X, n):
    """Rolling pct rank of current value in window; method=average, pct.

    pandas rolling(N).rank honors min_periods=N (default = window size):
    ANY NaN inside the window -> NaN (same any-NaN rule as all rolling ops).
    rank_avg = 1 + #(<cur) + ( #(==cur) - 1 ) / 2   (self counts in ==)
    pct      = rank_avg / #valid-in-window (= n on clean windows)
    """
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    fin = np.isfinite(X)
    kfin = _prefix(fin.astype(np.float64))
    cnt = kfin[n:] - kfin[:-n]                    # (T-n+1, C)
    cur = X[n - 1:]
    curf = fin[n - 1:]
    less = np.zeros((T - n + 1, C))
    eq = np.zeros((T - n + 1, C))
    for k in range(n):
        Xs = X[n - 1 - k: T - k]
        f = fin[n - 1 - k: T - k] & curf
        less += ((Xs < cur) & f).astype(float)
        eq += ((Xs == cur) & f).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        rank = 1.0 + less + (eq - 1.0) / 2.0
        pct = rank / cnt
    clean = _any_nan_out(X, n) & curf
    out[n - 1:] = np.where(clean, pct, np.nan)
    return out


# --------------------------------------------- DataFrame-facing op functions
# Signatures mirror research/shortline/screening/gtja191_ops.py exactly
# (the net-room layer the alpha191 vendor bodies call).

NR = None            # lazily-bound net-room module (re-exports)


def _bind():
    global NR
    if NR is None:
        NR = _netroom()
    return NR


def _v(df):
    return np.asarray(df.values, dtype=np.float64)


def _wrap(a, df):
    return pd.DataFrame(a, index=df.index, columns=df.columns)


def MEAN(A: pd.DataFrame, N: int):
    return _wrap(roll_mean_stream(_v(A), N), A)


def SUM(A: pd.DataFrame, n: int):
    return _wrap(roll_sum_stream(_v(A), n), A)


def STD(price: pd.DataFrame, N: int):
    return _wrap(roll_std_stream(_v(price), N), price)


def WMA(data: pd.DataFrame, n: int):
    weight = (np.arange(n) + 1).astype(float)
    weight = weight / weight.sum()
    return _wrap(roll_wma_stream(_v(data), n, weight), data)


def DECAYLINEAR(data: pd.DataFrame, n: int):
    weight = np.array([2 * i / (n * (n + 1)) for i in range(1, n + 1)])
    return _wrap(roll_wma_stream(_v(data), n, weight), data)


def rolling_slope(X: pd.DataFrame, N: int):
    k = np.arange(N, dtype=float)
    denom = float(((k - (N - 1) / 2) ** 2).sum())
    weights = (k - (N - 1) / 2) / denom
    return _wrap(roll_wma_stream(_v(X), N, weights), X)


def CORR(A: pd.DataFrame, B: pd.DataFrame, n: int):
    return _wrap(roll_corr_stream(_v(A), _v(B), n), A)


def COVARIANCE(A: pd.DataFrame, B: pd.DataFrame, n: int, sign=False):
    cov = _wrap(roll_cov_stream(_v(A), _v(B), n), A)
    if sign:
        return np.sign(cov)
    return cov


def REGBETA(X: pd.DataFrame, Y: pd.DataFrame, N: int):
    """net-room: X.rolling(N).cov(Y) / X.rolling(N).var()."""
    xv, yv = _v(X), _v(Y)
    cov = roll_cov_stream(xv, yv, N)
    var = roll_var_x_stream(xv, N)
    with np.errstate(invalid="ignore", divide="ignore"):
        beta = cov / var
    return _wrap(beta, X)


def roll_var_x_stream(X, n):
    """Rolling var of X alone, ddof=1, min_periods=n (any-NaN -> NaN)."""
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    fin = np.isfinite(X)
    Xf = np.where(fin, X, 0.0)
    s1 = _prefix(Xf)
    s2 = _prefix(Xf * Xf)
    m1 = (s1[n:] - s1[:-n]) / n
    m2 = (s2[n:] - s2[:-n]) / n
    with np.errstate(invalid="ignore", divide="ignore"):
        var = (m2 - m1 * m1) * n / (n - 1.0)
    out[n - 1:] = np.where(_any_nan_out(X, n), var, np.nan)
    return out


def REGRESI(X: pd.DataFrame, Y: pd.DataFrame, N: int):
    """net-room: X.rolling(N).mean() - Y.rolling(N).mean() * REGBETA(X, Y, N)."""
    xv, yv = _v(X), _v(Y)
    beta = roll_cov_stream(xv, yv, N) / roll_var_x_stream(xv, N)
    mx = roll_mean_stream(xv, N)
    my = roll_mean_stream(yv, N)
    with np.errstate(invalid="ignore", divide="ignore"):
        resi = mx - my * beta
    return _wrap(resi, X)


def HIGHDAY(A: pd.DataFrame, N: int, zero_diff=False):
    na_map = A.isna().astype(float).replace(1., np.nan)
    res = _wrap(roll_highday_stream(_v(A), N), A)
    return res - int(zero_diff) + na_map


def LOWDAY(A: pd.DataFrame, N: int, zero_diff=False):
    na_map = A.isna().astype(float).replace(1., np.nan)
    res = _wrap(roll_lowday_stream(_v(A), N), A)
    return res - int(zero_diff) + na_map


def TS_RANK(data: pd.DataFrame, N: int):
    return _wrap(ts_rank_stream(_v(data), N), data)


def RANK(data: pd.DataFrame):
    return _bind().RANK(data)


def IFELSE(condition, A, B):
    return _bind().IFELSE(condition, A, B)


def COUNT(condition, n, na_map=None):
    return _bind().COUNT(condition, n, na_map)


def SMA(data, n, m, ignore_nan=True):
    return _bind().SMA(data, n, m, ignore_nan)


def MAX(A, B):
    return _bind().MAX(A, B)


def MIN(A, B):
    return _bind().MIN(A, B)


def DELTA(A, n):
    return _bind().DELTA(A, n)


def DELAY(A, n):
    return _bind().DELAY(A, n)


def TS_MAX(A, N):
    return _bind().TS_MAX(A, N)


def TS_MIN(A, N):
    return _bind().TS_MIN(A, N)


# ------------------------------------------------------------------- gates

def _cmp(a, b, name, rows):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.isnan(a), np.isnan(b)
    mask_equal = bool((na == nb).all())
    m = ~na & ~nb
    if m.any():
        diff = float(np.max(np.abs(a[m] - b[m])))
        ref = float(np.max(np.maximum(np.abs(b[m]), 1.0)))
        ok = mask_equal and diff <= TOL * ref
    else:
        diff, ref = 0.0, 1.0
        ok = mask_equal
    rows.append({"gate": name, "nan_mask_equal": mask_equal,
                 "max_abs_diff": diff, "tol_scale": ref, "pass": ok})
    return ok


def _gate_panel(X, Bv, nr, rows, tag):
    """X, Bv: (T, C) float64 arrays with NaNs. Compare vs net-room ops."""
    df = pd.DataFrame(X)
    dfb = pd.DataFrame(Bv)
    ok = True
    ok &= _cmp(roll_mean_stream(X, 20),
               nr.MEAN(df, 20).values, f"{tag}:MEAN(20)", rows)
    ok &= _cmp(roll_sum_stream(X, 20),
               nr.SUM(df, 20).values, f"{tag}:SUM(20)", rows)
    ok &= _cmp(roll_std_stream(X, 20),
               nr.STD(df, 20).values, f"{tag}:STD(20)", rows)
    ok &= _cmp(roll_corr_stream(X, Bv, 20),
               nr.CORR(df, dfb, 20).values, f"{tag}:CORR(20)", rows)
    ok &= _cmp(roll_cov_stream(X, Bv, 20),
               nr.COVARIANCE(df, dfb, 20).values, f"{tag}:COV(20)", rows)
    ok &= _cmp(np.asarray(REGBETA(df, dfb, 20).values),
               nr.REGBETA(df, dfb, 20).values, f"{tag}:REGBETA(20)", rows)
    ok &= _cmp(np.asarray(REGRESI(df, dfb, 20).values),
               nr.REGRESI(df, dfb, 20).values, f"{tag}:REGRESI(20)", rows)
    w = (np.arange(10) + 1) / (np.arange(10) + 1).sum()
    ok &= _cmp(roll_wma_stream(X, 10, w),
               nr._roll_weight(X, w), f"{tag}:WMA(10)", rows)
    dl = np.array([2 * i / (10 * 11) for i in range(1, 11)])
    ok &= _cmp(roll_wma_stream(X, 10, dl),
               nr._roll_weight(X, dl), f"{tag}:DECAYLINEAR(10)", rows)
    ok &= _cmp(np.asarray(rolling_slope(df, 20).values),
               nr.rolling_slope(df, 20).values, f"{tag}:rolling_slope(20)",
               rows)
    ok &= _cmp(roll_highday_stream(X, 20, block=64),
               np.asarray(nr.HIGHDAY(df, 20).values),
               f"{tag}:HIGHDAY(20)", rows)
    ok &= _cmp(roll_highday_stream(X, 20, block=64),
               np.asarray(nr.HIGHDAY(df, 20, zero_diff=True).values) + 1.0,
               f"{tag}:HIGHDAY(20,zero_diff+1)", rows)
    ok &= _cmp(roll_lowday_stream(X, 20, block=64),
               np.asarray(nr.LOWDAY(df, 20).values),
               f"{tag}:LOWDAY(20)", rows)
    ok &= _cmp(ts_rank_stream(X, 12),
               nr.TS_RANK(df, 12).values, f"{tag}:TS_RANK(12)", rows)
    return ok


def real_slice(n_syms=120, rows_head=3000, n_rows=400):
    """Real cache slice incl. 688/689 columns (probe convention)."""
    meta = json.load(open(os.path.join(CACHE_DIR, "meta.json"),
                          encoding="utf-8"))
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))]
    assert len(syms) == meta["shape"]["N"], "bars dir vs cache shape mismatch"
    N = meta["shape"]["N"]
    star = [i for i, s in enumerate(syms)
            if s.startswith("688") or s.startswith("689")][:20]
    rng = np.random.default_rng(20260923)
    cols = sorted(set(list(rng.choice(N, size=n_syms - 20,
                                      replace=False)) + star))
    close = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    X = np.asarray(close[rows_head:rows_head + n_rows, cols], dtype=np.float64)
    return np.where(np.isfinite(X), X, np.nan), rng


def selftest():
    """Offline equivalence gates vs net-room (real slice + synthetic)."""
    rows = []
    X, rng = real_slice()
    Bv = rng.normal(size=X.shape)
    ok = _gate_panel(X, Bv, _bind(), rows, "real_slice")
    Y = rng.normal(size=(200, 40))
    Y[50:70, 3] = np.nan
    Y[:, 7] = np.nan
    Y[120:126, 20:25] = np.nan
    ok &= _gate_panel(Y, rng.normal(size=Y.shape), _bind(), rows,
                      "synthetic_holes")
    print(json.dumps(rows, indent=2))
    print(f"BIGPANEL OPS {'PASS' if ok else 'FAIL'} "
          f"(scipy={'yes' if HAVE_SCIPY else 'NO-fallback-matmul'})")
    return ok


import json  # noqa: E402  (used by real_slice; kept at tail to minimize deps)

if __name__ == "__main__":
    import sys
    sys.exit(0 if selftest() else 1)
