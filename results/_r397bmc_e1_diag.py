# -*- coding: utf-8 -*-
# r397 E1 Leg C divergence diagnostic: per-symbol trade-count reconciliation
# + first divergent return day with per-symbol position context.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
import lowamp_deep_p1 as L
from live.paper import build_panels, COST_X1_RATE

CELL, AXIS, FACE = "LAD-EDGE", "deep", "base"
ART = json.load(open(os.path.join(L.OUT_DIR, f"cont_{CELL}_{AXIS}_{FACE}.json"), encoding="utf-8"))
prices = L.load_axis(AXIS)
P = build_panels(prices)
close = P["close"]
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])
active = [c for c in entry.columns if entry[c].any()]
cen = L._exit_reason_census(AXIS, CELL, FACE)
print("engine census per_sym n_trades:", {s: v["n_trades"] for s, v in cen["per_sym"].items()})

idx = close.index
r = COST_X1_RATE
pnl = pd.Series(0.0, index=idx)
events = {}
for sym in active:
    df = prices[sym]
    sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
    w = weights[sym].reindex(df.index)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    cash, qty = L.CAPITAL, 0.0
    nav_vals = []; pending = None; bought_today = -1
    nb = ns = 0
    for i in range(len(df)):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                cash += qty * op * (1 - r); qty = 0.0; ns += 1
                events.setdefault((df.index[i].date().isoformat(), sym), []).append("SELL")
                pending = None
            elif kind == "buy" and qty == 0:
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); nb += 1
                events.setdefault((df.index[i].date().isoformat(), sym), []).append("BUY")
                bought_today = i; pending = None
        if qty > 0:
            if not sig[i] and i > bought_today:
                pending = ("sell", None)
        else:
            if sig[i]:
                pending = ("buy", float(w.iloc[i]))
        nav_vals.append(cash + qty * closes[i])
    nav_sym = pd.Series(nav_vals, index=df.index)
    p = (nav_sym - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
    pnl = pnl + p
    print(f"legC {sym}: buys={nb} sells={ns} engine_trades={cen['per_sym'][sym]['n_trades']}")
nav = pnl + L.CAPITAL
rets = nav.pct_change().dropna()
a_rets = ART["returns"]
c_rets = [round(float(v), 8) for v in rets.to_numpy()]
print("len a=%d c=%d" % (len(a_rets), len(c_rets)))
if len(a_rets) == len(c_rets):
    diffs = [(i, abs(a - b)) for i, (a, b) in enumerate(zip(a_rets, c_rets))]
    over = [d for d in diffs if d[1] > 5e-4]
    print("days over 5bp:", len(over))
    for i, d in over[:10]:
        dt = rets.index[i]
        print("--- divergent day %s (pos %d) diff %.6g" % (dt.date(), i, d))
        ctx = [( (dt - pd.Timedelta(days=k)).date(), events.get(((dt - pd.Timedelta(days=k)).date().isoformat(), s), []))
               for k in range(4, -5, -1)]
        for cdt, ev in ctx:
            flat = [f"{s}:{e}" for (dt2, s), evs in [] for e in []]  # placeholder
        # simpler: dump all events within +-4 calendar days
        for (d2, s), evs in sorted(events.items()):
            dd = pd.Timestamp(d2)
            if abs((dd - dt).days) <= 5:
                print("    ", d2, s, evs)
