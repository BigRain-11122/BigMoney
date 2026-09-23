"""Folk-tactics school (P-4 folk expansion, CEO order O-20260923-2134).

Folk sayings / retail-lore tactics adapted to the ETF daily-bar domain
(each construction frozen, daily-OHLCV-only, no intraday). Single source
of truth for scripts/p4_folk_screen.py. Folk-lore validity is adjudicated
by the gate chain, never assumed (zoo s12 marking).

Conventions: per-symbol Series in -> 0/1 position out; state machines via
strategies.ta._hold; signals at close of day t, engine fills t+1 open.
"""
import numpy as np
import pandas as pd

from strategies.ta import _hold


def _ma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def low_suction(open_: pd.Series, high: pd.Series, low: pd.Series,
                close: pd.Series, volume: pd.Series,
                shrink: float = 0.8) -> pd.Series:
    """'低吸富三代' (folk): in an uptrend, price pulls back to the rising
    MA20, volume shrinks, and close holds above MA20. Near-family of P1
    pullback_bounce (uptrend pullback) -- discount pre-registered.
    Exit: decisive break below MA20."""
    ma20 = _ma(close, 20)
    uptrend = (ma20 > ma20.shift(5)) & (close > _ma(close, 60))
    touch = low <= ma20
    holding = close >= ma20
    vavg = volume.rolling(20, min_periods=20).mean()
    quiet = volume < shrink * vavg
    entry = (uptrend & touch & holding & quiet).fillna(False)
    return _hold(entry, (close < ma20 * 0.98).fillna(False))


def lian_yin_first_yang(open_: pd.Series, high: pd.Series, low: pd.Series,
                        close: pd.Series, n_down: int = 3) -> pd.Series:
    """First yang after >=N straight down days (folk '跌多了总有反抽').
    Exit: close below MA5."""
    down = (close < close.shift(1)).fillna(False)
    run = down.copy()
    for k in range(2, n_down + 1):
        run = run & down.shift(k - 1)
    first_yang = run.shift(1) & (close > open_) & (close > close.shift(1))
    ma5 = _ma(close, 5)
    return _hold(first_yang.fillna(False), (close < ma5).fillna(False))


def false_break_back(open_: pd.Series, high: pd.Series, low: pd.Series,
                     close: pd.Series, n_back: int = 3) -> pd.Series:
    """False-break reclaim (folk '假摔'): close broke below MA60 within
    the last 1-3 sessions and today closes back above it while MA60 is
    not collapsing (flat/up regime). Exit: close back below MA60."""
    ma60 = _ma(close, 60)
    broke = False
    for k in range(1, n_back + 1):
        broke = broke | (close.shift(k) < ma60.shift(k)).fillna(False)
    regime_ok = ma60 >= ma60.shift(20) * 0.99
    entry = (broke & (close > ma60) & regime_ok).fillna(False)
    return _hold(entry, (close < ma60).fillna(False))


def ants_climb(open_: pd.Series, high: pd.Series, low: pd.Series,
               close: pd.Series, max_day: float = 0.012) -> pd.Series:
    """'蚂蚁上树' (folk): 5 of the last 6 sessions are small green
    candles, cumulative gain mild (+3%~+8%) = quiet accumulation.
    Exit: MA5 turns down."""
    green = ((close > open_) & (close.pct_change() < max_day)).fillna(False)
    n_green = green.rolling(6).sum()
    cum = close.pct_change(6)
    entry = (n_green >= 5) & cum.between(0.03, 0.08)
    ma5 = _ma(close, 5)
    return _hold(entry.fillna(False), (ma5 < ma5.shift(2)).fillna(False))


def volume_mound(open_: pd.Series, high: pd.Series, low: pd.Series,
                 close: pd.Series, volume: pd.Series,
                 mound: float = 1.3) -> pd.Series:
    """Volume-mound accumulation (folk): 5-day avg volume >= 1.3x the
    60-day avg while price inches up (+1%~+6% over 10d, no blow-off).
    Exit: close below MA10."""
    v5 = volume.rolling(5).mean()
    v60 = volume.rolling(60, min_periods=60).mean()
    ret10 = close.pct_change(10)
    entry = ((v5 > mound * v60) & ret10.between(0.01, 0.06)).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def second_wave(open_: pd.Series, high: pd.Series, low: pd.Series,
                close: pd.Series, retest: float = 0.05) -> pd.Series:
    """Second-wave confirm (folk '二波'): the 60-day high was printed
    5-20 sessions ago, price has pulled back but stays near the breakout
    zone, and today turns green again. Exit: close below MA10."""
    hh60 = high.rolling(60, min_periods=60).max()
    made_before = ((high == hh60).rolling(20).max() > 0) & (high < hh60)
    near_zone = close >= hh60 * (1 - retest)
    entry = (made_before & near_zone & (close > open_)
             & (close > close.shift(1))).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def gap_up_hold(open_: pd.Series, high: pd.Series, low: pd.Series,
                close: pd.Series, gap_th: float = 0.01) -> pd.Series:
    """Gap-up unfilled (folk '跳空不补是强势'): yesterday gapped up >=1%
    and today's close still above the gap day's open = gap holds.
    Exit: close falls back into the gap (below that open)."""
    o1, c2 = open_.shift(1), close.shift(2)
    gap_up = (o1 > c2 * (1 + gap_th)).shift(1).fillna(False)
    entry = gap_up & (close > o1.shift(1))
    exit_ = close < o1.shift(1)
    return _hold(entry.fillna(False), exit_.fillna(False))


def rsi_low_flat(open_: pd.Series, high: pd.Series, low: pd.Series,
                close: pd.Series, n: int = 14,
                low_th: float = 25) -> pd.Series:
    """RSI low-flat rebound (folk): RSI below 25 while close holds above
    yesterday's low for two sessions = selling exhaustion. Exit: RSI
    recovers above 50 (bounce played out)."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    oversold = rsi < low_th
    stabilizing = (close >= low.shift(1)) & (low >= low.shift(1).shift(1))
    entry = (oversold & stabilizing).fillna(False)
    return _hold(entry, (rsi > 50).fillna(False))
