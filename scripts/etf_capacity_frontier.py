"""Capacity frontier: how much capital each cell can carry vs what it earns.

Capacity is measured the only way that matters for a real order: at every rebalance,
take the largest single-name trade weight change, divide by that name's 20-day traded
value, and find the capital at which even the p90 rebalance stays under 1% (and 5%) of
ADV. More names and a slower clock both buy capacity -- this table prices that trade-off.
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


def capacity(df, pct):
    return round(float(pct / df["max_dw_over_adv"].quantile(0.90)), 0)


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in W.BOND_FREE]
    score = E.build_score(close[cols], amt[cols], feats)
    print("universe", len(cols), flush=True)

    cells = [(5, 10), (5, 20), (5, 40), (8, 10), (8, 20), (8, 40),
             (12, 20), (12, 40), (20, 20), (20, 40)]
    rows = []
    for (n, r) in cells:
        ser, trades = W.run_book(close[cols], openp[cols], amt[cols], score, r, n,
                                 record_trades=True)
        m = A.stats2(ser, "x")
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
                recs.append({"max_dw_over_adv": worst})
        df = pd.DataFrame(recs)
        row = {"cell": "N%d_R%d" % (n, r), "cagr": m["cagr"], "sharpe": m["sharpe"],
               "maxdd": m["maxdd"], "turnover": round(float(np.mean([t["turnover"] for t in trades])), 2),
               "aum_1pct": capacity(df, 0.01), "aum_5pct": capacity(df, 0.05)}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    out = {"universe": len(cols), "cells": rows,
           "rule": "aum = pct / p90(max_single_name_trade_weight / 20d traded value)"}
    p = os.path.join(PATHS.results_dir, "etf_capacity_frontier.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()