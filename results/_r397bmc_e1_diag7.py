# -*- coding: utf-8 -*-
# r397 diag v7: solve engine entry dates from trade records (cost_price
# recovery) + print signal series; settle the T+1 exit-guard semantics.
import sys
sys.path.insert(0, r'K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts')
import pandas as pd
import lowamp_deep_p1 as L
from live.paper import build_panels, ExitPatch
from science_gates import CostPatch
from engine import run_backtest

CELL, AXIS = "LAD-EDGE", "deep"
prices = L.load_axis(AXIS)
P = build_panels(prices)
close = P["close"]
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])

for sym, w0, w1 in (("159920", "2018-09-10", "2018-09-19"),
                    ("159919", "2013-12-10", "2013-12-20"),
                    ("510050", "2017-05-08", "2017-05-17")):
    ent = entry[[sym]]
    sc = L.exec_day_scale(weights, sym)
    with ExitPatch(L.EXIT_PATCH_OVERRIDES):
        res = run_backtest({sym: prices[sym]}, dict(L.NEUTRALIZED_PARAMS),
                           entry_signal=ent, exit_signal=ent <= 0,
                           entry_size_scale=sc)
    print(f"=== {sym} ===")
    sig = entry[sym]
    for d, s in sig.loc[w0:w1].items():
        row = prices[sym].loc[d]
        print("  %s sig=%-5s open=%.4f high=%.4f low=%.4f" %
              (str(d.date()), bool(s), row['open'], row['high'], row['low']))
    for t in res["trades"]:
        # solve cost_price: pnl_full = (Pe-cost)*Q - Pe*Q*rs - cost*Q*rb
        Pe, Q = t["price"], t["qty"]
        rs = rb = 0.0013041
        pnl_full = t.get("pnl_full", t["pnl"] - Pe * Q * rs)
        cost = (Pe * Q - Pe * Q * rs - pnl_full) / (Q + Q * rb)
        print("  trade exit %s hold=%s qty=%.2f exit_px=%.4f -> implied cost=%.4f pnl_rate=%s" %
              (t["date"], t["hold_days"], Q, Pe, cost, t["pnl_rate"]))
