"""ETF composite -- robustness grid + volatility targeting, open-to-open execution.

Execution model (no lookahead):
  decide at close of day t -> execute at OPEN of t+1 -> hold until the OPEN of the
  next rebalance. Daily P&L is open-to-open for whatever is held.

Robustness is reported as a GRID (rebalance x holdings x cost), not a single best cell:
a parameter set that only works in one corner is not stable profit.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
from config import PATHS

IS_END = "2023-12-31"
START = "2020-01-01"
TARGET_VOL = 0.08


def open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                        vol_target=None, start=START):
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    rebal_idx = list(range(0, len(dates) - 1, rebal))
    equity, held, daily, turns = 1.0, {}, [], []

    # realised vol of the current book, for the sizing overlay
    rets = op.pct_change()

    def book_vol(book, upto):
        if not book:
            return np.nan
        window = rets.loc[:upto].tail(60)[list(book)]
        if window.shape[0] < 20:
            return np.nan
        w = np.array([book[k] for k in window.columns])
        cov = window.cov().to_numpy()
        return float(np.sqrt(w @ cov @ w) * np.sqrt(252))

    for i in range(len(dates) - 1):
        d = dates[i]
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                scale = 1.0
                if vol_target:
                    v = book_vol(w, d)
                    if np.isfinite(v) and v > 0:
                        scale = float(min(1.0, vol_target / v))
                w = {k: v * scale for k, v in w.items()}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                equity *= (1.0 - cost * turn)
                turns.append(turn)
                held = w
        nxt = dates[i + 1]
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))
    ser = pd.Series(dict(daily)).sort_index()
    return ser, (float(np.mean(turns)) if turns else 0.0)


def stats(ser, label):
    ser = ser.dropna()
    if len(ser) < 40:
        return {"label": label, "note": "short"}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    # Equity curves are running levels from the panel start, so a sub-window slice begins
    # at whatever level the book had reached. Growth must be measured against the slice's
    # own first level: `last ** (1/yrs) - 1` silently assumed start=1.0 and overstated
    # every IS/OOS CAGR (the 2026-10-25 OOS 26.5% was really 15.2%).
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    r = ser.pct_change().dropna()
    vol = r.std() * np.sqrt(252)
    dd = (ser / ser.cummax() - 1)
    yearly = ser.groupby(ser.index.year).apply(lambda x: x.iloc[-1] / x.iloc[0] - 1)
    monthly = ser.resample("ME").last().pct_change().dropna()
    cagr = growth ** (1 / yrs) - 1
    return {
        "label": label, "years": round(yrs, 2),
        "start_level": round(float(ser.iloc[0]), 4),
        "cagr": round(float(cagr), 4),
        "vol": round(float(vol), 4),
        "sharpe": round(float(r.mean() * 252 / vol), 3) if vol > 0 else 0.0,
        "maxdd": round(float(dd.min()), 4),
        "calmar": round(float(cagr / abs(dd.min())), 2) if dd.min() < 0 else None,
        "worst_year": round(float(yearly.min()), 4),
        "neg_years": int((yearly < 0).sum()),
        "worst_month": round(float(monthly.min()), 4),
        "pos_months_pct": round(float((monthly > 0).mean()), 3),
    }


def main():
    close, openp, amt, feats = E.build_panel()
    score = E.build_score(close, amt, feats)
    print("universe", close.shape[1], flush=True)

    grid = []
    for n_hold in (3, 5, 8):
        for rebal in (10, 20, 40):
            for cost in (0.0005, 0.0010):
                ser, turn = open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost)
                m = stats(ser, "N%d_R%d_%dbp" % (n_hold, rebal, cost * 1e4))
                m["turnover"] = round(turn, 2)
                for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
                    mm = stats(sl, m["label"] + "_" + lbl)
                    for k in ("cagr", "sharpe", "maxdd"):
                        m[k + "_" + lbl] = mm.get(k)
                grid.append(m)
                print(m, flush=True)

    df = pd.DataFrame(grid)
    print("\n=== grid, sorted by full Sharpe ===")
    cols = ["label", "cagr", "sharpe", "maxdd", "calmar", "worst_year",
            "worst_month", "pos_months_pct", "turnover", "cagr_is", "cagr_oos", "sharpe_oos"]
    print(df[cols].sort_values("sharpe", ascending=False).to_string(index=False))

    # volatility-targeted version of a mid-grid cell (not the best cell)
    base = "N5_R20_10bp"
    ser_base, _ = open_to_open_equity(close, openp, amt, score, 20, 5, 0.0010)
    ser_vt, _ = open_to_open_equity(close, openp, amt, score, 20, 5, 0.0010,
                                   vol_target=TARGET_VOL)
    print("\n=== vol target %.0f%% vs base (%s) ===" % (TARGET_VOL * 100, base))
    vt = []
    for lbl, s in (("base_full", ser_base), ("vt_full", ser_vt),
                   ("base_oos", ser_base[ser_base.index > IS_END]),
                   ("vt_oos", ser_vt[ser_vt.index > IS_END])):
        m = stats(s, lbl)
        vt.append(m)
        print(m)

    out = {"grid": grid, "vol_target": vt, "target_vol": TARGET_VOL,
           "execution": "decision at close t, execute at open t+1, hold to next open"}
    p = os.path.join(PATHS.results_dir, "etf_robust_pf.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()