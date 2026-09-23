"""Technical-analysis classic school (P-4 batch 2A, CEO order O-20260923-1828).

Migrated verbatim-semantics from Money0923 (SYSTEM_AUDIT s4 archive families)
plus two new candlestick-pattern designs; all daily-bar causal constructions,
single source of truth for scripts/p4_batch2a_screen.py (no dual impl, F-05).

Conventions (repo contract, PLAN s2.1):
- per-symbol Series in -> position Series out (0/1 int, long-only);
- state machines use np.where(entry,1,np.where(exit,0,nan)).ffill().fillna(0)
  (entry wins on same-day conflict, mean_reversion.py convention);
- signals computed on close of day t; engine executes at t+1 open (T+1).
"""
import numpy as np
import pandas as pd


def _hold(entry: pd.Series, exit_: pd.Series) -> pd.Series:
    """State machine: 1 on entry day, 0 on exit day, ffill between."""
    pos = np.where(entry, 1, np.where(exit_, 0, np.nan))
    return (pd.Series(pos, index=entry.index)
            .ffill().fillna(0).astype(int))


def strong_close(high: pd.Series, low: pd.Series, close: pd.Series,
                 volume: pd.Series, pos_th: float = 0.85,
                 vol_mult: float = 1.5, vol_len: int = 20) -> pd.Series:
    """Late-day strength (M0923 StrongClose, params frozen): close sits in
    the top of its daily range with volume surge and an up day -> hold until
    intraday position falls back below 0.5. Daily-frequency honest proxy for
    end-of-session accumulation (no intraday data used)."""
    rng = (high - low).replace(0, np.nan)
    pos_in_range = (close - low) / rng
    vavg = volume.rolling(vol_len, min_periods=vol_len).mean()
    up = close.pct_change() > 0
    entry = ((pos_in_range >= pos_th) & (volume >= vol_mult * vavg)
             & up & (vavg > 0)).fillna(False)
    exit_ = (pos_in_range < 0.5).fillna(False)
    return _hold(entry, exit_)


def macd_trend(close: pd.Series, fast: int = 12, slow: int = 26,
                signal: int = 9) -> pd.Series:
    """MACD golden-cross trend (Appel; M0923 MacdTrend need_positive=1,
    params frozen 12/26/9): hold while DIF>DEA AND DIF>0 (zero-line
    confirmation). Condition-state semantics per M0923 (re-evaluated daily)."""
    dif = (close.ewm(span=fast, adjust=False).mean()
           - close.ewm(span=slow, adjust=False).mean())
    dea = dif.ewm(span=signal, adjust=False).mean()
    return ((dif > dea) & (dif > 0)).astype(int)


def kdj_reversal(high: pd.Series, low: pd.Series, close: pd.Series,
                 kdj_n: int = 9, entry_j: float = 0.0, exit_j: float = 80.0,
                 trend_ma: int = 60) -> pd.Series:
    """KDJ oversold reversion (China-market classic; M0923 KdjReversal,
    params frozen 9/0/80/60): RSV=(C-Ln)/(Hn-Ln)*100, K=SMA(RSV,3,1),
    D=SMA(K,3,1), J=3K-2D. Enter when J<0 (oversold) above the trend MA;
    exit when J recovers above exit_j."""
    llv = low.rolling(kdj_n, min_periods=1).min()
    hhv = high.rolling(kdj_n, min_periods=1).max()
    rsv = ((close - llv) / (hhv - llv).replace(0, np.nan)) * 100.0
    k = rsv.ewm(alpha=1.0 / 3.0, adjust=False).mean()
    d = k.ewm(alpha=1.0 / 3.0, adjust=False).mean()
    j = 3.0 * k - 2.0 * d
    trend_up = close > close.rolling(trend_ma, min_periods=trend_ma).mean()
    entry = (trend_up & (j < entry_j)).fillna(False)
    exit_ = (j > exit_j).fillna(False)
    return _hold(entry, exit_)


def rsrs_timing(high: pd.Series, low: pd.Series, window: int = 18,
                z_win: int = 250, buy_z: float = 0.8,
                exit_z: float = -0.8) -> pd.Series:
    """RSRS support-resistance relative strength timing (Everbright 2017
    research-note family; M0923 RsrsTiming): OLS slope of high~low over
    `window` days, rolling z-scored over `z_win`; hold while z>buy_z, clear
    when z<exit_z. Panel adaptation (pre-registered): per-symbol state
    instead of M0923 single-target; z_win 600->250 disclosed (core48
    2020-anchored panel length)."""
    x, y, n = low, high, window
    sx = x.rolling(n).sum()
    sy = y.rolling(n).sum()
    sxy = (x * y).rolling(n).sum()
    sxx = (x * x).rolling(n).sum()
    denom = (n * sxx - sx * sx).replace(0, np.nan)
    beta = (n * sxy - sx * sy) / denom
    mu = beta.rolling(z_win, min_periods=z_win).mean()
    sd = beta.rolling(z_win, min_periods=z_win).std().replace(0, np.nan)
    z = (beta - mu) / sd
    entry = (z > buy_z).fillna(False)
    exit_ = (z < exit_z).fillna(False)
    return _hold(entry, exit_)


def streak_up(close: pd.Series, streak_n: int = 3,
              min_up: float = 0.0) -> pd.Series:
    """Consecutive up-day relay (M0923 Streak, params frozen): N straight
    up-days -> hold; a non-up day clears. Streak count is a different
    dimension from cumulative momentum (3x+1% != 1x+3%)."""
    up = (close > close.shift(1)) & (close.pct_change() >= min_up - 1e-9)
    cnt = up.astype(int)
    for k in range(2, streak_n + 1):
        cnt = np.where(up.shift(k - 1).fillna(False), cnt + 1, 0)
    cnt = pd.Series(cnt, index=close.index)
    entry = (cnt >= streak_n).fillna(False)
    return _hold(entry, (~up).fillna(False))


def vol_breakout(high: pd.Series, low: pd.Series, close: pd.Series,
                 volume: pd.Series, brk_len: int = 20,
                 vol_mult: float = 1.5, vol_avg_len: int = 20,
                 exit_len: int = 10) -> pd.Series:
    """Volume-confirmed breakout (M0923 VolBreak, params frozen 20/1.5/20/10):
    close breaks the prior N-day high of `high` with volume >= mult x
    average; exit when close falls below the prior N-day low of `low`.
    Same-intent family as P1-screened breakout_confirm (volume-confirmed
    breakout) -- read results with the pre-registered same-family discount
    (P4_BATCH2A s2)."""
    brk = close > high.rolling(brk_len).max().shift(1)
    vavg = volume.rolling(vol_avg_len, min_periods=vol_avg_len).mean()
    entry = (brk & (volume >= vol_mult * vavg) & (vavg > 0)).fillna(False)
    exit_ = (close < low.rolling(exit_len).min().shift(1)).fillna(False)
    return _hold(entry, exit_)


def hammer_reversal(open_: pd.Series, high: pd.Series, low: pd.Series,
                    close: pd.Series, body_max: float = 0.35,
                    shadow_mult: float = 2.0,
                    drop_th: float = -0.05) -> pd.Series:
    """Hammer reversal (NEW design; classic candlestick definition): small
    body near the session high, lower shadow >= shadow_mult x body, little
    upper shadow, appearing after a >=5% five-day drop. Exit when close
    reclaims the 20-day MA (reversal thesis played out)."""
    body = (close - open_).abs()
    rng = high - low
    ok_range = rng > 0.005 * close          # meaningful session range floor
    small_body = body <= body_max * rng.replace(0, np.nan)
    lower_shadow = (np.minimum(open_, close) - low) >= shadow_mult * body
    upper_shadow = (high - np.maximum(open_, close)) <= body
    hammer = (ok_range & small_body & lower_shadow & upper_shadow).fillna(False)
    downtrend = (close.pct_change(5) < drop_th).fillna(False)
    ma20 = close.rolling(20, min_periods=20).mean()
    return _hold(hammer & downtrend, (close > ma20).fillna(False))


def engulf_reversal(open_: pd.Series, close: pd.Series,
                    drop_th: float = -0.05) -> pd.Series:
    """Bullish engulfing reversal (NEW design; classic candlestick
    definition): green body fully engulfs the prior red body after a >=5%
    five-day drop. Exit when close reclaims the 20-day MA."""
    prev_red = (close.shift(1) < open_.shift(1)).fillna(False)
    red_body = (open_.shift(1) - close.shift(1)).fillna(0)
    green = (close > open_).fillna(False)
    engulf = (green & prev_red
              & (close >= open_.shift(1)) & (open_ <= close.shift(1))
              & ((close - open_) > red_body)).fillna(False)
    downtrend = (close.pct_change(5) < drop_th).fillna(False)
    ma20 = close.rolling(20, min_periods=20).mean()
    return _hold(engulf & downtrend, (close > ma20).fillna(False))
