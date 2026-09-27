"""r366 bm-b real-data probe: W2 intake registered-six recompute face.

Probes the exact cmd_intake registered-roster block (load_core ->
cutoff-truncate -> build_panels -> per-member SIGNAL_BUILDERS + ExitPatch
+ run_backtest -> pct_change daily returns) against real repo data so the
only un-probed intake face at judge-landing is the checkpoint-row join
(already shape-covered by selftest [16]). Zero writes, zero ledger.
"""
import sys, time
sys.path.insert(0, "scripts")
import trial_labor_w2 as w2
import trial_labor_w1 as tl1
import pandas as pd

t0 = time.time()
prices = tl1.load_core()
cut = pd.Timestamp(w2.CUTOFF)
pcut = {s: df[df.index <= cut] for s, df in prices.items()}
P = tl1.build_panels(pcut)
assert P["close"].index[-1] == cut, "cutoff tail drift"
reg_ret = {}
from live.paper import SIGNAL_BUILDERS
for t in tl1.A_TEMPLATES:
    trader = tl1.load_trader(t["trader_id"])
    entry = trader["params"]["entry"]
    sig = SIGNAL_BUILDERS[entry](P)
    params = {k: v for k, v in trader["params"].items() if k != "entry"}
    with tl1.ExitPatch(trader.get("exit_overrides")):
        res = tl1.run_backtest(pcut, params, entry_signal=sig,
                               exit_signal=(sig <= 0))
    eq = pd.Series(res["equity_curve"],
                   index=P["close"].index[:len(res["equity_curve"])])
    r = eq.pct_change().fillna(0.0)
    reg_ret[t["trader_id"]] = r
    print(f"{t['trader_id']}: n={len(r)} last={r.index[-1].date()} "
          f"finite={bool(r.notna().all())} std={r.std():.6f}")
n_members = len(reg_ret)
print(f"probe PASS: {n_members}/6 members, tail==cutoff, "
      f"elapsed {round(time.time() - t0, 1)}s")
