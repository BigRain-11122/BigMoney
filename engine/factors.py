"""Factor library: 15 factors across momentum/reversal/vol/liquidity/trend/RS.

All factors computed on daily OHLCV. Cross-sectional z-score applied downstream.
"""
import numpy as np
import pandas as pd


# ---------- Momentum ----------
def mom_n(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """N-day total return."""
    return close.pct_change(n)


def mom_12_1(close: pd.DataFrame) -> pd.DataFrame:
    """Academic classic: 12-1 month momentum (skip last month)."""
    return close.shift(20) / close.shift(240) - 1


# ---------- Reversal ----------
def rev_n(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """Short-term reversal: -1 * N-day return."""
    return -close.pct_change(n)


# ---------- Volatility ----------
def vol_n(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """N-day realized vol (annualized)."""
    rets = close.pct_change()
    return rets.rolling(n).std() * np.sqrt(252)


# ---------- Liquidity ----------
def amt_n(amount: pd.DataFrame, n: int) -> pd.DataFrame:
    """N-day average amount (RMB)."""
    return amount.rolling(n).mean()


# ---------- Trend ----------
def ma_bias(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """(close - MA_n) / MA_n."""
    ma = close.rolling(n).mean()
    return (close - ma) / ma


def adx(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame,
        n: int = 14) -> pd.DataFrame:
    """Average Directional Index (trend strength)."""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr = pd.concat([
        (high - low).stack(),
        (high - close.shift(1)).stack().abs(),
        (low - close.shift(1)).stack().abs(),
    ], axis=1).max(axis=1).unstack()
    atr = tr.rolling(n).mean()
    plus_di = 100 * (plus_dm.rolling(n).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(n).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.rolling(n).mean()


# ---------- Relative strength vs benchmark ----------
def rs_vs(close: pd.DataFrame, bench: pd.Series, n: int) -> pd.DataFrame:
    """ETF N-day return minus benchmark N-day return."""
    r = close.pct_change(n)
    br = bench.pct_change(n)
    return r.subtract(br, axis=0)


# ---------- Volume-price correlation ----------
def vol_price_corr(close: pd.DataFrame, volume: pd.DataFrame,
                   n: int = 20) -> pd.DataFrame:
    rets = close.pct_change()
    return rets.rolling(n).corr(volume)


# ---------- Registry ----------
def gap_overnight(open_: pd.DataFrame, close: pd.DataFrame) -> pd.DataFrame:
    """Overnight gap: today's open vs yesterday's close."""
    return open_ / close.shift(1) - 1


def intraday_range(high: pd.DataFrame, low: pd.DataFrame,
                   close: pd.DataFrame) -> pd.DataFrame:
    """Normalized intraday range."""
    return (high - low) / close


def volume_trend(volume: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.DataFrame:
    """Volume MA ratio: fast MA / slow MA - 1."""
    return volume.rolling(fast).mean() / volume.rolling(slow).mean() - 1


def price_position(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame,
                   n: int = 20) -> pd.DataFrame:
    """Where close sits in N-day high-low range (0=low, 1=high)."""
    hh = high.rolling(n).max()
    ll = low.rolling(n).min()
    return (close - ll) / (hh - ll).replace(0, np.nan)


def mom_accel(close: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.DataFrame:
    """Momentum acceleration: fast momentum minus slow momentum."""
    return close.pct_change(fast) - close.pct_change(slow)


def vol_regime(close: pd.DataFrame, n_short: int = 20, n_long: int = 60) -> pd.DataFrame:
    """Volatility regime: short-term vol / long-term vol."""
    return close.pct_change().rolling(n_short).std() / \
           close.pct_change().rolling(n_long).std()


def up_day_ratio(close: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Fraction of up days in last N days."""
    rets = close.pct_change()
    return (rets > 0).rolling(n).mean()


def extreme_freq(close: pd.DataFrame, n: int = 20,
                 threshold: float = 0.02) -> pd.DataFrame:
    """Frequency of extreme moves (|return| > threshold) in N days."""
    rets = close.pct_change()
    return (rets.abs() > threshold).rolling(n).mean()


def drawdown_from_high(close: pd.DataFrame, n: int = 60) -> pd.DataFrame:
    """Drawdown from N-day high."""
    hh = close.rolling(n).max()
    return close / hh - 1


def volume_price_diverge(close: pd.DataFrame, volume: pd.DataFrame,
                         n: int = 20) -> pd.DataFrame:
    """Negative when price up but volume down (divergence)."""
    return close.pct_change(n) - volume.pct_change(n)


def return_skew(close: pd.DataFrame, n: int = 60) -> pd.DataFrame:
    """Skewness of returns (negative skew = crash-prone)."""
    return close.pct_change().rolling(n).skew()


def return_kurt(close: pd.DataFrame, n: int = 60) -> pd.DataFrame:
    """Excess kurtosis of returns."""
    return close.pct_change().rolling(n).kurt()


def overnight_minus_intraday(open_: pd.DataFrame, close: pd.DataFrame) -> pd.DataFrame:
    """Overnight return minus intraday return (momentum style)."""
    overnight = open_ / close.shift(1) - 1
    intraday = close / open_ - 1
    return overnight - intraday


def ma_slope(close: pd.DataFrame, n: int = 20, lookback: int = 5) -> pd.DataFrame:
    """Slope of MA_n over last lookback days (normalized)."""
    ma = close.rolling(n).mean()
    return ma / ma.shift(lookback) - 1


def amihud_illiquidity(close: pd.DataFrame, amount: pd.DataFrame,
                       n: int = 20) -> pd.DataFrame:
    """Amihud illiquidity: mean(|return|/amount). Higher = less liquid."""
    rets = close.pct_change().abs()
    return (rets / amount).rolling(n).mean()


FACTORS = {
    # --- classic ---
    "mom_20":  lambda d: mom_n(d["close"], 20),
    "mom_60":  lambda d: mom_n(d["close"], 60),
    "mom_120": lambda d: mom_n(d["close"], 120),
    "mom_12_1": lambda d: mom_12_1(d["close"]),
    "rev_5":   lambda d: rev_n(d["close"], 5),
    "rev_10":  lambda d: rev_n(d["close"], 10),
    "vol_20":  lambda d: vol_n(d["close"], 20),
    "vol_60":  lambda d: vol_n(d["close"], 60),
    "amt_20":  lambda d: amt_n(d["amount"], 20),
    "ma_bias_20": lambda d: ma_bias(d["close"], 20),
    "ma_bias_60": lambda d: ma_bias(d["close"], 60),
    "adx_14":     lambda d: adx(d["high"], d["low"], d["close"], 14),
    "vol_price_corr": lambda d: vol_price_corr(d["close"], d["volume"], 20),

    # --- exotic ---
    "gap_overnight": lambda d: gap_overnight(d["open"], d["close"]),
    "intraday_range": lambda d: intraday_range(d["high"], d["low"], d["close"]),
    "volume_trend":  lambda d: volume_trend(d["volume"]),
    "price_position": lambda d: price_position(d["high"], d["low"], d["close"]),
    "mom_accel":     lambda d: mom_accel(d["close"]),
    "vol_regime":    lambda d: vol_regime(d["close"]),
    "up_day_ratio":  lambda d: up_day_ratio(d["close"]),
    "extreme_freq":  lambda d: extreme_freq(d["close"]),
    "drawdown_60":   lambda d: drawdown_from_high(d["close"]),
    "vol_price_diverge": lambda d: volume_price_diverge(d["close"], d["volume"]),
    "return_skew":   lambda d: return_skew(d["close"]),
    "return_kurt":   lambda d: return_kurt(d["close"]),
    "overnight_minus_intraday": lambda d: overnight_minus_intraday(d["open"], d["close"]),
    "ma_slope_20":   lambda d: ma_slope(d["close"], 20, 5),
    "amihud_illiq":  lambda d: amihud_illiquidity(d["close"], d["amount"]),
}


def compute_all(prices: dict, bench: pd.Series = None) -> dict:
    """prices: dict[sym] -> DataFrame with OHLCV.
    Returns dict[factor_name] -> DataFrame (date x symbol).
    """
    panel = {}
    for field in ["open", "high", "low", "close", "volume", "amount"]:
        df = pd.DataFrame({sym: p[field] for sym, p in prices.items()
                          if field in p.columns})
        panel[field] = df.sort_index().ffill()

    factors = {}
    for name, fn in FACTORS.items():
        try:
            factors[name] = fn(panel)
        except Exception as e:
            print(f"  {name} fail: {e}")

    if bench is not None:
        bench = bench.reindex(panel["close"].index).ffill()
        factors["rs_20_csi300"] = rs_vs(panel["close"], bench, 20)
        factors["rs_60_csi300"] = rs_vs(panel["close"], bench, 60)

    return factors
