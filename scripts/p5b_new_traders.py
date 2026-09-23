"""P-5B new-trader due-diligence live-fire check (CEO orders O-20260923-2345).

Pre-registered (research/shortline/P5B_NEW_TRADERS.md, written first).
Same calibre as scripts/p5_random_entry.py (seed 20260924 fresh draw,
K=50, 25td greedy-gap fallback, 3m/6m/12m windows, EW passive, beat line
0.70 / dd line -0.35) -- applied to the 3 NEW registrants only:
ENGULF-CE-01 / NEEDLE-DE-01 / DROUGHT-CE-01.

FIRST BATCH through scripts/parallel_runner.py (CPU mobilization): the
150 strategy runs execute in a ProcessPool (floor(cores*0.8) workers),
audit section records the worker count. Determinism clause: pool only
distributes -- same seeds, same engine, same panel, results identical.

Ledger: prev 2521 + 206 (150 strategy + 50 passive + 6 anchors) = 2727.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (ExitPatch, SIGNAL_BUILDERS, anchor_gate,
                        build_panels, load_core, self_test_patches)
from parallel_runner import run_cells_parallel, worker_cap
from p5_random_entry import (BEAT_LINE, DD_RED_LINE, K, MIN_GAP_TD,
                             MIN_LISTED, W12M, W3M, W6M, WARMUP_TD,
                             passive_rel, sample_starts, slice_metrics)

SEED = 20260924            # fresh independent draw (P-5 used 20260923)
NEW_TRADERS = ["ENGULF-CE-01", "NEEDLE-DE-01", "DROUGHT-CE-01"]
LEDGER_PREV = 2521
LEDGER_ADDED = 206         # 150 strategy + 50 passive + 6 anchors
RES_JSON = os.path.join(PATHS.results_dir, "p5b_new_traders.json")
RES_CSV = os.path.join(PATHS.root, "research", "shortline",
                       "p5b_new_traders_results.csv")


def _p5b_starts(idx, listed):
    """Same greedy sampler, fresh seed (prereg s2)."""
    eligible = [p for p in range(WARMUP_TD, len(idx) - W6M + 1)
                if int(listed.iloc[p]) >= MIN_LISTED]
    if len(eligible) < K:
        raise SystemExit(f"P5B-GATE: eligible {len(eligible)} < K")
    gap = MIN_GAP_TD
    while True:
        rng = np.random.default_rng(SEED)
        accepted = []
        for i in rng.permutation(len(eligible)):
            p = eligible[i]
            if all(abs(p - a) >= gap for a in accepted):
                accepted.append(p)
                if len(accepted) == K:
                    break
        if len(accepted) == K:
            break
        gap -= 1
        if gap < 5:
            raise SystemExit("P5B-GATE: cannot reach K=50 at 5td gap")
    return {"starts": sorted(accepted), "gap_final": gap,
            "n_eligible": len(eligible)}


# module-level shared state, set per pool worker via the initializer
# (ProcessPool pickles job fns -- closures are FORBIDDEN)
_P = None
_PRICES = None
_IDX = None
_PARAMS = None
_OVR = None
_ENTRY = None


def _init_worker(prices, params, overrides, entry, panel):
    global _PRICES, _PARAMS, _OVR, _ENTRY, _P, _IDX
    _PRICES, _PARAMS, _OVR = prices, params, overrides
    _ENTRY = entry
    _P = panel
    _IDX = panel["close"].index


def _run_one_cell(tid: str, p: int) -> dict:
    """One (trader, start) cell inside a pool worker (top-level = picklable)."""
    sdate = _IDX[p]
    e12 = _IDX[min(p + W12M - 1, len(_IDX) - 1)]
    window = {s: df[(df.index >= sdate) & (df.index <= e12)]
              for s, df in _PRICES.items()}
    with ExitPatch(_OVR.get(tid, {})):
        res = run_backtest(window, _PARAMS[tid],
                           entry_signal=_ENTRY[tid],
                           exit_signal=(_ENTRY[tid] <= 0))
    widx = _IDX[p:p + W12M][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    m3, m6, m12 = (slice_metrics(eq, res["trades"], W3M),
                   slice_metrics(eq, res["trades"], W6M),
                   slice_metrics(eq, res["trades"], W12M))
    syms = _P["close"].columns[_P["close"].loc[sdate].notna()]
    rel = passive_rel(_P["close"], syms, sdate, e12)
    p3 = slice_metrics(rel, [], W3M)
    p6 = slice_metrics(rel, [], W6M)
    p12 = slice_metrics(rel, [], W12M)
    return {"trader": tid, "start": str(sdate.date()),
            "n_listed": int(len(syms)),
            "partial_12m": m12["n_bars"] < W12M,
            "ret_3m": m3["ret"], "ret_6m": m6["ret"], "ret_12m": m12["ret"],
            "p_ret_3m": p3["ret"], "p_ret_6m": p6["ret"],
            "p_ret_12m": p12["ret"],
            "sharpe_6m": m6["sharpe"], "dd_6m": m6["dd"],
            "trades_6m": m6["trades"],
            "sharpe_3m": m3["sharpe"], "dd_3m": m3["dd"],
            "sharpe_12m": m12["sharpe"], "dd_12m": m12["dd"],
            "beat_3m": m3["ret"] > p3["ret"],
            "beat_6m": m6["ret"] > p6["ret"],
            "beat_12m": m12["ret"] > p12["ret"]}


def main() -> int:
    t0 = time.time()
    print("=== P-5B new-trader due diligence (O-20260923-2345) ===")
    if not self_test_patches():
        print("P5B-GATE FAIL: patch self-test")
        return 2

    prices = load_core()
    P = build_panels(prices)
    close = P["close"]
    idx = close.index
    listed = close.notna().sum(axis=1)
    print(f"panel {idx[0].date()} -> {idx[-1].date()} | "
          f"{len(close.columns)} syms | worker cap = {worker_cap()}")

    # anchor hard gate: ALL SIX registered traders reproduce evidence
    anchors = {}
    all_ids = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in ("INTERN", "TRAINEE"):
            all_ids.append(t["id"])
            a = anchor_gate(t, prices)
            anchors[t["id"]] = {"ok": a["ok"], "cutoff": a.get("cutoff")}
            if not a["ok"]:
                print(f"P5B-GATE FAIL: anchor drift {t['id']} -- batch void")
                return 3
    print(f"anchors {len(anchors)}/6 OK (all registered reproduce)")

    new_traders = [load_trader(i) for i in NEW_TRADERS]
    samp = _p5b_starts(idx, listed)
    starts = samp["starts"]
    print(f"starts: K={len(starts)} gap={samp['gap_final']}td "
          f"(seed {SEED})")

    params, ovr, entry = {}, {}, {}
    for t in new_traders:
        entry[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params[t["id"]] = {k: v for k, v in t["params"].items()
                           if k != "entry"}
        ovr[t["id"]] = t.get("exit_overrides") or {}

    jobs = [(f"{t['id']}@{p}", _run_one_cell, (t["id"], p))
            for t in new_traders for p in starts]
    print(f"pool: {len(jobs)} strategy cells across {worker_cap()} workers")
    t_pool = time.time()
    results = run_cells_parallel(jobs, desc="cells",
                                 initializer=_init_worker,
                                 initargs=(prices, params, ovr, entry, P))
    workers = results.pop("__workers__")
    rows = list(results.values())
    pool_sec = time.time() - t_pool
    print(f"pool done: {len(rows)} cells in {pool_sec:.1f}s "
          f"(workers={workers})")

    def agg(tid):
        rs = [r for r in rows if r["trader"] == tid]
        full12 = [r for r in rs if not r["partial_12m"]]
        beat6 = [bool(r["beat_6m"]) for r in rs]
        beat3 = [bool(r["beat_3m"]) for r in rs]
        beat12 = [bool(r["beat_12m"]) for r in full12]
        dd6 = [r["dd_6m"] for r in rs]
        rate6 = float(np.mean(beat6))
        min_dd = float(min(dd6))
        worst = sorted(rs, key=lambda r: r["ret_6m"])[:5]
        return {"n_starts": len(rs), "beat_rate_3m": round(float(np.mean(beat3)), 4),
                "beat_rate_6m": round(rate6, 4),
                "beat_rate_12m": round(float(np.mean(beat12)), 4) if beat12 else None,
                "min_dd_6m": round(min_dd, 4),
                "median_ret_6m": round(float(np.median(
                    [r["ret_6m"] for r in rs])), 4),
                "worst_starts": [{"start": w["start"], "ret_6m": w["ret_6m"],
                                   "dd_6m": w["dd_6m"],
                                   "beat_6m": w["beat_6m"]} for w in worst],
                "verdict_pass": bool(rate6 >= BEAT_LINE and min_dd >= DD_RED_LINE)}

    per_trader = {t["id"]: agg(t["id"]) for t in new_traders}
    pooled_beat6 = float(np.mean([bool(r["beat_6m"]) for r in rows]))
    pooled_min_dd = float(min(r["dd_6m"] for r in rows))

    out = {
        "order": "O-20260923-2345", "prereg": "research/shortline/P5B_NEW_TRADERS.md",
        "seed": SEED, "k": len(starts), "min_gap_td": samp["gap_final"],
        "traders": NEW_TRADERS,
        "windows_td": {"3m": W3M, "6m": W6M, "12m": W12M},
        "judgment": {"beat_line_6m": BEAT_LINE, "dd_red_line": DD_RED_LINE},
        "anchors": anchors,
        "per_trader": per_trader,
        "pooled": {"beat_rate_6m": round(pooled_beat, 4) if False else round(pooled_beat6, 4),
                   "min_dd_6m": round(pooled_min_dd, 4)},
        "trials_ledger": {"prev_total": LEDGER_PREV,
                          "batch_trials": LEDGER_ADDED,
                          "total": LEDGER_PREV + LEDGER_ADDED,
                          "note": "150 strategy (3 new traders x 50 starts, "
                                  "PARALLEL pool) + 50 passive windows + "
                                  "6 anchors; prev 2521 = queue-batch head"},
        "audit": {"workers": workers, "pool_elapsed_sec": round(pool_sec, 1),
                  "note": "parallel_runner first use (O-2345 CPU "
                          "mobilization); pool distributes only -- "
                          "determinism unchanged"},
        "honesty": "robustness distribution re-check for NEW hires (selected "
                   "on full history), NOT new OOS; 2025+ windows discounted; "
                   "verdicts recorded in trader notes only, level/paper "
                   "untouched; paper tracking remains the forward channel",
        "runtime_sec": round(time.time() - t0, 1),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(RES_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=bool)

    cols = ["trader", "start", "n_listed", "partial_12m", "ret_3m", "ret_6m",
            "ret_12m", "p_ret_3m", "p_ret_6m", "p_ret_12m", "sharpe_3m",
            "sharpe_6m", "sharpe_12m", "dd_3m", "dd_6m", "dd_12m",
            "trades_6m", "beat_3m", "beat_6m", "beat_12m"]
    with open(RES_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})

    print("\n--- P-5B verdicts (main window 6m) ---")
    for tid, a in per_trader.items():
        print(f"{tid}: beat_rate_6m={a['beat_rate_6m']} "
              f"min_dd_6m={a['min_dd_6m']} "
              f"-> {'PASS' if a['verdict_pass'] else 'FAIL'}")
    print(f"pooled beat_rate_6m={out['pooled']['beat_rate_6m']} "
          f"min_dd_6m={out['pooled']['min_dd_6m']}")
    print(f"products: {RES_JSON}\n          {RES_CSV}")
    print(f"runtime {out['runtime_sec']}s (pool {pool_sec:.1f}s "
          f"@ {workers} workers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
