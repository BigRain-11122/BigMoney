# -*- coding: utf-8 -*-
"""r283 pre-flight timing probe: one engine sim on the real joint face.
Infra fact only (no outputs, no ledger, not a burn)."""
import sys, time, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import alloc_backtest as ab
import pandas as pd

SYMS = ["510300", "511010", "518880", "513500"]
px, amt = {}, {}
for s in SYMS:
    df = pd.read_csv(os.path.join("data", "daily", "sh%s.csv" % s))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= "2026-09-22"]
    d = df.set_index("date")
    px[s] = d["close"]
    amt[s] = d["amount"]
panel = pd.DataFrame(px).dropna().sort_index()
panel = panel[panel.index >= "2014-01-15"]
amounts = pd.DataFrame(amt).reindex(panel.index)
adv = {s: amounts[s].rolling(20).mean().to_numpy() for s in SYMS}
dates = [str(x) for x in panel.index]
prices = {s: panel[s].to_numpy() for s in SYMS}
cash = list(ab.load_repo(panel.index).fillna(0.0))
t0 = time.time()
res = ab.simulate(dates, prices, adv, cash,
                  {"510300": 0.25, "511010": 0.25, "518880": 0.25,
                   "513500": 0.25, "CASH": 0.0}, 1_000_000.0,
                  mode="monthly", cost_fn=ab.side_cost_v2, p2=False,
                  start_idx=0)
dt = time.time() - t0
m = ab.four_metrics(res["eq"])
print("bars=%d one_sim=%.2fs est_456=%.1fmin ann=%.4f" %
      (len(dates), dt, dt * 456 / 60.0, m["ann_ret"]))
