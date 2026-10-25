"""Walk-forward + capacity for the bond-free ETF book.

Two questions the grid could not answer:

1) WALK-FORWARD -- if we had picked the configuration in real time (best trailing Sharpe
   among the nine cells, re-chosen every year using only data already elapsed), what would
   we actually have earned? A grid that is positive everywhere is not the same as a rule
   that picks well ex ante.

2) CAPACITY -- how much money fits. At each rebalance the trade is turnover x NAV; against
   each ETF's 20-day traded value that gives a participation rate. The capital at which the
   worst rebalance still stays under 1% of ADV is the honest size for one book.

Universe: bond/money/convertible excluded (the sleeve split showed no bond-selection skill),
quote-face flips repaired, decision at close t filled at open t+1.
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
from config import PATHS

START = "2020-01-01"
COST = 0.0010
CELLS = [(3, 10), (3, 20), (3, 40), (5, 10), (5, 20), (5, 40), (8, 10), (8, 20), (8, 40)]
FIXED = (5, 20)
BOND_FREE = ("equity", "commodity", "convertible")


def run_book(close, openp, amt, score, rebal, n_hold, cost=COST, start=START, record_trades=False):
    """Same leg chain as the production engine; optionally returns per-rebalance trades."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]

    equity, held = 1.0, {}
    curve, trades = [], []
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                equity *= (1.0 - cost * turn)
                if record_trades:
                    trades.append({"date": d, "turnover": turn,
                                   "delta": {k: abs(w.get(k, 0.0) - held.get(k, 0.0))
                                             for k in set(w) | set(held)}})
                held = w
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        curve.append((nxt, equity))
    return pd.Series(dict(curve)).sort_index(), trades


def sharpe(ser):
    r = ser.pct_change().dropna()
    if len(r) < 20:
        return np.nan
    sd = r.std()
    return float(r.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in BOND_FREE]
    print("universe", len(cols), "flips repaired", n_flip, flush=True)

    score = E.build_score(close[cols], amt[cols], feats)

    # ---- dead-series census (survivorship face) --------------------------------
    last_bar = close[cols].apply(lambda s: s.dropna().index[-1] if s.notna().any() else pd.NaT)
    cutoff = close.index[-1] - pd.Timedelta(days=30)
    dead = int((last_bar < cutoff).sum())
    stale = int((last_bar < close.index[-1] - pd.Timedelta(days=1)).sum())
    print("universe last-bar: total %d, not trading in last month %d, stale>1d %d, panel last %s"
          % (len(cols), dead, stale, close.index[-1].date()), flush=True)

    # ---- 1) all nine cells, full curve each (cheap: one pass per cell) ---------
    curves = {}
    for (n, r) in CELLS:
        ser, _ = run_book(close[cols], openp[cols], amt[cols], score, r, n)
        curves[(n, r)] = ser
        m = A.stats2(ser, "N%d_R%d" % (n, r))
        print("cell N%d R%d  cagr %.4f  sharpe %.3f  maxdd %.4f" %
              (n, r, m["cagr"], m["sharpe"], m["maxdd"]), flush=True)

    # ---- 2) walk-forward: pick on trailing Sharpe, earn the next year ----------
    years = list(range(2021, close.index[-1].year + 1))
    wf_rows, wf_level = [], 1.0
    fixed_level = 1.0
    for y in years:
        sel = None
        best = -9e9
        for cfg, ser in curves.items():
            trail = ser[ser.index < pd.Timestamp("%d-01-01" % y)]
            if len(trail) < 120:
                continue
            s = sharpe(trail)
            if np.isfinite(s) and s > best:
                best, sel = s, cfg
        if sel is None:
            sel = FIXED
        ser = curves[sel]
        yr = ser[(ser.index >= pd.Timestamp("%d-01-01" % y)) & (ser.index < pd.Timestamp("%d-01-01" % (y + 1)))]
        ret = float(yr.iloc[-1] / yr.iloc[0] - 1) if len(yr) > 1 else 0.0
        wf_level *= (1.0 + ret)
        fx = curves[FIXED]
        fyr = fx[(fx.index >= pd.Timestamp("%d-01-01" % y)) & (fx.index < pd.Timestamp("%d-01-01" % (y + 1)))]
        fret = float(fyr.iloc[-1] / fyr.iloc[0] - 1) if len(fyr) > 1 else 0.0
        fixed_level *= (1.0 + fret)
        wf_rows.append({"year": y, "picked": "N%d_R%d" % sel, "trailing_sharpe": round(best, 3),
                        "wf_ret": round(ret, 4), "fixed_ret": round(fret, 4)})
        print("WF %d picked N%d_R%d (trailing SR %.2f) -> %.2f%% | fixed %.2f%%" %
              (y, sel[0], sel[1], best, ret * 100, fret * 100), flush=True)

    yrs = len(years)
    wf_cagr = wf_level ** (1 / yrs) - 1 if yrs else 0
    fx_cagr = fixed_level ** (1 / yrs) - 1 if yrs else 0
    print("walk-forward chained CAGR %.4f | fixed N%d_R%d %.4f" % (wf_cagr, FIXED[0], FIXED[1], fx_cagr), flush=True)

    # ---- 3) capacity: participation vs 20d traded value ------------------------
    ser, trades = run_book(close[cols], openp[cols], amt[cols], score, FIXED[1], FIXED[0],
                           record_trades=True)
    adv = amt[cols]   # 20d median close*volume (already the liquidity gate)
    rows = []
    for t in trades:
        d = t["date"]
        if d not in adv.index:
            continue
        a = adv.loc[d]
        worst = 0.0
        worst_sym = None
        for sym, dw in t["delta"].items():
            v = a.get(sym, np.nan)
            if not np.isfinite(v) or v <= 0:
                continue
            ratio = dw / v          # capital C multiplies this to a participation rate
            if ratio > worst:
                worst, worst_sym = ratio, sym
        if worst > 0:
            rows.append({"date": str(d.date()), "turnover": round(t["turnover"], 3),
                         "max_dw_over_adv": worst, "binding": worst_sym})
    df = pd.DataFrame(rows)
    caps = {}
    for pct in (0.01, 0.05):
        cap = pct / df["max_dw_over_adv"].quantile(0.90)
        caps["aum_at_p90_under_%d%%_adv" % int(pct * 100)] = round(float(cap), 0)
    caps["aum_at_p99_under_1pct_adv"] = round(float(0.01 / df["max_dw_over_adv"].quantile(0.99)), 0)
    caps["rebalances"] = int(len(df))
    caps["median_max_dw_over_adv"] = float(df["max_dw_over_adv"].median())
    print("capacity", json.dumps(caps, ensure_ascii=False), flush=True)
    print("binding names (top 5):", df["binding"].value_counts().head(5).to_dict(), flush=True)

    out = {
        "universe": len(cols),
        "flips_repaired": n_flip,
        "survivorship": {"dead_last_month": dead, "stale_gt_1d": stale,
                         "panel_last": str(close.index[-1].date())},
        "cells": {("N%d_R%d" % k): {"cagr": A.stats2(v, "x")["cagr"],
                                    "sharpe": A.stats2(v, "x")["sharpe"],
                                    "maxdd": A.stats2(v, "x")["maxdd"]}
                  for k, v in curves.items()},
        "walk_forward": {"rows": wf_rows, "chained_cagr": round(wf_cagr, 4),
                         "fixed_cagr": round(fx_cagr, 4),
                         "fixed_cell": "N%d_R%d" % FIXED},
        "capacity": caps,
    }
    p = os.path.join(PATHS.results_dir, "etf_walkforward_capacity.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()