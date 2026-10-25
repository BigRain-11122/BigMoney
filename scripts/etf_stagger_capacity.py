"""Does staggering a rebalance into two half-size sleeves buy capacity?

Same signal, same clock. Instead of trading all N names on one day, the book is split into
two sleeves of N/2 names: sleeve A rebalances on the grid, sleeve B is offset half a period.
Each sleeve trades half the capital, so the largest single-name order on any day is roughly
halved -- which is exactly what the capacity line is made of.

Reported: return / drawdown of the staggered book (its own, not the single-sleeve one) and
the capital that keeps p90 participation under 1% / 5% of ADV, next to the same numbers for
the un-staggered cell.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_walkforward_capacity as W
from config import PATHS

N_TOTAL = 8
REBAL = 10
COST = 0.0010


def run_staggered(close, openp, amt, score, rebal=REBAL, n_total=N_TOTAL, cost=COST,
                  start=W.START):
    """Two sleeves, each n_total/2 names, decisions offset by rebal//2."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    half = n_total // 2
    w_unit = 0.5 / half                     # each sleeve is half the capital

    equity = 1.0
    held = [{}, {}]
    curve, trades = [], []

    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        for k in (0, 1):
            if i % rebal != (k * (rebal // 2)) % rebal:
                continue
            s = score.loc[d].dropna()
            if len(s) < n_total:
                continue
            window = list(s.nlargest(n_total).index)[k * half:(k + 1) * half]
            new = {p: w_unit for p in window}
            old = held[k]
            turn = sum(abs(new.get(x, 0.0) - old.get(x, 0.0)) for x in set(new) | set(old))
            equity *= (1.0 - cost * turn)
            trades.append({"date": d, "turnover": turn,
                           "delta": {x: abs(new.get(x, 0.0) - old.get(x, 0.0))
                                     for x in set(new) | set(old)}})
            held[k] = new
        r = 0.0
        for book in held:
            for p, wt in book.items():
                a, b = op.at[d, p], op.at[nxt, p]
                if np.isfinite(a) and np.isfinite(b) and a > 0:
                    r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        curve.append((nxt, equity))

    return pd.Series(dict(curve)).sort_index(), trades


def cap_of(trades, amt, close):
    recs = []
    for t in trades:
        d = t["date"]
        if d not in amt.index:
            continue
        a = amt.loc[d]
        worst = 0.0
        for sym, dw in t["delta"].items():
            v = a.get(sym, np.nan)
            if np.isfinite(v) and v > 0:
                worst = max(worst, dw / v)
        if worst > 0:
            recs.append(worst)
    s = pd.Series(recs)
    return {"aum_1pct": round(float(0.01 / s.quantile(0.90)), 0),
            "aum_5pct": round(float(0.05 / s.quantile(0.90)), 0),
            "rebalances": int(len(s))}


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in W.BOND_FREE]
    score = E.build_score(close[cols], amt[cols], feats)
    print("universe", len(cols), flush=True)

    out = {}
    # control: single sleeve, all 8 names on the grid
    ser1, tr1 = W.run_book(close[cols], openp[cols], amt[cols], score, REBAL, N_TOTAL,
                           record_trades=True)
    m1 = A.stats2(ser1, "single")
    c1 = cap_of(tr1, amt[cols], close[cols])
    out["single_sleeve"] = {"cagr": m1["cagr"], "sharpe": m1["sharpe"], "maxdd": m1["maxdd"],
                            "turnover": round(float(np.mean([t["turnover"] for t in tr1])), 2), **c1}
    print("single", json.dumps(out["single_sleeve"], ensure_ascii=False), flush=True)

    # staggered: 4 + 4, offset half a period
    ser2, tr2 = run_staggered(close[cols], openp[cols], amt[cols], score)
    m2 = A.stats2(ser2, "staggered")
    c2 = cap_of(tr2, amt[cols], close[cols])
    out["staggered"] = {"cagr": m2["cagr"], "sharpe": m2["sharpe"], "maxdd": m2["maxdd"],
                        "turnover": round(float(np.mean([t["turnover"] for t in tr2])), 2), **c2}
    print("staggered", json.dumps(out["staggered"], ensure_ascii=False), flush=True)

    # activity assertion: a stagger that never fired would look identical in the ratios
    out["assertions"] = {"single_trades": len(tr1), "staggered_trades": len(tr2),
                         "sleeves_fired": bool(len(tr2) > len(tr1))}
    print("assertions", out["assertions"], flush=True)

    p = os.path.join(PATHS.results_dir, "etf_stagger_capacity.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()