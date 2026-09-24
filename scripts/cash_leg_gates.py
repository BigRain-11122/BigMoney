"""T-2026-09-24-09 -- CASH_LEG acceptance gates (prereg research/CASH_LEG.md).

Engine-feature acceptance batch (tool-validation class, cost_v2_gates
precedent): ZERO registration claims, zero survivor screening, zero N_eff
growth (audit.ledger_trials_added=0). Runs AFTER engine/backtester.py
gained the additive cash_parking flag (default None = legacy path
byte-identical) and firm/risk/regime.py gained the additive
major_bear_series helper. Any gate red -> fix -> re-run ALL gates.

Gates (frozen in prereg s4):
  G0 smoke: 23/23 with the flag absent (default-path zero perturbation)
  G1 legacy byte-identity: 6/6 registered-trader anchor gate (live.paper
     machinery, flag OFF) -- registered evidence reproduced bit-level =
     end-to-end proof the engine edit is invisible when off
  G2 determinism: flag-ON synthetic double-run identical
  G3 hand-computed fixture: 2-symbol flat panel, known rate series with
     bear / non-bear / missing-rate(->ffill) days; parked balances,
     yield and equity chain re-derived by hand (J18 self-consistency law)
  G4 no-look-ahead: rates/bear rows dated AFTER the window never change
     in-window results (mechanical truncation invariance); rate(T) is
     published morning-of-T (documentation-level statement, prereg s2)
  G5 keyset discipline: flag-OFF keys == legacy set (no new keys);
     flag-ON new keys == exactly the five frozen in prereg s2
  G6 descriptive (no gate verdict): 6 traders flag ON vs OFF on the
     evidence-cutoff-truncated panel; bear_days / parked_days /
     parking_yield_total / d_sharpe / d_annual disclosed per trader

Products: results/cash_leg_acceptance.json (top-level evidence_cutoff +
audit block). Exit 0 iff all gates pass; exit 2 = data-completeness
precondition failed (honest stop, fetch guidance printed).

Usage:
    python scripts/cash_leg_gates.py gates    # full acceptance (real data)
    python scripts/cash_leg_gates.py selftest  # offline synthetic only
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from firm.risk import regime as _regime
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (
    build_panels, load_core, SIGNAL_BUILDERS, ExitPatch, anchor_gate,
    evidence_cutoff,
)
from scripts.science_gates import cutoff_meta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_CSV = os.path.join(ROOT, "Money0923", "data", "repo_daily.csv")
OUT_JSON = os.path.join(PATHS.results_dir, "cash_leg_acceptance.json")
CUTOFF = "2026-09-22"          # prereg s3 evidence-cutoff discipline
PARK_FRAC = 0.80               # R-配3 frozen value (prereg s2)
NEW_KEYS = {"parked_days", "bear_days_in_window", "parking_yield_total",
            "parked_balance_end", "parking_accrual_series"}


# ---------------------------------------------------------------- fixture
def _fixture_prices(days: int = 4) -> dict:
    """2-symbol flat-price panel (open=close=10) -- no trades ever fire."""
    idx = pd.bdate_range("2026-01-05", periods=days)
    frame = pd.DataFrame({"open": 10.0, "high": 10.0, "low": 10.0,
                          "close": 10.0, "volume": 1000.0,
                          "amount": 10000.0}, index=idx)
    return {"AAA": frame, "BBB": frame.copy()}


def _fixture_no_signals(prices: dict) -> pd.DataFrame:
    idx = next(iter(prices.values())).index
    return pd.DataFrame(False, index=idx, columns=list(prices))


def _fixture_cp(rates: dict, bears: dict) -> dict:
    """cash_parking dict from {date->rate%} and {date->bool}."""
    repo = pd.Series(rates)
    repo.index = pd.to_datetime(list(rates))
    bear = pd.Series(bears)
    bear.index = pd.to_datetime(list(bears))
    return {"repo_rate": repo, "major_bear": bear, "bear_park_frac": PARK_FRAC}


def _fixture_case():
    """Prereg G3 fixture: 4 days = bear / bear / non-bear / bear+missing-rate."""
    prices = _fixture_prices(4)
    idx = next(iter(prices.values())).index
    rates = {str(idx[0].date()): 1.0, str(idx[1].date()): 2.52,
             str(idx[2].date()): 1.26}          # day-4 rate missing -> ffill
    bears = {str(idx[0].date()): True, str(idx[1].date()): True,
             str(idx[2].date()): False, str(idx[3].date()): True}
    return prices, _fixture_cp(rates, bears), idx


def _g3_expected(idx) -> dict:
    """Hand-derived 4-day chain (prereg s2 semantics; float-honest arithmetic,
    written day-by-day -- NOT by calling the engine).

    pos_val = 0 on every day (flat prices, no signals -> no positions).
    accrual series is per-day over the WHOLE window (0.0 on no-deposit days).
    """
    cash = 1_000_000.0
    parked = 0.0
    eq, accr, yield_total = [], [], 0.0
    parked_days = bear_days = 0
    # day 1 (bear): mark = cash (nothing on deposit); interest 0; park 80%
    eq.append(cash + parked)                       # 1,000,000
    accr.append(0.0)
    parked = min(cash, PARK_FRAC * cash)           # 0.8 float -> 800000.0000000001
    cash -= parked
    bear_days += 1
    # day 2 (bear): mark = cash + held; interest 2.52% on held; settle; re-park
    eq.append(cash + parked)                       # back to 1,000,000
    interest = parked * 2.52 / 100.0 / 252.0       # 80.0 (float ~8e-16 off)
    eq[-1] = eq[-1] + interest                     # mark includes the yield
    accr.append(round(interest, 6))
    yield_total += interest
    cash += parked + interest
    parked_days += 1
    parked = min(cash, PARK_FRAC * cash)           # re-park 80% of new equity
    cash -= parked
    bear_days += 1
    # day 3 (NON-bear): interest accrues on the held balance, then FULL release
    eq.append(cash + parked)                       # 1,000,000 + int2
    interest = parked * 1.26 / 100.0 / 252.0       # 40.0032
    eq[-1] = eq[-1] + interest
    accr.append(round(interest, 6))
    yield_total += interest
    cash += parked + interest
    parked_days += 1
    parked = 0.0                                   # non-bear: full release
    # day 4 (bear, rate row MISSING -> ffill 1.26 would apply, but nothing
    # was held overnight): interest 0; park 80% of equity at close
    eq.append(cash + parked)
    accr.append(0.0)
    parked = min(cash, PARK_FRAC * cash)
    cash -= parked
    bear_days += 1
    return {"equity_curve": [round(v, 2) for v in eq],
            "parked_days": parked_days, "bear_days_in_window": bear_days,
            "parking_yield_total": round(yield_total, 6),
            "parked_balance_end": round(parked, 2),
            "parking_accrual_series": accr}


def _run(prices, cp=None, initial=1_000_000.0):
    sig = _fixture_no_signals(prices)
    kw = {"entry_signal": sig, "exit_signal": sig}
    if cp is not None:
        kw["cash_parking"] = cp
    return run_backtest(prices, {}, initial_cash=initial, **kw)


# ---------------------------------------------------------------- offline gates
def gate_g2() -> bool:
    prices, cp, _ = _fixture_case()
    a, b = _run(prices, cp), _run(prices, cp)
    same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    print(f"  [G2] flag-ON double-run identical... {'PASS' if same else 'FAIL'}")
    return bool(same)


def gate_g3() -> bool:
    prices, cp, idx = _fixture_case()
    got = _run(prices, cp)
    want = _g3_expected(idx)
    m = got["metrics"]
    checks = {
        "equity_chain": got["equity_curve"] == want["equity_curve"],
        "parked_days": m["parked_days"] == want["parked_days"],
        "bear_days": m["bear_days_in_window"] == want["bear_days_in_window"],
        "yield_total": m["parking_yield_total"] == want["parking_yield_total"],
        "balance_end": m["parked_balance_end"] == want["parked_balance_end"],
        "accrual_series": (m["parking_accrual_series"]
                           == want["parking_accrual_series"]),
        "no_trades": m["num_trades"] == 0,
    }
    ok = all(checks.values())
    print(f"  [G3] hand fixture "
          f"(bear/non-bear/missing-rate)... {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"       want={want}")
        print(f"       got ={{'equity_curve': {got['equity_curve']}, "
              f"'parked_days': {m['parked_days']}, "
              f"'bear_days': {m['bear_days_in_window']}, "
              f"'yield': {m['parking_yield_total']}, "
              f"'end': {m['parked_balance_end']}, "
              f"'accr': {m['parking_accrual_series']}}}")
        print(f"       checks={checks}")
    return bool(ok)


def gate_g4() -> bool:
    """Future-dated rate/bear rows must never change in-window results."""
    prices, cp, idx = _fixture_case()
    base = _run(prices, cp)
    # append FUTURE rows (beyond the 4-day window) with extreme values
    repo = cp["repo_rate"].copy()
    future = pd.Timestamp("2026-02-02")
    repo[future] = 999.0                       # absurd future rate
    bear = cp["major_bear"].copy()
    bear[future] = True
    poisoned = _run(prices, {"repo_rate": repo, "major_bear": bear,
                             "bear_park_frac": PARK_FRAC})
    same = (base["equity_curve"] == poisoned["equity_curve"]
            and base["metrics"] == poisoned["metrics"])
    print(f"  [G4] future rate/bear rows inert in-window... "
          f"{'PASS' if same else 'FAIL'}")
    return bool(same)


def gate_g5() -> bool:
    prices, cp, _ = _fixture_case()
    keys_off = set(_run(prices)["metrics"])
    keys_on = set(_run(prices, cp)["metrics"])
    leak = sorted(NEW_KEYS & keys_off)
    extra = sorted(keys_on - keys_off - NEW_KEYS)
    missing = sorted(NEW_KEYS - keys_on)
    ok = not leak and not extra and not missing
    print(f"  [G5] keyset discipline (OFF legacy / ON +5 only)... "
          f"{'PASS' if ok else 'FAIL'}"
          + (f" leak={leak} extra={extra} missing={missing}" if not ok else ""))
    return bool(ok)


def gate_regime_equivalence() -> bool:
    """Additive series helper == point-in-time detector at the last bar."""
    ok = True
    idx = pd.bdate_range("2024-01-01", periods=260)
    bear_s = pd.Series([100.0] * 250 + [78.0] * 10, index=idx)
    non_bear_s = pd.Series([100.0] * 250 + [89.5] * 10, index=idx)
    warmup_s = pd.Series([100.0] * 100,
                          index=pd.bdate_range("2024-01-01", periods=100))
    ok &= bool(_regime.major_bear_series(bear_s).iloc[-1]
               == _regime.major_bear_state(bear_s)["is_major_bear"])
    ok &= bool(_regime.major_bear_series(non_bear_s).iloc[-1]
               == _regime.major_bear_state(non_bear_s)["is_major_bear"])
    ok &= not bool(_regime.major_bear_series(warmup_s).any())
    print(f"  [RG] major_bear_series == major_bear_state @last bar... "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


# ---------------------------------------------------------------- real-data
def _load_roster() -> list:
    out = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in ("INTERN", "TRAINEE"):
            out.append(t)
    return out


def _precheck() -> dict:
    """Prereg s3 data-completeness gate (fail -> honest exit 2)."""
    miss = []
    if not os.path.exists(REPO_CSV):
        miss.append(f"repo csv absent: {REPO_CSV} "
                    "(bm-c: git sparse-checkout add --skip-checks "
                    "Money0923/data/repo_daily.csv; fallback = api.github.com "
                    "blobs recipe)")
    if not os.path.exists(os.path.join(PATHS.daily_dir, "510300.csv")) \
            and not os.path.exists(os.path.join(PATHS.daily_dir,
                                                "sh510300.csv")):
        miss.append("510300 daily file absent (regime detector input)")
    roster = _load_roster()
    if len(roster) != 6:
        miss.append(f"expected 6 registered traders, found {len(roster)}")
    return {"ok": not miss, "missing": miss, "roster": roster}


def _repo_series() -> pd.Series:
    df = pd.read_csv(REPO_CSV, parse_dates=["date"])
    s = pd.Series(df["rate"].astype(float).values, index=df["date"])
    return s[~s.index.duplicated(keep="last")].sort_index()


def _assemble_cp(repo: pd.Series, bear: pd.Series) -> dict:
    """Causality discipline: truncate BOTH series at the evidence cutoff."""
    ps = pd.Timestamp(CUTOFF)
    return {"repo_rate": repo[repo.index <= ps],
            "major_bear": bear[bear.index <= ps],
            "bear_park_frac": PARK_FRAC}


def gate_g0() -> bool:
    p = subprocess.run([sys.executable, "-m", "smoke_test"],
                       capture_output=True, text=True, cwd=ROOT)
    tail = (p.stdout or "").strip().splitlines()
    summary = tail[-1] if tail else ""
    ok = p.returncode == 0 and "0 FAIL" in summary
    print(f"  [G0] smoke 23/23 (flag absent)... "
          f"{'PASS' if ok else 'FAIL'} | {summary}")
    return bool(ok)


def gate_g1(prices_full, roster) -> tuple:
    per = {}
    for t in roster:
        a = anchor_gate(t, prices_full)
        per[t["id"]] = bool(a.get("ok"))
        print(f"  [G1] anchor(flag OFF) {t['id']}... "
              f"{'PASS' if per[t['id']] else 'FAIL'}"
              + (f" -- {a.get('error', '')}" if not per[t['id']] else ""))
    return all(per.values()), per


def gate_g6(prices_full, roster, repo, bear) -> dict:
    """Descriptive per-trader flag ON vs OFF -- NO gate verdict (prereg s4-G6)."""
    per = {}
    for t in roster:
        cut = evidence_cutoff(t, prices_full)
        ps = pd.Timestamp(cut)
        prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
        P = build_panels(prices)
        entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params = {k: v for k, v in t["params"].items() if k != "entry"}
        cp = _assemble_cp(repo, bear)
        with ExitPatch(t.get("exit_overrides")):
            off = run_backtest(prices, params, entry_signal=entry,
                               exit_signal=(entry <= 0))
            on = run_backtest(prices, params, entry_signal=entry,
                              exit_signal=(entry <= 0), cash_parking=cp)
        mo, mn = off["metrics"], on["metrics"]
        per[t["id"]] = {
            "cutoff": cut,
            "sharpe_off": mo["sharpe"], "sharpe_on": mn["sharpe"],
            "d_sharpe": round(mn["sharpe"] - mo["sharpe"], 4),
            "annual_off": mo["annual_return"],
            "annual_on": mn["annual_return"],
            "d_annual_pp": round(
                (mn["annual_return"] - mo["annual_return"]) * 100, 4),
            "max_dd_off": mo["max_drawdown"],
            "max_dd_on": mn["max_drawdown"],
            "trades_off": mo["num_trades"], "trades_on": mn["num_trades"],
            "bear_days_in_window": mn["bear_days_in_window"],
            "parked_days": mn["parked_days"],
            "parking_yield_total": mn["parking_yield_total"],
            "parked_balance_end": mn["parked_balance_end"],
            "parking_accrual_series": [round(v, 4) for v in
                                       mn["parking_accrual_series"]],
        }
        print(f"  [G6] {t['id']}: bear_days={mn['bear_days_in_window']} "
              f"parked_days={mn['parked_days']} "
              f"yield={mn['parking_yield_total']} "
              f"d_sharpe={per[t['id']]['d_sharpe']:+.4f} "
              f"d_annual={per[t['id']]['d_annual_pp']:+.4f}pp")
    return per


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        ok = gate_g2() and gate_g3() and gate_g4() and gate_g5() \
            and gate_regime_equivalence()
        print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
        return 0 if ok else 1

    print(f"=== CASH_LEG acceptance gates {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    t0 = time.time()
    pre = _precheck()
    if not pre["ok"]:
        for m in pre["missing"]:
            print(f"  [PRE] MISSING: {m}")
        print("data-completeness precondition failed -> honest stop (exit 2)")
        return 2
    runs = 0
    gates = {}
    gates["G0_smoke"] = {"pass": gate_g0()}; runs += 1
    prices_full = load_core()
    roster = pre["roster"]
    ok_g1, per_g1 = gate_g1(prices_full, roster)
    runs += len(roster)
    gates["G1_legacy_anchor_6of6"] = {"pass": bool(ok_g1), "per_trader": per_g1}
    ok = gate_g2(); runs += 2
    gates["G2_determinism"] = {"pass": ok}
    ok_g3 = gate_g3(); runs += 1
    gates["G3_hand_fixture"] = {"pass": ok_g3}
    ok_g4 = gate_g4(); runs += 2
    gates["G4_no_lookahead"] = {
        "pass": ok_g4,
        "note": "future rate/bear rows inert; rate(T) is morning-published "
                "overnight info (prereg s2 doc statement)",
    }
    ok_g5 = gate_g5(); runs += 2
    gates["G5_keyset"] = {"pass": ok_g5}
    ok_rg = gate_regime_equivalence()
    gates["G_additive_regime_helper"] = {"pass": ok_rg}
    repo = _repo_series()
    bear = _regime.major_bear_series(_regime.load_benchmark_close())
    g6 = gate_g6(prices_full, roster, repo, bear)
    runs += 2 * len(roster)
    gates["G6_descriptive"] = {"per_trader": g6}
    all_pass = all(bool(g.get("pass", True)) for g in gates.values())
    payload = {
        "batch": "CASH_LEG",
        "batch_class": "tool-validation (engine feature acceptance)",
        "claimed_by": "bm-c",
        "task": "T-2026-09-24-09",
        "prereg": "research/CASH_LEG.md",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engine_change": "engine/backtester.py additive cash_parking flag "
                         "(default None = legacy byte-identical) + "
                         "firm/risk/regime.py additive major_bear_series",
        "evidence_cutoff": cutoff_meta(CUTOFF)["evidence_cutoff"],
        "all_pass": all_pass,
        "elapsed_sec": round(time.time() - t0, 1),
        "audit": {
            "workers": 1,
            "purpose": "engine-feature acceptance (CASH_LEG parking leg), "
                       "zero strategy selection, zero registration claims",
            "ledger_trials_added": 0,
            "runs": runs,
        },
        "gates": gates,
    }
    os.makedirs(PATHS.results_dir, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
    print(f"all gates: {'PASS' if all_pass else 'FAIL'} "
          f"| runs={runs} elapsed={payload['elapsed_sec']}s")
    print(f"saved {OUT_JSON}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
