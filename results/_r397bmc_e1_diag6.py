# -*- coding: utf-8 -*-
# r397 E1 diag v6: day-by-day trace of signal + engine orders vs my sim state
# on the exact divergence window per symbol.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
import lowamp_deep_p1 as L
from live.paper import build_panels, ExitPatch, COST_X1_RATE
from engine import run_backtest

CELL, AXIS, FACE = "LAD-EDGE", "deep", "base"
prices = L.load_axis(AXIS)
P = build_panels(prices)
close = P["close"]
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])

WINDOWS = {
    "159919": ("2013-12-04", "2013-12-20"),
    "510300": ("2014-01-02", "2014-01-09"),
    "510050": ("2017-05-10", "2017-05-18"),
    "510330": ("2014-06-24", "2014-07-01"),
}
r = COST_X1_RATE
for sym, (d0, d1) in WINDOWS.items():
    df = prices[sym]
    sig_full = entry[sym].reindex(df.index).fillna(False)
    w_full = weights[sym].reindex(df.index)
    print(f"=== {sym} {d0}..{d1} ===")
    print("  date        sig   w        (panel-sig)")
    for d, s in sig_full.loc[d0:d1].items():
        print("  %s  %5s  %s" % (str(d.date()), bool(s),
                                 round(float(w_full.loc[d]), 4) if s else ""))
    # my sim trace on window
    sig = sig_full.to_numpy(dtype=bool)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    i0 = df.index.get_loc(pd.Timestamp(d0)); i1 = df.index.get_loc(pd.Timestamp(d1))
    cash, qty = L.CAPITAL, 0.0
    pending = None; bought_today = -1
    # replay from the beginning to reach window state consistently
    for i in range(i0 + 1):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                if i >= i0 - 3:
                    print("   [mine] SELL fill", str(df.index[i].date()))
                cash += qty * op * (1 - r); qty = 0.0; pending = None
            elif kind == "buy" and qty == 0:
                if i >= i0 - 3:
                    print("   [mine] BUY fill %.4f" % pw, str(df.index[i].date()))
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); bought_today = i; pending = None
        if qty > 0:
            if not sig[i]:
                pending = ("sell", None)
        else:
            if sig[i]:
                pending = ("buy", float(w_full.iloc[i]))
    for i in range(i0 + 1, i1 + 1):
        d = df.index[i]
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                print("   [mine] SELL fill", str(d.date()))
                cash += qty * op * (1 - r); qty = 0.0; pending = None
            elif kind == "buy" and qty == 0:
                print("   [mine] BUY fill %.4f @ %s" % (pw, str(d.date())))
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); bought_today = i; pending = None
        if qty > 0:
            if not sig[i]:
                print("   [mine] sell-queued at close", str(d.date()))
                pending = ("sell", None)
        else:
            if sig[i]:
                print("   [mine] buy-queued at close", str(d.date()))
                pending = ("buy", float(w_full.iloc[i]))
