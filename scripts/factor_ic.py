"""Factor IC analysis: Spearman rank correlation between factor value
and forward N-day return, cross-sectionally, averaged over time.

IC > 0.05 meaningful, > 0.1 strong.
IR = mean(IC) / std(IC) > 0.5 good.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from tasks.backtest_task import _load_prices
from engine.factors import compute_all
from config import PATHS


def ic_series(factor: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
    """Cross-sectional Spearman IC per date."""
    common = factor.index.intersection(fwd_ret.index)
    ics = []
    for dt in common:
        f = factor.loc[dt].dropna()
        r = fwd_ret.loc[dt].dropna()
        both = f.index.intersection(r.index)
        if len(both) < 5:
            continue
        ic, _ = spearmanr(f[both], r[both])
        if not np.isnan(ic):
            ics.append((dt, ic))
    return pd.Series(dict(ics)).sort_index()


def main():
    print("loading prices...")
    prices = _load_prices()
    print(f"  {len(prices)} ETFs")

    bench = None
    bench_path = os.path.join(PATHS.basic_dir, "csi300.csv")
    if os.path.exists(bench_path):
        b = pd.read_csv(bench_path, parse_dates=["date"]).set_index("date")["close"]
        bench = b

    print("computing factors...")
    factors = compute_all(prices, bench)
    print(f"  {len(factors)} factors")

    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index().ffill()

    results = {}
    for horizon in [5, 10, 20]:
        fwd = close.shift(-horizon) / close - 1
        for name, fac in factors.items():
            s = ic_series(fac, fwd)
            if len(s) < 30:
                continue
            key = f"{name}_h{horizon}"
            results[key] = {
                "ic_mean": round(s.mean(), 4),
                "ic_std": round(s.std(), 4),
                "ic_ir": round(s.mean() / s.std(), 3) if s.std() > 0 else 0,
                "ic_pos_pct": round((s > 0).mean(), 3),
                "n_periods": len(s),
            }

    # print table
    df = pd.DataFrame(results).T
    df = df.sort_values("ic_mean", key=abs, ascending=False)
    print("\n=== Factor IC (sorted by |IC|) ===")
    print(df.to_string())

    out = os.path.join(PATHS.results_dir, "factor_ic.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
