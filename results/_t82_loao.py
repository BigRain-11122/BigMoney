"""Leave-one-factor-out: does the edge survive dropping any single factor?"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R

FACTORS = list(E.SIGNS)


def main():
    close, openp, amt, feats = E.build_panel()
    base_signs = dict(E.SIGNS)
    rows = []
    for drop in [None] + FACTORS:
        signs = {k: v for k, v in base_signs.items() if k != drop}
        E.SIGNS = signs
        score = E.build_score(close, amt, feats)
        ser, turn = R.open_to_open_equity(close, openp, amt, score, 20, 5, 0.0010)
        m = R.stats(ser, "drop=%s" % (drop or "none"))
        m["turnover"] = round(turn, 2)
        rows.append(m)
        print(m, flush=True)
    E.SIGNS = base_signs
    df = pd.DataFrame(rows)
    print("\n", df[["label", "cagr", "sharpe", "maxdd", "worst_year"]].to_string(index=False))


if __name__ == "__main__":
    main()