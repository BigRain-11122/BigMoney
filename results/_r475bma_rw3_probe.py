# r475 bm-a: RW-3 probe -- recompute 6 registered members under explicit
# trade_pnl_mode="full" + strict_open_fills=True vs FROZEN anchors.
# Deterministic, zero network, zero backtest-batch (anchor-repro path only).
# Read-only on trader JSONs (prints the would-be new anchor values; the
# refreeze step consumes this JSON only after old-vs-new diff is recorded).
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from firm.hr import TRADERS_DIR, load_trader
from live import paper as lp
from live.paper import (OOS_START, SIGNAL_BUILDERS, ExitPatch, anchor_gate,
                        build_panels, evidence_cutoff)
from engine import run_backtest
from engine.metrics import sharpe

MEMBERS = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]
NEW_PARAMS = {"trade_pnl_mode": "full", "strict_open_fills": True}

out = {"probe": "rw3_member_recompute", "round": 475,
       "new_params": NEW_PARAMS, "members": {}}

prices_full = lp.load_core()

def seg_metrics(eq, start=None):
    seg = eq[eq.index >= start] if start else eq
    from engine.metrics import annual_return, max_drawdown
    return {"sharpe": round(float(sharpe(seg)), 4),
            "annual_return": round(float(annual_return(seg)), 4),
            "max_drawdown": round(float(max_drawdown(seg)), 4)}

for name in MEMBERS:
    t = load_trader(name)
    cutoff = evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    params.update(NEW_PARAMS)
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0),
                           dd_control=t.get("dd_control"),
                           evidence_cutoff=cutoff)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    n_trades = res["metrics"]["num_trades"]
    oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    got = {"in_sample": {**seg_metrics(eq[eq.index < OOS_START]),
                         "trades": n_trades - oos_trades},
           "out_sample": {**seg_metrics(eq, OOS_START), "trades": oos_trades}}
    want = t["backtest"]
    # JSON anchor face stores sharpe/max_dd/annual (engine metric names are
    # max_drawdown/annual_return) -- compare the true frozen key set.
    def _want(seg, k):
        v = want[seg].get(k)
        if v is None and k == "max_drawdown":
            v = want[seg].get("max_dd")
        if v is None and k == "annual_return":
            v = want[seg].get("annual")
        return v
    seg_keys = ("sharpe", "max_drawdown", "annual_return", "trades")
    moved = {seg: {k: (_want(seg, k), got[seg].get(k))
                   for k in seg_keys
                   if abs(float(_want(seg, k)) - float(got[seg].get(k))) > 1e-9}
             for seg in ("in_sample", "out_sample")}
    out["members"][name] = {
        "cutoff": cutoff, "got": got,
        "want": {seg: {k: _want(seg, k) for k in seg_keys}
                 for seg in ("in_sample", "out_sample")},
        "moved_fields": {s: m for s, m in moved.items() if m},
        "moved": bool(any(moved.values())),
    }
    m = out["members"][name]
    print(f"{name}: moved={m['moved']} "
          f"IS {want['in_sample']['sharpe']} -> {got['in_sample']['sharpe']} | "
          f"OOS {want['out_sample']['sharpe']} -> {got['out_sample']['sharpe']} "
          f"(trades {want['out_sample'].get('trades')} -> {got['out_sample']['trades']})")

n_moved = sum(1 for v in out["members"].values() if v["moved"])
print(f"moved members: {n_moved}/6")
out["n_moved"] = n_moved
with open("results/_r475bma_rw3_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("probe written: results/_r475bma_rw3_probe.json")
