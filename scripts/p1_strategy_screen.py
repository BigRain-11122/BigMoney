"""J7 P1 strategy screen (research/BACKTEST_PLAN.md section 2).

Runs every strategy skeleton with DEFAULT params + the J7 composite-factor
Top-N rotation (N in {3,5,8}) + 20 random-entry baselines through the SAME
engine (default exit rules, T+1, 13bp cost model always on), on the core
48-ETF pool (bare-code files), full history 2020-2026.

Products:
  research/strategy_rank.csv  -- one row per run, ranked by OOS Sharpe
  results/p1_screen.json      -- full detail + G1 gates + trial ledger

G1 validity gate (BACKTEST_PLAN S2):
  full-period annual return > 0
  AND OOS (2025+) Sharpe >= 0.8
  AND total trades >= 30
  AND full-period max drawdown >= -35%
  AND OOS Sharpe > 95th percentile of the random-baseline OOS Sharpe.

Iron rules: no look-ahead (signals on close T execute at T+1 open, enforced
by the engine), cost always on, OOS split constant (2025-01-01), one-shot
run (no p-hacking), random-null accounting (Money02 discipline).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown
from strategies import (trend, mean_reversion, momentum, volatility,
                        sentiment, seasonal, event, macro)
from strategies.composite_rotation import top_n_rotation

OOS_START = "2025-01-01"          # constant-blind split, same as J6 study
N_BASELINES = 20
BASELINE_P = [0.02, 0.05]         # two entry-frequency regimes x 10 seeds


def load_core(min_listing_days: int = 60) -> dict:
    """Core 48-ETF universe: bare-code CSVs in data/daily (J6 definition).
    Keeps amount for sentiment-school factors."""
    out = {}
    daily = PATHS.daily_dir
    for f in sorted(os.listdir(daily)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < min_listing_days:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        if "amount" not in df.columns:
            df["amount"] = df["volume"] * df["close"]
        out[f[:-4]] = df[["open", "high", "low", "close", "volume", "amount"]]
    return out


def load_bench() -> pd.Series:
    p = os.path.join(PATHS.basic_dir, "csi300.csv")
    df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
    return df["close"].sort_index()


def seg_metrics(equity: pd.Series, start: str | None = None) -> dict:
    seg = equity[equity.index >= start] if start else equity
    if len(seg) < 20:
        return {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    return {
        "sharpe": round(float(sharpe(seg)), 4),
        "annual_return": round(float(annual_return(seg)), 4),
        "max_drawdown": round(float(max_drawdown(seg)), 4),
    }


def build_registry(P: dict, bench: pd.Series):
    """Return list of (name, school, kind, note, params, entry_df, exit_df).

    kinds:
      sym   -- per-symbol position signal (Series per sym)
      panel -- cross-sectional weights DataFrame
      mask  -- market-level Series mask applied to all symbols
      macro -- regime filter overlaid on the default MA(5,20) cross
    """
    close, high, low = P["close"], P["high"], P["low"]
    opn, vol, amt = P["open"], P["volume"], P["amount"]
    syms = list(close.columns)
    idx = close.index

    def sym_panel(fn) -> tuple:
        pos = pd.DataFrame({s: fn(s) for s in syms}, index=idx).fillna(0)
        return (pos > 0), (pos <= 0)  # binarize: state signals may carry -1

    def mask_panel(mask: pd.Series) -> tuple:
        m = mask.reindex(idx).fillna(False).astype(bool)
        entry = pd.DataFrame(np.tile(m.values[:, None], (1, len(syms))),
                             index=idx, columns=syms)
        return entry, ~entry

    # default MA(5,20) cross events (engine default, panel form)
    f, s = close.rolling(5).mean(), close.rolling(20).mean()
    ma_entry = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False)
    ma_exit = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False)

    def macro_panel(filt: pd.Series) -> tuple:
        m = filt.reindex(idx).fillna(False).astype(bool)
        flt = pd.DataFrame(np.tile(m.values[:, None], (1, len(syms))),
                           index=idx, columns=syms)  # tile: Series&DataFrame
        # would column-align (dates vs tickers -> all-empty), so broadcast manually
        return (ma_entry & flt), (ma_exit | ~flt)

    R = []

    def add(name, school, kind, note, entry, exit_, params=None):
        R.append((name, school, kind, note, params or {}, entry, exit_))

    # ---- trend (5) ----
    e, x = sym_panel(lambda sm: trend.donchian_breakout(
        close[sm], high[sm], low[sm], entry_n=20, exit_n=10))
    add("donchian_20_10", "trend", "sym", "", e, x)
    e, x = sym_panel(lambda sm: trend.dual_ma_cross(close[sm], 5, 20))
    add("dual_ma_5_20", "trend", "sym", "state-hold semantics (vs 432 event)", e, x)
    e, x = sym_panel(lambda sm: trend.triple_ma(close[sm], 5, 20, 60))
    add("triple_ma_5_20_60", "trend", "sym", "", e, x)
    e, x = sym_panel(lambda sm: trend.parabolic_sar(close[sm]))
    add("parabolic_sar", "trend", "sym", "", e, x)
    e, x = sym_panel(lambda sm: trend.supertrend(close[sm], high[sm], low[sm], 10, 3.0))
    add("supertrend_10_3", "trend", "sym", "", e, x)

    # ---- mean_reversion (5) ----
    e, x = sym_panel(lambda sm: mean_reversion.bollinger_breakout(close[sm], 20, 2.0))
    add("bollinger_revert_20_2", "mean_reversion", "sym", "", e, x)
    e, x = sym_panel(lambda sm: mean_reversion.rsi_revert(close[sm], 14, 30, 70))
    add("rsi_revert_14_30_70", "mean_reversion", "sym", "", e, x)
    e, x = sym_panel(lambda sm: mean_reversion.zscore_revert(close[sm], 20, -2.0))
    add("zscore_revert_20_-2", "mean_reversion", "sym", "", e, x)
    e, x = sym_panel(lambda sm: mean_reversion.pullback_bounce(close[sm], 60, 10))
    add("pullback_bounce_60_10", "mean_reversion", "sym", "", e, x)
    e, x = sym_panel(lambda sm: mean_reversion.rsi2(close[sm], 2))
    add("rsi2", "mean_reversion", "sym", "", e, x)

    # ---- event (3) ----
    e, x = sym_panel(lambda sm: event.gap_fill(opn[sm], close[sm], 5))
    add("gap_fill_5", "event", "sym", "", e, x)
    e, x = sym_panel(lambda sm: event.breakout_confirm(close[sm], vol[sm], 20, 1.5))
    add("breakout_confirm_20_1.5", "event", "sym", "", e, x)
    e, x = sym_panel(lambda sm: event.double_bottom(close[sm], 20, 0.03))
    add("double_bottom_20", "event", "sym", "", e, x)

    # ---- volatility (4) ----
    e, x = sym_panel(lambda sm: volatility.vol_target(close[sm], 0.15, 20))
    add("vol_target_15", "volatility", "sym", "fractional signal binarized >0", e, x)
    e, x = sym_panel(lambda sm: volatility.vol_breakout(close[sm], 20))
    add("vol_breakout_20", "volatility", "sym", "", e, x)
    e, x = sym_panel(lambda sm: volatility.vol_regime_switch(close[sm], 20, 200))
    add("vol_regime_switch_20_200", "volatility", "sym", "", e, x)
    w = volatility.low_vol_long(close, 60, top_k=5)
    add("low_vol_long_60", "volatility", "panel", "", w, (w <= 0))

    # ---- momentum (5) ----
    w = momentum.cross_sectional_momentum(close, n=120, skip=20, top_k=5)
    add("xsec_mom_120_20", "momentum", "panel", "skip-last-20d", w, (w <= 0))
    w = momentum.dual_momentum(close, bench, n=120, top_k=5)
    add("dual_mom_120", "momentum", "panel", "bench=CSI300", w, (w <= 0))
    e, x = sym_panel(lambda sm: momentum.time_series_momentum(close[sm], 200))
    add("ts_mom_200", "momentum", "sym", "price>MA200", e, x)
    w = momentum.relative_strength_rotation(close, bench, n=20, top_k=5)
    add("rs_rotation_20", "momentum", "panel", "bench=CSI300", w, (w <= 0))
    w = momentum.momentum_acceleration(close, fast=20, slow=120)
    add("mom_accel_20_120", "momentum", "panel", "", w, (w <= 0))

    # ---- sentiment (5) ----
    w = sentiment.turnover_surge(vol, n=20, threshold=2.0)
    add("turnover_surge_20_2", "sentiment", "panel", "", w, (w <= 0))
    w = sentiment.amount_rank(amt, n=20, top_k=10)
    add("amount_rank_20_10", "sentiment", "panel",
        "top_k=10 vs max_pos=5: engine fills first 5 by column order", w, (w <= 0))
    w = sentiment.price_volume_trend(close, vol, n=20)
    add("price_volume_trend_20", "sentiment", "panel", "", w, (w <= 0))
    w = sentiment.intraday_momentum(opn, close, n=10)
    add("intraday_momentum_10", "sentiment", "panel", "", w, (w <= 0))
    w = sentiment.overnight_drift(opn, close, n=10)
    add("overnight_drift_10", "sentiment", "panel", "", w, (w <= 0))

    # ---- seasonal (5) ----
    e, x = mask_panel(seasonal.month_seasonality(close, month=1))
    add("month_seasonality_jan", "seasonal", "mask",
        "market mask, engine holds first 5 by column order", e, x)
    e, x = mask_panel(seasonal.month_end_effect(close, window=3))
    add("month_end_effect_3", "seasonal", "mask",
        "fixed: original crashed on RangeIndex.year", e, x)
    e, x = mask_panel(seasonal.weekday_effect(close, weekday=4))
    add("weekday_effect_fri", "seasonal", "mask", "", e, x)
    e, x = sym_panel(lambda sm: seasonal.holiday_effect(close[sm], pre_days=3))
    add("holiday_effect", "seasonal", "sym", "months 1/2/10/11 approximation", e, x)
    e, x = sym_panel(lambda sm: seasonal.trend_by_season(close[sm], month=1, ma_n=200))
    add("trend_by_season_jan", "seasonal", "sym", "", e, x)

    # ---- macro overlays on default MA cross (4) ----
    bench_al = bench.reindex(idx).ffill()
    e, x = macro_panel(macro.csi300_trend_filter(bench_al, bench, ma_n=200))
    add("macro_trend_filter", "macro", "macro", "MA5/20 cross AND bench>MA200", e, x)
    e, x = macro_panel(macro.csi300_momentum_filter(bench_al, bench, n=60))
    add("macro_mom_filter", "macro", "macro", "MA cross AND bench 60d mom>0", e, x)
    e, x = macro_panel(macro.volatility_regime_filter(bench, n=60))
    add("macro_vol_regime", "macro", "macro", "MA cross AND low-vol regime", e, x)
    e, x = macro_panel(macro.drawdown_filter(bench, max_dd=-0.15))
    add("macro_drawdown_filter", "macro", "macro", "MA cross AND bench dd>-15%", e, x)

    # ---- composite rotation (3 variants) ----
    for n in (3, 5, 8):
        w = top_n_rotation(high, low, close, top_n=n, rebal_days=20)
        add(f"composite_top{n}", "composite", "panel",
            "J6 composite, 20d rebalance, 240d warmup; fully-invested sizing",
            w, (w <= 0), params={"max_positions": n,
                                 "position_size_pct": round(0.95 / n, 4)})
    return R


def run_one(prices, idx, entry, exit_, params, name):
    res = run_backtest(prices, params, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    full = res["metrics"]
    oos = seg_metrics(eq, OOS_START)
    oos_trades = sum(1 for t in res["trades"] if str(t["date"]) >= OOS_START)
    return {"name": name, "full": full, "oos": oos,
            "n_trades": full["num_trades"], "oos_trades": oos_trades}


def main():
    t0 = time.time()
    print("loading core universe (bare codes)...")
    prices = load_core()
    print(f"  {len(prices)} ETFs")
    bench = load_bench()

    P = {f: pd.DataFrame({s: df[f] for s, df in prices.items()}).sort_index().ffill()
         for f in ["open", "high", "low", "close", "volume", "amount"]}
    idx = P["close"].index

    rows, baselines = [], []

    print("building signals...")
    reg = build_registry(P, bench)
    print(f"  {len(reg)} signal strategies")

    for (name, school, kind, note, params, entry, exit_) in reg:
        t1 = time.time()
        try:
            r = run_one(prices, idx, entry, exit_, params, name)
            rows.append({"strategy": name, "school": school, "kind": kind,
                         "note": note, **r, "status": "ok"})
            print(f"  {name:<28} sharpe={r['full']['sharpe']:>7.3f} "
                  f"oos_sharpe={r['oos']['sharpe']:>7.3f} "
                  f"trades={r['n_trades']:>4} ({time.time()-t1:.1f}s)")
        except Exception as ex:
            rows.append({"strategy": name, "school": school, "kind": kind,
                         "note": note, "status": "signal_error",
                         "error": f"{type(ex).__name__}: {ex}"})
            print(f"  {name:<28} SIGNAL_ERROR {type(ex).__name__}: {ex}")

    # ---- random-entry baselines (null hypothesis, Money02 discipline) ----
    syms = list(P["close"].columns)
    n_days, n_syms = len(idx), len(syms)
    print(f"running {N_BASELINES} random baselines...")
    for k in range(N_BASELINES):
        p = BASELINE_P[k // 10]
        seed = k % 10
        rng = np.random.default_rng(10_000 + k)
        entry = pd.DataFrame(
            (rng.random((n_days, n_syms)) < p).astype(int),
            index=idx, columns=syms)
        exit_ = pd.DataFrame(False, index=idx, columns=syms)  # engine rules only
        t1 = time.time()
        r = run_one(prices, idx, entry, exit_, {}, f"rand_p{p}_s{seed}")
        baselines.append({**r, "strategy": r["name"],
                          "school": "random_baseline", "kind": "baseline",
                          "note": f"random entry p={p} seed={seed}; exits=engine rules",
                          "status": "ok"})
        print(f"  rand_p{p}_s{seed}  oos_sharpe={r['oos']['sharpe']:>7.3f} "
              f"trades={r['n_trades']:>4} ({time.time()-t1:.1f}s)")

    # ---- null distribution ----
    rand_oos = [b["oos"]["sharpe"] for b in baselines if b["status"] == "ok"]
    rand_full = [b["full"]["sharpe"] for b in baselines if b["status"] == "ok"]
    p95_oos = round(float(np.percentile(rand_oos, 95)), 4)
    p95_full = round(float(np.percentile(rand_full, 95)), 4)
    print(f"\nrandom baselines: n={len(rand_oos)}  "
          f"oos p95={p95_oos}  full p95={p95_full}")

    # ---- G1 gate + ranking ----
    all_rows = rows + baselines
    for r in all_rows:
        if r["status"] != "ok":
            r["g1_pass"] = False
            continue
        f_, o_ = r["full"], r["oos"]
        r["rand_oos_p95"] = p95_oos
        r["beats_rand_oos"] = bool(o_["sharpe"] > p95_oos)
        r["beats_rand_full"] = bool(f_["sharpe"] > p95_full)
        if r["school"] == "random_baseline":
            r["g1_pass"] = False  # null family is the gate, not a candidate
            continue
        r["g1_pass"] = bool(
            f_["annual_return"] > 0
            and o_["sharpe"] >= 0.8
            and r["n_trades"] >= 30
            and f_["max_drawdown"] >= -0.35
            and o_["sharpe"] > p95_oos)

    ok = [r for r in all_rows if r["status"] == "ok"]
    ok.sort(key=lambda r: r["oos"]["sharpe"], reverse=True)
    cands = [r for r in rows if r["status"] == "ok"]
    survivors = [r["strategy"] for r in cands if r["g1_pass"]]

    # ---- CSV ----
    csv_path = os.path.join(PATHS.root, "research", "strategy_rank.csv")
    cols = ["strategy", "school", "kind", "status", "n_trades", "oos_trades",
            "annual_return", "sharpe", "max_drawdown", "win_rate",
            "oos_sharpe", "oos_annual_return", "oos_max_drawdown",
            "rand_oos_p95", "beats_rand_oos", "beats_rand_full", "g1_pass",
            "note"]
    import csv as _csv
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for r in ok:
            flat = {**r["full"],
                    **{f"oos_{k}": v for k, v in r["oos"].items()},
                    "strategy": r["strategy"], "school": r["school"],
                    "kind": r["kind"], "status": r["status"],
                    "n_trades": r["n_trades"], "oos_trades": r["oos_trades"],
                    "rand_oos_p95": r.get("rand_oos_p95", ""),
                    "beats_rand_oos": r.get("beats_rand_oos", ""),
                    "beats_rand_full": r.get("beats_rand_full", ""),
                    "g1_pass": r["g1_pass"], "note": r.get("note", "")}
            w.writerow([flat.get(c, "") for c in cols])
    print(f"saved: {csv_path}")

    # ---- JSON ----
    out = {
        "batch": "P1-strategy-screen",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": OOS_START,
        "g1_gate": {"ann_full_gt_0": True, "oos_sharpe_min": 0.8,
                    "min_trades": 30, "max_dd_full": -0.35,
                    "beat_rand_oos_p95": True},
        "random_null": {"n": len(rand_oos), "p95_oos": p95_oos,
                        "p95_full": p95_full,
                        "oos_sharpes": sorted(rand_oos)},
        "survivors_g1": survivors,
        "trials_ledger": [
            {"batch": "432-MA-param-grid (pre-plan)", "n": 432,
             "note": "all dead, best Sharpe 0.44 - lesson: validity before tuning"},
            {"batch": "J6-factor-IC-study", "n": 30,
             "note": "informational factor ranking"},
            {"batch": "P1-strategy-screen", "n": len(reg) + N_BASELINES,
             "note": f"{len(reg)} signal strategies + {N_BASELINES} random baselines"},
        ],
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(reg) + N_BASELINES, "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
        "runs": all_rows,
    }
    json_path = os.path.join(PATHS.results_dir, "p1_screen.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    print(f"\n===== G1 survivors ({len(survivors)}) =====")
    for s in survivors:
        print(f"  {s}")
    if not survivors:
        print("  (none - honest result, see strategy_rank.csv)")
    print(f"\ntotal elapsed: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
