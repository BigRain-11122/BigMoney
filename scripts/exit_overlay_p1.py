"""T-78 s3: EXIT-OVERLAY-P1 paired-judgment bench (6 carriers x 4 cells).

PRE-REGISTERED before running: research/EXIT_OVERLAY_P1.md (r240 frozen;
run-backfill of §7/§8 only, no criterion edits, no re-runs). Five trade-
management unlocks -> four cells via the P3/P2 convergence map (unlock
grid engine lives in the separate CN-GRID-SLEEVE prereg, §9).

Judgment face (frozen §4): per member x cell, cell WIN iff
d(full Sharpe) >= 0 AND d(OOS Sharpe) >= 0 AND not both exactly zero
(no-gain -> no wiring). Anchor hard gate: every carrier's OFF baseline
must reproduce its registered evidence via live.paper.anchor_gate
(|d| < 0.002 both segments) -- any BROKEN = batch VOID.

Overlay application = J15 canon: bridged fields (take_profit_levels /
trailing_stop_activate / trailing_lock) via params; non-bridged
(take_profit_fractions) via ExitPatch factory injection merged ON TOP of
the member's own exit_overrides; ov_dd_control = T-78 s2 additive ENGINE
flag (engine/backtester.py dd_control kwarg; None -> legacy byte-equal).

Costs: V1 legacy 13bp x1 primary; x2 stress on WINNER faces only
(descriptive, never a gate). T+1 / cost model / exit priority untouched.

Products: results/exit_overlay_p1.json + research/exit_overlay_p1_results.csv
+ gate_attrition.json one row. Trials ledger: batch_trials=30 frozen in §3
(6 anchors + 24 judgment cells); off-baselines + stress runs disclosed in
audit.n_backtests (engine honesty, not ledger-inflated).

Usage:
    python scripts/exit_overlay_p1.py selftest   # hermetic, no data/net
    python scripts/exit_overlay_p1.py run        # the batch (inline, <5min)
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
from engine import run_backtest
from live import paper as lp          # lib reuse: load_core/build_panels/
                                      # ExitPatch/SIGNAL_BUILDERS/anchor_gate/
                                      # seg_metrics/OOS_START (zero rewrite)
from science_gates import CostPatch, append_ledger, cutoff_meta

ANCHOR_TOL = 0.002                    # house standard (J14/J15, lp.ANCHOR_TOL)

CARRIERS = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
            "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]

# frozen cells (prereg §3 table; params-merge -> bridge wins, patch-merge
# stacks on member exit_overrides, engine_kw -> additive flags)
CELLS = {
    "ov_tp_ladder": {
        "params": {"take_profit_levels": (0.05, 0.08)},
        "patch": {"take_profit_fractions": (0.5, 0.5)},
        "engine_kw": {}, "unlocks": "1+5 (TP ladder = staged scale-out)"},
    "ov_trail_peak": {
        "params": {"trailing_stop_activate": 0.03, "trailing_lock": 0.05},
        "patch": {}, "engine_kw": {},
        "unlocks": "2 (trailing stop 3% activate / 5% peak lock)"},
    "ov_dd_control": {
        "params": {}, "patch": {},
        "engine_kw": {"dd_control": {"dd_trigger": -0.10,
                                     "de_risk_to": 0.50,
                                     "re_up_at": -0.05}},
        "unlocks": "3 (portfolio drawdown governor, entry-size face)"},
    "ov_full": {
        "params": {"take_profit_levels": (0.05, 0.08),
                   "trailing_stop_activate": 0.03, "trailing_lock": 0.05},
        "patch": {"take_profit_fractions": (0.5, 0.5)},
        "engine_kw": {"dd_control": {"dd_trigger": -0.10,
                                     "de_risk_to": 0.50,
                                     "re_up_at": -0.05}},
        "unlocks": "1+2+3+5 (CEO synthetic face)"},
    }


def win_verdict(d_full: float, d_oos: float) -> bool:
    """Frozen §4: dual-face non-hurt; both-exactly-zero = REJECT."""
    return bool(d_full >= 0.0 and d_oos >= 0.0
                and not (d_full == 0.0 and d_oos == 0.0))


def yearly_worst(equity: pd.Series) -> float:
    if equity is None or len(equity) == 0:
        return 0.0
    yearly = {}
    for year, seg in equity.groupby(equity.index.year):
        yearly[int(year)] = float(seg.iloc[-1] / seg.iloc[0] - 1)
    return round(min(yearly.values()), 4) if yearly else 0.0


def run_carrier(prices: dict, P: dict, t: dict, params_ov: dict | None,
                patch_ov: dict | None, engine_kw: dict | None):
    """One carrier run at the batch panel. Overlay = merge on member faces."""
    entry = lp.SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    if params_ov:
        params = {**params, **params_ov}
    patch = dict(t.get("exit_overrides") or {})
    if patch_ov:
        patch = {**patch, **patch_ov}
    kw = dict(engine_kw or {})
    with lp.ExitPatch(patch):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0), **kw)
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= lp.OOS_START)
    return {"full": lp.seg_metrics(eq), "oos": lp.seg_metrics(eq, lp.OOS_START),
            "n_trades": res["metrics"]["num_trades"],
            "oos_trades": oos_trades,
            "dd_control": {k: res["metrics"][k] for k in res["metrics"]
                           if k.startswith("dd_control_")} or None,
            "equity": eq}


# ---------------- selftest (hermetic: synthetic panels, zero repo data) --

def _synth(seed: int, drift: float, vol: float, n: int = 200):
    import numpy as np
    rs = np.random.RandomState(seed)
    px = 100.0 * (1 + rs.normal(drift, vol, n)).cumprod()
    dates = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame({"open": px, "high": px * 1.01, "low": px * 0.99,
                         "close": px,
                         "volume": abs(rs.normal(1e6, 1e5, n)),
                         "amount": abs(rs.normal(1e8, 1e7, n))}, index=dates)


def selftest() -> int:
    ok = True

    # [1/5] judgment math (frozen §4 faces)
    ok &= win_verdict(0.10, 0.0) is True       # non-neg both, some gain
    ok &= win_verdict(0.0, 0.05) is True
    ok &= win_verdict(0.10, -0.01) is False    # OOS hurt -> REJECT
    ok &= win_verdict(-0.01, 0.10) is False    # full hurt -> REJECT
    ok &= win_verdict(0.0, 0.0) is False       # zero-gain -> no wiring
    print("selftest [1/5] paired-judgment math: PASS" if ok else "FAIL")

    # [2/5] ExitPatch merge-on-member precedent + restore (patched name =
    # engine.backtester.ExitConfig -- the factory the engine consumes)
    import engine.backtester as _eb
    with lp.ExitPatch({"loss_time_days": 16, "take_profit_fractions": (0.5, 0.5)}):
        cfg = _eb.ExitConfig(take_profit_levels=(0.05, 0.08))
        ok &= cfg.loss_time_days == 16 and cfg.take_profit_fractions == (0.5, 0.5)
        ok &= cfg.take_profit_levels == (0.05, 0.08)   # bridge kwarg wins
    cfg = _eb.ExitConfig()
    ok &= cfg.loss_time_days == 8 and cfg.take_profit_fractions == (1 / 3, 1 / 3, 1.0)
    print(f"selftest [2/5] ExitPatch merge/precedence/restore: "
          f"{'PASS' if ok else 'FAIL'}")

    # [3/5] dd_control engine legs -- crash forcing fixture (production
    # run_backtest form, r157 mirror law; 90%-deployed continuous entry)
    ddc = {"dd_trigger": -0.05, "de_risk_to": 0.50, "re_up_at": -0.02}
    prices = {s: _synth(seed, -0.004, 0.02) for seed, s in
              enumerate(["111111", "222222", "333333"], start=5)}
    sig = pd.DataFrame(True, index=prices["111111"].index,
                       columns=list(prices))
    force = {"max_positions": 3, "position_size_pct": 0.30,
             "initial_stop": -0.95, "take_profit_levels": (5.0, 5.0),
             "time_decay_period": 9999}
    r = run_backtest(prices, force, entry_signal=sig, exit_signal=(sig <= 0),
                     dd_control=ddc)
    m = r["metrics"]
    ok &= m["dd_control_min_dd"] <= -0.05 and m["dd_control_days_de_risked"] > 0
    ok &= m["dd_control_scaled_entries"] > 0
    ok &= m["dd_control_state_end"] == "de_risked"
    # None path: no new keys, deterministic
    r0 = run_backtest(prices, force, entry_signal=sig, exit_signal=(sig <= 0))
    r0b = run_backtest(prices, force, entry_signal=sig, exit_signal=(sig <= 0))
    ok &= not any(k.startswith("dd_control_") for k in r0["metrics"])
    ok &= (json.dumps(r0["metrics"], sort_keys=True, default=str)
           == json.dumps(r0b["metrics"], sort_keys=True, default=str))
    print(f"selftest [3/5] dd_control crash fixture + None byte-face: "
          f"{'PASS' if ok else 'FAIL'}")

    # [4/5] dd_control validation guards
    guarded = True
    for bad in ({"dd_trigger": -0.05, "de_risk_to": 0.0, "re_up_at": -0.02},
                 {"dd_trigger": -0.02, "de_risk_to": 0.5, "re_up_at": -0.05},
                 {"dd_trigger": -0.05, "de_risk_to": 0.5, "re_up_at": 0.01}):
        try:
            run_backtest(prices, {}, entry_signal=sig, exit_signal=(sig <= 0),
                         dd_control=bad)
            guarded = False
        except ValueError:
            pass
    ok &= guarded
    print(f"selftest [4/5] dd_control config guards: "
          f"{'PASS' if guarded else 'FAIL'}")

    # [5/5] V-recovery hysteresis fixture
    import numpy as np
    rs = np.random.RandomState(11)
    leg1 = 100 * (1 + rs.normal(-0.006, 0.005, 100)).cumprod()
    leg2 = leg1[-1] * (1 + rs.normal(0.008, 0.003, 100)).cumprod()
    px = np.concatenate([leg1, leg2])
    vdf = pd.DataFrame({"open": px, "high": px * 1.005, "low": px * 0.995,
                        "close": px, "volume": np.full(200, 1e6),
                        "amount": np.full(200, 1e8)},
                       index=pd.bdate_range("2020-01-01", periods=200))
    vsig = pd.DataFrame(True, index=vdf.index, columns=["111111"])
    rv = run_backtest({"111111": vdf},
                      {"max_positions": 1, "position_size_pct": 0.90,
                       "initial_stop": -0.95, "take_profit_levels": (5.0, 5.0),
                       "time_decay_period": 9999},
                      entry_signal=vsig, exit_signal=(vsig <= 0), dd_control=ddc)
    mv = rv["metrics"]
    ok &= mv["dd_control_days_de_risked"] > 0 and mv["dd_control_state_end"] == "normal"
    print(f"selftest [5/5] V-recovery hysteresis: "
          f"{'PASS' if (mv['dd_control_days_de_risked'] > 0 and mv['dd_control_state_end'] == 'normal') else 'FAIL'}")

    if not ok:
        print("SELFTEST FAILED -- batch refused (fake-evidence guard)")
        return 2
    print("selftest: ALL LEGS PASS")
    return 0


# ------------------------------ the batch --------------------------------

def main() -> int:
    t0 = time.time()
    print("loading core48 panel (live.paper.load_core)...")
    prices_full = lp.load_core()
    P = lp.build_panels(prices_full)
    cutoff = str(P["close"].index[-1].date())
    print(f"  {len(prices_full)} ETFs, batch cutoff = {cutoff} "
          f"(latest complete bar)")

    # ---- anchor hard gate: registered-evidence reproduction (stored
    # cutoff, live.paper.anchor_gate = smoke canon, zero rewrite) ----
    anchors, anchor_ok = {}, True
    for tid in CARRIERS:
        with open(os.path.join(PATHS.root, "firm", "traders", f"{tid}.json"),
                  encoding="utf-8") as fh:
            t = json.load(fh)
        a = lp.anchor_gate(t, prices_full)
        anchors[tid] = {"ok": a.get("ok"), "cutoff": a.get("cutoff"),
                        "checks": a.get("checks"),
                        "error": a.get("error")}
        anchor_ok &= bool(a.get("ok"))
        print(f"  anchor {tid}: {'OK' if a.get('ok') else 'BROKEN ' + str(a.get('error'))}")
    print(f"anchor gate: {'6/6 OK' if anchor_ok else 'BROKEN -> batch VOID'}")
    if not anchor_ok:
        out = {"batch": "EXIT-OVERLAY-P1", "generated":
               time.strftime("%Y-%m-%d %H:%M:%S"),
               **cutoff_meta(cutoff), "anchor_ok": False,
               "anchors": anchors,
               "verdict": {"void": True,
                           "void_reason": "anchor reproduction failed (frozen §4 hard gate)"},
               "audit": {"elapsed_sec": round(time.time() - t0, 1)}}
        with open(os.path.join(PATHS.results_dir, "exit_overlay_p1.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
        print("VOID written; no judgment faces consumed the ledger")
        return 0

    n_runs = len(CARRIERS)          # anchors consumed (ledger-frozen 6)
    pairs, rows = {}, []
    for tid in CARRIERS:
        with open(os.path.join(PATHS.root, "firm", "traders", f"{tid}.json"),
                  encoding="utf-8") as fh:
            t = json.load(fh)
        off = run_carrier(prices_full, P, t, None, None, None)
        n_runs += 1                 # batch-cutoff OFF baseline (audit face)
        pairs[tid] = {"off": {k: off[k] for k in
                              ("full", "oos", "n_trades", "dd_control")},
                      "worst_year_off": yearly_worst(off["equity"]),
                      "off_equity_end": round(float(off["equity"].iloc[-1]), 2),
                      "cells": {}}
        for cname, spec in CELLS.items():
            cell = run_carrier(prices_full, P, t, spec["params"],
                                spec["patch"], spec["engine_kw"])
            n_runs += 1
            d_full = round(cell["full"]["sharpe"] - off["full"]["sharpe"], 4)
            d_oos = round(cell["oos"]["sharpe"] - off["oos"]["sharpe"], 4)
            win = win_verdict(d_full, d_oos)
            entry = {"full": cell["full"], "oos": cell["oos"],
                     "n_trades": cell["n_trades"],
                     "dd_control": cell["dd_control"],
                     "worst_year": yearly_worst(cell["equity"]),
                     "d_full": d_full, "d_oos": d_oos, "win": win,
                     "unlocks": spec["unlocks"]}
            pairs[tid]["cells"][cname] = entry
            rows.append({"member": tid, "cell": cname,
                         "full_off": off["full"]["sharpe"],
                         "full_cell": cell["full"]["sharpe"], "d_full": d_full,
                         "oos_off": off["oos"]["sharpe"],
                         "oos_cell": cell["oos"]["sharpe"], "d_oos": d_oos,
                         "ann_off": off["full"]["annual_return"],
                         "ann_cell": cell["full"]["annual_return"],
                         "d_ann": round(cell["full"]["annual_return"]
                                        - off["full"]["annual_return"], 4),
                         "dd_off": off["full"]["max_drawdown"],
                         "dd_cell": cell["full"]["max_drawdown"],
                         "d_dd": round(cell["full"]["max_drawdown"]
                                       - off["full"]["max_drawdown"], 4),
                         "trades_off": off["n_trades"],
                         "trades_cell": cell["n_trades"],
                         "worst_year_off": pairs[tid]["worst_year_off"],
                         "worst_year_cell": entry["worst_year"],
                         "win": win})
            print(f"  {tid:<16} {cname:<14} d_full={d_full:>7.4f} "
                  f"d_oos={d_oos:>7.4f} d_dd={rows[-1]['d_dd']:>7.4f} "
                  f"{'WIN' if win else 'REJECT'}")

    wins = [(tid, c) for tid in pairs for c, e in pairs[tid]["cells"].items()
            if e["win"]]

    # ---- winner-face x2 cost stress (descriptive, never a gate) ----
    stress = {}
    for tid, cname in wins:
        with open(os.path.join(PATHS.root, "firm", "traders", f"{tid}.json"),
                  encoding="utf-8") as fh:
            t = json.load(fh)
        spec = CELLS[cname]
        with CostPatch(2):
            r2 = run_carrier(prices_full, P, t, spec["params"], spec["patch"],
                             spec["engine_kw"])
        n_runs += 1
        stress[f"{tid}:{cname}"] = {
            "full_x2": r2["full"]["sharpe"], "oos_x2": r2["oos"]["sharpe"],
            "d_full_x2": round(r2["full"]["sharpe"]
                               - pairs[tid]["cells"][cname]["full"]["sharpe"], 4)}
        print(f"  stress {tid}:{cname} x2 full={r2['full']['sharpe']}")

    n_win, n_rej = len(wins), len(rows) - len(wins)
    verdict = {"void": False, "n_win": n_win, "n_reject": n_rej,
               "wins": [f"{a}:{b}" for a, b in wins],
               "note": "WIN = dual-face non-hurt (frozen §4); winners -> "
                       "s4 registration/wiring per §10, rejects -> §8 lessons"}

    # ---- products ----
    csv_path = os.path.join(PATHS.root, "research", "exit_overlay_p1_results.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"saved: {csv_path} ({len(rows)} rows)")

    ledger = append_ledger(
        "EXIT-OVERLAY-P1", 30, "results/exit_overlay_p1.json",
        note="T-78 s3 paired-judgment bench: 6 anchor repro + 24 overlay "
             "cells (N_eff=30 frozen §3); x2 stress + OFF baselines "
             "disclosed in audit only",
        evidence_cutoff=cutoff)
    out = {
        "batch": "EXIT-OVERLAY-P1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/EXIT_OVERLAY_P1.md (r240 frozen)",
        **cutoff_meta(cutoff),
        "universe": {"pool": "core48-bare-codes",
                     "n_syms": len(prices_full),
                     "history": (f"{P['close'].index[0].date()} .. "
                                 f"{P['close'].index[-1].date()}")},
        "oos_start": lp.OOS_START,
        "cells": CELLS,
        "anchor_ok": anchor_ok, "anchors": anchors,
        "pairs": pairs, "stress_x2": stress, "verdict": verdict,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)",
                  "ledger_n_eff": 30},
    }
    json_path = os.path.join(PATHS.results_dir, "exit_overlay_p1.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    # gate_attrition row (science_audit C4 face)
    ga_path = os.path.join(PATHS.results_dir, "gate_attrition.json")
    with open(ga_path, encoding="utf-8") as fh:
        ga = json.load(fh)
    ga["entries"].append({
        "batch": "EXIT-OVERLAY-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "retro_fill": False,
        "cells_ledger_delta": 30,
        "ledger_total_after": ledger["total"],
        "gates": {"anchor_repro_all": anchor_ok, "n_win": n_win,
                  "n_reject": n_rej, "void": False},
        "eliminated": None,
        "refs": {"results": "results/exit_overlay_p1.json",
                 "prereg": "research/EXIT_OVERLAY_P1.md"},
    })
    with open(ga_path, "w", encoding="utf-8") as fh:
        json.dump(ga, fh, indent=2, ensure_ascii=False)
    print(f"gate_attrition appended (ledger total -> {ledger['total']})")

    print(f"\n===== EXIT-OVERLAY-P1: {n_win} WIN / {n_rej} REJECT "
          f"(elapsed {time.time() - t0:.0f}s, {n_runs} engine runs) =====")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    if mode != "run":
        print(f"usage: {sys.argv[0]} [run|selftest] (got {mode!r})")
        sys.exit(2)
    sys.exit(main())
