"""Paper ledger for the bond-free ETF book (production candidate, staggered 5+5).

Production book (decided 2026-10-25 from the capacity/stagger study):
  * universe: equity + commodity + convertible ETFs (bond/money excluded -- the sleeve
    split showed the composite has no bond-selection skill)
  * two sleeves of 5 names each, 10-day clock, offset 5 days: on any given day only one
    sleeve turns over, which cut turnover from 1.22 to 0.74 and lifted Sharpe 1.16 -> 1.32
  * 10% per name (0.5 sleeve capital / 5 names), signal at close, fill next open
  * 8% volatility target as a scale on the combined book (de-lever only, never above 1)

Ledger contract: append-only JSONL, one row per signal date; re-running the same date
replaces that row (idempotent for a scheduled task). Each sleeve carries its own next-due
date, so a skipped run still rebalances on the next run instead of silently drifting.
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

LEDGER = os.path.join(PATHS.results_dir, "etf_paper", "ledger.jsonl")
REBAL = 10
SLEEVES = 2
PER_SLEEVE = 5
N_TOTAL = SLEEVES * PER_SLEEVE
TARGET_VOL = 0.08
BOND_FREE = ("equity", "commodity", "convertible")


def load_ledger():
    if not os.path.exists(LEDGER):
        return []
    rows = []
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_ledger(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, LEDGER)


def book_vol(rets, weights, upto):
    if not weights:
        return np.nan
    window = rets.loc[:upto].tail(60)[list(weights)]
    if window.shape[0] < 20:
        return np.nan
    w = np.array([weights[k] for k in window.columns])
    cov = window.cov().to_numpy()
    return float(np.sqrt(w @ cov @ w) * np.sqrt(252))


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in BOND_FREE]
    score = E.build_score(close[cols], amt[cols], feats)

    dates = [d for d in close.index if d in score.index]
    today = dates[-1]
    pos = len(dates) - 1

    rows = load_ledger()
    prev = rows[-1] if rows else None

    # initialise sleeves on first ever run; afterwards carry their own positions forward
    if prev:
        sleeve_state = prev.get("sleeves", [])
    else:
        sleeve_state = [{"leg": k, "next_due_pos": pos, "weights": {}, "picks": []}
                        for k in range(SLEEVES)]

    if len(sleeve_state) != SLEEVES:
        sleeve_state = [{"leg": k, "next_due_pos": pos, "weights": {}, "picks": []}
                        for k in range(SLEEVES)]
    for st in sleeve_state:
        st.setdefault("next_due_pos", pos)

    s = score.loc[today].dropna()
    ranked = list(s.nlargest(N_TOTAL).index) if len(s) >= N_TOTAL else []

    # initialising both sleeves on the same day would make them rebalance together and
    # lose the stagger, so the first due position carries a half-period offset per sleeve.
    first_run = prev is None
    for st in sleeve_state:
        if ranked and pos >= int(st.get("next_due_pos", pos)):
            leg = int(st["leg"])
            window = ranked[leg * PER_SLEEVE:(leg + 1) * PER_SLEEVE]
            if len(window) == PER_SLEEVE:
                st["weights"] = {p: round(0.5 / PER_SLEEVE, 6) for p in window}
                st["picks"] = window
                step = REBAL + (REBAL // SLEEVES) * leg if first_run else REBAL
                st["next_due_pos"] = pos + step

    combined = {}
    for st in sleeve_state:
        for p, w in st["weights"].items():
            combined[p] = round(combined.get(p, 0.0) + w, 6)

    rets = close[cols].pct_change()
    v = book_vol(rets, combined, today) if combined else np.nan
    scale = float(min(1.0, TARGET_VOL / v)) if np.isfinite(v) and v > 0 else 1.0
    weights = {p: round(w * scale, 6) for p, w in combined.items()}

    nav = 1.0
    period_ret = None
    if prev and prev.get("as_of") != str(today.date()):
        a = pd.Timestamp(prev["as_of"])
        r = 0.0
        for p, w in prev["weights"].items():
            x, y = close.at[a, p], close.at[today, p]
            if np.isfinite(x) and np.isfinite(y) and x > 0:
                r += w * (y / x - 1.0)
        period_ret = round(float(r), 6)
        nav = round(float(prev["nav"]) * (1.0 + r), 6)

    row = {
        "as_of": str(today.date()),
        "config": "bond-free, staggered 5+5, R10, 8% vol target",
        "sleeves": sleeve_state,
        "weights": weights,
        "picks": [{"symbol": p, "class": str(cls[p]), "weight": weights[p],
                   "score": round(float(s[p]), 4) if p in s.index else None}
                  for p in weights],
        "realised_vol_60d": round(float(v), 4) if np.isfinite(v) else None,
        "vol_scale": round(scale, 4),
        "cash_weight": round(1.0 - sum(weights.values()), 6),
        "period_return": period_ret,
        "nav": nav,
    }

    rows = [r for r in rows if r.get("as_of") != row["as_of"]] + [row]
    rows.sort(key=lambda x: x["as_of"])
    save_ledger(rows)

    print("as_of", row["as_of"], "nav", nav, "period_ret", period_ret,
          "vol", row["realised_vol_60d"], "scale", row["vol_scale"])
    for p in row["picks"]:
        print("  ", p["symbol"], p["class"], p["weight"], p["score"])
    for st in sleeve_state:
        print("  sleeve", st["leg"], "next_due_pos", st["next_due_pos"], "n", len(st["weights"]))


if __name__ == "__main__":
    main()
