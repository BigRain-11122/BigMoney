# -*- coding: utf-8 -*-
# r397 E1 diag v4: per-symbol engine equity curve vs Leg-C sub-account,
# pinpoint WHICH symbol's sub-account diverges and by how much.
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
    # engine sub-account pnl (run_cell_portfolio face)
    ent = entry[[sym]]
    sc = L.exec_day_scale(weights, sym)
    with ExitPatch(L.EXIT_PATCH_OVERRIDES):
        res = run_backtest({sym: df}, dict(L.NEUTRALIZED_PARAMS),
                           entry_signal=ent, exit_signal=ent <= 0,
                           entry_size_scale=sc)
    eq = pd.Series(res["equity_curve"], index=df.index[:len(res["equity_curve"])])
    epnl = (eq - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
    # leg-C sub-account pnl
    sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
    w = weights[sym].reindex(df.index)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    cash, qty = L.CAPITAL, 0.0
    nav_vals = []; pending = None; bought_today = -1
    buys = []
    for i in range(len(df)):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                cash += qty * op * (1 - r); qty = 0.0; pending = None
            elif kind == "buy" and qty == 0:
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); bought_today = i; pending = None
                buys.append((str(df.index[i].date()), round(pw, 4), round(qty, 2)))
        if qty > 0:
            if not sig[i] and i > bought_today:
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
        first = d[d > 1.0].index[0]
        print(f"{sym}: max_sub_diff={mx:.2f} first_div={first.date()}  my_buys={buys}")
        # engine entry reconstruction: qty from trades
        for t in res["trades"]:
            print(f"    eng exit {t['date']} qty={t['qty']} hold={t['hold_days']}")
    else:
        print(f"{sym}: max_sub_diff={mx:.2f} OK")
