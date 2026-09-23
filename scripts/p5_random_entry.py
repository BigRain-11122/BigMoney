"""P-5 random-entry live-fire check (CEO order O-20260923-1816).

Pre-registered in research/shortline/P5_RANDOM_ENTRY.md BEFORE the run
(written 18:35, frozen). No threshold/seed changes after results; no
param tuning from results (iron rules, same source as BACKTEST_PLAN).

Pipeline per trader (registered evidence untouched):
  anchor gate (live.paper.anchor_gate) must PASS first, then 50 random
  historical starts: full-history CAUSAL entry signal (warmup uses past
  closes only), engine runs forward from the start with real T+1/13bp/
  exits, fixed evaluation windows 3m/6m/12m (63/126/252 trading days),
  vs same-window passive = EW buy&hold of core48 members listed at the
  start (equal cash, price-relative mean).

Verdict per trader (pre-registered): beat_rate_6m >= 0.70 AND
min_dd_6m >= -0.35 (no single start breaks the -35% red line).

Honesty clauses: 3 traders were selected on full history -> this is a
robustness DISTRIBUTION re-check, NOT a new out-of-sample test; windows
overlapping 2025+ are read with the OOS discount; true forward evidence
remains the paper tracking pipeline. Adjacent 6m windows overlap ~80%
under the 25td min gap -> 50 starts are correlated samples (effective
n < 50, disclosed in prereg s4).
"""
import csv
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (PAPER_LEVELS, SIGNAL_BUILDERS, ExitPatch,
                        anchor_gate, build_panels, load_core,
                        self_test_patches)
from science_gates import ledger_head  # T-03-F3 (audit P0-7)

SEED = 20260923
K = 50
MIN_GAP_TD = 25          # panel-fit adaptation (2mo infeasible, prereg s2)
WARMUP_TD = 252
W3M, W6M, W12M = 63, 126, 252
MIN_LISTED = 24
BEAT_LINE = 0.70
DD_RED_LINE = -0.35
LEDGER_PREV = ledger_head()["total"]   # T-03-F3 data-driven chain head (recorded 1680 at run time)
LEDGER_ADDED = 203       # 150 strategy + 50 passive + 3 anchors
RES_JSON = os.path.join(PATHS.results_dir, "p5_random_entry.json")
RES_CSV = os.path.join(PATHS.root_dir, "research", "p5_random_entry_results.csv"
                       ) if hasattr(PATHS, "root_dir") else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "research", "p5_random_entry_results.csv")


def sample_starts(idx: pd.DatetimeIndex, listed: pd.Series) -> dict:
    """Deterministic greedy sampling per prereg s2 (seed fixed)."""
    eligible = [p for p in range(WARMUP_TD, len(idx) - W6M + 1)
                if int(listed.iloc[p]) >= MIN_LISTED]
    if len(eligible) < K:
        raise SystemExit(f"P5-GATE: eligible starts {len(eligible)} < K={K}")
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
            raise SystemExit("P5-GATE: cannot reach K=50 even at 5td gap")
    return {"starts": sorted(accepted), "gap_final": gap,
            "n_eligible": len(eligible)}


def slice_metrics(eq: pd.Series, trades: list, k: int) -> dict:
    seg = eq.iloc[:min(k, len(eq))]
    if len(seg) < 2:
        return {"ret": 0.0, "sharpe": 0.0, "dd": 0.0, "trades": 0, "n_bars": len(seg)}
    end = seg.index[-1]
    return {"ret": round(float(seg.iloc[-1] / seg.iloc[0] - 1), 6),
            "sharpe": round(float(sharpe(seg)), 4),
            "dd": round(float(max_drawdown(seg)), 4),
            "trades": sum(1 for tr in trades if pd.Timestamp(tr["date"]) <= end),
            "n_bars": int(len(seg))}


def passive_rel(close: pd.DataFrame, syms, sdate, e12) -> pd.Series:
    """EW buy&hold price relatives of listed members (equal cash at start)."""
    base = close.loc[sdate, syms]
    rel = close.loc[sdate:e12, syms] / base
    return rel.mean(axis=1)


def run_audit() -> dict:
    """O-1810 discipline: no audit section -> not ledgered."""
    try:
        out = subprocess.run(
            [sys.executable, os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "compute_audit.py")],
            capture_output=True, text=True, timeout=120)
        rec = json.loads(out.stdout.strip().splitlines()[-1])
        return {"verdict": rec.get("verdict"), "sampled_at": rec.get("ts"),
                "audit_file": "results/compute_audit.json"}
    except Exception as exc:  # audit unavailable = batch NOT ledgered
        return {"verdict": "UNAVAILABLE", "error": str(exc)}


def main() -> int:
    t0 = time.time()
    print("=== P-5 random-entry live-fire check (O-20260923-1816) ===")
    if not self_test_patches():
        print("P5-GATE FAIL: patch self-test -- abort")
        return 2

    prices = load_core()
    P = build_panels(prices)
    close = P["close"]
    idx = close.index
    listed = close.notna().sum(axis=1)
    print(f"panel {idx[0].date()} -> {idx[-1].date()} | {len(close.columns)} syms")

    traders = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            traders.append(t)
    print(f"traders: {[t['id'] for t in traders]}")
    if len(traders) != 3:
        print("P5-GATE FAIL: expected 3 registered paper-level traders")
        return 2

    anchors = {}
    for t in traders:
        a = anchor_gate(t, prices)
        anchors[t["id"]] = {"ok": a["ok"], "cutoff": a.get("cutoff")}
        print(f"anchor {t['id']}: {'PASS' if a['ok'] else 'FAIL'}")
        if not a["ok"]:
            print("P5-GATE FAIL: anchor drift -- batch void, trader JSONs untouched")
            return 3

    samp = sample_starts(idx, listed)
    starts = samp["starts"]
    sdates = [idx[p] for p in starts]
    print(f"starts: K={len(starts)} gap={samp['gap_final']}td "
          f"eligible={samp['n_eligible']} "
          f"first={sdates[0].date()} last={sdates[-1].date()}")

    entries, params_by_id = {}, {}
    for t in traders:
        entries[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params_by_id[t["id"]] = {k: v for k, v in t["params"].items()
                                 if k != "entry"}

    rows = []
    for t in traders:
        entry = entries[t["id"]]
        exit_sig = entry <= 0
        for p in starts:
            sdate = idx[p]
            e12 = idx[min(p + W12M - 1, len(idx) - 1)]  # inclusive 252-bar end
            window = {s: df[(df.index >= sdate) & (df.index <= e12)]
                      for s, df in prices.items()}
            with ExitPatch(t.get("exit_overrides")):
                res = run_backtest(window, params_by_id[t["id"]],
                                   entry_signal=entry, exit_signal=exit_sig)
            widx = idx[p:p + W12M][:len(res["equity_curve"])]
            eq = pd.Series(res["equity_curve"], index=widx)
            m3, m6, m12 = (slice_metrics(eq, res["trades"], W3M),
                           slice_metrics(eq, res["trades"], W6M),
                           slice_metrics(eq, res["trades"], W12M))
            syms = close.columns[close.loc[sdate].notna()]
            rel = passive_rel(close, syms, sdate, e12)
            p3 = slice_metrics(rel, [], W3M)
            p6 = slice_metrics(rel, [], W6M)
            p12 = slice_metrics(rel, [], W12M)
            rows.append({
                "trader": t["id"], "start": str(sdate.date()),
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
                "beat_12m": m12["ret"] > p12["ret"]})

    def agg(tid: str) -> dict:
        rs = [r for r in rows if r["trader"] == tid]
        full12 = [r for r in rs if not r["partial_12m"]]
        beat6 = [bool(r["beat_6m"]) for r in rs]
        beat3 = [bool(r["beat_3m"]) for r in rs]
        beat12 = [bool(r["beat_12m"]) for r in full12]
        ret6 = [r["ret_6m"] for r in rs]
        sh6 = [r["sharpe_6m"] for r in rs]
        dd6 = [r["dd_6m"] for r in rs]
        rate6 = float(np.mean(beat6))
        min_dd = float(min(dd6))
        worst = sorted(rs, key=lambda r: r["ret_6m"])[:5]
        return {"n_starts": len(rs), "n_full_12m": len(full12),
                "beat_rate_3m": round(float(np.mean(beat3)), 4),
                "beat_rate_6m": round(rate6, 4),
                "beat_rate_12m": round(float(np.mean(beat12)), 4) if beat12 else None,
                "min_dd_6m": round(min_dd, 4),
                "median_ret_6m": round(float(np.median(ret6)), 4),
                "median_sharpe_6m": round(float(np.median(sh6)), 4),
                "median_dd_6m": round(float(np.median(dd6)), 4),
                "q25_ret_6m": round(float(np.quantile(ret6, .25)), 4),
                "q75_ret_6m": round(float(np.quantile(ret6, .75)), 4),
                "worst_starts": [{"start": w["start"], "ret_6m": w["ret_6m"],
                                   "dd_6m": w["dd_6m"], "p_ret_6m": w["p_ret_6m"],
                                   "beat_6m": w["beat_6m"]} for w in worst],
                "verdict_pass": bool(rate6 >= BEAT_LINE and min_dd >= DD_RED_LINE)}

    per_trader = {t["id"]: agg(t["id"]) for t in traders}
    pooled_beat6 = float(np.mean([bool(r["beat_6m"]) for r in rows]))
    pooled_min_dd = float(min(r["dd_6m"] for r in rows))

    audit = run_audit()
    out = {
        "order": "O-20260923-1816", "prereg": "research/shortline/P5_RANDOM_ENTRY.md",
        "seed": SEED, "k": len(starts), "min_gap_td": samp["gap_final"],
        "gap_note": ("2-month gap infeasible on 2020-01-02-anchored panel "
                     "(62 eligible months < 100); 25td = K-50 panel-fit cap, "
                     "prereg s2 adjudication, disclosed"),
        "windows_td": {"3m": W3M, "6m": W6M, "12m": W12M},
        "start_positions": starts,
        "start_dates": [str(d.date()) for d in sdates],
        "n_eligible": samp["n_eligible"],
        "warmup_td": WARMUP_TD, "min_listed": MIN_LISTED,
        "passive": "EW buy&hold of core48 members listed at start (equal cash)",
        "judgment": {"beat_line_6m": BEAT_LINE, "dd_red_line": DD_RED_LINE,
                     "rule": "per-trader PASS iff beat_rate_6m>=0.70 AND "
                             "min_dd_6m>=-0.35 (frozen prereg s4)"},
        "anchors": anchors,
        "per_trader": per_trader,
        "pooled": {"beat_rate_6m": round(pooled_beat6, 4),
                   "min_dd_6m": round(pooled_min_dd, 4)},
        "trials_ledger": {
            "prev_total": LEDGER_PREV, "batch_trials": LEDGER_ADDED,
            "total": LEDGER_PREV + LEDGER_ADDED,
            "note": ("150 strategy runs (3 traders x 50 starts) + 50 passive "
                     "windows + 3 anchor reproductions; prev 1680 = formal "
                     "chain 1556 + 124 GM-session P-4b1 dual-implementation "
                     "runs retro-counted (real trials, prereg s5)")},
        "audit": audit,
        "honesty": ("robustness distribution re-check, NOT new OOS; 2025+ "
                    "windows read with OOS discount; 25td gap -> adjacent 6m "
                    "windows overlap ~80%, effective n < 50; no param changes "
                    "from these results; paper tracking remains the forward "
                    "evidence channel"),
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

    print(f"\n--- P-5 verdicts (main window 6m) ---")
    for tid, a in per_trader.items():
        print(f"{tid}: beat_rate_6m={a['beat_rate_6m']} "
              f"min_dd_6m={a['min_dd_6m']} "
              f"-> {'PASS' if a['verdict_pass'] else 'FAIL'}")
    print(f"pooled beat_rate_6m={out['pooled']['beat_rate_6m']} "
          f"min_dd_6m={out['pooled']['min_dd_6m']}")
    print(f"products: {RES_JSON}\n          {RES_CSV}")
    print(f"runtime {out['runtime_sec']}s | audit {audit.get('verdict')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
