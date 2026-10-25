"""Stock composite: parameter sweep on holdings / rebalance / cost.

Baseline (20 names, 20d, 20bp/side) lost badly to the equal-weight universe, so this
sweep separates the two suspects: idiosyncratic concentration and turnover cost.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import stock_composite_pf as S

CONFIGS = [
    (20, 20, 0.0020),
    (50, 20, 0.0010),
    (100, 20, 0.0010),
    (50, 60, 0.0010),
    (100, 60, 0.0010),
    (100, 60, 0.0005),
]


def main():
    prices = S.load_universe()
    from engine.factors import compute_all
    from config import PATHS
    bench = None
    bp = os.path.join(PATHS.basic_dir, "csi300.csv")
    if os.path.exists(bp):
        bench = pd.read_csv(bp, parse_dates=["date"]).set_index("date")["close"]
    feats = compute_all(prices, bench)
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index().replace(0.0, np.nan)
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    amt = (close * vol).rolling(20, min_periods=10).median()

    is_ic = S.ic_table(feats, close, 20, S.START, S.IS_END)
    signs = {k: (1.0 if v["ic"] >= 0 else -1.0) for k, v in is_ic.items()}
    score = S.build_score(close, feats, signs, close.columns)
    print("stocks", len(prices), "factors", len(signs), flush=True)

    rows = []
    for n_hold, rebal, cost in CONFIGS:
        S.COST = cost
        ser, turn = S.run_portfolio(close, openp, amt, score, rebal, n_hold=n_hold)
        for lbl, sl in (("full", ser), ("oos", ser[ser.index > S.IS_END])):
            m = S.metrics(sl, "n%d_r%d_c%gbp_%s" % (n_hold, rebal, cost * 1e4, lbl))
            m["turnover"] = round(turn, 2)
            rows.append(m)
            print(m, flush=True)
    df = pd.DataFrame(rows)
    print("\n=== sorted by OOS sharpe ===")
    print(df[df.label.str.endswith("oos")].sort_values("sharpe", ascending=False)
          [["label", "cagr", "sharpe", "maxdd", "turnover"]].to_string(index=False))


if __name__ == "__main__":
    main()