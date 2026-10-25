"""Quick probe: what does the composite actually hold over time (bond-like vs equity-like)?"""
import os
import sys

sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
import numpy as np
import pandas as pd

sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts")
from etf_composite_pf import build_panel, build_score, MIN_AMT, MIN_HIST, N_HOLD

close, openp, amt, feats = build_panel()
score = build_score(close, amt, feats)
px = close.ffill()
dvol = px.pct_change().rolling(60, min_periods=30).std()
bond_like = dvol < 0.0025   # <0.25% daily sd ~ bond/money-market

dates = [d for d in score.index if d >= pd.Timestamp("2020-01-01")][::20]
rows = []
for d in dates:
    s = score.loc[d].dropna()
    if len(s) < N_HOLD:
        continue
    picks = list(s.nlargest(N_HOLD).index)
    nb = int(bond_like.loc[d].reindex(picks).fillna(False).sum()) if d in bond_like.index else 0
    rows.append((d, nb, N_HOLD - nb, ",".join(picks)))
mix = pd.DataFrame(rows, columns=["date", "bond", "equity", "picks"])
mix["year"] = mix["date"].dt.year
print(mix.groupby("year")[["bond", "equity"]].mean().round(2))
print("share of rebalances all-bond:", round((mix["bond"] == N_HOLD).mean(), 3))
print("share with >=1 equity:", round((mix["equity"] >= 1).mean(), 3))
print(mix.tail(6).to_string(index=False))