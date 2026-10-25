"""ETF composite factor portfolio -- does the IC edge survive construction and costs?

Signal at close of day t; the book is set at that close and earns close-to-close
returns from t (no lookahead). NOTE: the open panel is loaded but NOT used -- there is
no open-fill model yet, so entry slippage is not represented; only turnover is charged.
Universe: ETFs with >=120 bars of history and 20d median (close*volume) >= 20M CNY.
Composite: cross-sectional rank-score of six factors, signs as in SIGNS.
Hold top-N equal weight, rebalance every R bars. Cost = 8bp per side on turnover.
--null=N adds a per-date permutation null (factor->return link destroyed) and writes
the real-vs-shuffled Sharpe p-value into the results JSON.

Outputs results/etf_composite_pf.json and a printed table (full / 2020-2023 / 2024+).
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from tasks.backtest_task import _load_prices
from engine.factors import compute_all
from config import PATHS

SIGNS = {
    "mom_12_1": +1.0,
    "price_position": +1.0,
    "drawdown_60": +1.0,
    "adx_14": +1.0,
    "vol_60": -1.0,
    "intraday_range": -1.0,
}
COST = 0.0008           # per side
MIN_AMT = 20e6          # 20d median close*volume
MIN_HIST = 120
N_HOLD = 5
REBAL = (5, 20)


def build_panel():
    prices = _load_prices()
    bench = None
    bp = os.path.join(PATHS.basic_dir, "csi300.csv")
    if os.path.exists(bp):
        bench = pd.read_csv(bp, parse_dates=["date"]).set_index("date")["close"]
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    close = close.replace(0.0, np.nan)
    feats = compute_all(prices, bench)
    amt = (close * vol).rolling(20, min_periods=10).median()
    return close, openp, amt, feats


def zscore(df):
    r = df.rank(axis=1, pct=True)
    return (r - 0.5) * 2.0


def composite(feats, cols):
    parts = []
    for c in cols:
        f = feats.get(c)
        if f is None:
            continue
        parts.append(SIGNS[c] * zscore(f.reindex(columns=cols and f.columns)))
    if not parts:
        return None
    return sum(parts) / len(parts)


def build_score(close, amt, feats):
    idx = close.index
    hist = close.notna().cumsum()
    elig = (amt >= MIN_AMT) & (hist >= MIN_HIST)
    cols = close.columns
    parts = []
    for c, sgn in SIGNS.items():
        f = feats.get(c)
        if f is None:
            continue
        f = f.reindex(index=idx, columns=cols)
        parts.append(sgn * ((f.rank(axis=1, pct=True) - 0.5) * 2.0))
    score = sum(parts) / len(parts)
    score = score.where(elig)
    score.index = pd.to_datetime(score.index)
    return score


def run(close, openp, amt, feats, rebal, n_hold=N_HOLD, cost=COST, start="2020-01-01"):
    idx = close.index
    score = build_score(close, amt, feats)
    cols = close.columns

    px = close.reindex(columns=cols).ffill()
    op = openp.reindex(columns=cols)
    ret = px.pct_change()

    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    rebal_days = set(dates[::rebal])

    equity = 1.0
    curve = []
    held = {}
    turnover_sum = 0.0
    n_rebal = 0
    for i, d in enumerate(dates[:-1]):
        if d in rebal_days:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                new = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(new.get(k, 0.0) - held.get(k, 0.0)) for k in set(new) | set(held))
                equity *= (1.0 - cost * turn)
                turnover_sum += turn
                n_rebal += 1
                held = new
        if held and i + 1 < len(dates):
            nd = dates[i + 1]
            r = 0.0
            for p, w in held.items():
                rp = ret.at[nd, p] if p in ret.columns else np.nan
                if np.isfinite(rp):
                    r += w * rp
            equity *= (1.0 + r)
        curve.append((d, equity))

    ser = pd.Series(dict(curve))
    return ser, (turnover_sum / n_rebal if n_rebal else 0.0)


def metrics(ser, label):
    ser = ser.dropna()
    if len(ser) < 30:
        return {"label": label, "bars": len(ser), "note": "too short"}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    cagr = ser.iloc[-1] ** (1 / yrs) - 1
    rets = ser.pct_change().dropna()
    vol = rets.std() * np.sqrt(252)
    sharpe = (rets.mean() * 252) / vol if vol > 0 else 0.0
    dd = (ser / ser.cummax() - 1).min()
    return {
        "label": label,
        "bars": len(ser),
        "years": round(yrs, 2),
        "total_ret": round(ser.iloc[-1] - 1, 4),
        "cagr": round(cagr, 4),
        "vol": round(vol, 4),
        "sharpe": round(sharpe, 3),
        "maxdd": round(dd, 4),
    }


def run_ew(close, amt, rebal, start="2020-01-01"):
    """Control: equal weight across the whole eligible universe, same rebalance cadence."""
    idx = close.index
    hist = close.notna().cumsum()
    elig = (amt >= MIN_AMT) & (hist >= MIN_HIST)
    px = close.ffill()
    ret = px.pct_change()
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    rebal_days = set(dates[::rebal])
    equity, held, curve = 1.0, [], []
    for i, d in enumerate(dates[:-1]):
        if d in rebal_days:
            cands = elig.loc[d][elig.loc[d]].index.tolist()
            held = cands
        if held and i + 1 < len(dates):
            nd = dates[i + 1]
            r = ret.loc[nd, held].mean() if len(held) else 0.0
            if np.isfinite(r):
                equity *= (1.0 + r)
        curve.append((d, equity))
    return pd.Series(dict(curve))


def today_picks(score, close, n_hold=N_HOLD):
    last = score.index[-1]
    s = score.loc[last].dropna()
    return last.strftime("%Y-%m-%d"), list(s.nlargest(n_hold).items())


def null_test(close, openp, amt, feats, rebal, n_iter=200, seed=7):
    """Permutation null, vectorised over rebalance periods.

    Each iteration shuffles every factor's cross-section date by date (killing the
    factor->return link, keeping the per-date rank distribution), rebuilds the
    composite, re-picks top-N and recomputes the period-by-period portfolio.
    """
    rng = np.random.default_rng(seed)
    idx = close.index
    hist = close.notna().cumsum()
    elig = ((amt >= MIN_AMT) & (hist >= MIN_HIST)).to_numpy()
    cols = close.columns
    px = close.reindex(columns=cols).ffill()
    R = px.pct_change().fillna(0.0).to_numpy()
    dates = [d for d in px.index if d >= pd.Timestamp("2020-01-01")]
    dpos = {d: i for i, d in enumerate(px.index)}
    ib = [dpos[d] for d in dates[::rebal]] + [dpos[dates[-1]]]

    growth = np.cumprod(1.0 + R, axis=0)
    period_ret = np.zeros((len(ib) - 1, len(cols)))
    for p in range(len(ib) - 1):
        a, b = ib[p] + 1, ib[p + 1] + 1
        period_ret[p] = growth[b - 1] / growth[a - 1] - 1.0

    base = []
    for c in SIGNS:
        f = feats.get(c)
        if f is not None:
            base.append((c, f.reindex(index=idx, columns=cols).rank(axis=1, pct=True).to_numpy()))

    def period_sharpe(score):
        pr = []
        prev = set()
        for p in range(len(ib) - 1):
            row = score[ib[p]]
            mask = elig[ib[p]] & np.isfinite(row)
            if mask.sum() < N_HOLD:
                pr.append(0.0)
                continue
            vals = np.where(mask, row, -np.inf)
            top = np.argpartition(-vals, N_HOLD - 1)[:N_HOLD]
            r = period_ret[p][top].mean()
            cur = set(top.tolist())
            turn = len(cur ^ prev) / N_HOLD
            prev = cur
            pr.append(r - COST * turn)
        pr = np.array(pr)
        sd = pr.std()
        per_year = 252.0 / rebal
        return (pr.mean() * per_year) / (sd * np.sqrt(per_year)) if sd > 0 else 0.0

    real_score = sum(s * z for c, arr in base for s in [SIGNS[c]] for z in [arr])
    real_score = real_score / len(base)
    real_sr = period_sharpe(np.where(elig, real_score, np.nan))

    sharpes = []
    for _ in range(n_iter):
        parts = []
        for c, arr in base:
            a = arr.copy()
            for i in range(a.shape[0]):
                rng.shuffle(a[i])
            parts.append(SIGNS[c] * a)
        sc = sum(parts) / len(parts)
        sharpes.append(period_sharpe(np.where(elig, sc, np.nan)))
    return real_sr, np.array(sharpes)


def bench_series(close, start):
    for sym in ("510300", "sh510300"):
        if sym in close.columns:
            s = close[sym].dropna()
            s = s[s.index >= pd.Timestamp(start)]
            return s / s.iloc[0]
    return None


def main():
    close, openp, amt, feats = build_panel()
    out = {"universe": int(close.shape[1]), "cost_per_side": COST,
           "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
           "min_amt_cny": MIN_AMT, "n_hold": N_HOLD, "factors": {k: v for k, v in SIGNS.items()},
           "runs": []}
    for rebal in REBAL:
        ser, turn = run(close, openp, amt, feats, rebal)
        for lbl, sl in (("full", ser), ("is_2020_2023", ser[ser.index <= "2023-12-31"]),
                        ("oos_2024_plus", ser[ser.index >= "2024-01-01"])):
            m = metrics(sl, "rebal%d_%s" % (rebal, lbl))
            m["turnover_per_rebal"] = round(turn, 3)
            out["runs"].append(m)
            print(m)

    bs = bench_series(close, "2020-01-01")
    if bs is not None:
        for lbl, sl in (("full", bs), ("is_2020_2023", bs[bs.index <= "2023-12-31"]),
                        ("oos_2024_plus", bs[bs.index >= "2024-01-01"])):
            m = metrics(sl, "bench510300_%s" % lbl)
            out["runs"].append(m)
            print(m)

    for rebal in REBAL:
        ew = run_ew(close, amt, rebal)
        for lbl, sl in (("full", ew), ("is_2020_2023", ew[ew.index <= "2023-12-31"]),
                        ("oos_2024_plus", ew[ew.index >= "2024-01-01"])):
            m = metrics(sl, "ew_universe_rebal%d_%s" % (rebal, lbl))
            out["runs"].append(m)
            print(m)

    score = build_score(close, amt, feats)
    d, picks = today_picks(score, close)
    out["live_picks"] = {"as_of": d,
                         "picks": [{"symbol": s, "score": round(float(v), 3)} for s, v in picks]}
    print("live picks as of", d, [(s, round(float(v), 3)) for s, v in picks])

    ser20, _ = run(close, openp, amt, feats, 20)
    yr = ser20.groupby(ser20.index.year).apply(lambda s: round(s.iloc[-1] / s.iloc[0] - 1, 4))
    out["yearly_ret_rebal20"] = {int(k): float(v) for k, v in yr.items()}
    print("yearly (rebal20):", dict(yr))

    if any(a.startswith("--null") for a in sys.argv):
        n_iter = 200
        for a in sys.argv:
            if a.startswith("--null="):
                n_iter = int(a.split("=")[1])
        print("null test: %d shuffles ..." % n_iter)
        real, ns = null_test(close, openp, amt, feats, 20, n_iter=n_iter)
        p = float((ns >= real).mean())
        out["null_test"] = {"iter": n_iter, "mean": round(float(ns.mean()), 3),
                            "p95": round(float(np.percentile(ns, 95)), 3),
                            "max": round(float(ns.max()), 3),
                            "real_sharpe": real, "p_value": round(p, 4)}
        print(out["null_test"])

    p = os.path.join(PATHS.results_dir, "etf_composite_pf.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()