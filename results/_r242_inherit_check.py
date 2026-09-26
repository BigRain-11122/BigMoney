"""r242 T-78 s4 inheritance check (bm-b).

Three faces:
1. batch-caliber parity -- registration-as-wired run at the batch panel
   (cutoff 2026-09-24) must reproduce the judged cell's stored full/oos
   sharpe (wiring == judged config, zero drift);
2. dd_control flag flows through the AGGR sleeve consumer
   (t28_stable_profit._sleeve_worker) -- metric keys present;
3. sleeve equity path == batch path for COMPOSITE-CE-02.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
from live import paper as lp
from firm.hr import load_trader
from t28_stable_profit import _sleeve_worker

BATCH_CUTOFF = "2026-09-24"
WIRE = {"COMPOSITE-CE-01": "ov_tp_ladder",
        "COMPOSITE-CE-02": "ov_full",
        "ENGULF-CE-01": "ov_full"}


def run_at(t, prices_full, cutoff):
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = lp.build_panels(prices)
    entry = lp.SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with lp.ExitPatch(t.get("exit_overrides")):
        res = lp.run_backtest(prices, params, entry_signal=entry,
                              exit_signal=(entry <= 0),
                              dd_control=t.get("dd_control"))
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    return {"full": lp.seg_metrics(eq), "oos": lp.seg_metrics(eq, lp.OOS_START),
            "metrics": res["metrics"], "eq": eq}


def main() -> int:
    with open(os.path.join(ROOT, "results", "exit_overlay_p1.json"),
              encoding="utf-8-sig") as fh:
        batch = json.load(fh)
    prices_full = lp.load_core()
    ok = True

    for tid, cname in WIRE.items():
        t = load_trader(tid)
        r = run_at(t, prices_full, BATCH_CUTOFF)
        want = batch["pairs"][tid]["cells"][cname]
        d_full = abs(r["full"]["sharpe"] - want["full"]["sharpe"])
        d_oos = abs(r["oos"]["sharpe"] - want["oos"]["sharpe"])
        line = (f"PARITY {tid} <- {cname}: got full={r['full']['sharpe']} "
                f"oos={r['oos']['sharpe']} | judged full={want['full']['sharpe']} "
                f"oos={want['oos']['sharpe']} | d_full={d_full:.4f} "
                f"d_oos={d_oos:.4f}")
        print(line)
        ok &= d_full < 0.002 and d_oos < 0.002

    # dd_control flows through the AGGR sleeve consumer
    t = load_trader("COMPOSITE-CE-02")
    sl = _sleeve_worker("COMPOSITE-CE-02", None, prices_full,
                        pd.Timestamp(BATCH_CUTOFF))
    dd_on = run_at(t, prices_full, BATCH_CUTOFF)["metrics"]
    has_ddc = any(k.startswith("dd_control_") for k in dd_on)
    print(f"AGGR-SLEEVE COMPOSITE-CE-02: worker eq_days={len(sl['eq'])} "
          f"n_trades={sl['n_trades']} | registration engine dd_control "
          f"keys present={has_ddc}")
    ok &= has_ddc
    ok &= len(sl["eq"]) > 0

    # sleeve equity path == batch path
    r = run_at(t, prices_full, BATCH_CUTOFF)
    sleeve_tail = round(sl["eq"][-1], 6)
    batch_tail = round(float(r["eq"].iloc[-1]), 6)
    print(f"AGGR-SLEEVE eq parity: sleeve_tail={sleeve_tail} "
          f"batch_tail={batch_tail} equal={sleeve_tail == batch_tail}")
    ok &= sleeve_tail == batch_tail

    print("INHERIT-CHECK " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
