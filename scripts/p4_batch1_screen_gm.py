"""P-4 batch 1: A-layer easy-family screen (pre-registered P4_BATCH1_SCREEN.md).

Families (ASTYLE_ZOO batch 1): oversold_bounce / low_prox / dca_pulse /
turnover_spike. Default engine exits, T+1, 13bp cost always on, OOS 2025+,
in-batch nulls: 100 random-entry baselines + 2 passive EW benchmarks.
G1' gate per NULL_CALIBRATION s3: full Sharpe > max(rand_full_p95,
passive+0.1), annual>0, dd>=-35%, trades>=30, OOS double-positive.
Compute: ProcessPoolExecutor, workers = min(floor(cores*0.8), freeGB/0.5)
per CEO order O-20260923-1738 (20% system reserve).
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

from config import PATHS
from engine import run_backtest
from engine.metrics import annual_return, sharpe, max_drawdown

OOS_START = "2025-01-01"
N_BASELINES = 100
PREREG = "research/shortline/P4_BATCH1_SCREEN.md"

_P: dict | None = None      # worker global: prices dict
_IDX: pd.DatetimeIndex | None = None


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
    return {"sharpe": round(float(sharpe(seg)), 4),
            "annual_return": round(float(annual_return(seg)), 4),
            "max_drawdown": round(float(max_drawdown(seg)), 4)}


def _init_worker(prices, idx):
    global _P, _IDX
    _P, _IDX = prices, idx


def _run_task(task):
    name, entry, exit_ = task
    res = run_backtest(_P, {}, entry_signal=entry, exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=_IDX[:len(res["equity_curve"])])
    full = res["metrics"]
    oos = seg_metrics(eq, OOS_START)
    oos_trades = sum(1 for t in res["trades"] if str(t["date"]) >= OOS_START)
    return {"name": name, "full": full, "oos": oos,
            "n_trades": full["num_trades"], "oos_trades": oos_trades}


def build_tasks(P):
    close, vol, amt = P["close"], P["volume"], P["amount"]
    idx = close.index
    syms = list(close.columns)
    exit_never = pd.DataFrame(False, index=idx, columns=syms)
    tasks = []

    # -- family 1: oversold_bounce (N, X) with volume contraction --
    vol_ma20 = vol.rolling(20).mean()
    quiet = (vol < 0.8 * vol_ma20).fillna(False)
    for N in (10, 20, 60):
        ret_n = close.pct_change(N)
        for X in (0.08, 0.12, 0.20):
            e = ((ret_n < -X) & quiet).fillna(False)
            tasks.append((f"oversold_N{N}_X{int(X*100)}", e, exit_never))

    # -- family 2: low_prox (W, P) with up-day confirm --
    up_day = (close > close.shift(1)).fillna(False)
    for W in (120, 252):
        roll_min = close.rolling(W).min()
        prox = (close / roll_min - 1).fillna(1.0)
        for Pct in (0.03, 0.05, 0.08):
            e = ((prox < Pct) & up_day)
            tasks.append((f"lowprox_W{W}_P{int(Pct*100)}", e, exit_never))

    # -- family 3: dca_pulse (W pulse, mom filter) --
    day_no = pd.Series(np.arange(len(idx)), index=idx)
    for W in (5, 10, 20):
        pulse = (day_no % W == 0)
        for M in (20, 60):
            mom = close.pct_change(M)
            e = pd.DataFrame(
                np.tile((pulse & (mom.iloc[:, 0] > 0)).values[:, None],
                        (1, len(syms))), index=idx, columns=syms) \
                if False else (mom > 0).where(pulse, False).fillna(False)
            tasks.append((f"dca_pulse_W{W}_mom{M}", e, exit_never))

    # -- family 4: turnover_spike (z threshold) --
    z = (amt - amt.rolling(20).mean()) / (amt.rolling(20).std() + 1e-12)
    for Z in (1.5, 2.0, 2.5):
        e = ((z > Z) & up_day).fillna(False)
        tasks.append((f"turnover_z{Z}", e, exit_never))

    # -- random baselines: p in {0.02, 0.05} x 50 seeds --
    n_days = len(idx)
    for k in range(N_BASELINES):
        p = 0.02 if k < 50 else 0.05
        rng = np.random.default_rng(20_260 + k)
        e = pd.DataFrame((rng.random((n_days, len(syms))) < p).astype(int),
                         index=idx, columns=syms)
        tasks.append((f"rand_p{p}_s{k}", e, exit_never))

    return tasks


def passive_benchmarks(close: pd.DataFrame) -> dict:
    rets = close.pct_change().fillna(0)
    ew_daily = rets.mean(axis=1)
    eq_bh = (1 + ew_daily).cumprod()
    eq_m = eq_bh.copy()
    return {"passive_ew_bh": seg_metrics(eq_bh),
            "passive_ew_monthly": seg_metrics(eq_bh)}


def main():
    t0 = time.time()
    print("P-4 batch1 A-layer screen | prereg:", PREREG)
    prices = load_core()
    print(f"  universe: {len(prices)} core ETFs")
    P = {f: pd.DataFrame({s: df[f] for s, df in prices.items()})
         .sort_index().ffill()
         for f in ["open", "high", "low", "close", "volume", "amount"]}
    idx = P["close"].index

    tasks = build_tasks(P)
    n_family = 24
    print(f"  tasks: {len(tasks)} ({n_family} family + {len(tasks)-n_family} null)")

    cores = mp.cpu_count()
    free_gb = int(__import__("psutil").virtual_memory().available / 1e9) \
        if _try_psutil() else 32
    workers = min(int(cores * 0.8), int(free_gb / 0.5), 25)
    print(f"  workers={workers} (cores={cores}, freeGB~{free_gb}, cap25)")

    rows = []
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                              initargs=(prices, idx)) as ex:
        for r in ex.map(_run_task, tasks, chunksize=1):
            rows.append(r)
            print(f"  {r['name']:<24} full={r['full']['sharpe']:>7.3f} "
                  f"oos={r['oos']['sharpe']:>7.3f} trades={r['n_trades']:>4}")

    fam_rows = rows[:n_family]
    null_rows = rows[n_family:]

    rand_full = [r["full"]["sharpe"] for r in null_rows]
    rand_oos = [r["oos"]["sharpe"] for r in null_rows]
    p95_full = round(float(np.percentile(rand_full, 95)), 4)
    p95_oos = round(float(np.percentile(rand_oos, 95)), 4)

    pas = passive_benchmarks(P["close"])
    pas_full = pas["passive_ew_bh"]["sharpe"]
    vi = round(max(p95_full, pas_full + 0.1), 4)
    print(f"\nnull: n={len(rand_full)} full_p95={p95_full} oos_p95={p95_oos} "
          f"passive={pas_full} -> vi={vi}")

    survivors = []
    for r in fam_rows:
        f_, o_ = r["full"], r["oos"]
        r["vi_line"] = vi
        r["i_line_oos"] = p95_oos
        r["g1_prime_pass"] = bool(
            f_["sharpe"] > vi and f_["annual_return"] > 0
            and f_["max_drawdown"] >= -0.35 and r["n_trades"] >= 30
            and o_["sharpe"] > 0 and o_["annual_return"] > 0)
        if r["g1_prime_pass"]:
            survivors.append(r["name"])

    ok = sorted(fam_rows, key=lambda r: r["full"]["sharpe"], reverse=True)
    csv_path = os.path.join(PATHS.root, "research", "p4_batch1_results.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "sharpe", "annual_return", "max_drawdown",
                    "n_trades", "oos_sharpe", "oos_annual", "oos_max_dd",
                    "vi_line", "i_line_oos", "g1_prime_pass"])
        for r in ok:
            w.writerow([r["name"], r["full"]["sharpe"], r["full"]["annual_return"],
                        r["full"]["max_drawdown"], r["n_trades"],
                        r["oos"]["sharpe"], r["oos"]["annual_return"],
                        r["oos"]["max_drawdown"], r["vi_line"], r["i_line_oos"],
                        r["g1_prime_pass"]])
    print("saved:", csv_path)

    out = {
        "batch": "P4-batch1-A-layer",
        "prereg": PREREG,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "oos_start": OOS_START,
        "gate_g1_prime": {"vi": vi, "passive_full": pas_full,
                          "rand_full_p95": p95_full, "rand_oos_p95": p95_oos,
                          "criteria": "full>vi & ann>0 & dd>=-35% & trades>=30 & oos double+"},
        "survivors_g1_prime": survivors,
        "passive": pas,
        "trial_ledger": {"prior_N": 1435, "this_batch": len(tasks),
                         "new_N": 1435 + len(tasks)},
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": len(tasks), "workers": workers,
                  "cpu_cap_policy": "O-20260923-1738 floor(cores*0.8), reserve 20%"},
        "family_runs": fam_rows, "null_runs": null_rows,
    }
    json_path = os.path.join(PATHS.results_dir, "p4_batch1.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print("saved:", json_path)
    print(f"\n===== G1' survivors ({len(survivors)}) =====")
    for s in survivors:
        print(" ", s)
    if not survivors:
        print("  (none - honest result)")
    print(f"elapsed {time.time()-t0:.0f}s | workers={workers}")


def _try_psutil():
    try:
        import psutil  # noqa
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()
