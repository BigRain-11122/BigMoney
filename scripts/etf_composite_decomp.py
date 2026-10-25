"""ETF composite factor book -- decompose the edge into asset-class legs.

The R20 composite book (scripts/etf_composite_pf.py) reported ~9%/yr full-sample and
~15%/yr after 2024, but roughly half its rebalance periods sat fully in bond ETFs. That
raises the only question that matters for a tradeable product: is the edge a cross-
sectional equity signal, or just "hold bonds when equity momentum is bad"?

This module answers it with two books built on the SAME score and cost model:
  A. as-published  : top-5 by composite score over the full ETF panel.
  B. equity-only   : the same scoring restricted to equity ETFs (bond / commodity /
                     cross-border ETFs removed from the universe before ranking).
Each book is attributed per asset class (time-in-class, weight, return contribution),
and each is compared with an equal-weight control built the same way.

Basis notes (carried from the published module, not re-litigated here):
  * close-to-close from the decision close; no open-fill model, so entry slippage is
    not represented -- only turnover is charged (8bp/side).
  * survivorship: the on-disk panel contains ETFs that still exist.
  * exploratory, not a preregistered judgement.

Usage: python scripts/etf_composite_decomp.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

from config import PATHS
from scripts.etf_asset_class import classify
from scripts.etf_composite_pf import (COST, N_HOLD, build_panel, build_score, metrics,
                                      run_ew)

CLASSES = {}


def asset_class(sym):
    """Name-keyword class from scripts/etf_asset_class.py (prefix fallback inside)."""
    return CLASSES.get(sym, "equity")


REBAL = 20
START = "2020-01-01"
IS_END = "2023-12-31"
OOS = "2024-01-01"








def run_attrib(close, amt, score, rebal=REBAL, start=START, n_hold=N_HOLD):
    """Book loop identical to etf_composite_pf.run(), plus per-class attribution."""
    px = close.ffill()
    ret = px.pct_change()
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    rebal_days = set(dates[::rebal])

    equity, held, curve = 1.0, {}, []
    contrib = {}          # class -> compounded-ish sum of w*r (arithmetic, documented)
    day_class_mix = []    # (date, {class: weight})
    turnover_sum, n_rebal, all_bond_rebals = 0.0, 0, 0

    for i, d in enumerate(dates[:-1]):
        if d in rebal_days:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                new = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(new.get(k, 0.0) - held.get(k, 0.0))
                           for k in set(new) | set(held))
                equity *= (1.0 - COST * turn)
                turnover_sum += turn
                n_rebal += 1
                held = new
                mix = {}
                for p in picks:
                    mix[asset_class(p)] = mix.get(asset_class(p), 0.0) + 1.0 / n_hold
                if set(mix) == {"bond"}:
                    all_bond_rebals += 1
        if held and i + 1 < len(dates):
            nd = dates[i + 1]
            r = 0.0
            mix = {}
            for p, w in held.items():
                rp = ret.at[nd, p] if p in ret.columns else np.nan
                if np.isfinite(rp):
                    r += w * rp
                    cls = asset_class(p)
                    contrib[cls] = contrib.get(cls, 0.0) + w * rp
                    mix[cls] = mix.get(cls, 0.0) + w
            equity *= (1.0 + r)
            day_class_mix.append((nd, mix))
        curve.append((d, equity))

    ser = pd.Series(dict(curve))
    bond_w = [m.get("bond", 0.0) for _, m in day_class_mix]
    hist = {"0": sum(1 for w in bond_w if w == 0.0),
            "0-50%": sum(1 for w in bond_w if 0.0 < w < 0.5),
            "50%": sum(1 for w in bond_w if 0.4 <= w <= 0.6),
            ">50%": sum(1 for w in bond_w if w > 0.6)}
    return {"series": ser,
            "bond_weight_hist_days": hist,
            "turnover_per_rebal": round(turnover_sum / n_rebal, 3) if n_rebal else 0.0,
            "rebalances": n_rebal,
            "all_bond_rebalances": all_bond_rebals,
            "all_bond_share": round(all_bond_rebals / n_rebal, 3) if n_rebal else 0.0,
            "contrib_arithmetic": {k: round(v, 4) for k, v in sorted(contrib.items())},
            "day_class_mix": day_class_mix}


def mix_stats(mix_series):
    """Days exposure and mean weight per class across the book's life."""
    n = len(mix_series)
    out = {}
    for c in ("equity", "bond", "commodity", "crossborder"):
        days = sum(1 for _, m in mix_series if m.get(c, 0.0) > 0)
        wsum = sum(m.get(c, 0.0) for _, m in mix_series)
        out[c] = {"days_held": days, "day_share": round(days / n, 3) if n else 0.0,
                  "mean_weight_when_live": round(wsum / days, 3) if days else 0.0,
                  "avg_weight_all_days": round(wsum / n, 3) if n else 0.0}
    return out


def window_rows(res, tag):
    rows = []
    ser = res["series"]
    for lbl, sl in (("full", ser),
                    ("is_2020_2023", ser[ser.index <= IS_END]),
                    ("oos_2024_plus", ser[ser.index >= OOS])):
        m = metrics(sl, "%s_%s" % (tag, lbl))
        m["turnover_per_rebal"] = res["turnover_per_rebal"]
        rows.append(m)
    return rows


def main():
    close, openp, amt, feats = build_panel()
    CLASSES.update(classify(list(close.columns)))
    classes = pd.Series({c: asset_class(c) for c in close.columns})
    score = build_score(close, amt, feats)

    out = {"evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
           "basis": "close-to-close from decision close; 8bp/side on turnover; "
                    "no open-fill model (slippage not represented)",
           "caveats": ["survivorship: on-disk panel lists ETFs that still exist",
                       "exploratory analysis, not a preregistered judgement",
                       "class tags are code-prefix heuristics, not vendor metadata"],
           "rebal": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
           "universe_total": int(close.shape[1]),
           "universe_by_class": {k: int(v) for k, v in classes.value_counts().items()},
           "books": {}}

    # A. as published (all classes eligible)
    a = run_attrib(close, amt, score)
    out["books"]["all_classes"] = {
        "runs": window_rows(a, "book"),
        "mix": mix_stats(a["day_class_mix"]),
        "contrib_arithmetic": a["contrib_arithmetic"],
        "bond_weight_hist_days": a["bond_weight_hist_days"],
        "rebalances": a["rebalances"],
        "all_bond_share": a["all_bond_share"]}

    # B. equity-only universe: same score, restricted ranking
    eq_cols = [c for c in close.columns if classes[c] == "equity"]
    eq_close = close[eq_cols]
    eq_score = score[eq_cols]
    b = run_attrib(eq_close, amt[eq_cols], eq_score)
    out["books"]["equity_only"] = {
        "runs": window_rows(b, "book"),
        "mix": mix_stats(b["day_class_mix"]),
        "contrib_arithmetic": b["contrib_arithmetic"],
        "rebalances": b["rebalances"],
        "universe": len(eq_cols)}

    # Controls: equal weight over the same eligible universes, same cadence.
    ew_all = run_ew(close, amt, REBAL)
    for lbl, sl in (("full", ew_all), ("is_2020_2023", ew_all[ew_all.index <= IS_END]),
                    ("oos_2024_plus", ew_all[ew_all.index >= OOS])):
        out["books"].setdefault("controls", []).append(metrics(sl, "ew_all_%s" % lbl))
    ew_eq = run_ew(eq_close, amt[eq_cols], REBAL)
    for lbl, sl in (("full", ew_eq), ("is_2020_2023", ew_eq[ew_eq.index <= IS_END]),
                    ("oos_2024_plus", ew_eq[ew_eq.index >= OOS])):
        out["books"].setdefault("controls", []).append(metrics(sl, "ew_equity_%s" % lbl))

    for name in ("all_classes", "equity_only"):
        for r in out["books"][name]["runs"]:
            print(r)
        print("mix:", out["books"][name]["mix"])
        print("contrib:", out["books"][name]["contrib_arithmetic"])
        if "all_bond_share" in out["books"][name]:
            print("all-bond rebalance share:", out["books"][name]["all_bond_share"])
    print("\n=== controls ===")
    for r in out["books"]["controls"]:
        print(r)

    if any(a.startswith("--null") for a in sys.argv):
        n_iter = 200
        for a in sys.argv:
            if a.startswith("--null="):
                n_iter = int(a.split("=")[1])
        from scripts.etf_composite_pf import null_test
        print("null test on the equity-only book: %d shuffles ..." % n_iter)
        real, ns = null_test(eq_close, openp[eq_cols], amt[eq_cols], feats, REBAL,
                            n_iter=n_iter)
        out["null_test_equity_only"] = {
            "iter": n_iter,
            "real_period_sharpe": float(real),
            "mean": round(float(ns.mean()), 3),
            "p95": round(float(np.percentile(ns, 95)), 3),
            "max": round(float(ns.max()), 3),
            "p_value": round(float((ns >= real).mean()), 4)}
        print(out["null_test_equity_only"])

    p = os.path.join(PATHS.results_dir, "etf_composite_decomp.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()