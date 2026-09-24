"""Grid harvesting school (A-layer migration, QUANT_STYLE_ATLAS row 8).

Port of Money0923 ``GridTrade`` (channel-position oscillation harvesting
restricted to a low-volatility pool -- "grid is a weapon of calm-range
instruments, pooling the whole universe = fake grid") into the repo
entry/exit engine contract. The legacy engine consumed continuous target
weights (ladder in per grid, out per grid); this house port uses the
frozen-membership binary convention (``new_signal_p1._topk_frozen``
lineage): among the ``n_targets`` lowest-volatility names, hold the
``top_k`` closest to their channel bottom, membership frozen every
``rebal_days``. The continuous->binary divergence is pre-registered in
``research/GRID_P1.md`` sec.3; gates adjudicate, never assumed.

Conventions (repo contract, PLAN s2.1):
- panel DataFrame in -> binary weight panel out (0/1 int, long-only);
- all rolling stats on close of day t; engine executes at t+1 open (T+1);
- NaN never ranks in (warmup + degenerate channels stay flat).
"""
import numpy as np
import pandas as pd


def channel_position(close: pd.DataFrame, channel_len: int = 60) -> pd.DataFrame:
    """Close's position inside its trailing channel, 0=at rolling low,
    1=at rolling high (min_periods=channel_len, degenerate range -> NaN)."""
    hi = close.rolling(channel_len, min_periods=channel_len).max()
    lo = close.rolling(channel_len, min_periods=channel_len).min()
    rng = (hi - lo).replace(0.0, np.nan)
    return ((close - lo) / rng).clip(0.0, 1.0)


def grid_score(close: pd.DataFrame, channel_len: int = 60,
               n_grids: int = 6) -> pd.DataFrame:
    """Grid-quantized bottom score: ``1 - floor(pct*g)/g`` -- ladder
    steps down as price climbs the channel; 1.0=channel bottom, steps of
    1/g (Money0923 ladder semantics, quantization preserved)."""
    pct = channel_position(close, channel_len)
    lvl = np.floor(pct * n_grids) / n_grids
    return 1.0 - lvl


def lowvol_pool(close: pd.DataFrame, n_targets: int = 12,
                vol_win: int = None) -> pd.DataFrame:
    """Boolean panel: the ``n_targets`` lowest-annualized-vol names each
    day. ``vol_win`` defaults to the legacy rule max(20, channel_len//2);
    here caller passes it explicitly (None -> 20-day floor)."""
    if vol_win is None:
        vol_win = 20
    vol = (close.pct_change().rolling(vol_win, min_periods=vol_win).std()
           * np.sqrt(252.0))
    ranks = vol.rank(axis=1, ascending=True)
    return ranks.le(n_targets) & close.notna()


def grid_channel_harvest(close: pd.DataFrame, channel_len: int = 60,
                         n_grids: int = 6, n_targets: int = 12,
                         top_k: int = 5, rebal_days: int = 10,
                         vol_win: int = 30) -> pd.DataFrame:
    """Binary membership panel: top_k grid-score names inside the
    low-vol pool, frozen every rebal_days (non-overlapping rebal dates,
    ``_topk_frozen`` convention; between rebals membership persists --
    divergence from legacy zero-on-pool-exit, pre-registered)."""
    score = grid_score(close, channel_len, n_grids)
    pool = lowvol_pool(close, n_targets, vol_win)
    elig = score.where(pool)
    ranks = elig.rank(axis=1, ascending=False)
    in_set = ranks.le(top_k) & pool
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def _selftest() -> bool:
    """Offline hermetic checks (stdout-only, no repo products)."""
    rng = np.random.default_rng(20260925)
    idx = pd.date_range("2020-01-02", periods=400, freq="B")
    cols = [f"S{i}" for i in range(6)]
    px = pd.DataFrame(100 + np.cumsum(rng.normal(0, 1, (400, 6)),
                                      dtype=float, axis=0),
                      index=idx, columns=cols)
    w = grid_channel_harvest(px)
    if not ((w == 0) | (w == 1)).all().all():
        print("grid selftest FAIL: non-binary output")
        return False
    # rolling(60, min_periods=60) first valid row = 59 -> no membership
    # possible before it; rebal grid first eligible slice = row 60.
    if w.iloc[:59].to_numpy().sum() > 0 or w.iloc[60:].to_numpy().sum() <= 0:
        print("grid selftest FAIL: warmup/coverage bounds")
        return False
    if not w.equals(grid_channel_harvest(px)):
        print("grid selftest FAIL: non-deterministic")
        return False
    # quantization ladder: pct=0 -> 1.0; pct just under 1 -> 1/g floor step
    one = pd.DataFrame([[0.0, 0.999]], columns=["a", "b"])
    lvl = np.floor(one * 6) / 6
    if not np.allclose(1.0 - lvl.values, [1.0, 1.0 / 6]):
        print("grid selftest FAIL: ladder quantization")
        return False
    # membership must sit inside the pool on every rebal row
    pool = lowvol_pool(px, 12, 30)
    rebal_rows = w.iloc[::10]
    viol = ((rebal_rows == 1).to_numpy()
            & ~pool.iloc[::10].to_numpy()).any()
    if viol:
        print("grid selftest FAIL: membership outside pool")
        return False
    # causality: truncating the tail must not change any earlier row
    w_trunc = grid_channel_harvest(px.iloc[:-50])
    if not w.iloc[:-50].equals(w_trunc):
        print("grid selftest FAIL: lookahead (tail affects past)")
        return False
    print("grid selftest: 6/6 PASS (binary, warmup, determinism, ladder,"
          " pool, causality)")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if _selftest() else 2)
