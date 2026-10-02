# -*- coding: utf-8 -*-
# r397 E1 diag v5: per-symbol with entry-day-exit-read fix; list my SELL dates
# vs engine exit dates side by side for divergent symbols.
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
idx = close.index
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])
active = [c for c in entry.columns if entry[c].any()]
r = COST_X1_RATE

for sym in active:
    df = prices[sym]
    ent = entry[[sym]]
    sc = L.exec_day_scale(weights, sym)
    with ExitPatch(L.EXIT_PATCH_OVERRIDES):
        res = run_backtest({sym: df}, dict(L.NEUTRALIZED_PARAMS),
                           entry_signal=ent, exit_signal=ent <= 0,
                           entry_size_scale=sc)
    eq = pd.Series(res["equity_curve"], index=df.index[:len(res["equity_curve"])])
    epnl = (eq - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
    sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
    w = weights[sym].reindex(df.index)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    highs = df["high"].to_numpy(); lows = df["low"].to_numpy()
    cash, qty = L.CAPITAL, 0.0
    nav_vals = []; pending = None; bought_today = -1
    ev = []
    for i in range(len(df)):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                cash += qty * op * (1 - r); qty = 0.0
                ev.append((str(df.index[i].date()), "SELL")); pending = None
            elif kind == "buy" and qty == 0:
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); bought_today = i; pending = None
                ow = bool(op == highs[i] == lows[i] == closes[i])
                ev.append((str(df.index[i].date()), "BUY %.4f%s" % (pw, " ONEWORD" if ow else "")))
        if qty > 0:
            if not sig[i]:
                pending = ("sell", None)
        else:
            if sig[i]:
                pending = ("buy", float(w.iloc[i]))
        nav_vals.append(cash + qty * closes[i])
    nav_sym = pd.Series(nav_vals, index=df.index)
    cpnl = (nav_sym - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
    d = (epnl - cpnl).abs()
    mx = float(d.max())
    if mx > 1.0:
        print(f"=== {sym}: max_sub_diff={mx:.2f} first_div={d[d>1.0].index[0].date()}")
        print("    mine:", ev)
        print("    eng :", [(str(pd.Timestamp(t['date']).date()), t['reason'][:7], round(t['qty'],2)) for t in res['trades']])
    else:
        print(f"{sym}: max_sub_diff={mx:.2f} OK")
