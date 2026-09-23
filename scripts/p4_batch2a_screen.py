"""P-4 batch 2A: TA-classic/style families (A-layer migration), core48 mini screen.

PRE-REGISTERED before running (research/shortline/P4_BATCH2A.md, written
first). Do NOT tune thresholds or re-run after seeing results (p-hacking
ban, BACKTEST_PLAN iron rule 3).

Order chain: CEO O-20260923-1828 (TA/style strategy families, 3-15d)
-> digest DIGEST-20260923-ta-styles -> playbook s6 P-4 batch 2A (GM-session
lane) -> claim MSG-20260923-1841 (F-04 claim-at-start norm).

Fixed grid (no search): 8 entries x 2 exit regimes = 16 cells
  strong_close     -- zoo s1.2, M0923 StrongClose migration (late-day strength)
  macd_trend       -- M0923 MacdTrend (DIF>DEA & DIF>0, 12/26/9)
  kdj_reversal     -- M0923 KdjReversal (J<0 oversold above MA60)
  rsrs_timing      -- M0923 RsrsTiming (Everbright 2017, panel adaptation
                      pre-registered: per-symbol beta z-state, z_win 250)
  streak_up        -- M0923 Streak (3 consecutive up-days relay)
  vol_breakout     -- M0923 VolBreak (same-intent family vs P1-screened
                      breakout_confirm: read with pre-registered discount)
  hammer_reversal  -- NEW design (classic hammer candlestick + 5d drop)
  engulf_reversal  -- NEW design (bullish engulfing + 5d drop)
SINGLE SOURCE OF TRUTH: strategies/ta.py -- this script imports and applies
per-symbol (batch-1 sym_panel convention, pos>0 binarization). NO dual
implementation (F-05 lesson).

Panels truncated to EVIDENCE_CUT (G2_NSP1 pattern): the batch judges exactly
the recorded evidence; later data growth can never break it.

Gates (recorded-constants rule, J19 drift-proof pattern):
  default cells i-line = recorded 0.3521 (p2_calibration n=100);
  CE cells i-line = max(in-batch CE p95, batch-1-recorded CE line
                        (shortline_p4_batch1.json gate.i_bar_ce_used),
                        NSP1-recorded CE null 0.4229, 0.3521);
  vi-line = recorded 0.4004 (passive + 0.10, regime-free).
  In-batch: n=50 random per exit regime (p in {0.02,0.05} x 25, seeds
  42_000+k / 42_050+k -- fresh independent draw vs NSP1 40_000 and
  batch-1 41_000) + passive EW48 re-computation (consistency info only).

G1' six clauses verbatim from p2_calibration.json g1_prime_gate.
Survivors = G1' CANDIDATES ONLY -- NO registration this batch (G2
deepening = separate pre-registration). Sleeve-tag informational
(!g1_pass & full>0 & OOS double positive & >=30 trades & max|corr| vs
the 3 registered traders' anchor equity daily returns < 0.30).

Hard gates (batch void if broken): patch self-test + 3 trader anchor
reproduction + TA self-test (binary / no-NaN / causality on synthetic
series, NSP1 pre-run check paradigm).

Products: research/shortline/p4_batch2a_results.csv +
results/shortline_p4_batch2a.json + doc s8. Trial ledger (engine-trial
research-line N): prev_total from p5_random_entry.json (1883, r13 head)
+ 137 (16 cells x(1x+x2) + 100 random + 3 anchors + 2 passive) = 2020.
"""
import csv
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # p2/p3 imports

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
N_RAND = 50                       # per exit regime (pre-registered)
BASELINE_P = [0.02, 0.05]         # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 42_000                 # fresh draw (NSP1 40_000, batch1 41_000)
SLEEVE_MAX_CORR = 0.30
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
TRIALS_PRIOR = "p5_random_entry.json"        # chain head: 1883 (r13)
LEDGER_KEY = "shortline-p4-batch2a-ta-A-migration"


def load_gate() -> dict:
    """Recorded G1' constants (J19 drift-proof pattern, not in-batch)."""
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        return json.load(fh)["g1_prime_gate"]


def recorded_ce_nulls():
    """Recorded CE lines: NSP1 0.4229 + batch-1 used line (0.4474)."""
    with open(os.path.join(PATHS.results_dir, "new_signal_p1.json"),
              encoding="utf-8") as fh:
        nsp1 = float(json.load(fh)["gate"]["random_p95_inbatch_full"]["ce"])
    with open(os.path.join(PATHS.results_dir, "shortline_p4_batch1.json"),
              encoding="utf-8") as fh:
        b1 = float(json.load(fh)["gate"]["i_bar_ce_used"])
    return nsp1, b1


GATE = load_gate()
I_LINE_RECORDED = GATE["i_full_sharpe_gt"]      # 0.3521 (n=100 calibrated)
VI_BAR = GATE["vi_full_sharpe_gt"]              # 0.4004 (passive + 0.10)
CE_NULL_NSP1, CE_LINE_BATCH1 = recorded_ce_nulls()


def ta_self_test() -> bool:
    """Pre-run gate: 8 TA functions on synthetic series must be binary,
    NaN-free and causal (truncation prefix identity)."""
    rng = np.random.default_rng(42)
    n = 900
    idx = pd.date_range("2023-01-02", periods=n)
    close = pd.Series(1 + np.abs(np.cumsum(rng.normal(0, 0.01, n))), index=idx)
    open_ = close * (1 + rng.normal(0, 0.005, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, n)))
    vol = pd.Series(rng.lognormal(10, .4, n), index=idx)
    half = n // 2
    ctx = {k: v.iloc[:half] for k, v in
           dict(O=open_, H=high, L=low, C=close, V=vol).items()}
    fns = {
        "strong_close": lambda d: ta.strong_close(d["H"], d["L"], d["C"], d["V"]),
        "macd_trend": lambda d: ta.macd_trend(d["C"]),
        "kdj_reversal": lambda d: ta.kdj_reversal(d["H"], d["L"], d["C"]),
        "rsrs_timing": lambda d: ta.rsrs_timing(d["H"], d["L"]),
        "streak_up": lambda d: ta.streak_up(d["C"]),
        "vol_breakout": lambda d: ta.vol_breakout(d["H"], d["L"], d["C"], d["V"]),
        "hammer_reversal": lambda d: ta.hammer_reversal(d["O"], d["H"], d["L"], d["C"]),
        "engulf_reversal": lambda d: ta.engulf_reversal(d["O"], d["C"]),
    }
    full = dict(O=open_, H=high, L=low, C=close, V=vol)
    ok = True
    for name, fn in fns.items():
        sig = fn(full)
        short = fn(ctx)
        binary = bool(set(pd.unique(sig.values)).issubset({0, 1}))
        no_nan = bool(not sig.isna().any())
        causal = bool((sig.iloc[:half].values == short.values).all())
        if not (binary and no_nan and causal):
            ok = False
            print(f"  TA SELF-TEST FAIL {name}: binary={binary} "
                  f"no_nan={no_nan} causal={causal}")
    return ok


def _apply_sym(fn, panels, syms):
    """Batch-1 sym_panel convention: per-symbol Series -> pos DataFrame,
    (pos>0) binarization (J7 pitfall compliance)."""
    pos = pd.DataFrame({s: fn({k: v[s] for k, v in panels.items()})
                       for s in syms})
    pos = pos.fillna(0)
    return (pos > 0), (pos <= 0)


def build_entries(P: dict):
    """Fixed 8-entry grid (constructions verbatim = strategies/ta.py frozen
    params, P4_BATCH2A s3). Returns (name, family, params, entry, exit,
    note) tuples."""
    idx = P["close"].index
    syms = list(P["close"].columns)
    O, H, L, C, V = P["open"], P["high"], P["low"], P["close"], P["volume"]
    E = []

    def add(name, family, fn, needs, note=""):
        panels = {k: v for k, v in
                  dict(O=O, H=H, L=L, C=C, V=V).items() if k in needs}
        entry, exit_ = _apply_sym(fn, panels, syms)
        E.append((name, family, {}, entry, exit_, note))

    add("strong_close", "ta_strong_close",
        lambda d: ta.strong_close(d["H"], d["L"], d["C"], d["V"]),
        "HLCV", "M0923 StrongClose frozen 0.85/1.5/20, state")
    add("macd_trend", "ta_macd_trend",
        lambda d: ta.macd_trend(d["C"]), "C",
        "M0923 MacdTrend 12/26/9 condition-state, zero-line confirm")
    add("kdj_reversal", "ta_kdj_reversal",
        lambda d: ta.kdj_reversal(d["H"], d["L"], d["C"]), "HLC",
        "M0923 KdjReversal 9/0/80/60, J oversold above MA60")
    add("rsrs_timing", "ta_rsrs_timing",
        lambda d: ta.rsrs_timing(d["H"], d["L"]), "HL",
        "Everbright RSRS 18/250/0.8/-0.8, panel adaptation pre-reg")
    add("streak_up", "ta_streak_up",
        lambda d: ta.streak_up(d["C"]), "C",
        "M0923 Streak 3-day up relay")
    add("vol_breakout", "ta_vol_breakout",
        lambda d: ta.vol_breakout(d["H"], d["L"], d["C"], d["V"]), "HLCV",
        "M0923 VolBreak 20/1.5/20/10, same-family discount vs P1 "
        "breakout_confirm (pre-reg s2)")
    add("hammer_reversal", "ta_hammer_reversal",
        lambda d: ta.hammer_reversal(d["O"], d["H"], d["L"], d["C"]), "OHLC",
        "NEW: classic hammer + 5d drop>=5%, exit reclaim MA20")
    add("engulf_reversal", "ta_engulf_reversal",
        lambda d: ta.engulf_reversal(d["O"], d["C"]), "OC",
        "NEW: bullish engulfing + 5d drop>=5%, exit reclaim MA20")
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
                            "p4_batch2a_results.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in cells:
            w.writerow([
                c["name"], c["family"], c["exit_regime"], c["status"],
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
    if prior_total != 1883:
        print(f"WARNING: chain head drift -- prior_total {prior_total} "
              f"!= prereg 1883; using chain head (honest count)")
    n_runs = len(cells) * 2 + len(randoms) + len(anchors) + len(passive_rows)
    ledger = {"prev_total": prior_total, "batch_trials": n_runs,
              "note": f"{len(cells)} cells x(1x+x2) + {len(randoms)} random "
                      f"+ {len(anchors)} trader anchors + "
                      f"{len(passive_rows)} passive; pre-registered n=137 "
                      f"(research/shortline/P4_BATCH2A.md sec.7); "
                      f"prereg prev=1883 (p5 chain head)",
              "total": prior_total + n_runs}
    verdict = {
        "void": void,
        "n_survivors": None if survivors is None else len(survivors),
        "n_sleeves": None if sleeves is None else len(sleeves),
        "survivors_are": "G1' CANDIDATES ONLY -- no registration this batch; "
                         "G2 deepening (neighborhood + cost + yearly) "
                         "requires a separate pre-registration",
        "fail_branch": None if (void or (survivors and len(survivors)))
        else "no G1' candidate this batch: honest verdict; NO threshold "
             "tuning, NO re-run (iron rule 3); zoo s11 TA batch-2A line "
             "closes; queued families (#48 CCI/morning-star/squeeze) "
             "material unaffected",
    }
    out = {
        "batch": LEDGER_KEY,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P4_BATCH2A.md",
        "order_chain": ["O-20260923-1828 (CEO TA/style families)",
                        "digest DIGEST-20260923-ta-styles",
                        "playbook s6 P-4 batch 2A (GM lane)",
                        "MSG-20260923-1841 claim (quant-GM session)"],
        "universe": {"pool": "core48-bare-codes", "data_end": data_end,
                     "evidence_cutoff": EVIDENCE_CUT,
                     "oos_start": OOS_START},
        "void": void,
        "gate": {"recorded_constants": GATE,
                 "i_line_recorded": I_LINE_RECORDED,
                 "ce_null_recorded_nsp1": CE_NULL_NSP1,
                 "ce_line_recorded_batch1": CE_LINE_BATCH1,
                 "vi_bar_recorded": VI_BAR,
                 "i_line_rule": "default cells: recorded 0.3521; CE cells: "
                                "max(in-batch CE p95, batch1-recorded CE "
                                "line, NSP1-recorded 0.4229, 0.3521)",
                 "i_bar_ce_used": i_bar_ce,
                 "random_p95_inbatch_full": p95_inbatch,
                 "passive_consistency_check": passive_check,
                 "sleeve_max_corr": SLEEVE_MAX_CORR},
        "passive": passive_rows,
        "anchors": anchors,
        "cells": [{k: v for k, v in c.items() if k != "eq"} for c in cells],
        "survivors_g1_prime": survivors,
        "sleeve_candidates": sleeves,
        "verdict": verdict,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "shortline_p4_batch2a.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"runs={n_runs} elapsed={time.time()-t0:.0f}s "
          f"ledger N={ledger['total']}")
    return 0


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    print("patch self-tests: PASS")
    if not ta_self_test():
        print("TA self-test FAILED -- abort (look-ahead/binary guard)")
        return 2
    print("TA self-tests: PASS (8 functions, binary/no-NaN/causal)")

    prices_full = load_core()
    cut = pd.Timestamp(EVIDENCE_CUT)
    raw_end = max(df.index[-1] for df in prices_full.values())
    prices = prices_full
    if raw_end > cut:
        prices = {s: df.loc[:cut].copy() for s, df in prices_full.items()}
        print(f"panels truncated to evidence cut {EVIDENCE_CUT} "
              f"(raw end {raw_end.date()})")
    P = build_panels(prices)
    idx, syms = P["close"].index, list(P["close"].columns)
    data_end = str(idx[-1].date())
    print(f"core48: {len(syms)} syms, window {idx[0].date()} .. {data_end}")

    # ---------- fixed grid: 8 entries x 2 regimes + x2 info ----------
    print("running 16 cells (8 entries x 2 exit regimes) + x2 info...")
    cells = []
    for (name, fam, params, entry, exit_, note) in build_entries(P):
        for ce in (False, True):
            tag = "ce" if ce else "default"
            try:
                r = run_cell(prices, idx, entry, exit_, params, ce)
                r2 = run_cell(prices, idx, entry, exit_, params, ce,
                              cost_mult=2)
                cells.append({"name": name, "family": fam,
                              "exit_regime": tag, "status": "ok",
                              "params": params, "note": note, **r,
                              "x2_full_sharpe": r2["full"]["sharpe"],
                              "x2_oos_sharpe": r2["oos"]["sharpe"],
                              "x2_n_trades": r2["n_trades"]})
                print(f"  {name:<24} {'CE ' if ce else 'def'} "
                      f"full_s={r['full']['sharpe']:>7.3f} "
                      f"oos_s={r['oos']['sharpe']:>7.3f} "
                      f"trades={r['n_trades']:<5} "
                      f"| x2 full_s={r2['full']['sharpe']:>7.3f}")
            except Exception as ex:
                cells.append({"name": name, "family": fam,
                              "exit_regime": tag,
                              "status": f"signal_error: {ex}",
                              "params": params, "note": note})
                print(f"  {name:<24} {tag} SIGNAL_ERROR {ex}")

    # ---------- random baselines: n=50 per exit regime ----------
    n_days, n_syms = len(idx), len(syms)
    randoms = []
    for ce in (False, True):
        tag = "ce" if ce else "default"
        print(f"running 50 random baselines (exit regime={tag})...")
        for k in range(N_RAND):
            p = BASELINE_P[k // 25]
            seed = SEED_BASE + (k if not ce else N_RAND + k)
            rng = np.random.default_rng(seed)
            entry = pd.DataFrame(
                (rng.random((n_days, n_syms)) < p).astype(int),
                index=idx, columns=syms)
            r = run_cell(prices, idx, entry, _false_panel(idx, syms), {}, ce)
            randoms.append({"name": f"rand_{tag}_p{p}_s{k}", "family":
                            "random_baseline", "exit_regime": tag,
                            "status": "ok", "p": p, "seed": seed, **r})
        print(f"  regime {tag}: 50 done")

    # ---------- passive nulls (J8 formulas, consistency info only) ------
    from knowledge.rules import FeeSchedule
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)
    closes = P["close"]
    passive = {"ew48_buyhold": passive_buyhold(closes, cost_rate),
               "ew48_monthly_rebal": passive_monthly_rebal(closes, cost_rate)}
    passive_rows = {}
    for k, eq in passive.items():
        passive_rows[k] = {"full": seg_metrics(eq),
                           "oos": seg_metrics(eq, OOS_START)}
        print(f"  {k:<20} full_s={passive_rows[k]['full']['sharpe']:>7.3f} "
              f"oos_s={passive_rows[k]['oos']['sharpe']:>7.3f}")

    # ---------- trader anchors (hard gate + sleeve correlation ref) ------
    tids = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
            if not p.name.startswith("_")]
    traders = {tid: load_trader(tid) for tid in tids}
    print(f"anchor runs for {tids}...")
    anchors, trader_eq = {}, {}
    for tid in tids:
        r1 = member_run(traders[tid], prices_full, None)
        got_is = {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
                  "trades": r1["n_trades"] - r1["oos_trades"]}
        got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
        t = traders[tid]
        ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
              and _evidence_matches(got_oos, t["backtest"]["out_sample"]))
        anchors[tid] = {"anchor_ok": bool(ok), "got_is": got_is,
                        "got_oos": got_oos,
                        "full_sharpe": r1["full"]["sharpe"]}
        trader_eq[tid] = r1["eq"]
        print(f"  {tid:<16} full_s={r1['full']['sharpe']:>7.4f} "
              f"anchor={'OK' if ok else 'BROKEN'}")
    if not all(a["anchor_ok"] for a in anchors.values()):
        print("ANCHOR BROKEN -- batch void, no verdicts")
        return write_outputs(cells, randoms, passive_rows, anchors,
                             None, None, (None, None, None), data_end, t0,
                             void=True)

    # ---------- nulls + gates (recorded constants rule) ----------
    p95_inbatch = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in randoms
         if r["exit_regime"] == reg and r["status"] == "ok"], 95)), 4)
        for reg in ("default", "ce")}
    i_bar_ce = round(max(p95_inbatch["ce"], CE_LINE_BATCH1,
                         CE_NULL_NSP1, I_LINE_RECORDED), 4)
    print(f"\nin-batch random p95: default={p95_inbatch['default']} "
          f"(recorded gate line {I_LINE_RECORDED}), ce={p95_inbatch['ce']} "
          f"(recorded CE lines {CE_LINE_BATCH1}/{CE_NULL_NSP1}) "
          f"-> CE i-line={i_bar_ce}")
    print(f"vi_bar (recorded, regime-free): {VI_BAR}")
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
        c["corr_vs_traders"] = {tid: round(float(
            rets.corr(trader_rets[tid])), 4) for tid in tids}
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
    print(f"\n===== G1' candidates ({len(survivors)}): {survivors}")
    print(f"===== sleeve candidates ({len(sleeves)}): {sleeves}")

    return write_outputs(cells, randoms, passive_rows, anchors,
                         survivors, sleeves,
                         (p95_inbatch, passive_check, i_bar_ce),
                         data_end, t0, void=False)


if __name__ == "__main__":
    sys.exit(main())
