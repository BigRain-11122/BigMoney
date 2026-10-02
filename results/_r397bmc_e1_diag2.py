# -*- coding: utf-8 -*-
# r397 E1 diag v2: for the two divergent symbols, dump my-sim event dates vs
# engine trade dates + one-word (sealed board) flags on fill bars.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
import lowamp_deep_p1 as L
from live.paper import build_panels, ExitPatch
from science_gates import CostPatch
from engine import run_backtest

CELL, AXIS, FACE = "LAD-EDGE", "deep", "base"
prices = L.load_axis(AXIS)
P = build_panels(prices)
close = P["close"]
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])

for sym in ("511010", "511260"):
    df = prices[sym]
    sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
    w = weights[sym].reindex(df.index)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    highs = df["high"].to_numpy(); lows = df["low"].to_numpy()
    cash, qty = L.CAPITAL, 0.0
    pending = None; bought_today = -1
    mine = []
    for i in range(len(df)):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                cash += qty * op * (1 - 0.0013041); qty = 0.0
                mine.append((str(df.index[i].date()), "SELL"))
                pending = None
            elif kind == "buy" and qty == 0:
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + 0.0013041)
                oneword = bool(op == highs[i] == lows[i] == closes[i])
                mine.append((str(df.index[i].date()), "BUY pw=%.4f oneword=%s" % (pw, oneword)))
                bought_today = i; pending = None
        if qty > 0:
            if not sig[i] and i > bought_today:
                pending = ("sell", None)
        else:
            if sig[i]:
                pending = ("buy", float(w.iloc[i]))
    ent = entry[[sym]]
    sc = L.exec_day_scale(weights, sym)
    with ExitPatch(L.EXIT_PATCH_OVERRIDES):
        res = run_backtest({sym: prices[sym]}, dict(L.NEUTRALIZED_PARAMS),
                           entry_signal=ent, exit_signal=ent <= 0,
                           entry_size_scale=sc)
    eng = [(str(pd.Timestamp(t["date"]).date()), t.get("reason", "?")) for t in res["trades"]]
    print(f"=== {sym} ===")
    print(" mine:", mine)
    print(" engine:", eng)
