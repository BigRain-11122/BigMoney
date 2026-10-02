# -*- coding: utf-8 -*-
# r397 E1 diag v3: dump full engine trade records (entry dates/sizes) for the
# two suspect symbols + all 6 divergent return days.
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
ART = json.load(open(os.path.join(L.OUT_DIR, f"cont_{CELL}_{AXIS}_{FACE}.json"), encoding="utf-8"))
prices = L.load_axis(AXIS)
P = build_panels(prices)
close = P["close"]
spec = L.CELLS[CELL]
entry, weights, _ = L.build_signal(close, P["volume"], P["amount"], spec["W"], spec["N"], spec["sizing"])
active = [c for c in entry.columns if entry[c].any()]

for sym in ("511010", "511260"):
    ent = entry[[sym]]
    sc = L.exec_day_scale(weights, sym)
    with ExitPatch(L.EXIT_PATCH_OVERRIDES):
        res = run_backtest({sym: prices[sym]}, dict(L.NEUTRALIZED_PARAMS),
                           entry_signal=ent, exit_signal=ent <= 0,
                           entry_size_scale=sc)
    print(f"=== {sym} engine trades full ===")
    for t in res["trades"]:
        print("  ", json.dumps(t, default=str)[:400])
    print(f"    equity_curve last={res['equity_curve'][-1]:.2f} n={len(res['equity_curve'])}")
    # scale series non-NaN days
    scn = sc.dropna()
    print("    scale days:", [(str(pd.Timestamp(d).date()), round(v, 4)) for d, v in scn.items()][:12], "...")

# all divergent days
idx = close.index
r = COST_X1_RATE
pnl = pd.Series(0.0, index=idx)
for sym in active:
    df = prices[sym]
    sig = entry[sym].reindex(df.index).fillna(False).to_numpy(dtype=bool)
    w = weights[sym].reindex(df.index)
    opens = df["open"].to_numpy(); closes = df["close"].to_numpy()
    cash, qty = L.CAPITAL, 0.0
    nav_vals = []; pending = None; bought_today = -1
    for i in range(len(df)):
        op = opens[i]
        if pending is not None:
            kind, pw = pending
            if kind == "sell" and qty > 0 and i > bought_today:
                cash += qty * op * (1 - r); qty = 0.0; pending = None
            elif kind == "buy" and qty == 0:
                budget = L.CAPITAL * pw; qty = budget / op
                cash -= budget * (1 + r); bought_today = i; pending = None
        if qty > 0:
            if not sig[i] and i > bought_today:
                pending = ("sell", None)
        else:
            if sig[i]:
                pending = ("buy", float(w.iloc[i]))
        nav_vals.append(cash + qty * closes[i])
    nav_sym = pd.Series(nav_vals, index=df.index)
    pnl = pnl + (nav_sym - L.CAPITAL).reindex(idx).ffill().fillna(0.0)
nav = pnl + L.CAPITAL
rets = nav.pct_change().dropna()
a_rets = ART["returns"]
c_rets = [round(float(v), 8) for v in rets.to_numpy()]
over = [(i, abs(a - b)) for i, (a, b) in enumerate(zip(a_rets, c_rets)) if abs(a - b) > 5e-4]
print("=== divergent days ===")
for i, d in over:
    print("  %s (pos %d) diff %.8g  a=%.8f c=%.8f" % (rets.index[i].date(), i, d, a_rets[i], c_rets[i]))
