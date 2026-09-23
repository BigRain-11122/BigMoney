"""Crypto panel builder - same .npy format as the A-share cache, so the
WHOLE engine (31 families, GA, league, backtest) runs on crypto unchanged.

Market profile (markets.py "crypto"): 7x24 continuous calendar, NO price
limits (ban/bust always False), amount = USDT notional. Config's
MONEY_CACHE_DIR env switch points load_cache/window at this dir.

Universe: the backfilled Gate.io pairs minus pegged stables (USDC/FDUSD).
Panel fields: the full PER_STOCK_T set computed via indicators.py so every
family (incl. the sleeping TA-Lib ones) wakes with real crypto data.
Standalone: python crypto_cache.py   (after crypto_backfill.py)
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, r"E:\Money")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import config as C
import data as D
import indicators as ind

BARS = Path(r"E:\Money\data\mkt_crypto\bars")
CACHE = Path(r"E:\Money\data\mkt_crypto\cache")
CACHE.mkdir(parents=True, exist_ok=True)
DROP = {"USDC_USDT", "FDUSD_USDT"}  # pegged stables: no tradable edge
MIN_DAYS = 120


def main():
    files = sorted(BARS.glob("*.parquet"))
    frames = {}
    for f in files:
        if f.stem in DROP:
            continue
        df = pd.read_parquet(f)
        if len(df) < MIN_DAYS:
            continue
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])  # string -> DatetimeIndex
        frames[f.stem] = df.set_index("date")
    if not frames:
        print("no bars - run crypto_backfill.py first")
        return
    codes = list(frames.keys())
    print(f"universe: {len(codes)} pairs")

    # continuous 7x24 calendar: union of all dates (BTC covers most);
    # drop the last UTC day if it has not closed yet (partial candle hygiene
    # - same principle as the A-share tick never touching intraday bars)
    all_dates = sorted(set().union(*[set(df.index) for df in frames.values()]))
    today_utc = pd.Timestamp.utcnow().floor("D")
    all_dates = [d for d in all_dates if d < today_utc]
    if not all_dates:
        print("no completed days")
        return
    cal = pd.DatetimeIndex(all_dates)
    T = len(cal)
    N = len(codes)
    print(f"calendar: {T} days {str(cal[0].date())}~{str(cal[-1].date())}")

    def stack(col, cast_float=True):
        m = np.full((T, N), np.nan)
        for j, c in enumerate(codes):
            s = frames[c][col].reindex(cal)
            m[:, j] = s.values
        return m

    open_ = pd.DataFrame(stack("open"), index=cal, columns=codes)
    close = pd.DataFrame(stack("close"), index=cal, columns=codes)
    high = pd.DataFrame(stack("high"), index=cal, columns=codes)
    low = pd.DataFrame(stack("low"), index=cal, columns=codes)
    volume = pd.DataFrame(stack("volume"), index=cal, columns=codes)
    amount = pd.DataFrame(stack("amount"), index=cal, columns=codes)

    preclose = close.shift(1)
    pc = close / preclose - 1.0
    gap = (open_ / preclose - 1.0) * 100.0
    ma10, ma20, ma60 = (ind.sma(close, n) for n in (10, 20, 60))
    vol_ratio5 = volume / volume.rolling(5, min_periods=5).mean()
    rsi14 = ind.rsi(close, 14)
    rh20, rh60, rh250 = (ind.rmax(close, n) for n in (20, 60, 250))
    mom20, mom60 = ind.pct_change(close, 20), ind.pct_change(close, 60)
    mom50, mom120 = ind.pct_change(close, 50), ind.pct_change(close, 120)
    rng_pos = (close - low) / (high - low + 1e-6)
    ma20_slope = ma20 / ma20.shift(5) - 1.0
    dd60 = close / rh60 - 1.0
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_dif = ema12 - ema26
    macd_dea = macd_dif.ewm(span=9, adjust=False).mean()
    maxret20 = pc.rolling(20, min_periods=20).max()
    mom_accel = mom20 - mom50
    intraday_ret = close / open_ - 1.0

    # TA-Lib per-column indicators
    atr14 = cci14 = wr10 = mfi14 = adx14 = sk = sd_ = None
    try:
        import talib
        H = np.ascontiguousarray(high.values, dtype=np.float64)
        L = np.ascontiguousarray(low.values, dtype=np.float64)
        Cv = np.ascontiguousarray(close.values, dtype=np.float64)
        Vv = np.ascontiguousarray(volume.values, dtype=np.float64)
        a = np.full((T, N), np.nan); cc = np.full((T, N), np.nan)
        w = np.full((T, N), np.nan); mf = np.full((T, N), np.nan)
        ax = np.full((T, N), np.nan); k1 = np.full((T, N), np.nan)
        d1 = np.full((T, N), np.nan)
        for i in range(N):
            h, l, c, v = H[:, i], L[:, i], Cv[:, i], Vv[:, i]
            if not np.isfinite(c).any():
                continue
            a[:, i] = talib.ATR(h, l, c, timeperiod=14)
            cc[:, i] = talib.CCI(h, l, c, timeperiod=14)
            w[:, i] = talib.WILLR(h, l, c, timeperiod=10)
            mf[:, i] = talib.MFI(h, l, c, v, timeperiod=14)
            ax[:, i] = talib.ADX(h, l, c, timeperiod=14)
            kk, dd2 = talib.STOCH(h, l, c, fastk_period=9, slowk_period=3,
                                  slowk_matype=0, slowd_period=3)
            k1[:, i] = kk; d1[:, i] = dd2
        atr14 = pd.DataFrame(a, index=cal, columns=codes)
        cci14 = pd.DataFrame(cc, index=cal, columns=codes)
        wr10 = pd.DataFrame(w, index=cal, columns=codes)
        mfi14 = pd.DataFrame(mf, index=cal, columns=codes)
        adx14 = pd.DataFrame(ax, index=cal, columns=codes)
        sk = pd.DataFrame(k1, index=cal, columns=codes)
        sd_ = pd.DataFrame(d1, index=cal, columns=codes)
    except Exception as e:  # noqa: BLE001
        print("talib block failed:", e)

    def daily_rank(mat):
        r = np.full((T, N), np.nan, dtype=np.float32)
        for t in range(T):
            row = mat[t]
            m = np.isfinite(row)
            if m.sum() < 3:
                continue
            idx = np.argsort(row[m], kind="stable")
            r[t, m] = (np.argsort(idx) / max(m.sum() - 1, 1)).astype(np.float32)
        return pd.DataFrame(r, index=cal, columns=codes)

    amt_rank = daily_rank(amount.values.astype(np.float64))
    rps50 = daily_rank(mom50.values.astype(np.float64))
    rps120 = daily_rank(mom120.values.astype(np.float64))

    first_valid = np.argmax(np.isfinite(close.values), axis=0)
    day_idx = (np.arange(T)[:, None] - first_valid[None, :]).astype(np.int32)
    has = np.isfinite(close.values).any(axis=0)
    day_idx[:, ~has] = -10 ** 6
    tradable = ((day_idx >= MIN_DAYS) & np.isfinite(close.values)
                & (close.values > 1e-12)
                & (amount.values >= 1e5))  # >=10万USDT日成交额

    above = (close.values > ma20.values) & np.isfinite(ma20.values)
    listed = np.isfinite(close.values) & (day_idx >= MIN_DAYS)
    breadth = np.where(listed.sum(1) > 0,
                       (above & listed).sum(1) / np.maximum(listed.sum(1), 1),
                       0.0).astype(np.float32)

    def f32(x):
        a = x.values if hasattr(x, "values") else x
        return a.astype(np.float32)

    np.save(CACHE / "codes.npy", np.asarray(codes, dtype="<U16"))
    np.save(CACHE / "names.npy", np.asarray(codes, dtype="<U16"))
    np.save(CACHE / "dates.npy", cal.values.astype("datetime64[D]"))
    np.save(CACHE / "lim_pct.npy", np.zeros(N, dtype=np.float32))
    np.save(CACHE / "day_idx.npy", day_idx)
    np.save(CACHE / "breadth.npy", breadth)
    for nm, arr in {
        "open": open_, "close": close, "pct_chg": pc, "amount": amount,
        "gap": gap, "ma10": ma10, "ma20": ma20, "ma60": ma60,
        "vol_ratio5": vol_ratio5, "rsi14": rsi14, "roll_high20": rh20,
        "roll_high60": rh60, "mom20": mom20, "mom60": mom60,
        "rng_pos": rng_pos, "ma20_slope": ma20_slope, "dd60": dd60,
        "amt_rank": amt_rank, "mom50": mom50, "rps50": rps50,
        "rps120": rps120, "rh250": rh250, "macd_dif": macd_dif,
        "macd_dea": macd_dea, "maxret20": maxret20, "mom_accel": mom_accel,
        "intraday_ret": intraday_ret,
        "mktcap_rank": pd.DataFrame(np.nan, index=cal, columns=codes),
        **({"atr14": atr14, "cci14": cci14, "wr10": wr10, "mfi14": mfi14,
            "adx14": adx14, "stoch_k": sk, "stoch_d": sd_}
           if atr14 is not None else {}),
    }.items():
        np.save(CACHE / f"{nm}.npy", f32(arr))
    for nm in ("limit_up", "open_ban", "open_bust"):  # no price limits: all 0
        np.save(CACHE / f"{nm}.npy",
                np.zeros((T, N), dtype=bool))
    np.save(CACHE / "tradable.npy", tradable)
    # benchmarks: BTC as the market proxy in all three bench slots
    btc = np.asarray(frames.get("BTC_USDT", list(frames.values())[0])
                     ["close"].reindex(cal)).astype(np.float32)
    for b in ("hs300", "csi500", "sse"):
        np.save(CACHE / f"bench_{b}.npy", btc)
    lhb = np.full((T, N), np.nan, dtype=np.float32)
    np.save(CACHE / "lhb_net.npy", lhb)  # no LHB in crypto: family sleeps
    print(f"crypto panel: T={T} N={N} -> {CACHE}")


if __name__ == "__main__":
    main()
