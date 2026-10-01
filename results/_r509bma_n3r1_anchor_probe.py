"""r509 bm-a N3-R1 anchor probe (read-only, zero ledger).

Question: does the t24_g2_pack member_run convention (full-panel run,
ExitPatch on member exit_overrides, params = member file params minus
entry) reproduce each registered member's recorded in_sample / out_sample
segment sharpe + trade counts at the 2026-09-22 evidence cutoff?

This is the prereg-freeze pre-flight: anchor convention facts only.
No ledger writes, no checkpoint writes, no member-file writes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import pandas as pd

from config import PATHS
from firm.hr import TRADERS_DIR
from live.paper import (OOS_START, SIGNAL_BUILDERS, ExitPatch,
                         build_panels, load_core)
from p3_portfolio import yearly_returns
from science_gates import recorded_lines

EVIDENCE_CUT = "2026-09-22"
OUT = os.path.join(PATHS.results_dir, "_r509bma_n3r1_anchor_probe.json")


def sharpe(series: pd.Series) -> float:
    ret = series.pct_change().dropna()
    if len(ret) < 2 or ret.std() == 0:
        return 0.0
    return float(ret.mean() / ret.std() * (252 ** 0.5))


def main() -> int:
    members = []
    for name in sorted(os.listdir(TRADERS_DIR)):
        if not name.endswith(".json") or name.startswith("PROS-") \
                or name.startswith("_"):
            continue
        with open(os.path.join(TRADERS_DIR, name), encoding="utf-8") as fh:
            members.append(json.load(fh))

    prices = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    prices = {s: df[df.index <= cut] for s, df in prices.items()}
    P = build_panels(prices)
    if str(P["close"].index[-1].date()) != EVIDENCE_CUT:
        print("HONEST ABORT: panel tail != cutoff")
        return 2

    rows = []
    for m in members:
        entry = SIGNAL_BUILDERS[m["params"]["entry"]](P)
        params = {k: v for k, v in m["params"].items() if k != "entry"}
        with ExitPatch(m.get("exit_overrides")):
            from engine import run_backtest
            res = run_backtest(prices, params, entry_signal=entry,
                               exit_signal=(entry <= 0),
                               dd_control=m.get("dd_control"))
        idx = P["close"].index
        eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
        full_s = sharpe(eq)
        oos = eq[eq.index >= OOS_START]
        ins = eq[eq.index < OOS_START]
        oos_s = sharpe(oos)
        ins_s = sharpe(ins)
        trades = res["trades"]
        n_in = sum(1 for t in trades if str(t["date"]) < OOS_START)
        n_oos = sum(1 for t in trades if str(t["date"]) >= OOS_START)
        rec = m["backtest"]
        rows.append({
            "id": m["id"],
            "entry": m["params"]["entry"],
            "recorded": {"in_s": rec["in_sample"]["sharpe"],
                         "in_trades": rec["in_sample"]["trades"],
                         "oos_s": rec["out_sample"]["sharpe"],
                         "oos_trades": rec["out_sample"]["trades"]},
            "reproduced": {"in_s": round(ins_s, 4), "n_in": n_in,
                           "oos_s": round(oos_s, 4), "n_oos": n_oos,
                           "full_s": round(full_s, 4),
                           "n_total": int(res["metrics"]["num_trades"])},
            "d_in_s": round(abs(ins_s - rec["in_sample"]["sharpe"]), 6),
            "d_oos_s": round(abs(oos_s - rec["out_sample"]["sharpe"]), 6),
            "trades_in_match": bool(n_in == rec["in_sample"]["trades"]),
            "trades_oos_match": bool(n_oos == rec["out_sample"]["trades"]),
            "yearly": {str(k): round(v, 4)
                       for k, v in yearly_returns(eq).items()},
        })
        r = rows[-1]
        print(f"{m['id']}: in {r['reproduced']['in_s']} vs "
              f"{r['recorded']['in_s']} (d={r['d_in_s']}, trades "
              f"{n_in} vs {r['recorded']['in_trades']}) | oos "
              f"{r['reproduced']['oos_s']} vs {r['recorded']['oos_s']} "
              f"(d={r['d_oos_s']}, trades {n_oos} vs "
              f"{r['recorded']['oos_trades']}) | full_s "
              f"{r['reproduced']['full_s']} n={r['reproduced']['n_total']}")

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"probe": "n3r1-anchor", "machine": "bm-a",
                   "cutoff": EVIDENCE_CUT, "rows": rows,
                   "rl": recorded_lines()},
                  fh, ensure_ascii=False, indent=1)
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
