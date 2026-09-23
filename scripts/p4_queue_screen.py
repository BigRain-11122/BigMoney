"""P-4 queue-batch: 5 remaining classic families, core48 mini screen.

PRE-REGISTERED (research/shortline/P4_QUEUE.md, written first). No tuning,
no re-run after results. Order: CEO O-20260923-2210 -> MSG-20260923-2212.

Fixed grid: 5 entries x 2 exit regimes = 10 cells, x(1x+x2) cost info.
Entries (constructions verbatim = strategies/ta.py, additive queue
functions): cci_revert / williams_reversal / nr7_breakout /
bb_squeeze_breakout / rsi_divergence (same-family discount vs
macd_divergence pre-registered).

Gates: recorded constants -- default i 0.3521, CE i = max(in-batch CE p95,
0.4474, 0.4229, 0.3521), vi 0.4004. Random n=50/regime, seed base 44_000
(40/41/42/43k used). Panel truncated at 2026-09-22 (calibration-era anchor;
raw end 09-23 disclosed). Hard gates: patch self-test + queue self-test
(5 fns binary/no-NaN/causal, passed 5/5 pre-commit) + 3 trader anchors.

Products: research/shortline/p4_queue_results.csv +
results/shortline_p4_queue.json. Ledger: prev from shortline_p4_folk.json
(2299) + 123 (10 cells x2 + 100 random + 3 anchors + 2 passive) = 2422.
"""
import csv
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from live.paper import (OOS_START, CostPatch, ExitPatch, _evidence_matches,
                        build_panels, load_core, seg_metrics,
                        self_test_patches)
from firm.hr import TRADERS_DIR, load_trader
from p2_null_calibration import passive_buyhold, passive_monthly_rebal
from p3_portfolio import member_run

import strategies.ta as ta

EVIDENCE_CUT = "2026-09-22"
N_RAND = 50
BASELINE_P = [0.02, 0.05]
SEED_BASE = 44_000
SLEEVE_MAX_CORR = 0.30
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
TRIALS_PRIOR = "shortline_g2_folk.json"   # chain head 2393 (G2 ran first)
PREREG_PREV = 2393
LEDGER_KEY = "shortline-p4-queue"

FAMILIES = {
    "cci_revert": (ta.cci_revert, "HLC"),
    "williams_reversal": (ta.williams_reversal, "HLC"),
    "nr7_breakout": (ta.nr7_breakout, "HLC"),
    "bb_squeeze_breakout": (ta.bb_squeeze_breakout, "HLC"),
    "rsi_divergence": (ta.rsi_divergence, "OHLC"),
}


def load_gate() -> dict:
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        return json.load(fh)["g1_prime_gate"]


def recorded_ce_nulls():
    with open(os.path.join(PATHS.results_dir, "new_signal_p1.json"),
              encoding="utf-8") as fh:
        nsp1 = float(json.load(fh)["gate"]["random_p95_inbatch_full"]["ce"])
    with open(os.path.join(PATHS.results_dir, "shortline_p4_batch1.json"),
              encoding="utf-8") as fh:
        b1 = float(json.load(fh)["gate"]["i_bar_ce_used"])
    return nsp1, b1


GATE = load_gate()
I_LINE_RECORDED = GATE["i_full_sharpe_gt"]
VI_BAR = GATE["vi_full_sharpe_gt"]
CE_NULL_NSP1, CE_LINE_BATCH1 = recorded_ce_nulls()


def queue_self_test() -> bool:
    rng = np.random.default_rng(44)
    n = 1200
    idx = pd.date_range("2022-01-03", periods=n)
    walk = rng.normal(0.0003, 0.013, n)
    for i in range(1, n):
        if i % 200 < 40:
            walk[i] -= 0.005
    close = pd.Series(1 + np.cumsum(walk), index=idx)
    open_ = close.shift(1) * (1 + rng.normal(0, 0.005, n))
    open_.iloc[0] = 1.0
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, n)))
    D = dict(O=open_, H=high, L=low, C=close)
    half = n // 2
    Ds = {k: v.iloc[:half] for k, v in D.items()}
    ok = True
    for name, (fn, keys) in FAMILIES.items():
        sig = fn(*[D[k] for k in keys])
        short = fn(*[Ds[k] for k in keys])
        binary = bool(set(pd.unique(sig.values)).issubset({0, 1}))
        no_nan = bool(not sig.isna().any())
        causal = bool((sig.iloc[:half].values == short.values).all())
        if not (binary and no_nan and causal):
            ok = False
            print(f"  QUEUE SELF-TEST FAIL {name}")
    return ok


def build_entries(P: dict):
    idx = P["close"].index
    syms = list(P["close"].columns)
    panels = dict(O=P["open"], H=P["high"], L=P["low"], C=P["close"],
                  V=P["volume"])
    E = []
    for name, (fn, keys) in FAMILIES.items():
        pos = pd.DataFrame({s: fn(*[panels[k][s] for k in keys])
                           for s in syms}).fillna(0)
        E.append((name, "s9_ta_queue", {}, (pos > 0), (pos <= 0),
                  f"ta.{fn.__name__} frozen"))
    return E


def run_cell(prices, idx, entry, exit_, params, ce, cost_mult=None):
    pp = dict(params or {})
    if ce:
        pp.update(CE_PARAMS)
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    xctx = ExitPatch(CE_OVERRIDES) if ce else nullcontext()
    with cctx, xctx:
        res = run_backtest(prices, pp, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_ts = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    return {"eq": eq, "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_ts}


def g1_clauses(full, oos, n_trades, i_bar, vi_bar):
    return {"i_beats_rand_p95": full["sharpe"] > i_bar,
            "ii_ann_pos": full["annual_return"] > GATE["ii_ann_gt"],
            "iii_dd_ok": full["max_drawdown"] >= GATE["iii_dd_min"],
            "iv_trades_ok": n_trades >= GATE["iv_trades_min"],
            "v_oos_ok": (oos["sharpe"] > GATE["v_oos_sharpe_gt"]
                         and oos["annual_return"] > GATE["v_oos_ann_gt"]),
            "vi_beats_passive": full["sharpe"] > vi_bar}


def _false_panel(idx, syms):
    return pd.DataFrame(False, index=idx, columns=syms)


def write_outputs(cells, randoms, passive_rows, anchors, survivors, sleeves,
                  bars, data_end, t0, void=False):
    p95_inbatch, passive_check, i_bar_ce = bars
    cols = ["name", "family", "exit_regime", "status", "n_trades",
            "oos_trades", "annual_return", "sharpe", "max_drawdown",
            "win_rate", "oos_sharpe", "oos_annual_return",
            "oos_max_drawdown", "i_bar", "vi_bar", "g1_pass", "sleeve_tag",
            "x2_full_sharpe", "x2_oos_sharpe", "max_corr", "note"]
    csv_path = os.path.join(PATHS.root, "research", "shortline",
                            "p4_queue_results.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in cells:
            w.writerow([c["name"], c["family"], c["exit_regime"], c["status"],
                        c["n_trades"], c["oos_trades"],
                        c["full"]["annual_return"], c["full"]["sharpe"],
                        c["full"]["max_drawdown"], c["full"].get("win_rate", ""),
                        c["oos"]["sharpe"], c["oos"]["annual_return"],
                        c["oos"]["max_drawdown"], c.get("i_bar", ""),
                        c.get("vi_bar", ""), c.get("g1_pass", ""),
                        c.get("sleeve_tag", ""), c.get("x2_full_sharpe", ""),
                        c.get("x2_oos_sharpe", ""), c.get("max_corr", ""),
                        c.get("note", "")])
        for r in randoms:
            w.writerow([r["name"], r["family"], r["exit_regime"], r["status"],
                        r["n_trades"], r["oos_trades"],
                        r["full"]["annual_return"], r["full"]["sharpe"],
                        r["full"]["max_drawdown"],
                        r["full"].get("win_rate", ""), r["oos"]["sharpe"],
                        r["oos"]["annual_return"], r["oos"]["max_drawdown"],
                        "", "", "", "", "", "", "",
                        f"p={r['p']} seed={r['seed']}"])
        for k, v in passive_rows.items():
            w.writerow([k, "passive_null", "none", "ok", 0, 0,
                        v["full"]["annual_return"], v["full"]["sharpe"],
                        v["full"]["max_drawdown"], "", v["oos"]["sharpe"],
                        v["oos"]["annual_return"], v["oos"]["max_drawdown"],
                        "", "", "", "", "", "", "J8 formula, consistency info"])
    print(f"saved: {csv_path}")

    with open(os.path.join(PATHS.results_dir, TRIALS_PRIOR),
              encoding="utf-8") as fh:
        prior_total = int(json.load(fh)["trials_ledger"]["total"])
    if prior_total != PREREG_PREV:
        print(f"WARNING: chain head drift -- prior_total {prior_total} "
              f"!= prereg {PREREG_PREV}; using chain head")
    n_runs = len(cells) * 2 + len(randoms) + len(anchors) + len(passive_rows)
    ledger = {"prev_total": prior_total, "batch_trials": n_runs,
              "note": f"{len(cells)} cells x(1x+x2) + {len(randoms)} random "
                      f"+ {len(anchors)} anchors + {len(passive_rows)} "
                      f"passive; prereg n=123 (P4_QUEUE.md s7)",
              "total": prior_total + n_runs}
    out = {
        "batch": LEDGER_KEY,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P4_QUEUE.md",
        "order_chain": ["O-20260923-2210 (CEO max-backtest order)",
                        "MSG-20260923-2212 claim"],
        "universe": {"pool": "core48-bare-codes", "data_end": data_end,
                     "evidence_cutoff": EVIDENCE_CUT, "oos_start": OOS_START},
        "void": void,
        "gate": {"recorded_constants": GATE,
                 "i_line_recorded": I_LINE_RECORDED,
                 "ce_null_recorded_nsp1": CE_NULL_NSP1,
                 "ce_line_recorded_batch1": CE_LINE_BATCH1,
                 "vi_bar_recorded": VI_BAR, "i_bar_ce_used": i_bar_ce,
                 "random_p95_inbatch_full": p95_inbatch,
                 "passive_consistency_check": passive_check,
                 "sleeve_max_corr": SLEEVE_MAX_CORR},
        "passive": passive_rows, "anchors": anchors,
        "cells": [{k: v for k, v in c.items() if k != "eq"} for c in cells],
        "survivors_g1_prime": survivors,
        "sleeve_candidates": sleeves,
        "verdict": {"void": void,
                    "n_survivors": len(survivors), "n_sleeves": len(sleeves),
                    "survivors_are": "G1' CANDIDATES ONLY -- no registration "
                                     "this batch"},
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs},
    }
    json_path = os.path.join(PATHS.results_dir, "shortline_p4_queue.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"runs={n_runs} elapsed={time.time()-t0:.0f}s "
          f"ledger N={ledger['total']}")
    return 0


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort")
        return 2
    print("patch self-tests: PASS")
    if not queue_self_test():
        print("queue self-test FAILED -- abort")
        return 2
    print("queue self-tests: PASS (5 functions)")

    prices_full = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    raw_end = max(df.index[-1] for df in prices_full.values())
    prices = prices_full
    if raw_end > cut:
        prices = {s: df.loc[:cut].copy() for s, df in prices_full.items()}
        print(f"panels truncated to {EVIDENCE_CUT} (raw {raw_end.date()})")
    P = build_panels(prices)
    idx, syms = P["close"].index, list(P["close"].columns)
    data_end = str(idx[-1].date())
    print(f"core48: {len(syms)} syms .. {data_end}")

    cells = []
    for (name, fam, params, entry, exit_, note) in build_entries(P):
        for ce in (False, True):
            tag = "ce" if ce else "default"
            try:
                r = run_cell(prices, idx, entry, exit_, params, ce)
                r2 = run_cell(prices, idx, entry, exit_, params, ce, cost_mult=2)
                cells.append({"name": name, "family": fam,
                              "exit_regime": tag, "status": "ok",
                              "params": params, "note": note, **r,
                              "x2_full_sharpe": r2["full"]["sharpe"],
                              "x2_oos_sharpe": r2["oos"]["sharpe"],
                              "x2_n_trades": r2["n_trades"]})
                print(f"  {name:<22} {tag} full_s={r['full']['sharpe']:>7.3f} "
                      f"oos_s={r['oos']['sharpe']:>7.3f} "
                      f"trades={r['n_trades']:<5} | x2={r2['full']['sharpe']:>7.3f}")
            except Exception as ex:
                cells.append({"name": name, "family": fam,
                              "exit_regime": tag,
                              "status": f"signal_error: {ex}",
                              "params": params, "note": note})
                print(f"  {name:<22} {tag} SIGNAL_ERROR {ex}")

    n_days, n_syms = len(idx), len(syms)
    randoms = []
    for ce in (False, True):
        tag = "ce" if ce else "default"
        for k in range(N_RAND):
            p = BASELINE_P[k // 25]
            seed = SEED_BASE + (k if not ce else N_RAND + k)
            rng = np.random.default_rng(seed)
            entry = pd.DataFrame(
                (rng.random((n_days, n_syms)) < p).astype(int),
                index=idx, columns=syms)
            r = run_cell(prices, idx, entry, _false_panel(idx, syms), {}, ce)
            randoms.append({"name": f"rand_{tag}_p{p}_s{k}",
                            "family": "random_baseline",
                            "exit_regime": tag, "status": "ok",
                            "p": p, "seed": seed, **r})

    from knowledge.rules import FeeSchedule
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)
    passive = {"ew48_buyhold": passive_buyhold(P["close"], cost_rate),
               "ew48_monthly_rebal": passive_monthly_rebal(P["close"],
                                                           cost_rate)}
    passive_rows = {k: {"full": seg_metrics(eq),
                        "oos": seg_metrics(eq, OOS_START)}
                    for k, eq in passive.items()}

    tids = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
            if not p.name.startswith("_")]
    anchors, trader_eq = {}, {}
    for tid in tids:
        r1 = member_run(load_trader(tid), prices_full, None)
        got_is = {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
                 "trades": r1["n_trades"] - r1["oos_trades"]}
        got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
        t = load_trader(tid)
        ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
              and _evidence_matches(got_oos, t["backtest"]["out_sample"]))
        anchors[tid] = {"anchor_ok": bool(ok), "got_is": got_is,
                        "got_oos": got_oos,
                        "full_sharpe": r1["full"]["sharpe"]}
        trader_eq[tid] = r1["eq"]
        print(f"  anchor {tid:<16} {'OK' if ok else 'BROKEN'}")
    if not all(a["anchor_ok"] for a in anchors.values()):
        print("ANCHOR BROKEN -- batch void")
        return write_outputs(cells, randoms, passive_rows, anchors,
                             None, None, (None, None, None), data_end, t0,
                             void=True)

    p95_inbatch = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in randoms
         if r["exit_regime"] == reg and r["status"] == "ok"], 95)), 4)
        for reg in ("default", "ce")}
    i_bar_ce = round(max(p95_inbatch["ce"], CE_LINE_BATCH1,
                         CE_NULL_NSP1, I_LINE_RECORDED), 4)
    print(f"p95 default={p95_inbatch['default']} ce={p95_inbatch['ce']} "
          f"-> CE i-line={i_bar_ce}")
    passive_check = {k: {"inbatch_full_sharpe": v["full"]["sharpe"],
                         "recorded_gate_vi": VI_BAR}
                     for k, v in passive_rows.items()}

    trader_rets = {tid: trader_eq[tid].pct_change().dropna() for tid in tids}
    for c in cells:
        if c["status"] != "ok":
            c["g1_pass"], c["sleeve_tag"] = False, False
            continue
        c["i_bar"] = i_bar_ce if c["exit_regime"] == "ce" else I_LINE_RECORDED
        c["vi_bar"] = VI_BAR
        c["clauses"] = g1_clauses(c["full"], c["oos"], c["n_trades"],
                                  c["i_bar"], c["vi_bar"])
        c["g1_pass"] = all(c["clauses"].values())
        rets = c["eq"].pct_change().dropna()
        c["corr_vs_traders"] = {tid: round(float(rets.corr(trader_rets[tid])), 4)
                                for tid in tids}
        c["max_corr"] = max(abs(v) for v in c["corr_vs_traders"].values())
        c["sleeve_tag"] = bool(
            not c["g1_pass"] and c["full"]["sharpe"] > 0
            and c["oos"]["sharpe"] > 0 and c["oos"]["annual_return"] > 0
            and c["n_trades"] >= GATE["iv_trades_min"]
            and c["max_corr"] < SLEEVE_MAX_CORR)

    survivors = [c["name"] + "@" + c["exit_regime"]
                 for c in cells if c.get("g1_pass")]
    sleeves = [c["name"] + "@" + c["exit_regime"]
               for c in cells if c.get("sleeve_tag")]
    print(f"\nG1' candidates: {survivors}")
    print(f"sleeve candidates: {sleeves}")
    return write_outputs(cells, randoms, passive_rows, anchors,
                         survivors, sleeves,
                         (p95_inbatch, passive_check, i_bar_ce),
                         data_end, t0, void=False)


if __name__ == "__main__":
    sys.exit(main())
