"""J8 P2 null-hypothesis calibration (research/NULL_CALIBRATION.md).

PRE-REGISTERED before running (2026-09-23 09:47). Do NOT tune thresholds
after seeing results (p-hacking ban, BACKTEST_PLAN iron rule 3).

Families, all on the core 48-ETF bare-code pool, same engine + 13bp costs:
  A. random entry x 100 seeds (p in {0.02, 0.05} x 50), exits = engine only
     -> noise null replacing P1's n=20 (p95 estimate too noisy)
  B. paired subset of A (first 20 seeds, same entry matrices) + random exit
     events (p_exit=0.05/day) -> exit-machinery decomposition (paired delta)
  C. passive nulls (no engine): EW48 buy&hold + EW48 monthly rebalance
     -> pure drift floor

Then re-reads the 39 P1 candidates (research/strategy_rank.csv) against the
PRE-REGISTERED G1' gate (see NULL_CALIBRATION.md section 3):
  i   full Sharpe  > random full p95 (n=100)
  ii  full annual_return > 0
  iii full max_drawdown >= -35%
  iv  n_trades >= 30
  v   OOS sharpe > 0 AND OOS annual_return > 0
  vi  full Sharpe  > passive EW48 full Sharpe + 0.10
Effective skill bar = max(i, vi) -- both clauses active, not interchangeable.

Products: results/p2_calibration.json + console verdict.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from science_gates import append_ledger, passive_strict_max  # T-03 F3/F10
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown
from knowledge.rules import FeeSchedule

OOS_START = "2025-01-01"            # constant-blind split (same as J6/P1)
N_BASELINES = 100                    # pre-registered
BASELINE_P = [0.02, 0.05]            # 50 seeds x 2 entry-frequency regimes
N_PAIRED = 20                        # exit-symmetric paired subset
P_EXIT = 0.05                        # random exit probability / day
MONTHLY_TURNOVER = 0.1               # est. one-way turnover for EW monthly rebal
PASSIVE_MARGIN = 0.10                # gate (vi) buffer over passive EW48
MIN_TRADES = 30
MAX_DD = -0.35


def load_core(min_listing_days: int = 60) -> dict:
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


def seg_metrics(equity: pd.Series, start: str | None = None) -> dict:
    seg = equity[equity.index >= start] if start else equity
    if len(seg) < 20:
        return {"sharpe": 0.0, "annual_return": 0.0, "max_drawdown": 0.0}
    return {
        "sharpe": round(float(sharpe(seg)), 4),
        "annual_return": round(float(annual_return(seg)), 4),
        "max_drawdown": round(float(max_drawdown(seg)), 4),
    }


def run_one(prices, idx, entry, exit_, params, name):
    res = run_backtest(prices, params, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    full = res["metrics"]
    oos = seg_metrics(eq, OOS_START)
    oos_trades = sum(1 for t in res["trades"] if str(t["date"]) >= OOS_START)
    return {"name": name, "full": full, "oos": oos,
            "n_trades": full["num_trades"], "oos_trades": oos_trades}


# ---------- family C: passive nulls (no engine, drift only) ----------

def passive_buyhold(closes: pd.DataFrame, cost_rate: float) -> pd.Series:
    """EW buy&hold: each sleeve buys its symbol at first listed price with
    1/N of cash; before listing the sleeve stays in cash (value 1.0)."""
    n = closes.shape[1]
    sleeves = []
    for sym in closes.columns:
        s = closes[sym]
        v0 = s.dropna().iloc[0]
        sleeves.append((s / v0).fillna(1.0))
    equity = pd.concat(sleeves, axis=1).mean(axis=1)
    return equity * (1 - cost_rate)  # one-time entry cost


def passive_monthly_rebal(closes: pd.DataFrame, cost_rate: float) -> pd.Series:
    """EW monthly rebalance: 1/N per sleeve fixed at each month start;
    within a month sleeve value = close_t / close_month_start (cash=1.0
    before listing). Monthly cost = cost_rate * est. one-way turnover."""
    rets = closes.pct_change()
    equity_parts, months = [], closes.index.to_period("M")
    equity_parts.append(pd.Series(1.0, index=[closes.index[0]]))
    prev = pd.Series([1.0], index=[closes.index[0]])
    for _, grp in rets.groupby(months):
        growth = (1 + grp).cumprod()          # per-sleeve intra-month growth
        sleeve_val = growth.fillna(1.0)       # unlisted sleeve: cash, no growth
        month_path = sleeve_val.sum(axis=1) / closes.shape[1]
        month_path = month_path * (1 - cost_rate * MONTHLY_TURNOVER)
        equity_parts.append(prev.iloc[-1] * month_path)
        prev = equity_parts[-1]
    return pd.concat(equity_parts).sort_index()


def main():
    t0 = time.time()
    print("loading core universe (bare codes)...")
    prices = load_core()
    print(f"  {len(prices)} ETFs")

    closes = pd.DataFrame({s: df["close"] for s, df in prices.items()})
    closes = closes.sort_index().ffill()
    idx = closes.index
    syms = list(closes.columns)
    n_days, n_syms = len(idx), len(syms)
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)

    # ---------- family C: passive (cheap, run first) ----------
    print("family C: passive nulls...")
    passive = {}
    bh = passive_buyhold(closes, cost_rate)
    passive["ew48_buyhold"] = {
        "full": seg_metrics(bh), "oos": seg_metrics(bh, OOS_START),
        "n_trades": 0, "oos_trades": 0}
    mr = passive_monthly_rebal(closes, cost_rate)
    passive["ew48_monthly_rebal"] = {
        "full": seg_metrics(mr), "oos": seg_metrics(mr, OOS_START),
        "n_trades": 0, "oos_trades": 0}
    for k, v in passive.items():
        print(f"  {k:<22} full_sharpe={v['full']['sharpe']:>7.3f} "
              f"oos_sharpe={v['oos']['sharpe']:>7.3f} "
              f"full_ann={v['full']['annual_return']:>7.3f}")

    # ---------- family A: random entry x engine exits (n=100) ----------
    print(f"family A: {N_BASELINES} random-entry baselines (engine exits)...")
    fam_a = []
    for k in range(N_BASELINES):
        p = BASELINE_P[k // 50]
        rng = np.random.default_rng(10_000 + k)
        entry = pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                             index=idx, columns=syms)
        exit_ = pd.DataFrame(False, index=idx, columns=syms)
        t1 = time.time()
        r = run_one(prices, idx, entry, exit_, {}, f"rand_p{p}_s{k % 50}")
        fam_a.append({**r, "p": p, "seed": k % 50,
                      "note": f"random entry p={p} seed={k % 50}; exits=engine rules"})
        if k % 20 == 0 or k == N_BASELINES - 1:
            print(f"  [{k+1}/{N_BASELINES}] oos_sharpe={r['oos']['sharpe']:>7.3f} "
                  f"full_sharpe={r['full']['sharpe']:>7.3f} ({time.time()-t1:.1f}s)")

    # ---------- family B: paired random entry + random exit ----------
    print(f"family B: {N_PAIRED} paired random-entry+random-exit runs...")
    fam_b = []
    for k in range(N_PAIRED):
        p = BASELINE_P[k // 50]
        rng = np.random.default_rng(10_000 + k)   # SAME entry matrix as A[k]
        entry = pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                             index=idx, columns=syms)
        rng_x = np.random.default_rng(20_000 + k)
        exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < P_EXIT),
                             index=idx, columns=syms)
        t1 = time.time()
        r = run_one(prices, idx, entry, exit_, {}, f"randexit_p{p}_s{k % 50}")
        fam_b.append({**r, "p": p, "seed": k % 50,
                      "note": f"random entry p={p} seed={k % 50} + random exit p={P_EXIT}"})
        print(f"  randexit_s{k % 50:<3} oos_sharpe={r['oos']['sharpe']:>7.3f} "
              f"full_sharpe={r['full']['sharpe']:>7.3f} ({time.time()-t1:.1f}s)")

    # ---------- null distribution stats ----------
    a_full = [r["full"]["sharpe"] for r in fam_a]
    a_oos = [r["oos"]["sharpe"] for r in fam_a]
    b_full = [r["full"]["sharpe"] for r in fam_b]
    b_oos = [r["oos"]["sharpe"] for r in fam_b]
    p95_full = round(float(np.percentile(a_full, 95)), 4)
    p95_oos = round(float(np.percentile(a_oos, 95)), 4)
    passive_full_sharpe = passive_strict_max(
        [passive["ew48_buyhold"]["full"]["sharpe"],
         passive["ew48_monthly_rebal"]["full"]["sharpe"]])  # T-03-F10 strict-max (recorded 0.3004 bh at run time)
    skill_bar = round(max(p95_full, passive_full_sharpe + PASSIVE_MARGIN), 4)
    paired_delta_oos = [a_oos[k] - b_oos[k] for k in range(N_PAIRED)]
    paired_delta_full = [a_full[k] - b_full[k] for k in range(N_PAIRED)]

    print(f"\nnull A (n={N_BASELINES}): full p95={p95_full}  oos p95={p95_oos}  "
          f"oos median={round(float(np.median(a_oos)), 4)}")
    print(f"family B (n={N_PAIRED}): full median={round(float(np.median(b_full)), 4)}  "
          f"oos median={round(float(np.median(b_oos)), 4)}")
    print(f"paired delta (A-B): full median={round(float(np.median(paired_delta_full)), 4)}  "
          f"oos median={round(float(np.median(paired_delta_oos)), 4)}")
    print(f"passive EW48: full_sharpe={passive_full_sharpe}  "
          f"oos_sharpe={passive['ew48_buyhold']['oos']['sharpe']}")
    print(f"effective skill bar (max of gate i, vi) = {skill_bar}")

    # ---------- G1' re-read of P1 candidates ----------
    rank_path = os.path.join(PATHS.root, "research", "strategy_rank.csv")
    with open(rank_path, encoding="utf-8") as fh:
        cands = [row for row in csv.DictReader(fh)
                 if row["school"] != "random_baseline" and row["status"] == "ok"]
    print(f"\nre-reading {len(cands)} P1 candidates against pre-registered G1'...")
    verdicts, survivors = [], []
    for row in cands:
        full_s = float(row["sharpe"])
        full_ar = float(row["annual_return"])
        full_dd = float(row["max_drawdown"])
        oos_s = float(row["oos_sharpe"])
        oos_ar = float(row["oos_annual_return"])
        n_tr = int(row["n_trades"])
        clauses = {
            "i_beats_rand_full_p95": full_s > p95_full,
            "ii_ann_pos": full_ar > 0,
            "iii_dd_ok": full_dd >= MAX_DD,
            "iv_trades_ok": n_tr >= MIN_TRADES,
            "v_oos_ok": oos_s > 0 and oos_ar > 0,
            "vi_beats_passive": full_s > passive_full_sharpe + PASSIVE_MARGIN,
        }
        passed = all(clauses.values())
        if passed:
            survivors.append(row["strategy"])
        verdicts.append({"strategy": row["strategy"], "school": row["school"],
                         "full_sharpe": full_s, "oos_sharpe": oos_s,
                         "n_trades": n_tr, "clauses": clauses, "g1_prime_pass": passed})
        flags = "".join(k.split("_")[0] for k, v in clauses.items() if not v)
        print(f"  {row['strategy']:<28} full_s={full_s:>7.3f} oos_s={oos_s:>7.3f} "
              f"{'PASS' if passed else 'fail(' + flags + ')'}")

    # ---------- output ----------
    out = {
        "batch": "P2-null-calibration",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/NULL_CALIBRATION.md (section 3, written before run)",
        "universe": {"pool": "core48-bare-codes", "n_syms": len(prices),
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": OOS_START,
        "families": {
            "A_random_engine_exit": {
                "n": N_BASELINES,
                "full_sharpe_p95": p95_full, "oos_sharpe_p95": p95_oos,
                "full_median": round(float(np.median(a_full)), 4),
                "oos_median": round(float(np.median(a_oos)), 4),
                "runs": fam_a},
            "B_random_entry_random_exit": {
                "n": N_PAIRED,
                "full_median": round(float(np.median(b_full)), 4),
                "oos_median": round(float(np.median(b_oos)), 4),
                "paired_delta_full_median": round(float(np.median(paired_delta_full)), 4),
                "paired_delta_oos_median": round(float(np.median(paired_delta_oos)), 4),
                "note": "engine exit rules still active underneath; random exit adds signal_reversed triggers",
                "runs": fam_b},
            "C_passive": {
                "runs": passive,
                "note": "no engine; EW sleeves, cash before listing; buyhold=13bp once, monthly=13bp*0.1 turnover"},
        },
        "g1_prime_gate": {
            "i_full_sharpe_gt": p95_full,
            "ii_ann_gt": 0, "iii_dd_min": MAX_DD, "iv_trades_min": MIN_TRADES,
            "v_oos_sharpe_gt": 0, "v_oos_ann_gt": 0,
            "vi_full_sharpe_gt": round(passive_full_sharpe + PASSIVE_MARGIN, 4),
            "effective_skill_bar": skill_bar},
        "survivors_g1_prime": survivors,
        "candidate_verdicts": verdicts,
        "trials_ledger": append_ledger(
            "P2-null-calibration", N_BASELINES + N_PAIRED + 2, "p2_calibration.json",
            note=f"{N_BASELINES} rand+engine + {N_PAIRED} rand+rand + 2 passive "
                 f"(not engine runs); T-03-F3 unified dict schema"),
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": N_BASELINES + N_PAIRED,
                  "workers": 1, "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "p2_calibration.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nsaved: {json_path}")

    print(f"\n===== G1' survivors ({len(survivors)}) =====")
    for s in survivors:
        print(f"  {s}")
    if not survivors:
        print("  (none - honest result; next = strategy-factory regen, see job #3 note)")
    print(f"\ntotal elapsed: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
