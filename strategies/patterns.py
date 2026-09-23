"""K-line pattern school (P-4 folk expansion, CEO order O-20260923-2134).

Classic + folk candlestick/MA-structure patterns, all daily-bar causal
constructions; single source of truth for scripts/p4_folk_screen.py
(no dual implementation, F-05). Folk-lore families are marked as such in
the zoo (s12) -- validity is adjudicated by the gate chain, never assumed.

Conventions (repo contract, PLAN s2.1):
- per-symbol Series in -> position Series out (0/1 int, long-only);
- state machines via strategies.ta._hold (entry wins same-day, ffill);
- reversal-class exits: reclaim MA20 (thesis played out, batch-2A pattern
  convention); continuation-class exits: close below MA10;
- signals computed on close of day t; engine executes at t+1 open (T+1).
"""
import numpy as np
import pandas as pd

from strategies.ta import _hold


def _ma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


# ---------------- reversal class (exit: reclaim MA20) ----------------

def morning_star(open_: pd.Series, high: pd.Series, low: pd.Series,
                 close: pd.Series, big_red: float = -0.03,
                 small_body: float = 0.01) -> pd.Series:
    """Morning star (Wikipedia verbatim): large black body -> small body
    -> white body closing well into the black body."""
    c1, o1 = close.shift(2), open_.shift(2)
    c2 = close.shift(1)
    day1_red = (c1 < o1) & (c1 / o1 - 1 < big_red)
    day2_small = (close.shift(1) / c1 - 1).abs() < small_body
    day3_into = (close > (o1 + c1) / 2) & (close > c2)
    entry = (day1_red & day2_small & day3_into).fillna(False)
    ma20 = _ma(close, 20)
    return _hold(entry, (close > ma20).fillna(False))


def three_soldiers(open_: pd.Series, high: pd.Series, low: pd.Series,
                   close: pd.Series, min_body: float = 0.004) -> pd.Series:
    """Three white soldiers: three rising green candles with substantial
    bodies (continuation, exit MA10)."""
    green = (close > open_).fillna(False)
    body = (close - open_) / open_
    bodies = body > min_body
    rising = (close > close.shift(1)) & (close.shift(1) > close.shift(2))
    entry = (green & bodies & green.shift(1) & bodies.shift(1)
             & green.shift(2) & bodies.shift(2) & rising).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def piercing_line(open_: pd.Series, close: pd.Series,
                  big_red: float = -0.02) -> pd.Series:
    """Piercing line (Wikipedia): after a black candle, today opens below
    yesterday's close and closes above the midpoint of yesterday's body."""
    o1, c1 = open_.shift(1), close.shift(1)
    prev_red = (c1 < o1) & (c1 / o1 - 1 < big_red)
    gap_down = open_ < c1
    into = close > (o1 + c1) / 2
    entry = (prev_red & gap_down & into & (close < o1)).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def needle_probe(open_: pd.Series, high: pd.Series, low: pd.Series,
                 close: pd.Series, drop_th: float = -0.05,
                 shadow_pct: float = 0.02) -> pd.Series:
    """Golden-needle probe (folk, hammer cousin -- same-family discount
    pre-registered): long lower shadow in deep water, confirmed by a
    close above the needle day's high next session."""
    body = (close - open_).abs()
    rng = (high - low).replace(0, np.nan)
    shadow = np.minimum(open_, close) - low
    needle = ((shadow >= 2.0 * body) & (shadow >= shadow_pct * close)
              & (high - np.maximum(open_, close) <= body)).shift(1)
    deep = (close.pct_change(5) < drop_th).shift(1)
    entry = (needle & deep & (close > high.shift(1))).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def three_methods_up(open_: pd.Series, high: pd.Series, low: pd.Series,
                     close: pd.Series, big_yang: float = 0.03) -> pd.Series:
    """Rising three methods (classic): big yang, then 3 small pullback
    candles inside its range, then a yang closing above the first close."""
    o1, c1, h1, l1 = open_.shift(5), close.shift(5), high.shift(5), low.shift(5)
    big1 = (c1 > o1) & (c1 / o1 - 1 > big_yang)
    inside = True
    for k in (4, 3, 2):
        ok = ((high.shift(k) <= h1) & (low.shift(k) >= l1)).fillna(False)
        inside = inside & ok
    entry = (big1 & inside & (close > open_) & (close > c1)).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def island_reversal(open_: pd.Series, high: pd.Series, low: pd.Series,
                    close: pd.Series, gap: float = 0.01) -> pd.Series:
    """Island bottom (classic, low frequency disclosed): yesterday gapped
    below the close of two days ago, today gaps above yesterday's high."""
    down_gap = (high.shift(1) < close.shift(2) * (1 - gap))
    up_gap = (low > high.shift(1) * (1 + gap))
    entry = (down_gap & up_gap).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def doji_at_low(open_: pd.Series, high: pd.Series, low: pd.Series,
                close: pd.Series, drop_th: float = -0.05) -> pd.Series:
    """Low doji stall (folk): doji after a >=5% five-day drop."""
    body = (close - open_).abs()
    rng = (high - low).replace(0, np.nan)
    doji = (body <= 0.15 * rng) & (rng > 0.008 * close)
    deep = close.pct_change(5) < drop_th
    entry = (doji & deep & (close.shift(1) < open_.shift(1))).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def big_yin_shakeout(open_: pd.Series, high: pd.Series, low: pd.Series,
                     close: pd.Series, big_yin: float = -0.035) -> pd.Series:
    """Big-yin shakeout done (folk): uptrend, one big red day, next day
    closes back above that day's open = washout completed."""
    ma20 = _ma(close, 20)
    uptrend = (close > ma20).shift(2).fillna(False)
    yin = (close.shift(1) < open_.shift(1)) & \
          (close.shift(1) / open_.shift(1) - 1 < big_yin)
    recover = close > open_.shift(1)
    entry = (uptrend & yin & recover).fillna(False)
    return _hold(entry, (close < ma20).fillna(False))


def macd_divergence(open_: pd.Series, high: pd.Series, low: pd.Series,
                    close: pd.Series, look: int = 30) -> pd.Series:
    """Bullish MACD divergence (folk, daily-bar honest approximation):
    price prints a `look`-day low while DIF sits above its own 60-day
    low + margin = momentum not confirming the new price low."""
    dif = (close.ewm(span=12, adjust=False).mean()
           - close.ewm(span=26, adjust=False).mean())
    price_low = close <= close.rolling(look, min_periods=look).min() * 1.001
    dif_floor = dif.rolling(60, min_periods=60).min()
    entry = (price_low & (dif > dif_floor + 0.002)).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def obv_divergence(open_: pd.Series, high: pd.Series, low: pd.Series,
                   close: pd.Series, volume: pd.Series,
                   look: int = 30) -> pd.Series:
    """OBV accumulation divergence (folk): price at `look`-day low while
    OBV holds above its 60-day mean = quiet accumulation proxy."""
    ret = close.diff().fillna(0)
    obv = (np.sign(ret) * volume).cumsum()
    price_low = close <= close.rolling(look, min_periods=look).min() * 1.001
    entry = (price_low & (obv > obv.rolling(60, min_periods=60).mean())
             ).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


def vol_drought_reversal(open_: pd.Series, high: pd.Series, low: pd.Series,
                         close: pd.Series, volume: pd.Series,
                         vol_floor: float = 0.55,
                         drop_th: float = -0.05) -> pd.Series:
    """Volume-drought reversal (folk '地量出地价'): volume shrinks to a
    deep fraction of its 60-day mean while price is in deep water, first
    green day after."""
    vavg = volume.rolling(60, min_periods=60).mean()
    drought = (volume.shift(1) < vol_floor * vavg.shift(1)).fillna(False)
    deep = (close.pct_change(5) < drop_th).shift(1).fillna(False)
    entry = (drought & deep & (close > open_) & (close > close.shift(1))
             ).fillna(False)
    return _hold(entry, (close > _ma(close, 20)).fillna(False))


# -------------- continuation / structure class (exit: MA10) --------------

def inside_bar_breakup(open_: pd.Series, high: pd.Series, low: pd.Series,
                       close: pd.Series) -> pd.Series:
    """Inside-bar breakout: yesterday fully inside the day before, today
    closes above the mother bar's high."""
    inside = ((high.shift(1) < high.shift(2))
              & (low.shift(1) > low.shift(2))).fillna(False)
    entry = (inside & (close > high.shift(2))).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def yang_break_3ma(open_: pd.Series, high: pd.Series, low: pd.Series,
                   close: pd.Series, spread: float = 0.015) -> pd.Series:
    """One-yang-through-3-MAs (folk): MA5/10/20 converged (spread within
    1.5% of close) and a single green close above all three."""
    ma5, ma10, ma20 = _ma(close, 5), _ma(close, 10), _ma(close, 20)
    converge = ((ma5.rolling(3).max() - ma20.rolling(3).min())
                <= spread * close)
    entry = (converge & (close > open_) & (close > ma5)
             & (close > ma10) & (close > ma20)).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def ma_converge_break(open_: pd.Series, high: pd.Series, low: pd.Series,
                      close: pd.Series, spread: float = 0.015) -> pd.Series:
    """MA-convergence state (folk, #57 same-family state variant -- discount
    pre-registered): after MA5/10/20 convergence, hold the bullish stack
    MA5>MA10>MA20 above close>MA20; exit when the stack breaks."""
    ma5, ma10, ma20 = _ma(close, 5), _ma(close, 10), _ma(close, 20)
    converge = ((ma5.rolling(3).max() - ma20.rolling(3).min())
                <= spread * close).shift(1).fillna(False)
    stack = (ma5 > ma10) & (ma10 > ma20) & (close > ma20)
    entry = converge & stack
    exit_ = (ma5 <= ma10) | (close < ma20)
    return _hold(entry.fillna(False), exit_.fillna(False))


def duck_head(open_: pd.Series, high: pd.Series, low: pd.Series,
              close: pd.Series, neck: int = 8) -> pd.Series:
    """Old-duck head (folk classic): MA5 dips below MA10 for a short while
    (the head) while MA10 keeps rising and price stays above MA60, then
    MA5 crosses back above MA10 = the beak. Exit on MA5 falling back."""
    ma5, ma10, ma60 = _ma(close, 5), _ma(close, 10), _ma(close, 60)
    below_recent = ((ma5 < ma10).rolling(neck).max() > 0).shift(1)
    was_above = (ma5 > ma10).shift(neck + 1).fillna(False)
    cross_up = (ma5 > ma10) & (ma5.shift(1) <= ma10.shift(1))
    ma10_rising = ma10 > ma10.shift(5)
    entry = (below_recent & was_above & cross_up & ma10_rising
             & (close > ma60)).fillna(False)
    return _hold(entry, (ma5 < ma10).fillna(False))


def box_breakout(open_: pd.Series, high: pd.Series, low: pd.Series,
                 close: pd.Series, volume: pd.Series, box_th: float = 0.08,
                 vol_mult: float = 1.3, box_n: int = 20) -> pd.Series:
    """Box breakout (folk, vol_breakout near-family -- discount pre-
    registered): N-day box range within 8% of price, close breaks the
    prior box top with volume confirm; exit below prior box bottom."""
    box_hi = high.rolling(box_n).max().shift(1)
    box_lo = low.rolling(box_n).min().shift(1)
    tight = (box_hi / box_lo - 1 <= box_th)
    entry = (tight & (close > box_hi)
             & (volume > vol_mult * volume.rolling(20, min_periods=20)
                .mean())).fillna(False)
    return _hold(entry, (close < box_lo).fillna(False))


def immortal_guide(open_: pd.Series, high: pd.Series, low: pd.Series,
                   close: pd.Series, shadow_pct: float = 0.015) -> pd.Series:
    """Immortal points the way (folk): long upper shadow probing upward,
                   then within 3 sessions close reclaims that probe high."""
    body = (close - open_).abs()
    upper = high - np.maximum(open_, close)
    probe = (upper >= 2.0 * body) & (upper >= shadow_pct * close)
    recent_probe = (probe.shift(1) | probe.shift(2) | probe.shift(3))
    probe_hi = pd.concat([high.shift(1), high.shift(2), high.shift(3)],
                         axis=1).max(axis=1)
    entry = (recent_probe & probe_hi.notna() & (close > probe_hi)
             ).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))


def n_shape(open_: pd.Series, high: pd.Series, low: pd.Series,
            close: pd.Series, leg_up: float = 0.04) -> pd.Series:
    """N-shape re-break (folk): up leg, short pullback, then close above
    the prior leg-top close."""
    leg = close.pct_change(5).shift(5) > leg_up
    pull = (close.rolling(3).min() / close.rolling(5).max().shift(2) - 1
            ).between(-0.08, -0.01)
    top = close.rolling(10).max().shift(1)
    entry = (leg & pull & (close > top)).fillna(False)
    return _hold(entry, (close < _ma(close, 10)).fillna(False))
