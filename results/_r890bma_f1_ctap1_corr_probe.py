# r890 bm-a T-177 leg-2 slice: F1 ETF momentum rotation vs CTA_P1 D6 correlation probe
# Gate: D6 same-family admission (max|corr| on daily sleeve returns, sleeve-tag precedent,
# threshold 0.7 per TRIAL_LABOR_W4 s4 intake / REGIME5_BULL_SUPPLY_SCAN next-pointer 1).
# Zero network, zero judgment, zero prereg -- admission probe only (supply face).
# CTA_P1 sleeve = frozen construction verbatim import (cta_p1_screen + futures_runner).
import sys, os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

from engine import futures_runner as fr
from cta_p1_screen import sig_vol_target_tsmom, build_weights, month_first_index

UNIVERSE = ["510300", "510050", "510500", "512100", "588000"]  # O-1555 frozen five
NINE = ["IF", "IC", "IH", "IM", "T", "TF", "RB", "AU", "SC"]    # frozen CTA_P1 nine
WINDOW_START = "2017-01-17"   # CTA_P1 frozen window start
WARMUP_START = "2016-03-01"   # momentum warmup headroom (250d max lookback)
INITIAL_CNY = 10_000_000.0    # CTA_P1 batch parity
COST_MULT = 1.0               # x1 production-aligned (futures engine internal fees)
ETF_COST_PER_SIDE = 13.041e-4  # x1 repo convention (system_v1_paper COST_X1 mirror)
D6_THRESHOLD = 0.70

def etf_close_panel() -> pd.DataFrame:
    cols = {}
    for code in UNIVERSE:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"sh{code}.csv"),
                         index_col=0, parse_dates=True).sort_index()
        cols[code] = df["close"]
    return pd.DataFrame(cols)

def futures_cutoff() -> pd.Timestamp:
    last = None
    for v in NINE:
        df = pd.read_csv(os.path.join(fr.FUT_DIR, f"{v}.csv"),
                         index_col=0, parse_dates=True).sort_index()
        t = df.index[-1]
        last = t if last is None else max(last, t)
    return last

def cta_p1_daily_returns(cutoff: pd.Timestamp) -> pd.Series:
    panel = fr.load_panel(WINDOW_START, str(cutoff.date()), varieties=NINE)
    state = sig_vol_target_tsmom(panel["close"], 60)
    weights = build_weights(state, panel["close"], None)
    r = fr.run(panel, weights, start_cash=INITIAL_CNY, cost_mult=COST_MULT)
    return r.equity.pct_change().dropna()

def f1_weights(close: pd.DataFrame, lookback: int, topk: int) -> pd.DataFrame:
    """Monthly-rebalanced long-only top-k inverse-vol rotation.
    Signal = close/close.shift(L)-1 at rebalance date; weight = inverse 60d
    realized vol within top-k, normalized to sum 1. At each rebalance the
    full vector REPLACES the allocation (non-picks = 0.0, not carried);
    between rebalances the vector is held. Effective with 1-day lag
    applied by caller (no lookahead)."""
    sig = close / close.shift(lookback) - 1.0
    vol = close.pct_change().rolling(60).std()
    reb = month_first_index(close.index)
    # all-NaN skeleton; full replacement vectors at rebalance rows only
    W = pd.DataFrame(np.nan, index=close.index, columns=close.columns)
    for t in reb:
        s = sig.iloc[t]
        v = vol.iloc[t]
        alive = s.dropna().index.intersection(v.dropna().index)
        if len(alive) == 0:
            continue
        ranked = s[alive].sort_values(ascending=False)
        picks = list(ranked.index[:topk])
        if not picks:
            continue
        iv = 1.0 / v[picks]
        w = iv / iv.sum()
        row = pd.Series(0.0, index=close.columns)
        row[picks] = w.to_numpy()
        W.iloc[t] = row.to_numpy()
    # carry the latest full vector forward between rebalances; head = flat
    W = W.ffill().fillna(0.0)
    return W

def f1_daily_returns(close: pd.DataFrame, lookback: int, topk: int) -> pd.Series:
    W = f1_weights(close, lookback, topk)
    gross_exp = W.sum(axis=1)
    if float(gross_exp.max()) > 1.0 + 1e-6:
        raise AssertionError(
            f"gross exposure leak: max {float(gross_exp.max())} (long-only sum-1 violated)")
    W_prev = W.shift(1).fillna(0.0)
    ret = close.pct_change().fillna(0.0)
    gross = (W_prev * ret).sum(axis=1)
    turnover = (W - W_prev).abs().sum(axis=1)
    cost = turnover * ETF_COST_PER_SIDE
    net = gross - cost
    # start after first valid rebalance window (warmup: max(lookback,60)+lag)
    warm = int(max(lookback, 60)) + 2
    net.iloc[:warm] = np.nan
    return net.dropna()

def main() -> int:
    close_all = etf_close_panel()
    fut_cutoff = futures_cutoff()
    etf_cutoff = close_all.index[-1]
    close = close_all.loc[WARMUP_START:].copy()
    cutoff = min(fut_cutoff, etf_cutoff)
    close = close.loc[:cutoff]

    cta_ret = cta_p1_daily_returns(cutoff)
    cells = []
    for L in (60, 120, 250):
        for k in (1, 2, 3):
            f1_ret = f1_daily_returns(close, L, k)
            joined = pd.concat([f1_ret.rename("f1"), cta_ret.rename("cta")],
                               axis=1, join="inner").dropna()
            n = len(joined)
            if n < 200:
                cells.append({"lookback": L, "topk": k, "n_overlap": n,
                              "corr": None, "note": "insufficient overlap"})
                continue
            c = float(np.corrcoef(joined["f1"], joined["cta"])[0, 1])
            cells.append({
                "lookback": L, "topk": k, "n_overlap": n, "corr": round(c, 4),
                "f1_ann_ret_pct": round(float(joined["f1"].mean() * 242 * 100), 2),
                "f1_ann_vol_pct": round(float(joined["f1"].std() * np.sqrt(242) * 100), 2),
            })
    valid = [abs(c["corr"]) for c in cells if c["corr"] is not None]
    max_abs = max(valid) if valid else None
    same_family = bool(max_abs is not None and max_abs >= D6_THRESHOLD)

    out = {
        "schema": "f1_ctap1_corr_probe_v1",
        "ticket": "T-2026-10-08-177 leg-2 next-pointer-1 (REGIME5_BULL_SUPPLY_SCAN)",
        "purpose": "D6 same-family admission probe: F1 ETF momentum rotation vs "
                   "registered CTA_P1 (vol_target_tsmom_60 futures nine-variety)",
        "d6_rule": "max|corr| on daily sleeve returns (sleeve-tag precedent); "
                   ">=0.70 = same-family merge path (no separate prereg); "
                   "<0.70 = cleared to own prereg",
        "cta_p1_construction": "frozen verbatim: cta_p1_screen.sig_vol_target_tsmom(60) "
                               "+ build_weights(daily regime) + futures_runner.run "
                               "cost x1, 10M parity, window 2017-01-17..cutoff",
        "f1_construction": "long-only top-k monthly rotation on O-1555 frozen five; "
                           "signal=close/close.shift(L)-1; weights=inverse 60d vol "
                           "within top-k sum 1; month-first rebalance (cta_p1_screen "
                           "month_first_index reuse); 1-day lag no-lookahead; cost "
                           "13.041bp/side x turnover (x1 repo convention)",
        "universe_note": "588000 alive-handled (inception 2020-11); ranked among "
                         "alive members only",
        "window": {"start": WINDOW_START, "end": str(cutoff.date()),
                   "futures_cutoff": str(fut_cutoff.date()),
                   "etf_cutoff": str(etf_cutoff.date())},
        "evidence_cutoff": str(cutoff.date()),
        "cells": cells,
        "max_abs_corr": None if max_abs is None else round(max_abs, 4),
        "d6_threshold": D6_THRESHOLD,
        "verdict": ("SAME_FAMILY_MERGE_PATH" if same_family
                    else "CLEARED_TO_OWN_PREREG"),
        "honest_notes": [
            "corr is scale-invariant: CTA_P1 futures sleeve embeds margin/leverage "
            "profile; correlation measured on realized daily equity returns",
            "representative cells only (lookback x topk x monthly); full grid "
            "belongs to the future prereg if cleared",
            "zero judgment gates in this probe -- admission face only; no "
            "beat/null/pbo claimed",
        ],
        "determinism": "no RNG; same panel bytes => same output bytes",
        "generated_by": "results/_r890bma_f1_ctap1_corr_probe.py (bm-a r890)",
    }
    outdir = os.path.join(ROOT, "results", "regime5_bull_scan")
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "f1_ctap1_corr_probe.bm-a.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ascii_summary = {
        "max_abs_corr": out["max_abs_corr"], "verdict": out["verdict"],
        "n_cells": len(cells),
        "cells_brief": [[c["lookback"], c["topk"], c["corr"]] for c in cells],
    }
    print(json.dumps(ascii_summary))
    return 0

if __name__ == "__main__":
    sys.exit(main())
