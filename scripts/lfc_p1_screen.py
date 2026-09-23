"""LFC low-frequency low-cost instrument family -- P1 mini screen.

PRE-REGISTERED before running (research/LFC_P1_SCREEN.md, incl. sec.1.5
amendment, written first). Do NOT tune thresholds or re-run after seeing
results (p-hacking ban, BACKTEST_PLAN iron rule 3).

Question (J19 6.5-2 / P3 diversification engine): on the low-frequency
low-cost pool (3 CGB bond ETFs + 2 gold ETFs, core48-maintained bare
files, zero pipeline change), can the existing signal families x the
existing exit machinery (default engine rules AND the registered CE
softening) produce (a) a G1' survivor or (b) a low-correlation
diversification sleeve candidate?

Fixed grid (no search): 10 entries x 2 exit regimes = 20 cells
  A low_vol(60/120, k=1/2) daily, sizing 0.10 x k (registered convention)
  B composite top_n(1/2) x rebal(20/40), sizing 0.95/n (P1 convention)
  C ts-trend: tsmom_200, donchian_55_20, engine-default sizing
Exit regimes: default | CE (registered contract: bridge params
  time_decay 25d/5% + trailing 0.10 + ExitPatch loss_time_days=16).

Nulls (pool-local, never borrowed cross-pool):
  random entry n=50 PER exit regime (p in {0.02,0.05} x 25 seeds,
  rng=default_rng(30_000+k), exits=engine rules of that regime)
  passive EW5 buy&hold + EW5 monthly rebal (J8 formulas verbatim).

G1' six clauses exactly as J8 sec.3, pool-localized: i beats same-regime
random p95; ii ann>0; iii dd>=-35%; iv trades>=30; v OOS double positive;
vi full sharpe > passive EW5 buy&hold full + 0.10. CE cells use the CE
random p95 as their i-line (honest null per regime). Sleeve-tag
(informational, NO registration): !g1_pass AND full>0 AND OOS double
positive AND trades>=30 AND max|corr| vs the 3 registered traders'
anchor equity daily returns < 0.30 (full window).

Hard gates (batch void if broken): patch self-test + 3 trader 1x
anchor reproduction (_evidence_matches vs firm/traders registrations).

Products: research/lfc_p1_results.csv + results/lfc_p1.json + doc sec.9.
Trial ledger: cumulative from p3_portfolio.json + this batch (pre-reg
n=145: 20 cells + 20 cost-x2 + 100 random + 3 anchor + 2 passive).
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
from science_gates import append_ledger, passive_strict_max  # T-03 F3/F10
from engine import run_backtest
from strategies import momentum, trend, volatility
from strategies.composite_rotation import top_n_rotation
from live.paper import (OOS_START, CostPatch, ExitPatch, _evidence_matches,
                        build_panels, evidence_cutoff, load_core, seg_metrics,
                        self_test_patches)
from firm.hr import TRADERS_DIR, load_trader
from p3_portfolio import member_run
from p2_null_calibration import passive_buyhold, passive_monthly_rebal

POOL = ["511010", "511090", "511260", "518880", "159934"]
N_RAND = 50                       # per exit regime (pre-registered)
BASELINE_P = [0.02, 0.05]         # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 30_000                # pre-registered rng recipe
MIN_TRADES = 30
MAX_DD = -0.35
PASSIVE_MARGIN = 0.10
SLEEVE_MAX_CORR = 0.30
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
TRIALS_PRIOR = "p3_portfolio.json"   # latest cumulative ledger


def build_entries(P: dict):
    """Fixed 10-entry grid on the LFC pool panels. Returns list of
    (name, family, params, entry_df, exit_df)."""
    close, high, low = P["close"], P["high"], P["low"]
    idx, syms = close.index, list(close.columns)
    E = []
    for n, k in ((60, 1), (60, 2), (120, 1), (120, 2)):
        w = volatility.low_vol_long(close, n, top_k=k)
        E.append((f"low_vol_{n}_k{k}", "low_vol",
                  {"max_positions": k, "position_size_pct": 0.10},
                  w, (w <= 0)))
    for n, r in ((1, 40), (1, 20), (2, 40), (2, 20)):
        w = top_n_rotation(high, low, close, top_n=n, rebal_days=r)
        E.append((f"composite_t{n}_r{r}", "composite",
                  {"max_positions": n,
                   "position_size_pct": round(0.95 / n, 4)},
                  w, (w <= 0)))
    pos = pd.DataFrame({s: momentum.time_series_momentum(close[s], 200)
                        for s in syms}, index=idx).fillna(0)
    E.append(("tsmom_200", "ts_trend",
              {"max_positions": 5, "position_size_pct": 0.10},
              (pos > 0), (pos <= 0)))
    pos = pd.DataFrame({s: trend.donchian_breakout(
        close[s], high[s], low[s], entry_n=55, exit_n=20)
        for s in syms}, index=idx).fillna(0)
    E.append(("donchian_55_20", "ts_trend",
              {"max_positions": 5, "position_size_pct": 0.10},
              (pos > 0), (pos <= 0)))
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
            "ii_ann_pos": full["annual_return"] > 0,
            "iii_dd_ok": full["max_drawdown"] >= MAX_DD,
            "iv_trades_ok": n_trades >= MIN_TRADES,
            "v_oos_ok": oos["sharpe"] > 0 and oos["annual_return"] > 0,
            "vi_beats_passive": full["sharpe"] > vi_bar}


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    print("patch self-tests: PASS")

    prices_full = load_core()                       # core48 for anchors
    prices = {s: prices_full[s] for s in POOL}      # LFC pool subset
    P = build_panels(prices)
    idx, syms = P["close"].index, list(P["close"].columns)
    assert len(syms) == 5, f"expected 5-symbol pool, got {syms}"
    ranges = {s: (str(prices[s].index[0].date()), str(prices[s].index[-1].date()))
              for s in syms}
    data_end = str(idx[-1].date())
    print(f"LFC pool: {syms} window {idx[0].date()} .. {data_end}")
    for s, (a, b) in ranges.items():
        print(f"  {s}: {a} .. {b}")

    # ---------- fixed strategy grid: 10 entries x 2 regimes, + x2 info ----------
    print("running 20 cells (10 entries x 2 exit regimes) + x2 info runs...")
    cells = []
    for (name, fam, params, entry, exit_) in build_entries(P):
        for ce in (False, True):
            r = run_cell(prices, idx, entry, exit_, params, ce)
            r2 = run_cell(prices, idx, entry, exit_, params, ce, cost_mult=2)
            cells.append({"name": name, "family": fam, "exit_regime":
                          "ce" if ce else "default", "status": "ok",
                          "params": params, **r,
                          "x2_full_sharpe": r2["full"]["sharpe"],
                          "x2_oos_sharpe": r2["oos"]["sharpe"],
                          "x2_n_trades": r2["n_trades"]})
            print(f"  {name:<18} {'CE ' if ce else 'def'} "
                  f"full_s={r['full']['sharpe']:>7.3f} "
                  f"oos_s={r['oos']['sharpe']:>7.3f} trades={r['n_trades']:<4} "
                  f"| x2 full_s={r2['full']['sharpe']:>7.3f}")

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
            entry = pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                                 index=idx, columns=syms)
            r = run_cell(prices, idx, entry, _false_panel(idx, syms), {}, ce)
            randoms.append({"name": f"rand_{tag}_p{p}_s{k}", "family":
                             "random_baseline", "exit_regime": tag,
                             "status": "ok", "p": p, "seed": seed, **r})
        print(f"  regime {tag}: 50 done")

    # ---------- passive nulls (J8 formulas verbatim, no engine) ----------
    from knowledge.rules import FeeSchedule
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)
    closes = P["close"]
    passive = {"ew5_buyhold": passive_buyhold(closes, cost_rate),
               "ew5_monthly_rebal": passive_monthly_rebal(closes, cost_rate)}
    passive_rows = {}
    for k, eq in passive.items():
        passive_rows[k] = {"full": seg_metrics(eq), "oos": seg_metrics(eq, OOS_START)}
        print(f"  {k:<18} full_s={passive_rows[k]['full']['sharpe']:>7.3f} "
              f"oos_s={passive_rows[k]['oos']['sharpe']:>7.3f}")

    # ---------- trader anchor runs (hard gate + correlation reference) ----------
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
        return write_outputs(cells, randoms, passive_rows, anchors, None,
                             None, None, ranges, data_end, t0, void=True)

    # ---------- null stats + gates ----------
    p95 = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in randoms
         if r["exit_regime"] == reg and r["status"] == "ok"], 95)), 4)
        for reg in ("default", "ce")}
    passive_full = passive_strict_max(
        [passive_rows["ew5_buyhold"]["full"]["sharpe"],
         passive_rows["ew5_monthly_rebal"]["full"]["sharpe"]])  # T-03-F10 strict-max (recorded 0.9898 bh at run time)
    vi_bar = round(passive_full + PASSIVE_MARGIN, 4)
    print(f"\nrandom p95: default={p95['default']} ce={p95['ce']}")
    print(f"passive EW5 buyhold full={passive_full} -> vi_bar={vi_bar}")

    trader_rets = {tid: trader_eq[tid].pct_change().dropna() for tid in tids}
    for c in cells:
        i_bar = p95["ce" if c["exit_regime"] == "ce" else "default"]
        c["i_bar"], c["vi_bar"] = i_bar, vi_bar
        c["clauses"] = g1_clauses(c["full"], c["oos"], c["n_trades"],
                                  i_bar, vi_bar)
        c["g1_pass"] = all(c["clauses"].values())
        rets = c["eq"].pct_change().dropna()
        c["corr_vs_traders"] = {tid: round(float(
            rets.corr(trader_rets[tid])), 4) for tid in tids}
        c["max_corr"] = max(abs(v) for v in c["corr_vs_traders"].values())
        c["sleeve_tag"] = bool(
            not c["g1_pass"] and c["full"]["sharpe"] > 0
            and c["oos"]["sharpe"] > 0 and c["oos"]["annual_return"] > 0
            and c["n_trades"] >= MIN_TRADES and c["max_corr"] < SLEEVE_MAX_CORR)

    survivors = [c["name"] + "@" + c["exit_regime"]
                 for c in cells if c["g1_pass"]]
    sleeves = [c["name"] + "@" + c["exit_regime"]
               for c in cells if c["sleeve_tag"]]
    print(f"\n===== G1' survivors ({len(survivors)}): {survivors}")
    print(f"===== sleeve candidates ({len(sleeves)}): {sleeves}")

    return write_outputs(cells, randoms, passive_rows, anchors,
                         survivors, sleeves, (p95, vi_bar),
                         ranges, data_end, t0, void=False)


def _false_panel(idx, syms):
    return pd.DataFrame(False, index=idx, columns=syms)


def write_outputs(cells, randoms, passive_rows, anchors, survivors, sleeves,
                  bars, ranges, data_end, t0, void=False):
    p95, vi_bar = bars if bars else (None, None)

    # ---------- CSV (p1 pattern) ----------
    cols = ["name", "family", "exit_regime", "status", "n_trades",
            "oos_trades", "annual_return", "sharpe", "max_drawdown",
            "win_rate", "oos_sharpe", "oos_annual_return",
            "oos_max_drawdown", "i_bar", "vi_bar", "g1_pass", "sleeve_tag",
            "x2_full_sharpe", "x2_oos_sharpe", "max_corr", "note"]
    csv_path = os.path.join(PATHS.root, "research", "lfc_p1_results.csv")
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
                json.dumps(c.get("corr_vs_traders", {}))])
        for r in randoms:
            w.writerow([r["name"], r["family"], r["exit_regime"], r["status"],
                        r["n_trades"], r["oos_trades"],
                        r["full"]["annual_return"], r["full"]["sharpe"],
                        r["full"]["max_drawdown"],
                        r["full"].get("win_rate", ""), r["oos"]["sharpe"],
                        r["oos"]["annual_return"], r["oos"]["max_drawdown"],
                        "", "", False, "", "", "", "",
                        f"p={r['p']} seed={r['seed']}"])
        for k, v in passive_rows.items():
            w.writerow([k, "passive_null", "none", "ok", 0, 0,
                        v["full"]["annual_return"], v["full"]["sharpe"],
                        v["full"]["max_drawdown"], "", v["oos"]["sharpe"],
                        v["oos"]["annual_return"], v["oos"]["max_drawdown"],
                        "", "", "", "", "", "", "J8 formula verbatim"])
    print(f"saved: {csv_path}")

    # ---------- JSON + ledger ----------
    with open(os.path.join(PATHS.results_dir, TRIALS_PRIOR),
              encoding="utf-8") as fh:
        prior = json.load(fh)
    n_runs = len(cells) * 2 + len(randoms) + len(anchors) + len(passive_rows)
    ledger = append_ledger(
        "LFC-P1-mini-screen", n_runs, "lfc_p1.json",
        note=f"{len(cells)} cells x(1x+x2) + {len(randoms)} random "
             f"+ {len(anchors)} trader anchors + {len(passive_rows)} passive; "
             f"pre-registered n=145 (research/LFC_P1_SCREEN.md sec.7); "
             f"T-03-F3 unified dict schema")
    out = {
        "batch": "LFC-P1-mini-screen",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc":
            "research/LFC_P1_SCREEN.md (incl. sec.1.5 pre-run amendment)",
        "universe": {"pool": POOL, "ranges": ranges, "data_end": data_end,
                     "oos_start": OOS_START},
        "void": void,
        "gate": {"random_p95_full": p95, "passive_margin": PASSIVE_MARGIN,
                 "vi_bar": vi_bar, "min_trades": MIN_TRADES, "max_dd": MAX_DD,
                 "sleeve_max_corr": SLEEVE_MAX_CORR},
        "passive": passive_rows,
        "anchors": anchors,
        "cells": [{k: v for k, v in c.items() if k != "eq"} for c in cells],
        "survivors_g1_prime": survivors,
        "sleeve_candidates": sleeves,
        "verdict": {
            "void": void,
            "n_survivors": len(survivors) if survivors is not None else None,
            "n_sleeves": len(sleeves) if sleeves is not None else None,
            "fail_branch": None if (void or (survivors and len(survivors)))
            else "no G1' survivor this batch: family verdict = existing "
                 "machinery (signals x exit regimes) finds no trader on the "
                 "core-5 bond/gold pool; sleeve candidates recorded for a "
                 "future P3-style pre-registered integration decision; "
                 "expansion material (money-market cash leg / convertible) "
                 "or new signal design = separate pre-registration. NO "
                 "threshold tuning, NO re-run (iron rule 3)"},
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "lfc_p1.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"runs={n_runs} elapsed={time.time()-t0:.0f}s "
          f"ledger N={sum(x['n'] for x in ledger)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
