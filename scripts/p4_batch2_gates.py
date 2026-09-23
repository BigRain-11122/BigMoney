"""P-4 batch 2 engine gates -- R37 of research/shortline/P4_BATCH2.md s7.

Runs AFTER engine/backtester.py gained the additive fill_guard param and
BEFORE any stock-panel build (R38). Every gate must PASS to unlock R38.

Gates (spec s7 R37 list, verbatim mapping):
  G0 smoke 20/20 (subprocess)                -- full pipeline regression
  G1 432-grid determinism, 5 sampled combos  -- fill_guard=None path
     byte-identical vs recorded results/<combo_hash>.json artifacts
     (proves the guard change is invisible when off, and replicates the
      original 432 panel: bare-code core48, min_listing 60, open-fallback
      -- bit-exact match IS the replication proof)
  G2 all-True guard == None guard (dict form + single-DataFrame form)
  G3 buy-rejection unit: sealed-limit-up open -> pending DROPPED, never
     retried on the stale signal (fresh signal may re-queue: not tested)
  G4 sell-deferral unit: sealed-limit-down close -> exit deferred, force-
     executed at next fillable close with ORIGINAL reason/size (1-day and
     2-day chains); stock code names exercise the T+1 path in-engine
  G5 is_t0: stock prefixes 60/00/30/68 -> False (T+1); ETF T+0 set sanity
  G6 CostPatch x1/x2/x3/restore = 0.0013041/0.0026082/0.0039123/0.0013041
     (stock round trip = 2 x 13.041bp = 26.082bp ~= spec s3.2 26bp;
      x2 = 52bp / x3 = 78bp stress scale, J14 mechanism re-verified)
  G7 guard-active determinism: guarded scenario rerun byte-identical

Products: results/shortline_p4_batch2_gates.json. Exit 0 iff all PASS.
Note: G1 is a one-time regression for THIS engine change; update_daily
appends new bars after 2026-09-22, so recorded equity lengths drift with
data growth (panel end == 2026-09-22 today -> bit-exact now).
"""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS, all_combinations, combo_hash
from engine import run_backtest
import engine.backtester as _eb
from knowledge.rules import is_t0
from live.paper import CostPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(PATHS.results_dir, "shortline_p4_batch2_gates.json")
G1_SAMPLE_IDX = [0, 108, 216, 324, 431]   # deterministic 5-point sample


def load_core48_like_432() -> dict:
    """Replicate tasks.backtest_task._load_prices as of the original 432 run.

    At 432-run time data/daily held exactly the 48 bare-code CSVs (recorded
    equity length 1631 == core48 union calendar, verified pre-gate), so the
    faithful panel = bare codes only, min_listing 60, open-fallback.
    Bare code = pure 6-digit stem (prefixed twins are 'sh510010' style).
    Bit-exact G1 match doubles as the replication proof.
    """
    out = {}
    for f in os.listdir(PATHS.daily_dir):
        if not f.endswith(".csv"):
            continue
        sym = f[:-4]
        if not re.fullmatch(r"\d{6}", sym):
            continue
        df = pd.read_csv(os.path.join(PATHS.daily_dir, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < 60:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        out[sym] = df[["open", "high", "low", "close", "volume"]].copy()
    return out


def run_engine(prices, params, entry=None, exit_=None, fill_guard=None):
    return run_backtest(prices, params, entry_signal=entry,
                        exit_signal=exit_, fill_guard=fill_guard)


def synth_panel(syms, days=12, price=100.0):
    """Constant-price synthetic panel: built-in MA signals never fire."""
    idx = pd.bdate_range("2026-01-01", periods=days)
    out = {}
    for s in syms:
        df = pd.DataFrame({"open": price, "high": price, "low": price,
                           "close": price, "volume": 1.0}, index=idx)
        out[s] = df
    return out, idx


def sig_df(idx, syms, on_days):
    """All-False entry/exit frame with True only for sym->day-index list."""
    df = pd.DataFrame(False, index=idx, columns=syms)
    for s, days in on_days.items():
        df.loc[idx[days], s] = True
    return df


def guard_df(idx, syms, false_days):
    """All-True fillability frame with False only where listed."""
    df = pd.DataFrame(True, index=idx, columns=syms)
    for s, days in false_days.items():
        if not isinstance(days, (list, tuple)):
            days = [days]
        df.loc[idx[list(days)], s] = False
    return df


BASE_PARAMS = {"position_size_pct": 0.10, "max_positions": 5}


def gate_g0(results):
    if "--skip-smoke" in sys.argv:
        results.append({"gate": "G0", "name": "smoke 20/20 (subprocess)",
                        "status": "SKIP", "detail": "--skip-smoke flag"})
        return True
    p = subprocess.run([sys.executable, "-m", "smoke_test"], cwd=ROOT,
                      capture_output=True, text=True, timeout=600)
    ok = p.returncode == 0 and "20/20 PASS" in p.stdout
    tail = [l for l in p.stdout.strip().splitlines() if l][-1:]
    results.append({"gate": "G0", "name": "smoke 20/20 (subprocess)",
                    "status": "PASS" if ok else "FAIL",
                    "detail": tail[0] if tail else f"rc={p.returncode}"})
    return ok


def gate_g1(results, prices):
    combos = all_combinations()
    ok = len(combos) == 432
    rows = []
    for k in G1_SAMPLE_IDX:
        combo = combos[k]
        h = combo_hash(combo)
        path = os.path.join(PATHS.results_dir, f"{h}.json")
        if not os.path.exists(path):
            rows.append({"hash": h, "idx": k, "status": "FAIL",
                         "detail": "recorded artifact missing"})
            ok = False
            continue
        rec = json.load(open(path, encoding="utf-8"))
        res = run_engine(prices, combo)          # fill_guard=None default
        m_ok = res["metrics"] == rec["metrics"]
        e_ok = res["equity_curve"] == rec["equity_curve"]
        t_ok = len(res["trades"]) == rec["n_trades"]
        row_ok = m_ok and e_ok and t_ok
        ok = ok and row_ok
        rows.append({"hash": h, "idx": k, "status": "PASS" if row_ok else "FAIL",
                     "metrics_eq": m_ok, "equity_eq": e_ok,
                     "trades_eq": t_ok,
                     "sharpe": res["metrics"].get("sharpe")})
    results.append({"gate": "G1", "name": "432-grid determinism (fill_guard=None, 5 sampled combos)",
                    "status": "PASS" if ok else "FAIL", "rows": rows})
    return ok


def gate_g2(results, prices):
    combos = all_combinations()
    combo = combos[0]
    base = run_engine(prices, combo)
    idx = pd.DatetimeIndex(
        pd.DataFrame({s: df["close"] for s, df in prices.items()}).sort_index().index)
    cols = list(prices.keys())
    all_true = pd.DataFrame(True, index=idx, columns=cols)
    r_dict = run_engine(prices, combo, fill_guard={"buy": all_true, "sell": all_true})
    r_flat = run_engine(prices, combo, fill_guard=all_true)
    ok = (base["equity_curve"] == r_dict["equity_curve"] == r_flat["equity_curve"]
          and base["metrics"] == r_dict["metrics"] == r_flat["metrics"]
          and base["trades"] == r_dict["trades"] == r_flat["trades"])
    results.append({"gate": "G2", "name": "all-True guard == None guard (dict + flat forms)",
                    "status": "PASS" if ok else "FAIL",
                    "n_equity": len(base["equity_curve"])})
    return ok


def gate_g3(results):
    """Buy rejection: guard False on execution day -> pending dropped."""
    panel, idx = synth_panel(["600000"])
    entry = sig_df(idx, ["600000"], {"600000": 2})        # signal day T=2
    params = dict(BASE_PARAMS)
    blocked = run_engine(panel, params, entry=entry,
                         fill_guard={"buy": guard_df(idx, ["600000"], {"600000": 3})})
    control = run_engine(panel, params, entry=entry)     # no guard
    ok = (len(blocked["trades"]) == 0
          and all(v == 1_000_000.0 for v in blocked["equity_curve"])
          and len(control["trades"]) == 0
          and control["equity_curve"][3] < 1_000_000.0)
    results.append({"gate": "G3", "name": "buy-rejection unit (pending dropped, not retried)",
                    "status": "PASS" if ok else "FAIL",
                    "blocked_eq_flat": all(v == 1_000_000.0 for v in blocked["equity_curve"]),
                    "control_bought_day3": control["equity_curve"][3] < 1_000_000.0})
    return ok


def _g4_run(sell_false_days, n_days=12):
    panel, idx = synth_panel(["300750"], days=n_days)
    entry = sig_df(idx, ["300750"], {"300750": 0})       # buy day1 open
    exit_ = sig_df(idx, ["300750"], {"300750": 5})       # reversed day5
    guard = guard_df(idx, ["300750"], {"300750": sell_false_days})
    res = run_engine(panel, dict(BASE_PARAMS), entry=entry, exit_=exit_,
                     fill_guard={"sell": guard})
    return res, idx


def gate_g4(results):
    """Sell deferral: exit decided day5, force-executed at next fillable close."""
    ctrl, idx = _g4_run([])          # no False days -> plain run (sell never blocked)
    one, _ = _g4_run([5])
    two, _ = _g4_run([5, 6])
    t_ctrl, t_one, t_two = ctrl["trades"], one["trades"], two["trades"]
    ok = (len(t_ctrl) == 1 and len(t_one) == 1 and len(t_two) == 1
          and str(idx[5].date()) == t_ctrl[0]["date"]
          and str(idx[6].date()) == t_one[0]["date"]
          and str(idx[7].date()) == t_two[0]["date"]
          and t_one[0]["reason"] == t_ctrl[0]["reason"] == "signal_reversal"
          and t_one[0]["hold_days"] == t_ctrl[0]["hold_days"] + 1
          and t_two[0]["hold_days"] == t_ctrl[0]["hold_days"] + 2)
    results.append({"gate": "G4", "name": "sell-deferral unit (1d + 2d chains, stock-code T+1)",
                    "status": "PASS" if ok else "FAIL",
                    "close_dates": [t["date"] for t in (t_ctrl[0], t_one[0], t_two[0])],
                    "hold_days": [t["hold_days"] for t in (t_ctrl[0], t_one[0], t_two[0])],
                    "reasons": [t["reason"] for t in (t_ctrl[0], t_one[0], t_two[0])]})
    return ok, one


def gate_g5(results):
    stocks = ["600000", "000001", "300750", "688111"]
    etf_t0 = ["511880", "511260", "511010", "518880", "159934"]
    ok = (not any(is_t0(s) for s in stocks)
          and all(is_t0(s) for s in etf_t0))
    results.append({"gate": "G5", "name": "is_t0: 60/00/30/68 -> T+1; ETF T+0 sanity",
                    "status": "PASS" if ok else "FAIL",
                    "stocks_t1": {s: not is_t0(s) for s in stocks},
                    "etf_t0": {s: is_t0(s) for s in etf_t0}})
    return ok


def gate_g6(results):
    def rate(f):
        return (f.commission_rate + f.handling_fee
                + f.supervision_fee + f.slippage_a)

    base = round(rate(_eb.FeeSchedule()), 7)
    with CostPatch(1):
        r1 = round(rate(_eb.FeeSchedule()), 7)
    with CostPatch(2):
        r2 = round(rate(_eb.FeeSchedule()), 7)
    with CostPatch(3):
        r3 = round(rate(_eb.FeeSchedule()), 7)
    restored = round(rate(_eb.FeeSchedule()), 7)
    ok = (r1 == 0.0013041 and r2 == 0.0026082 and r3 == 0.0039123
          and restored == 0.0013041 == base)
    results.append({"gate": "G6", "name": "CostPatch x1/x2/x3/restore (stock 26bp round trip scale)",
                    "status": "PASS" if ok else "FAIL",
                    "x1": r1, "x2": r2, "x3": r3, "restored": restored,
                    "stock_round_trip_bp": round(2 * r1 * 1e4, 4),
                    "stress_round_trip_bp": {"x2": round(2 * r2 * 1e4, 4),
                                             "x3": round(2 * r3 * 1e4, 4)}})
    return ok


def gate_g7(results, one):
    again, _ = _g4_run([5])
    ok = (again["trades"] == one["trades"]
          and again["equity_curve"] == one["equity_curve"])
    results.append({"gate": "G7", "name": "guard-active determinism (rerun identical)",
                    "status": "PASS" if ok else "FAIL"})
    return ok


def _jsonable(obj):
    """numpy scalar -> python scalar, recursively (backtest_task precedent)."""
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def main():
    t0 = time.time()
    results = []
    all_ok = True

    all_ok &= gate_g0(results)

    print("loading core48 panel (432-replication shape)...", flush=True)
    prices = load_core48_like_432()
    print(f"  {len(prices)} bare-code symbols", flush=True)

    all_ok &= gate_g1(results, prices)
    all_ok &= gate_g2(results, prices)
    all_ok &= gate_g3(results)
    g4_ok, one = gate_g4(results)
    all_ok &= g4_ok
    all_ok &= gate_g5(results)
    all_ok &= gate_g6(results)
    all_ok &= gate_g7(results, one)

    for r in results:
        line = f"[{r['status']}] {r['gate']} {r['name']}"
        print(line, flush=True)

    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "round": "R37 (P4_BATCH2.md s7 execution order)",
        "engine_change": "additive fill_guard param (default None = legacy "
                         "byte-identical); buy-rejection drop + sell-deferral "
                         "force-execute at next fillable close",
        "all_pass": bool(all_ok),
        "elapsed_sec": round(time.time() - t0, 1),
        "gates": results,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(payload), fh, ensure_ascii=False, indent=2)
    print(f"\nSummary: {'ALL PASS' if all_ok else 'GATE FAIL'} "
          f"({round(time.time() - t0, 1)}s) -> {OUT_JSON}", flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
