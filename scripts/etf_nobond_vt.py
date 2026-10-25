"""Production-candidate check: drop the bond sleeve, then apply the 8%/12% vol target.

Evidence that motivates this: bond/money-only composite earns 0.6%/yr vs 1.5%/yr for the
same sleeve equal-weighted (no bond-selection skill), while equity-only earns 11.2%/yr vs
3.8% EW. So bonds are a drag on the book, not a defence. This run sizes the consequence
and prints today's live picks for the bond-free book.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

IS_END = "2023-12-31"


def report(ser, label, out):
    m = A.stats2(ser, label)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    out.append(m)
    print(m, flush=True)


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    print("bond-free universe", len(cols), "flips repaired", n_flip, flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)
    out = []
    for label, vt in (("nobond_base", None), ("nobond_vt08", 0.08), ("nobond_vt12", 0.12)):
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                          vol_target=vt)
        report(ser, label, out)
        out[-1]["turnover"] = round(turn, 2)

    # live picks for the bond-free book
    last = sc.index[-1]
    s = sc.loc[last].dropna()
    picks = [(sym, round(float(v), 3), cls[sym]) for sym, v in s.nlargest(5).items()]
    print("live picks", last.date(), picks, flush=True)

    import json
    p = os.path.join(E.PATHS.results_dir, "etf_nobond_vt.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"runs": out,
                   "universe": len(cols),
                   "live_picks": {"as_of": str(last.date()),
                                  "picks": [{"symbol": a_, "score": b_, "class": c_}
                                            for a_, b_, c_ in picks]}}, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()