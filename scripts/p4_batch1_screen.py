"""P-4 batch 1: A-style-zoo A-layer easy families, core48 mini screen.

PRE-REGISTERED before running (research/shortline/P4_BATCH1.md, written
first). Do NOT tune thresholds or re-run after seeing results (p-hacking
ban, BACKTEST_PLAN iron rule 3).

Order chain: CEO O-20260923-1705 (style zoo) -> playbook s6 P-4 batch 1
-> claim MSG-20260923-1745 (bm-b, F-04 claim-at-start norm).

Fixed grid (no search): 4 entries x 2 exit regimes = 8 cells
  oversold_bounce_20_15  -- zoo #9, state: 20d ret < -15% & volume shrink
  low252_prox_top5_r20   -- zoo #12, 52wk-LOW proximity top5 frozen 20d
  amount_z_60_2          -- zoo #33, amount self z-score > 2 (state)
  vol_price_diverge_20_low -- zoo #34, factor verbatim, LONG pole =
                              most-negative diverge top5 frozen 20d
  (zoo #17 dca_filtered DROPPED pre-registered: engine-semantics
   degeneracy vs P1-screened xsec_mom rotations; true DCA = batch-3 #14)

Panels truncated to EVIDENCE_CUT (G2_NSP1 pattern): the batch judges
exactly the recorded evidence; later data growth can never break it.
member_run anchors self-truncate via trader evidence_cutoff (unchanged).

Gates (recorded-constants rule, J19 drift-proof pattern):
  default cells i-line = recorded 0.3521 (p2_calibration n=100);
  CE cells i-line = max(in-batch CE p95, NSP1-recorded CE null 0.4229,
                        0.3521) -- strictest defensible line, fixed here;
  vi-line = recorded 0.4004 (passive + 0.10, regime-free).
  In-batch: n=50 random per exit regime (p in {0.02,0.05} x 25, seeds
  41_000+k / 41_050+k -- fresh independent draw vs NSP1's 40_000 base)
  + passive EW48 re-computation (consistency info only).

G1' six clauses verbatim from p2_calibration.json g1_prime_gate.
Survivors = G1' CANDIDATES ONLY -- NO registration this batch (G2
deepening = separate pre-registration). Sleeve-tag informational
(!g1_pass & full>0 & OOS double positive & >=30 trades & max|corr| vs
the 3 registered traders' anchor equity daily returns < 0.30).

Hard gates (batch void if broken): patch self-test + 3 trader anchor
reproduction (_evidence_matches vs firm/traders registrations).

Products: research/shortline/p4_batch1_results.csv +
results/shortline_p4_batch1.json + doc s8. Trial ledger (engine-trial
research-line N): prev_total from shortline_p2_synth.json (1435) +
121 (8 cells x(1x+x2) + 100 random + 3 anchors + 2 passive) = 1556.
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

EVIDENCE_CUT = "2026-09-22"
N_RAND = 50                       # per exit regime (pre-registered)
BASELINE_P = [0.02, 0.05]         # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 41_000                 # fresh draw (NSP1 used 40_000)
SLEEVE_MAX_CORR = 0.30
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
TRIALS_PRIOR = "shortline_p2_synth.json"   # research-line N base (1435)
LEDGER_KEY = "shortline-p4-batch1-astyle-A-easy"


def load_gate() -> dict:
    """Recorded G1' constants (J19 drift-proof pattern, not in-batch)."""
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        return json.load(fh)["g1_prime_gate"]


def recorded_ce_null() -> float:
    """NSP1-recorded core48 CE null (first档, J19 drift-proof citation)."""
    with open(os.path.join(PATHS.results_dir, "new_signal_p1.json"),
              encoding="utf-8") as fh:
        return float(json.load(fh)["gate"]["random_p95_inbatch_full"]["ce"])


GATE = load_gate()
I_LINE_RECORDED = GATE["i_full_sharpe_gt"]      # 0.3521 (n=100 calibrated)
VI_BAR = GATE["vi_full_sharpe_gt"]              # 0.4004 (passive + 0.10)
CE_NULL_RECORDED = recorded_ce_null()           # 0.4229 (NSP1)


def _topk_frozen(score, top_k, rebal_days, ascending=False):
    """Top-k by score, membership frozen at non-overlapping rebal_days.
    NaN scores never rank in (low_vol_long rebal_days convention)."""
    ranks = score.rank(axis=1, ascending=ascending)
    in_set = ranks <= top_k
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def build_entries(P: dict):
    """Fixed 4-entry grid (zoo A-layer easy families, constructions
    verbatim from the pre-registration). Returns (name, family, params,
    entry_df, exit_df, note) tuples."""
    close, volume, amt = P["close"], P["volume"], P["amount"]
    idx, syms = close.index, list(close.columns)
    E = []

    def sym_panel(fn):
        pos = pd.DataFrame({s: fn(s) for s in syms}, index=idx).fillna(0)
        return (pos > 0), (pos <= 0)   # binarize: state signals may carry -1

    def add(name, family, params, entry, exit_, note=""):
        E.append((name, family, params, entry, exit_, note))

    # zoo #9: deep 20d drop + volume-shrink stabilization -> bounce entry
    deep = close.pct_change(20) < -0.15
    shrink = amt.rolling(5).mean() < 0.8 * amt.rolling(20).mean()
    state = (deep & shrink).fillna(False).astype(int)
    add("oversold_bounce_20_15", "zoo9_oversold", {}, state > 0, state <= 0,
        "20d<-15% & amt MA5<0.8*MA20, state semantics")

    # zoo #12: 52-week-LOW proximity (George-Hwang low mirror), top-5
    # ASCENDING (closest to low), frozen 20d membership
    rot = {"max_positions": 5, "position_size_pct": 0.19}
    score = close / close.rolling(252, min_periods=200).min()
    w = _topk_frozen(score, 5, 20, ascending=True)
    add("low252_prox_top5_r20", "zoo12_low_anchor", rot, w, (w <= 0),
        "close/min252 top5 ascending; frozen 20d")

    # zoo #33: amount self z-score spike (own-history normalization,
    # distinct from P1 turnover_surge_20_2 fixed 2xMA threshold)
    z = ((amt - amt.rolling(60).mean())
         / amt.rolling(60).std().replace(0, np.nan))
    state = (z > 2).fillna(False).astype(int)
    add("amount_z_60_2", "zoo33_amount_anomaly", {}, state > 0, state <= 0,
        "amount 60d z>2, state; same-intent variant of screened "
        "turnover_surge_20_2 (read with same-family discount)")

    # zoo #34: volume-price divergence, LONG pole = most-negative diverge
    # (price down + volume up = accumulation read); factor formula verbatim
    diverge = close.pct_change(20) - volume.pct_change(20)
    w = _topk_frozen(diverge, 5, 20, ascending=True)
    add("vol_price_diverge_20_low", "zoo34_vp_diverge", rot, w, (w <= 0),
        "factor verbatim close.pc20-vol.pc20, long pole top5 ascending")
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
                            "p4_batch1_results.csv")
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
        prior = json.load(fh)["trials_ledger"]
    prev_total = int(prior["total"]) if isinstance(prior, dict) else sum(
        x.get("n", 0) for x in prior)
    n_runs = len(cells) * 2 + len(randoms) + len(anchors) + len(passive_rows)
    ledger = {"prev_total": prev_total, "batch_trials": n_runs,
              "note": f"{len(cells)} cells x(1x+x2) + {len(randoms)} random "
                      f"+ {len(anchors)} trader anchors + "
                      f"{len(passive_rows)} passive; pre-registered n=121 "
                      f"(research/shortline/P4_BATCH1.md sec.7)",
              "total": prev_total + n_runs}
    verdict = {
        "void": void,
        "n_survivors": None if survivors is None else len(survivors),
        "n_sleeves": None if sleeves is None else len(sleeves),
        "survivors_are": "G1' CANDIDATES ONLY -- no registration this batch; "
                         "G2 deepening (neighborhood + cost + yearly) "
                         "requires a separate pre-registration",
        "fail_branch": None if (void or (survivors and len(survivors)))
        else "no G1' candidate this batch: honest verdict; NO threshold "
             "tuning, NO re-run (iron rule 3); zoo batch-1 A-layer easy "
             "line closes; batch 2 (M0923 migrations + lhb follow) "
             "material unaffected",
    }
    out = {
        "batch": LEDGER_KEY,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P4_BATCH1.md",
        "order_chain": ["O-20260923-1705 (CEO style zoo)",
                        "playbook s6 P-4 batch 1",
                        "MSG-20260923-1745 claim (bm-b)"],
        "universe": {"pool": "core48-bare-codes", "data_end": data_end,
                     "evidence_cutoff": EVIDENCE_CUT,
                     "oos_start": OOS_START},
        "void": void,
        "gate": {"recorded_constants": GATE,
                 "i_line_recorded": I_LINE_RECORDED,
                 "ce_null_recorded_nsp1": CE_NULL_RECORDED,
                 "vi_bar_recorded": VI_BAR,
                 "i_line_rule": "default cells: recorded 0.3521; CE cells: "
                                "max(in-batch CE p95, NSP1-recorded "
                                "0.4229, 0.3521)",
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
    json_path = os.path.join(PATHS.results_dir, "shortline_p4_batch1.json")
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

    # ---------- fixed grid: 4 entries x 2 regimes + x2 info ----------
    print("running 8 cells (4 entries x 2 exit regimes) + x2 info...")
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
    i_bar_ce = round(max(p95_inbatch["ce"], CE_NULL_RECORDED,
                         I_LINE_RECORDED), 4)
    print(f"\nin-batch random p95: default={p95_inbatch['default']} "
          f"(recorded gate line {I_LINE_RECORDED}), ce={p95_inbatch['ce']} "
          f"(recorded CE null {CE_NULL_RECORDED}) -> CE i-line={i_bar_ce}")
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
