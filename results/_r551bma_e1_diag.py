"""Diagnostic (non-gate): where does the 5.05e-4 engine-vs-C max diff land?
Same load path as the E1; computes the daily diff distribution."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

import lowamp_p3 as L
from live.paper import build_panels, COST_X1_RATE
import importlib

e1mod = importlib.import_module("_r551bma_t140_e1")

prices = L.load_axis("legacy")
P = build_panels(prices)
close = P["close"]
spec = L.CELLS["LA-REP"]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"],
                                    spec["W"], spec["N"])
active = [c for c in entry.columns if entry[c].any()]

run = L.run_cell_portfolio(prices, close, entry, weights, "base", active)
nav = (run["pnl"] + L.CAPITAL).reindex(close.index).ffill().fillna(L.CAPITAL)
a_rets = nav.pct_change().dropna()

C = e1mod.leg_c_independent(prices, close, entry, weights, active)
c_rets = pd.Series(C["returns"], index=a_rets.index[:len(C["returns"])])

diff = (a_rets - c_rets).abs()
over = diff[diff > 5e-4]
print("days:", len(diff), "| days >5bp:", len(over))
print("top-5 diff days:")
for d, v in diff.nlargest(5).items():
    print("  ", d.date(), f"{v:.8f}", f"= {v*1e4:.4f}bp")
# is the max day a trade/fill boundary day?
td = set(t.date() for t in run["trade_dates"])
print("max day is trade date:", diff.idxmax().date() in td)
print("trade dates:", sorted(td))
