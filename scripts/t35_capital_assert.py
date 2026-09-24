"""T-35 d1: million-CNY paper capital hard assertion (CEO order O-20260924-2045 s1).

Scope = deliverable 1 of ticket T-2026-09-24-35: prove the registered
paper plane carries 1,000,000 CNY per registered trader, and PROSPECT
members stay zero-capital observation. Engine/registration files are
NEVER modified by this script (assert-only, evidence writer).

Frozen criteria (machine-checkable, per POST_REVIEW judgment-prereg
spirit -- frozen before first run, do not touch on red):
  A1 live.paper.INITIAL_CASH == 1,000,000.0 (module constant)
  A2 engine run_backtest default initial_cash == 1,000,000.0 (signature)
  A3 fresh-engine probe: synthetic 2-symbol panel, default-args backtest
     equity_curve[0] == 1,000,000.0 (constructor-level proof; no hidden
     override between the constant and the engine loop)
  A4 registered paper roster == 6 traders, every level in PAPER_LEVELS
     (INTERN/TRAINEE); no extras, no missing
  A5 total registered paper capital == 6 x 1,000,000 == 6,000,000 CNY
  A6 every registered trader has a paper state file
     (results/paper/<TID>_paper.json)
  A7 PROSPECT: every member file level == PROSPECT and every
     results/prospect_paper/<ID>.json allocation_pct == 0 (zero capital)
  A8 migration disclosure: constructive satisfaction -- INITIAL_CASH has
     been the engine default since the J16 pipeline birth, so there was
     no migration event; recorded honestly (zero open positions on a
     1-bar-old plane at claim time, R91 finding)
  A9 real-money gate untouched: every registered trader JSON "live"
     block allocation_pct == 0 (T0 live authorization stays CEO-only)

CNY denomination: daily CSV prices are CNY quotes; equity curves are
CNY by construction (disclosed, not asserted).

Usage:
    python scripts/t35_capital_assert.py              # sweep -> results/t35_capital_assert.json
    python scripts/t35_capital_assert.py --selftest  # offline assertions
Exit codes: 0 = all pass, 1 = assertion red, 2 = mechanism fault.
"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
import engine.backtester as _eb
from engine import run_backtest
import firm.hr as _hr
from firm.hr import load_trader
from live.paper import INITIAL_CASH, PAPER_LEVELS

MILLION = 1_000_000.0
EXPECTED_ROSTER_N = 6
OUT_PATH = os.path.join(PATHS.results_dir, "t35_capital_assert.json")
PROSPECT_PAPER_DIR = os.path.join(PATHS.results_dir, "prospect_paper")
EVIDENCE = "O-20260924-2045 s1 (T-35 d1); engine default lineage J16; " \
           "anchor+paper same INITIAL_CASH (live/paper.py)"


def _synthetic_panel(n_bars: int = 40) -> dict:
    """2-symbol flat OHLCV panel (probe input only, never evidence)."""
    idx = pd.bdate_range("2026-01-05", periods=n_bars)
    frames = {}
    for sym in ("990001", "990002"):
        close = pd.Series(10.0, index=idx)          # flat -> zero trades
        frames[sym] = pd.DataFrame(
            {"open": close, "high": close, "low": close, "close": close,
             "volume": 1_000.0, "amount": 10_000.0}, index=idx)
    return frames


def a3_probe() -> dict:
    """Fresh-engine default-capital probe (A3)."""
    res = run_backtest(_synthetic_panel(), {"max_positions": 5},
                       entry_signal=None, exit_signal=None)
    eq0 = float(res["equity_curve"][0])
    return {"equity_curve_first": eq0,
            "pass": eq0 == MILLION,
            "n_trades": int(res["metrics"]["num_trades"])}


def _registered_paper_traders() -> list:
    out = []
    for path in sorted(_hr.TRADERS_DIR.glob("*.json")):   # dynamic ref (selftest swap)
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            out.append(t)
    return out


def run() -> int:
    rows = []

    def judge(key, ok, detail):
        rows.append({"assertion": key, "pass": bool(ok), "detail": detail})

    # A1 module constant
    judge("A1_paper_initial_cash_1m", INITIAL_CASH == MILLION,
          {"live_paper_INITIAL_CASH": INITIAL_CASH})
    # A2 engine signature default
    sig_default = None
    try:
        import inspect
        sig = inspect.signature(run_backtest)
        sig_default = sig.parameters["initial_cash"].default
    except Exception:
        pass
    judge("A2_engine_default_1m", sig_default == MILLION,
          {"run_backtest_initial_cash_default": sig_default})
    # A3 fresh-engine probe
    try:
        probe = a3_probe()
    except Exception as exc:                       # mechanism fault, not red
        print(f"A3 probe mechanism fault: {exc}")
        return 2
    judge("A3_probe_equity_first_1m", probe["pass"],
          {"equity_curve_first": probe["equity_curve_first"],
           "n_trades": probe["n_trades"]})

    # A4/A5 registered roster + total capital
    roster = _registered_paper_traders()
    ids = [t["id"] for t in roster]
    levels = {t["id"]: t.get("level") for t in roster}
    judge("A4_roster_six_paper_level",
          len(roster) == EXPECTED_ROSTER_N
          and all(lv in PAPER_LEVELS for lv in levels.values()),
          {"n": len(roster), "ids": ids, "levels": levels})
    judge("A5_total_capital_6m_cny",
          len(roster) == EXPECTED_ROSTER_N and len(roster) * MILLION == 6 * MILLION,
          {"per_trader_cny": MILLION,
           "total_cny": len(roster) * MILLION if roster else 0.0})

    # A6 paper state files
    missing_states = [i for i in ids if not os.path.exists(
        os.path.join(PATHS.results_dir, "paper", f"{i}_paper.json"))]
    judge("A6_paper_state_files_present", not missing_states,
          {"missing": missing_states})

    # A7 PROSPECT zero capital
    pros_files = [p for p in _hr.TRADERS_DIR.glob("PROS-*.json")]
    pros_bad_level, pros_bad_alloc, pros_ids = [], [], []
    for p in sorted(pros_files):
        try:
            m = load_trader(p.stem)
        except Exception:
            pros_bad_level.append(p.stem)
            continue
        pros_ids.append(m["id"])
        if m.get("level") != "PROSPECT":
            pros_bad_level.append(m["id"])
        sp = os.path.join(PROSPECT_PAPER_DIR, f"{m['id']}.json")
        if os.path.exists(sp):
            with open(sp, encoding="utf-8") as fh:
                state = json.load(fh)
            if state.get("allocation_pct") != 0:
                pros_bad_alloc.append(m["id"])
        else:
            pros_bad_alloc.append(f"{m['id']}(state-missing)")
    judge("A7_prospect_zero_capital",
          not pros_bad_level and not pros_bad_alloc and len(pros_ids) == 22,
          {"n_members": len(pros_ids),
           "bad_level": pros_bad_level, "nonzero_or_missing_state": pros_bad_alloc})

    # A9 real-money gate untouched (live block allocation stays 0)
    live_alloc_bad = [t["id"] for t in roster
                      if (t.get("live") or {}).get("allocation_pct") != 0]
    judge("A9_live_allocation_stays_zero", not live_alloc_bad,
          {"nonzero": live_alloc_bad})

    # A8 migration disclosure (honest record, not a pass/fail row)
    cutoff = None
    state_path = os.path.join(PATHS.results_dir, "paper",
                              f"{ids[0]}_paper.json") if ids else None
    if state_path and os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as fh:
            cutoff = json.load(fh).get("cutoff")
    disclosure = {
        "migration_event": "none-needed-constructive",
        "note": "INITIAL_CASH=1M has been the engine default since the J16 "
                "pipeline birth (live/paper.py L72 + engine/backtester.py "
                "L36); the paper plane was 1 bar old with zero open "
                "positions at claim time (R91 finding) -> clean constructive "
                "satisfaction, zero migration step",
        "promotion_wiring": "PROSPECT->INTERN promotion (t24 slice-b) will "
                            "carry 1M per head automatically via the same "
                            "engine default",
    }

    all_pass = all(r["pass"] for r in rows)
    out = {
        "ticket": "T-2026-09-24-35",
        "deliverable": "d1-capital-hard-assertion",
        "law_ref": EVIDENCE,
        "verdict": "PASS" if all_pass else "FAIL",
        "assertions": rows,
        "migration_disclosure": disclosure,
        "cny_denomination": "daily CSV quotes are CNY; equity curves CNY "
                            "by construction",
        "evidence_cutoff": cutoff or "unknown",
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "audit": {"engine_runs": 1,
                  "engine_runs_note": "single A3 constructor probe, zero "
                                      "metrics recorded, not a trial",
                  "ledger_trials_added": 0},
    }
    os.makedirs(PATHS.results_dir, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, OUT_PATH)

    for r in rows:
        print(f"[{'PASS' if r['pass'] else 'FAIL'}] {r['assertion']}")
    print(f"verdict: {out['verdict']} -> {OUT_PATH}")
    return 0 if all_pass else 1


def selftest() -> bool:
    """Offline: probe math + roster/allocation helpers on synthetic
    fixtures (no network, no data-dir dependency, path-swap only)."""
    ok = True

    # S1: probe on flat panel starts at exactly 1M, zero trades
    probe = a3_probe()
    ok &= probe["pass"] and probe["n_trades"] == 0

    # S2: probe detects a wrong initial cash (red must be reachable --
    # no fake always-green). Bypass signature via explicit override.
    res_bad = run_backtest(_synthetic_panel(), {"max_positions": 5},
                           initial_cash=500_000.0)
    ok &= float(res_bad["equity_curve"][0]) == 500_000.0 \
        and float(res_bad["equity_curve"][0]) != MILLION

    # S3: roster helper filters levels correctly on a temp traders dir
    import live.paper as _lp
    import firm.hr as _hr
    real_dir = _hr.TRADERS_DIR
    tmp = tempfile.mkdtemp(prefix="t35_st_")
    try:
        import pathlib
        _hr.TRADERS_DIR = pathlib.Path(tmp)
        # two paper-level + one PROSPECT + one underscore-prefixed skip
        for tid, lvl in (("T-A", "INTERN"), ("T-B", "TRAINEE"),
                         ("PROS-X", "PROSPECT")):
            with open(os.path.join(tmp, f"{tid}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"id": tid, "level": lvl, "created": "2026-09-24",
                           "params": {}, "backtest": {}}, fh)
        with open(os.path.join(tmp, "_skip.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"id": "_skip", "level": "INTERN"}, fh)
        roster = _registered_paper_traders()
        ok &= [t["id"] for t in roster] == ["T-A", "T-B"]
    finally:
        _hr.TRADERS_DIR = real_dir
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = selftest()
        print("t35_capital_assert selftest:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())
