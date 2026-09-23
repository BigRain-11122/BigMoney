"""NSP1 new-signal P1 mini screen (core48).

PRE-REGISTERED before running (research/NEW_SIGNAL_P1.md, written first).
Do NOT tune thresholds or re-run after seeing results (p-hacking ban,
BACKTEST_PLAN iron rule 3).

Question (LFC fail_branch option (b), sanctioned by round-15 pointer):
on the core48 equity pool, can (a) P1 entries never crossed with the CE
softened exit machine (transfer probes -- J19 migrated only composite,
LFC tested tsmom/donchian only on the weak 5-asset pool) and (b) four
new out-of-grid signal designs produce a G1' candidate or a
low-correlation diversification sleeve?

Fixed grid (no search): 12 entries x 2 exit regimes = 24 cells
  Transfer probes 8 (P1-identical construction, params={} engine sizing):
    tsmom_200, donchian_20_10, donchian_55_20, dual_ma_5_20,
    triple_ma_5_20_60, double_bottom_20 (sym, binarized pos>0),
    price_volume_trend_20, amount_rank_20_10 (panel, exit=w<=0)
  New designs 4 (in-script pure pandas, zero engine change):
    high252_prox_top5_r20  -- George-Hwang 52wk-high proximity, frozen 20d
    sharpe_mom_120_top5_r20 -- 120d return / 120d daily-return std
    trend_r2_120_top5_r20  -- R^2 x sign(slope) of log-price~time OLS
    tsmom_consensus_200_50 -- (close>MA200) & (MA20>MA60) state
  Rotations sized 0.95/5 (composite registered convention); state entries
  engine default. Exit regimes: default | CE (registered contract: bridge
  time_decay 25d/5% + trailing 0.10 + ExitPatch loss_time_days=16).

Nulls (recorded constants rule, J19 drift-proof pattern):
  default cells i-line = recorded 0.3521 (p2_calibration n=100);
  CE cells i-line = max(in-batch CE p95, 0.3521) -- core48 never had a CE
  null, this batch creates it; floor = recorded constant;
  vi-line = recorded 0.4004 (passive EW48 + 0.10, regime-free).
  In-batch: n=50 random per exit regime (p in {0.02,0.05} x 25, seeds
  40_000+k / 40_050+k) + passive EW48 re-computation (consistency info
  only, gates stay on recorded constants).

G1' six clauses verbatim from p2_calibration.json g1_prime_gate.
Survivors = G1' CANDIDATES ONLY -- NO registration this batch (G2
deepening = separate pre-registration). Sleeve-tag informational
(!g1_pass & full>0 & OOS double positive & >=30 trades & max|corr| vs
the 3 registered traders' anchor equity daily returns < 0.30).

Hard gates (batch void if broken): patch self-test + 3 trader anchor
reproduction (_evidence_matches vs firm/traders registrations) +
trend_r2 vectorized-vs-polyfit equivalence check.

Products: research/new_signal_p1_results.csv + results/new_signal_p1.json
+ doc sec.9. Trial ledger: cumulative from lfc_p1.json + this batch
(pre-reg n=153: 24 cells x(1x+x2) + 100 random + 3 anchors + 2 passive).
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
from strategies import trend, momentum, sentiment, event
from live.paper import (OOS_START, CostPatch, ExitPatch, _evidence_matches,
                        build_panels, load_core, seg_metrics,
                        self_test_patches)
from firm.hr import TRADERS_DIR, load_trader
from p3_portfolio import member_run
from p2_null_calibration import passive_buyhold, passive_monthly_rebal

N_RAND = 50                       # per exit regime (pre-registered)
BASELINE_P = [0.02, 0.05]         # 25 seeds x 2 entry-frequency regimes
SEED_BASE = 40_000                 # pre-registered rng recipe (default reg)
SLEEVE_MAX_CORR = 0.30
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}
CE_OVERRIDES = {"loss_time_days": 16}
TRIALS_PRIOR = "lfc_p1.json"       # latest cumulative ledger


def load_gate() -> dict:
    """Recorded G1' constants (J19 drift-proof pattern, not in-batch)."""
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        return json.load(fh)["g1_prime_gate"]


GATE = load_gate()
I_LINE_RECORDED = GATE["i_full_sharpe_gt"]      # 0.3521 (n=100 calibrated)
VI_BAR = GATE["vi_full_sharpe_gt"]              # 0.4004 (passive + 0.10)


def _topk_frozen(score, top_k, rebal_days, ascending=False):
    """Top-k by score, membership frozen at non-overlapping rebal_days
    (low_vol_long rebal_days convention). NaN scores never rank in."""
    ranks = score.rank(axis=1, ascending=ascending)
    in_set = ranks <= top_k
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def _trend_r2_score(close: pd.DataFrame, n: int = 120) -> pd.DataFrame:
    """R^2 x sign(slope), OLS of log(close) on time over trailing n bars.
    Closed form via rolling sums: for window ending at global row i,
    within-window time t = j - i + n - 1  =>  sum(t*y) = A_i - i * S1_i
    where A = rolling sum of (j + n - 1) * y_j. Positional numpy core
    (no DataFrame-alignment traps, J7 lesson), pandas rolling for speed,
    no lookahead."""
    yv = np.log(close.to_numpy(dtype=float))          # (T,N) positional
    jv = np.arange(len(yv), dtype=float)
    idx, cols = close.index, close.columns
    ydf = pd.DataFrame(yv, index=idx, columns=cols)
    adf = pd.DataFrame(yv * (jv + n - 1)[:, None], index=idx, columns=cols)
    Av = adf.rolling(n).sum().to_numpy()
    S1v = ydf.rolling(n).sum().to_numpy()
    S2v = (ydf * ydf).rolling(n).sum().to_numpy()
    mean_y = S1v / n
    mean_ty = (Av - jv[:, None] * S1v) / n
    cov = mean_ty - (n - 1) / 2.0 * mean_y
    var_t = (n * n - 1) / 12.0
    var_y = S2v / n - mean_y * mean_y
    r2 = cov * cov / (var_t * var_y)
    score = r2 * np.sign(cov)
    return pd.DataFrame(score, index=idx, columns=cols)


def _trend_r2_selftest(close: pd.DataFrame, n: int = 120) -> bool:
    """Vectorized score must equal polyfit R^2 x sign(slope) on samples.
    Uses GLOBAL row positions on the raw (pre-dropna) panel -- rolling
    window ending at row i covers rows [i-n+1, i] inclusive."""
    y = np.log(close)
    col = y.columns[0]
    score = _trend_r2_score(close, n)[col]
    T = len(y)
    if T < n + 5:
        return True  # too short to test; main pools are ~1600 bars
    checked = 0
    for end in (n + 60, T // 2, T - 1):
        win = y[col].iloc[end - n + 1:end + 1].to_numpy()
        if np.isnan(win).any():
            continue
        b, a0 = np.polyfit(np.arange(n), win, 1)
        yhat = a0 + b * np.arange(n)
        ss_res = float(((win - yhat) ** 2).sum())
        ss_tot = float(((win - win.mean()) ** 2).sum())
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        want = r2 * (1 if b >= 0 else -1)
        got = float(score.iloc[end])
        if np.isnan(got) or abs(got - want) > 1e-8:
            print(f"  trend_r2 mismatch col={col} end={end}: "
                  f"got={got} want={want}")
            return False
        checked += 1
    return checked > 0


def build_entries(P: dict):
    """Fixed 12-entry grid (8 transfer probes + 4 new designs).
    Returns list of (name, family, params, entry_df, exit_df, note)."""
    close, high, low = P["close"], P["high"], P["low"]
    vol, amt = P["volume"], P["amount"]
    idx, syms = close.index, list(close.columns)
    E = []

    def sym_panel(fn):
        pos = pd.DataFrame({s: fn(s) for s in syms}, index=idx).fillna(0)
        return (pos > 0), (pos <= 0)   # binarize: state signals may carry -1

    def add(name, family, params, entry, exit_, note=""):
        E.append((name, family, params, entry, exit_, note))

    # ---- transfer probes: P1-identical construction, params={} ----
    e, x = sym_panel(lambda s: momentum.time_series_momentum(close[s], 200))
    add("tsmom_200", "transfer", {}, e, x, "P1: ts_mom_200; LFC CE star")
    e, x = sym_panel(lambda s: trend.donchian_breakout(
        close[s], high[s], low[s], 20, 10))
    add("donchian_20_10", "transfer", {}, e, x, "P1 original params")
    e, x = sym_panel(lambda s: trend.donchian_breakout(
        close[s], high[s], low[s], 55, 20))
    add("donchian_55_20", "transfer", {}, e, x, "LFC-tested variant")
    e, x = sym_panel(lambda s: trend.dual_ma_cross(close[s], 5, 20))
    add("dual_ma_5_20", "transfer", {}, e, x,
        "state-hold semantics (vs 432 event)")
    e, x = sym_panel(lambda s: trend.triple_ma(close[s], 5, 20, 60))
    add("triple_ma_5_20_60", "transfer", {}, e, x, "")
    e, x = sym_panel(lambda s: event.double_bottom(close[s], 20, 0.03))
    add("double_bottom_20", "transfer", {}, e, x, "event family rep")
    w = sentiment.price_volume_trend(close, vol, n=20)
    add("price_volume_trend_20", "transfer", {}, w, (w <= 0),
        "P1 watchlist OOS 1.377")
    w = sentiment.amount_rank(amt, n=20, top_k=10)
    add("amount_rank_20_10", "transfer", {}, w, (w <= 0),
        "top_k=10 vs max_pos=5: engine fills first 5 by column order")

    # ---- new designs: out-of-grid, in-script pure pandas ----
    rot = {"max_positions": 5, "position_size_pct": round(0.95 / 5, 4)}
    w = _topk_frozen(close / close.rolling(252, min_periods=200).max(), 5, 20)
    add("high252_prox_top5_r20", "new_design", rot, w, (w <= 0),
        "George-Hwang 52wk-high proximity; frozen 20d membership")
    mom = close.pct_change(120)
    sd = close.pct_change().rolling(120).std()
    w = _topk_frozen(mom / sd.replace(0, np.nan), 5, 20)
    add("sharpe_mom_120_top5_r20", "new_design", rot, w, (w <= 0),
        "risk-adjusted momentum; frozen 20d")
    w = _topk_frozen(_trend_r2_score(close, 120), 5, 20)
    add("trend_r2_120_top5_r20", "new_design", rot, w, (w <= 0),
        "R^2 x sign(slope) trend quality; frozen 20d")
    e = ((close > close.rolling(200).mean())
         & (close.rolling(20).mean() > close.rolling(60).mean())
         ).fillna(False).astype(bool)
    add("tsmom_consensus_200_50", "new_design", {}, e, ~e,
        "multi-horizon ts-momentum consensus state")
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
    p95_inbatch, passive_check = bars

    cols = ["name", "family", "exit_regime", "status", "n_trades",
            "oos_trades", "annual_return", "sharpe", "max_drawdown",
            "win_rate", "oos_sharpe", "oos_annual_return",
            "oos_max_drawdown", "i_bar", "vi_bar", "g1_pass", "sleeve_tag",
            "x2_full_sharpe", "x2_oos_sharpe", "max_corr", "note"]
    csv_path = os.path.join(PATHS.root, "research",
                           "new_signal_p1_results.csv")
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
                        "", "", False, "", "", "", "",
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
        prior = json.load(fh)
    n_runs = len(cells) * 2 + len(randoms) + len(anchors) + len(passive_rows)
    ledger = list(prior["trials_ledger"]) + [{
        "batch": "NSP1-new-signal-mini-screen", "n": n_runs,
        "note": f"{len(cells)} cells x(1x+x2) + {len(randoms)} random "
                f"+ {len(anchors)} trader anchors + {len(passive_rows)} passive; "
                f"pre-registered n=153 (research/NEW_SIGNAL_P1.md sec.7)"}]
    verdict = {
        "void": void,
        "n_survivors": None if survivors is None else len(survivors),
        "n_sleeves": None if sleeves is None else len(sleeves),
        "survivors_are": "G1' CANDIDATES ONLY -- no registration this batch; "
                         "G2 deepening (neighborhood + cost + yearly) "
                         "requires a separate pre-registration",
        "fail_branch": None if (void or (survivors and len(survivors)))
        else "no G1' candidate this batch: honest verdict; core48 CE null "
             "recorded for all future CE-cell screening; survivors==0 means "
             "neither transfer probes nor the 4 new designs clear the "
             "recorded-constant gate -- NO threshold tuning, NO re-run "
             "(iron rule 3); next material (cash-leg engine feature, pool "
             "expansion) = separate pre-registration outside this batch",
    }
    out = {
        "batch": "NSP1-new-signal-mini-screen",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/NEW_SIGNAL_P1.md",
        "universe": {"pool": "core48-bare-codes", "data_end": data_end,
                     "oos_start": OOS_START},
        "void": void,
        "gate": {"recorded_constants": GATE,
                 "i_line_recorded": I_LINE_RECORDED,
                 "vi_bar_recorded": VI_BAR,
                 "i_line_rule": "default cells: recorded 0.3521; CE cells: "
                                "max(in-batch CE p95, 0.3521)",
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
    json_path = os.path.join(PATHS.results_dir, "new_signal_p1.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")
    print(f"runs={n_runs} elapsed={time.time()-t0:.0f}s "
          f"ledger N={sum(x['n'] for x in ledger)}")
    return 0


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    print("patch self-tests: PASS")

    prices = load_core()
    P = build_panels(prices)
    idx, syms = P["close"].index, list(P["close"].columns)
    data_end = str(idx[-1].date())
    print(f"core48: {len(syms)} syms, window {idx[0].date()} .. {data_end}")

    if not _trend_r2_selftest(P["close"]):
        print("trend_r2 vectorized self-test FAILED -- abort")
        return 2
    print("trend_r2 closed-form self-test: PASS")

    # ---------- fixed grid: 12 entries x 2 regimes + x2 info ----------
    print("running 24 cells (12 entries x 2 exit regimes) + x2 info...")
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
                print(f"  {name:<22} {'CE ' if ce else 'def'} "
                      f"full_s={r['full']['sharpe']:>7.3f} "
                      f"oos_s={r['oos']['sharpe']:>7.3f} "
                      f"trades={r['n_trades']:<5} "
                      f"| x2 full_s={r2['full']['sharpe']:>7.3f}")
            except Exception as ex:
                cells.append({"name": name, "family": fam,
                              "exit_regime": tag,
                              "status": f"signal_error: {ex}",
                              "params": params, "note": note})
                print(f"  {name:<22} {tag} SIGNAL_ERROR {ex}")

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
        r1 = member_run(traders[tid], prices, None)
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
                             None, None, (None, None), data_end, t0,
                             void=True)

    # ---------- nulls + gates (recorded constants rule) ----------
    p95_inbatch = {reg: round(float(np.percentile(
        [r["full"]["sharpe"] for r in randoms
         if r["exit_regime"] == reg and r["status"] == "ok"], 95)), 4)
        for reg in ("default", "ce")}
    i_bar_ce = round(max(p95_inbatch["ce"], I_LINE_RECORDED), 4)
    print(f"\nin-batch random p95: default={p95_inbatch['default']} "
          f"(recorded gate line {I_LINE_RECORDED}), ce={p95_inbatch['ce']} "
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
                         survivors, sleeves, (p95_inbatch, passive_check),
                         data_end, t0, void=False)


if __name__ == "__main__":
    sys.exit(main())
