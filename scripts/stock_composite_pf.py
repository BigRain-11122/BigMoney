"""A-share composite factor portfolio -- same construction as the ETF version.

Data: bigmoney/Money0923/data/daily/*.csv (stocks only, ETF codes excluded).
Factor signs are derived on the in-sample window (2020-2023) from raw IC, then the
portfolio is evaluated on the held-out window (2024+) without re-fitting.

Costs for stocks are higher than ETFs: commission ~2.5bp + stamp duty 5bp on sell
+ slippage => 20bp per side is applied on turnover.
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from engine.factors import compute_all
from config import PATHS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Money0923", "data", "daily")
ETF_PREFIX = ("159", "510", "511", "512", "513", "515", "518", "563", "588", "501", "502")
COST = 0.0020          # per side, stocks
MIN_AMT = 50e6         # 20d median turnover, CNY
MIN_HIST = 250
N_HOLD = 20
REBAL = (10, 20)
IS_END = "2023-12-31"
START = "2020-01-01"


def load_universe():
    prices = {}
    for p in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv"))):
        sym = os.path.splitext(os.path.basename(p))[0]
        if sym[:3] in ETF_PREFIX:
            continue
        try:
            df = pd.read_csv(p, parse_dates=["date"])
        except Exception:
            continue
        need = {"date", "open", "high", "low", "close", "volume"}
        if not need.issubset(df.columns):
            continue
        df = df.drop_duplicates("date").set_index("date").sort_index()
        df = df[~df.index.duplicated()]
        if len(df) < 300:
            continue
        prices[sym] = df[["open", "high", "low", "close", "volume"]]
    return prices


def ic_table(factors, close, horizon, lo, hi):
    fwd = close.shift(-horizon) / close - 1
    fwd = fwd.loc[(fwd.index >= lo) & (fwd.index <= hi)]
    out = {}
    for name, fac in factors.items():
        f = fac.reindex(fwd.index)
        vals = []
        for dt in f.index:
            a = f.loc[dt].dropna()
            b = fwd.loc[dt].dropna()
            idx = a.index.intersection(b.index)
            if len(idx) < 20:
                continue
            ic = a[idx].corr(b[idx], method="spearman")
            if np.isfinite(ic):
                vals.append(ic)
        if len(vals) < 100:
            continue
        s = pd.Series(vals)
        out[name] = {"ic": round(float(s.mean()), 4),
                     "ir": round(float(s.mean() / s.std()), 3) if s.std() > 0 else 0.0,
                     "n": len(s)}
    return out


def build_score(close, feats, signs, cols):
    parts = []
    for c, sgn in signs.items():
        f = feats.get(c)
        if f is None:
            continue
        f = f.reindex(index=close.index, columns=cols)
        parts.append(sgn * ((f.rank(axis=1, pct=True) - 0.5) * 2.0))
    return sum(parts) / len(parts)


def run_portfolio(close, openp, amt, score, rebal, start=START, n_hold=N_HOLD):
    hist = close.notna().cumsum()
    elig = (amt >= MIN_AMT) & (hist >= MIN_HIST)
    score = score.where(elig)
    px = close.ffill()
    ret = px.pct_change()
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    rebal_days = set(dates[::rebal])
    equity, held, curve, turns, nreb = 1.0, {}, [], 0.0, 0
    for i, d in enumerate(dates[:-1]):
        if d in rebal_days:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                new = {p: 1.0 / n_hold for p in s.nlargest(n_hold).index}
                turn = sum(abs(new.get(k, 0.0) - held.get(k, 0.0)) for k in set(new) | set(held))
                equity *= (1.0 - COST * turn)
                turns += turn
                nreb += 1
                held = new
        if held:
            nd = dates[i + 1]
            r = 0.0
            for p, w in held.items():
                rp = ret.at[nd, p] if p in ret.columns else np.nan
                if np.isfinite(rp):
                    r += w * rp
            equity *= (1.0 + r)
        curve.append((d, equity))
    return pd.Series(dict(curve)), (turns / nreb if nreb else 0.0)


def metrics(ser, label):
    ser = ser.dropna()
    if len(ser) < 30:
        return {"label": label, "note": "too short"}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    r = ser.pct_change().dropna()
    vol = r.std() * np.sqrt(252)
    # Running levels: a slice starts at the level the book had already reached,
    # so growth must be renormalised to the slice's own first level (not 1.0).
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    return {"label": label, "bars": len(ser), "years": round(yrs, 2),
            "start_level": round(float(ser.iloc[0]), 4),
            "total": round(growth - 1, 4),
            "cagr": round(float(growth ** (1 / yrs) - 1), 4),
            "vol": round(float(vol), 4),
            "sharpe": round(float(r.mean() * 252 / vol), 3) if vol > 0 else 0.0,
            "maxdd": round(float((ser / ser.cummax() - 1).min()), 4)}


def main():
    prices = load_universe()
    print("stocks:", len(prices))
    bench = None
    bp = os.path.join(PATHS.basic_dir, "csi300.csv")
    if os.path.exists(bp):
        bench = pd.read_csv(bp, parse_dates=["date"]).set_index("date")["close"]
    feats = compute_all(prices, bench)
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index().replace(0.0, np.nan)
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    amt = (close * vol).rolling(20, min_periods=10).median()
    print("panel:", close.shape, close.index.min().date(), close.index.max().date())

    is_ic = ic_table(feats, close, 20, START, IS_END)
    print("\n=== in-sample IC (2020-2023, h20), |ic| desc ===")
    for k, v in sorted(is_ic.items(), key=lambda kv: -abs(kv[1]["ic"]))[:14]:
        print("  %-22s ic=%+.4f ir=%+.3f n=%d" % (k, v["ic"], v["ir"], v["n"]))

    signs = {k: (1.0 if v["ic"] >= 0 else -1.0) for k, v in is_ic.items()}
    cols = close.columns
    score = build_score(close, feats, signs, cols)

    out = {"universe": len(prices), "cost_per_side": COST, "min_amt": MIN_AMT,
           "n_hold": N_HOLD, "signs": signs, "is_ic": is_ic, "runs": [],
           "evidence_cutoff": str(close.index[-1].date()),
           "metric_basis": "equity-curve slices renormalised to each slice own first level"}
    for rebal in REBAL:
        ser, turn = run_portfolio(close, openp, amt, score, rebal)
        for lbl, sl in (("full", ser), ("is_2020_2023", ser[ser.index <= IS_END]),
                        ("oos_2024_plus", ser[ser.index > IS_END])):
            m = metrics(sl, "rebal%d_%s" % (rebal, lbl))
            m["turnover_per_rebal"] = round(turn, 3)
            out["runs"].append(m)
            print(m)

    # controls: equal-weight universe and CSI300
    hist = close.notna().cumsum()
    elig = (amt >= MIN_AMT) & (hist >= MIN_HIST)
    px = close.ffill()
    ret = px.pct_change()
    dates = [d for d in px.index if d >= pd.Timestamp(START)]
    rbd = set(dates[::20])
    eq, held, curve = 1.0, [], []
    for i, d in enumerate(dates[:-1]):
        if d in rbd:
            held = elig.loc[d][elig.loc[d]].index.tolist()
        if held:
            r = ret.loc[dates[i + 1], held].mean()
            if np.isfinite(r):
                eq *= (1.0 + r)
        curve.append((d, eq))
    ew = pd.Series(dict(curve))
    for lbl, sl in (("full", ew), ("is_2020_2023", ew[ew.index <= IS_END]),
                    ("oos_2024_plus", ew[ew.index > IS_END])):
        m = metrics(sl, "ew_universe_%s" % lbl)
        out["runs"].append(m)
        print(m)
    if bench is not None:
        b = bench[bench.index >= pd.Timestamp(START)]
        b = b / b.iloc[0]
        for lbl, sl in (("full", b), ("is_2020_2023", b[b.index <= IS_END]),
                        ("oos_2024_plus", b[b.index > IS_END])):
            m = metrics(sl, "csi300_%s" % lbl)
            out["runs"].append(m)
            print(m)

    ser20, _ = run_portfolio(close, openp, amt, score, 20)
    out["yearly_rebal20"] = {int(k): round(float(v), 4) for k, v in
                             ser20.groupby(ser20.index.year).apply(
                                 lambda s: s.iloc[-1] / s.iloc[0] - 1).items()}
    print("yearly:", out["yearly_rebal20"])

    last = score.index[-1]
    picks = score.loc[last].dropna().nlargest(N_HOLD)
    out["live_picks"] = {"as_of": last.strftime("%Y-%m-%d"),
                         "picks": [{"symbol": s, "score": round(float(v), 3)}
                                   for s, v in picks.items()]}
    print("live picks", out["live_picks"]["as_of"], list(picks.index))

    p = os.path.join(PATHS.results_dir, "stock_composite_pf.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()