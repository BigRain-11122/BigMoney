"""T-24 PROSPECT onboarding anchor-repro batch (slice-2 CPU carrier).

Ticket T-20260924-24 spec: every first-batch PROSPECT candidate must
pass an anchor-repro gate (paper pipeline reuse, ZERO new engine code)
before its member file lands. This script replays each candidate's
recorded p4 cell through the IDENTICAL paper-pipeline code path:
p3_portfolio.member_run (entry = SIGNAL_BUILDERS raw state,
exit = (entry <= 0), CE regime = CE params merged + ExitPatch
loss_time_days 16 -- byte-equivalent to the p4 run_cell convention).

Recorded-cell replay precedent: the 22 cells were already counted in
their source-batch ledgers (p4_batch1/batch2a/folk/queue); this rerun
is a reproducibility GATE, not new trials -> ledger_trials_added = 0.

PASS = candidate eligible for its PROSPECT member file (next slice,
from this artifact's results). FAIL = SIGNAL_BUILDERS construction
mismatch -> fix the key construction, NEVER touch the recorded data
(J18 law: fix implementation, keep judgments).

Usage (detached BelowNormal per O-1612 full-load pool):
  python scripts/t24_prospect_onboard.py run        # replay all 22, JSONL
                                                   # checkpoint resumable
  python scripts/t24_prospect_onboard.py status     # progress read
  python scripts/t24_prospect_onboard.py selftest   # offline gate checks
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # p3 imports

import pandas as pd

from config import PATHS

POOL_PATH = os.path.join(PATHS.results_dir, "prospect_pool.json")
CELLS_PATH = os.path.join(PATHS.results_dir, "t24_prospect_cells.jsonl")
OUT_PATH = os.path.join(PATHS.results_dir, "t24_prospect_onboard.json")
ANCHOR_TOL = 0.002          # project standard (J14/J15, live.paper.ANCHOR_TOL)
CE_PARAMS = {"time_decay_period": 25, "time_decay_threshold": 0.05,
             "trailing_stop_activate": 0.1}   # p4 batches frozen constants
CE_OVERRIDES = {"loss_time_days": 16}

# pool (family, name) -> SIGNAL_BUILDERS key. Single mapping table; the
# member files (next slice) carry params.entry = the SAME key, so drift
# between this table and paper.py keys = KeyError hard-fail (safe).
FAM2KEY = {
    ("zoo9_oversold", "oversold_bounce_20_15"):
        "oversold_bounce(lookback=20, drop=-15%, shrink=0.8)",
    ("ta_rsrs_timing", "rsrs_timing"): "rsrs_timing(18/250/0.8/-0.8)",
    ("ta_vol_breakout", "vol_breakout"): "vol_breakout(20/1.5/20/10)",
    ("ta_hammer_reversal", "hammer_reversal"):
        "hammer_reversal(classic, drop5, reclaim_ma20)",
    ("s10_patterns", "three_methods_up"): "three_methods_up()",
    ("s10_patterns", "doji_at_low"): "doji_at_low()",
    ("s10_patterns", "inside_bar_breakup"): "inside_bar_breakup()",
    ("s10_patterns", "ma_converge_break"): "ma_converge_break()",
    ("s10_patterns", "duck_head"): "duck_head()",
    ("s10_patterns", "immortal_guide"): "immortal_guide()",
    ("s11_folk", "ants_climb"): "ants_climb()",
    ("s9_ta_queue", "bb_squeeze_breakout"): "bb_squeeze_breakout()",
}

NAME2ABBR = {   # member id abbreviation (PROS-<ABBR>[-CE]-01)
    "oversold_bounce_20_15": "OVB", "rsrs_timing": "RSRS",
    "vol_breakout": "VOB", "hammer_reversal": "HAM",
    "three_methods_up": "TMU", "doji_at_low": "DOJI",
    "inside_bar_breakup": "IBB", "ma_converge_break": "MCB",
    "duck_head": "DUCK", "immortal_guide": "IMM", "ants_climb": "ANTS",
    "bb_squeeze_breakout": "BBS",
}


def _load_pool() -> list:
    with open(POOL_PATH, encoding="utf-8") as fh:
        pool = json.load(fh)
    return pool["candidates"], pool.get("evidence_cutoff", "2026-09-22")


def candidate_id(c: dict) -> str:
    return f"{c['family']}::{c['name']}::{c['exit_regime']}"


def make_probe_trader(c: dict, key: str, cutoff: str) -> dict:
    """Synthetic trader dict consumed by member_run (probe id -- this
    dict never lands as a firm/traders file; member files are a separate
    slice gated on this batch's PASS verdicts)."""
    t = {"id": "PROBE::" + candidate_id(c), "evidence_cutoff": cutoff,
         "params": {"entry": key}}
    if c["exit_regime"] == "ce":
        t["params"].update(CE_PARAMS)
        t["exit_overrides"] = dict(CE_OVERRIDES)
    return t


def _recorded_keys_done() -> set:
    done = set()
    if os.path.exists(CELLS_PATH):
        with open(CELLS_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    done.add(json.loads(line)["id"])
                except (json.JSONDecodeError, KeyError):
                    continue   # corrupt tail tolerated (t22 convention)
    return done


def _append_cell(rec: dict):
    with open(CELLS_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _compare(r1: dict, r2: dict, c: dict) -> dict:
    """Repro verdict vs recorded p4 cell (tol = ANCHOR_TOL; trades exact).

    numpy.bool_ is not JSON serializable -> every check cast to bool().
    """
    checks = {
        "full_sharpe": bool(
            abs(r1["full"]["sharpe"] - c["recorded_full_sharpe"])
            < ANCHOR_TOL),
        "oos_sharpe": bool(
            abs(r1["oos"]["sharpe"] - c["recorded_oos_sharpe"])
            < ANCHOR_TOL),
        "x2_full_sharpe": bool(
            abs(r2["full"]["sharpe"] - c["recorded_x2_full_sharpe"])
            < ANCHOR_TOL),
        "n_trades": bool(r1["n_trades"] == c["recorded_n_trades"]),
        "oos_trades": bool(r1["oos_trades"] == c["recorded_oos_trades"]),
        "max_dd": bool(
            abs(r1["full"]["max_drawdown"] - c["recorded_max_dd"])
            < ANCHOR_TOL),
    }
    return {"pass": bool(all(checks.values())), "checks": checks,
            "got": {"full_sharpe": r1["full"]["sharpe"],
                    "oos_sharpe": r1["oos"]["sharpe"],
                    "x2_full_sharpe": r2["full"]["sharpe"],
                    "n_trades": r1["n_trades"],
                    "oos_trades": r1["oos_trades"],
                    "max_dd": r1["full"]["max_drawdown"]}}


def cmd_run() -> int:
    try:
        import psutil
        pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
        if pri is not None:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
    except Exception:
        pass
    from live.paper import load_core
    from p3_portfolio import member_run

    cands, cutoff = _load_pool()
    done = _recorded_keys_done()
    todo = [c for c in cands if candidate_id(c) not in done]
    print(f"pool=22 done={len(done)} todo={len(todo)} cutoff={cutoff}")
    if not todo:
        return _finalize(cands)
    prices = load_core()
    t0 = time.time()
    n_pass = 0
    for i, c in enumerate(todo):
        key = FAM2KEY[(c["family"], c["name"])]
        t = make_probe_trader(c, key, cutoff)
        r1 = member_run(t, prices)
        r2 = member_run(t, prices, cost_mult=2.0)
        verdict = _compare(r1, r2, c)
        n_pass += 1 if verdict["pass"] else 0
        _append_cell({"id": candidate_id(c), "name": c["name"],
                      "family": c["family"], "exit_regime": c["exit_regime"],
                      "entry_key": key, **verdict,
                      "recorded": {k: c[k] for k in
                                   ("recorded_full_sharpe",
                                    "recorded_oos_sharpe",
                                    "recorded_x2_full_sharpe",
                                    "recorded_n_trades",
                                    "recorded_oos_trades",
                                    "recorded_max_dd")},
                      "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
        print(f"[{i + 1}/{len(todo)}] {candidate_id(c)}: "
              f"{'PASS' if verdict['pass'] else 'FAIL'} "
              f"({time.time() - t0:.0f}s elapsed)")
    return _finalize(cands)


def _finalize(cands: list) -> int:
    cells = []
    with open(CELLS_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    cells.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    by_id = {candidate_id(c): c for c in cands}
    n_pass = sum(1 for x in cells if x.get("pass"))
    out = {
        "batch": "t24-prospect-onboard-anchor-repro",
        "ticket": "T-202609-24-24",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "evidence_cutoff": "2026-09-22",
        "pool_size": len(cands),
        "cells_replayed": len(cells),
        "n_pass": n_pass,
        "n_fail": len(cells) - n_pass,
        "complete": len(cells) >= len(cands),
        "verdict": ("PROSPECT-admissible members = anchor PASS set; "
                    "member files land as the next slice FROM this "
                    "artifact (FAIL = fix SIGNAL_BUILDERS construction, "
                    "never touch recorded data)"),
        "audit": {
            "ledger_trials_added": 0,
            "engine_runs": len(cells) * 2,
            "note": "recorded-cell replay gate (p4 cells already counted "
                    "in source-batch ledgers); repro reruns are gates, "
                    "not trials (T-24 spec verbatim)",
        },
        "cells": [{k: x.get(k) for k in
                   ("id", "entry_key", "pass", "checks", "got", "recorded")}
                  for x in cells],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"saved: {OUT_PATH} pass={n_pass}/{len(cells)} "
          f"complete={out['complete']}")
    return 0


def cmd_members() -> int:
    """Slice-3: emit PROSPECT member files for the anchor-PASS set only.
    Admission gate = this batch's repro verdicts (spec: anchor-repro
    gate before onboarding); FAIL members stay out until fixed."""
    from firm.hr import TRADERS_DIR
    cands, cutoff = _load_pool()
    by_id = {candidate_id(c): c for c in cands}
    cells = []
    with open(CELLS_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    cells.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    n_land = n_fail = 0
    for x in cells:
        c = by_id.get(x["id"])
        if c is None:
            continue
        abbr = NAME2ABBR[c["name"]]
        mid = (f"PROS-{abbr}-CE-01" if c["exit_regime"] == "ce"
               else f"PROS-{abbr}-01")
        if not x.get("pass"):
            n_fail += 1
            print(f"SKIP (anchor FAIL, stays out): {mid} {x['id']}")
            continue
        params = {"entry": x["entry_key"]}
        m = {
            "id": mid,
            "name": f"{c['name']} PROSPECT ({c['exit_regime']})",
            "school": c["family"],
            "author": "t24-prospect-onboard",
            "created": "2026-09-24",
            "evidence_cutoff": cutoff,
            "level": "PROSPECT",
            "params": params,
            "prospect": {
                "source_batch": c["source_batch"],
                "exit_regime": c["exit_regime"],
                "sleeve_tag": bool(c["sleeve_tag"]),
                "g1_pass": bool(c["g1_pass"]),
                "anchor_status": "repro-PASS "
                                 "(results/t24_prospect_onboard.json)",
                "recorded_full_sharpe": c["recorded_full_sharpe"],
                "recorded_oos_sharpe": c["recorded_oos_sharpe"],
                "recorded_x2_full_sharpe": c["recorded_x2_full_sharpe"],
                "recorded_n_trades": c["recorded_n_trades"],
                "recorded_oos_trades": c["recorded_oos_trades"],
                "recorded_max_dd": c["recorded_max_dd"],
            },
            "backtest": {
                "full": {"sharpe": c["recorded_full_sharpe"],
                         "max_dd": c["recorded_max_dd"],
                         "trades": c["recorded_n_trades"]},
                "out_sample": {"sharpe": c["recorded_oos_sharpe"],
                               "trades": c["recorded_oos_trades"]},
                "cost_x2": {"full_sharpe": c["recorded_x2_full_sharpe"]},
            },
            "paper": {"months_tracked": 0, "monthly_returns": [],
                      "current_dd": 0.0},
            "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": 0},
            "status_history": [
                {"date": "2026-09-24", "from": None, "to": "PROSPECT",
                 "note": "T-24 first-batch PROSPECT onboarding (pool "
                         "results/prospect_pool.json; anchor-repro PASS "
                         "results/t24_prospect_onboard.json); allocation "
                         "permanently 0; promotion INTERN needs full G2 "
                         "+ T-22 0.70 beat-passive (standards NOT relaxed)"}],
            "notes": c["note"],
        }
        if c["exit_regime"] == "ce":
            params.update(CE_PARAMS)
            m["exit_overrides"] = dict(CE_OVERRIDES)
        with open(os.path.join(TRADERS_DIR, mid + ".json"), "w",
                  encoding="utf-8") as fh:
            json.dump(m, fh, ensure_ascii=False, indent=1)
        n_land += 1
        print(f"landed: {mid} <- {x['id']}")
    print(f"members landed={n_land} skipped_fail={n_fail}")
    return 0 if n_fail == 0 else 2


def cmd_status() -> int:
    cands, cutoff = _load_pool()
    done = _recorded_keys_done()
    n_pass = 0
    if os.path.exists(CELLS_PATH):
        with open(CELLS_PATH, encoding="utf-8") as fh:
            for line in fh:
                try:
                    if json.loads(line).get("pass"):
                        n_pass += 1
                except json.JSONDecodeError:
                    continue
    print(f"pool={len(cands)} replayed={len(done)} pass={n_pass} "
          f"pending={len(cands) - len(done)}")
    return 0


def cmd_selftest() -> int:
    ok = True

    # S1: every pool candidate maps to a registered SIGNAL_BUILDERS key
    from live.paper import SIGNAL_BUILDERS
    cands, cutoff = _load_pool()
    for c in cands:
        key = FAM2KEY.get((c["family"], c["name"]))
        if key is None:
            print(f"FAIL S1: no FAM2KEY mapping for {c['family']}/{c['name']}")
            ok = False
        elif key not in SIGNAL_BUILDERS:
            print(f"FAIL S1: key not in SIGNAL_BUILDERS: {key}")
            ok = False
    print(f"S1 key-coverage: {'PASS' if ok else 'FAIL'} ({len(cands)} cands)")

    # S2: builder output sanity on a synthetic 2-symbol panel -- returns
    # a DataFrame, no NaN, causal (truncation prefix identity), and the
    # probe dict carries the frozen CE constants for ce cells.
    import numpy as np
    rng = np.random.default_rng(20260924)
    n = 900
    idx = pd.date_range("2023-01-02", periods=n)
    close = pd.DataFrame(
        {"AAA": 1 + np.cumsum(rng.normal(0.0002, 0.01, n)),
         "BBB": 1 + np.cumsum(rng.normal(-0.0001, 0.015, n))},
        index=idx)
    high = close * (1 + np.abs(rng.normal(0, 0.006, (n, 2))))
    low = close * (1 - np.abs(rng.normal(0, 0.006, (n, 2))))
    open_ = close.shift(1).fillna(1.0)
    vol = pd.DataFrame(rng.lognormal(12, .4, (n, 2)), index=idx,
                       columns=close.columns)
    P = {"open": open_, "high": high, "low": low, "close": close,
         "volume": vol, "amount": vol * close}
    half = n // 2
    keys = sorted(set(FAM2KEY.values()))
    s2 = True
    for k in keys:
        fn = SIGNAL_BUILDERS[k]
        full = fn(P)
        Phalf = {f: d.iloc[:half] for f, d in P.items()}
        short = fn(Phalf)
        is_df = isinstance(full, pd.DataFrame)
        no_nan = not full.isna().any().any()
        causal = bool((full.iloc[:half].values == short.values).all())
        if not (is_df and no_nan and causal):
            print(f"FAIL S2: key={k} df={is_df} no_nan={no_nan} "
                  f"causal={causal}")
            s2 = False
    print(f"S2 builder-sanity: {'PASS' if s2 else 'FAIL'} ({len(keys)} keys)")
    ok &= s2

    # S3: probe-trader dict contract (CE cells carry CE params +
    # exit_overrides; default cells carry neither)
    s3 = True
    for c in cands:
        t = make_probe_trader(c, FAM2KEY[(c["family"], c["name"])],
                              cutoff)
        if c["exit_regime"] == "ce":
            good = (t["params"].get("time_decay_period") == 25
                    and t.get("exit_overrides") == {"loss_time_days": 16})
        else:
            good = ("time_decay_period" not in t["params"]
                    and "exit_overrides" not in t)
        if not good:
            print(f"FAIL S3: probe contract {candidate_id(c)}")
            s3 = False
    print(f"S3 probe-contract: {'PASS' if s3 else 'FAIL'}")
    ok &= s3

    print(f"selftest: {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "members", "status", "selftest"])
    args = ap.parse_args()
    return {"run": cmd_run, "members": cmd_members, "status": cmd_status,
            "selftest": cmd_selftest}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
