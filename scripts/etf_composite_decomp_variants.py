"""ETF composite factor book -- sleeve-subset variants (r1244 bm-c).

Follow-up to scripts/etf_composite_decomp.py (r1243): that window showed the published
9%/yr headline splits roughly half-and-half between the defensive sleeve and everything
else, and that the equity-ONLY book loses to its own equal-weight control out of sample.
The open question for a tradeable product is narrower: WHICH sleeve subsets still keep
a positive, control-beating book? This module runs the same score, cost and cadence on
four subsets and prints each against its own equal-weight control:

  bond_removed       equity + commodity + crossborder
  commodity_removed  equity + bond + crossborder
  crossborder_removed equity + bond + commodity
  equity_gold_only   equity + commodity   (the "trend beef + gold hedge" book)

Basis notes are inherited, not re-litigated: close-to-close from the decision close,
8bp/side on turnover, no open-fill model, survivorship (on-disk panel = ETFs that still
exist), exploratory not preregistered. Asset classes come from
scripts/etf_asset_class.py (name keywords, prefix only as logged fallback).

Usage: python scripts/etf_composite_decomp_variants.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd

from config import PATHS
from scripts import etf_composite_decomp as D
from scripts.etf_asset_class import classify

VARIANTS = {
    "bond_removed": ("equity", "commodity", "crossborder"),
    "commodity_removed": ("equity", "bond", "crossborder"),
    "crossborder_removed": ("equity", "bond", "commodity"),
    "equity_gold_only": ("equity", "commodity"),
}


def book(close, amt, score, cols, rebal=D.REBAL):
    """Ranking book on a fixed column subset, plus its own equal-weight control."""
    sub_close, sub_amt, sub_score = close[cols], amt[cols], score[cols]
    b = D.run_attrib(sub_close, sub_amt, sub_score, rebal=rebal)
    rows = D.window_rows(b, "book")
    ew = D.run_ew(sub_close, sub_amt, rebal)
    ctrl = []
    for lbl, sl in (("full", ew),
                    ("is_2020_2023", ew[ew.index <= D.IS_END]),
                    ("oos_2024_plus", ew[ew.index >= D.OOS])):
        ctrl.append(D.metrics(sl, "ew_%s" % lbl))
    return {"runs": rows, "controls": ctrl,
            "mix": D.mix_stats(b["day_class_mix"]),
            "contrib_arithmetic": b["contrib_arithmetic"],
            "rebalances": b["rebalances"],
            "all_bond_share": b["all_bond_share"],
            "universe": len(cols)}


def compare(runs, ctrls):
    """Per-window excess of the book over its own equal-weight control (same window)."""
    out = {}
    for r, c in zip(runs, ctrls):
        win = r["label"].split("book_", 1)[-1]
        assert win == c["label"].split("ew_", 1)[-1], "window pairing drift: %r/%r" % (
            r["label"], c["label"])
        out[win] = {
            "book_cagr_pct": round(r["cagr"] * 100, 2),
            "ew_cagr_pct": round(c["cagr"] * 100, 2),
            "cagr_pp": round((r["cagr"] - c["cagr"]) * 100, 2),
            "book_sharpe": r["sharpe"],
            "ew_sharpe": c["sharpe"],
            "sharpe_delta": round(r["sharpe"] - c["sharpe"], 3),
            "book_maxdd_pct": round(r["maxdd"] * 100, 2),
            "ew_maxdd_pct": round(c["maxdd"] * 100, 2),
            "maxdd_pp": round((r["maxdd"] - c["maxdd"]) * 100, 2),
        }
    return out


def main():
    close, openp, amt, feats = D.build_panel()
    D.CLASSES.update(classify(list(close.columns)))
    classes = pd.Series({c: D.asset_class(c) for c in close.columns})
    score = D.build_score(close, amt, feats)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "basis": "close-to-close from decision close; 8bp/side on turnover; "
                 "no open-fill model (slippage not represented)",
        "caveats": ["survivorship: on-disk panel lists ETFs that still exist",
                    "exploratory analysis, not a preregistered judgement",
                    "each subset is ranked and controlled on the SAME columns",
                    "subsets are static: the book cannot rotate INTO a removed sleeve"],
        "cost_bp_per_side": 8,
        "n_hold": D.N_HOLD,
        "rebal": D.REBAL,
        "universe_classes": classes.value_counts().to_dict(),
        "variants": {},
    }

    for name, keep in VARIANTS.items():
        cols = [c for c in close.columns if classes[c] in keep]
        if len(cols) < D.N_HOLD * 4:
            out["variants"][name] = {"skipped": True, "universe": len(cols)}
            print(name, "SKIPPED universe", len(cols))
            continue
        v = book(close, amt, score, cols)
        v["vs_own_ew"] = compare(v["runs"], v["controls"])
        out["variants"][name] = v
        print("--- %s (universe %d)" % (name, len(cols)))
        for r in v["runs"]:
            print("   ", r)
        print("    vs own EW:", v["vs_own_ew"])

    p = os.path.join(PATHS.results_dir, "etf_composite_decomp_variants.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()