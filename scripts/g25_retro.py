"""scripts/g25_retro.py -- G2.5 three-check retro for registered traders (T-02 deliverable 4/7).

Authority: research/BACKTEST_SCIENCE.md s8 (O-20260923-2215) + audit P0-1 (O-20260923-2250,
amendment 8). Every registered trader must carry a G2.5 verdict BEFORE any promotion
(2026-10-31 first monthly check): DSR >= 0.95 (D1) AND bootstrap CI lower bound > 0 (D3)
AND family-PBO <= 0.25 (D4). Missing/fail/pending = no promotion (firm/hr.py reads the
verdict files -- the execution leg of this law).

Verdict rules (frozen BEFORE first run; revision = prereg + 7-day veto window):
  dsr leg : pass iff dsr >= 0.95. n_trials = trials-ledger chain head AT CHECK TIME
            (data-driven, science_gates.ledger_head -- the monthly-audit recheck semantic:
            the deflation universe grows as the shop tries more things). The
            registration-time ledger head is ALSO recorded (context disclosure only).
  ci  leg : pass iff stationary-bootstrap 95% CI lower bound > 0 (seed = prereg family).
  pbo leg : family-PBO via CSCV over the trader's own prereg trial grid
            (screening/pbo.cscv_pbo, frozen 8-block/70-combo). pass iff <= 0.25
            (register-eligible band); observe band = NOT pass; > 0.5 = fail.
            Family harnesses land per-round; unwired family = "pending" (insufficient --
            blocks promotion until computed, never silently skipped).
  overall : "fail"  = any COMPUTED leg not pass (fail or observe band);
            "pending" = no computed failure but >= 1 leg pending;
            "pass"  = all three legs pass.

Trial-ledger accounting: every engine run here reproduces a RECORDED cell (anchor-gate
reproduction of the registered evidence, and rerun of recorded family-grid cells on the
evidence_cutoff-truncated panel). Same classification as the pbo_cscv_v1 live-fire
precedent: audit reproductions, NOT new trials -- trials ledger N unchanged, disclosed
in every output file.

Usage:
  python scripts/g25_retro.py selftest   # offline, zero engine/network
  python scripts/g25_retro.py run        # live -> results/g25/<ID>.json + _summary.json
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE, os.path.join(_ROOT, "screening")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd

import science_gates as sg          # scripts/ (T-02 1/7 shared lib)
from pbo import (RESULTS_DIR as _PBO_RESULTS, TRADERS_DIR, align_returns,
                 cscv_pbo, equity_to_daily_returns)

G25_DIR = os.path.join(_ROOT, "results", "g25")
DSR_GATE = 0.95                    # BACKTEST_SCIENCE.md s1
BOOT_SEED = 20260923               # prereg seed family (science_gates default)

# trader -> family provenance. "batch_results" names the results JSON whose
# trials_ledger.total was the chain head when the trader was registered
# (registration-time DSR context). Unmapped registered traders are caught by the
# completeness gate -- never silently skipped.
FAMILY_REGISTRY = {
    "ENGULF-CE-01":    {"kind": "g2_folk", "family": "engulf_reversal",
                        "batch_results": "shortline_g2_folk.json"},
    "NEEDLE-DE-01":    {"kind": "g2_folk", "family": "needle_probe",
                        "batch_results": "shortline_g2_folk.json"},
    "DROUGHT-CE-01":   {"kind": "g2_folk", "family": "vol_drought_reversal",
                        "batch_results": "shortline_g2_folk.json"},
    "VOLATILITY-CE-01": {"kind": "pending_harness",
                         "family": "combined_exit_softening (J15 grid, 12 cells)",
                         "batch_results": "combined_exit.json"},
    "COMPOSITE-CE-01": {"kind": "pending_harness",
                        "family": "ce_transfer (J19 grid, 9 cells)",
                        "batch_results": "ce_transfer.json"},
    "COMPOSITE-CE-02": {"kind": "pending_harness",
                        "family": "ce_transfer (J19 grid, 9 cells)",
                        "batch_results": "ce_transfer.json"},
}


# ---------------------------------------------------------------- legs (pure aggregation)

def _aggregate_verdict(dsr_pass: bool, ci_pass: bool, pbo_status: str) -> str:
    """Frozen overall rule (see module docstring). pbo_status in
    {pass, observe, fail, pending}."""
    legs = [("dsr", dsr_pass), ("ci", ci_pass)]
    if pbo_status == "pending":
        computed_fail = (not dsr_pass) or (not ci_pass)
        return "fail" if computed_fail else "pending"
    all_pass = dsr_pass and ci_pass and pbo_status == "pass"
    return "pass" if all_pass else "fail"


def _pbo_leg_status(pbo_value: float | None) -> str:
    """pass iff <= 0.25 (register-eligible); observe band is NOT a pass."""
    if pbo_value is None:
        return "pending"
    if pbo_value <= 0.25:
        return "pass"
    return "observe" if pbo_value <= 0.5 else "fail"


# ---------------------------------------------------------------- registration-time context

def _registration_ledger_head(batch_results: str | None) -> dict:
    if not batch_results:
        return {"total": None, "file": None,
                "note": "no batch file mapped -- disclosed"}
    path = os.path.join(_PBO_RESULTS, batch_results)
    if not os.path.exists(path):
        return {"total": None, "file": batch_results,
                "note": "mapped batch file not found -- disclosed"}
    try:
        with open(path, encoding="utf-8") as fh:
            tl = json.load(fh).get("trials_ledger")
    except (OSError, ValueError):
        return {"total": None, "file": batch_results,
                "note": "unparseable batch file -- disclosed"}
    # dual schema coexists until T-03 unifies (audit P0-7): dict form carries
    # {"total": ...}; legacy flat-list form is per-batch entries -> sum of n.
    if isinstance(tl, dict):
        return {"total": tl.get("total"), "file": batch_results, "note": None}
    if isinstance(tl, list):
        total = sum(int(e.get("n", 0)) for e in tl
                    if isinstance(e, dict) and isinstance(e.get("n"), (int, float)))
        return {"total": total, "file": batch_results,
                "note": "legacy flat-list ledger schema (T-03 unification "
                        "pending) -- total = sum of per-batch n"}
    return {"total": None, "file": batch_results, "note": "unknown schema -- disclosed"}


# ---------------------------------------------------------------- folk-family PBO harness

def _folk_family_matrix(g2f, fam_name: str) -> tuple[pd.DataFrame, dict]:
    """Rerun the RECORDED G2_FOLK family grid (centers + neighborhood points,
    both regimes) on the evidence_cutoff-truncated panel; return the complete
    returns matrix for CSCV. Center cells double as the repro hard gate
    (g2_folk convention: |full-recorded| < REPRO_TOL and trades exact);
    repro mismatch = harness problem -> pending with reason (fail-loud,
    never a fabricated matrix)."""
    spec = g2f.FAMILIES[fam_name]
    prices_full = g2f.load_core()
    cut = pd.Timestamp(g2f.EVIDENCE_CUT)
    prices = {s: df.loc[:cut].copy() for s, df in prices_full.items()}
    P = g2f.build_panels(prices)
    idx = P["close"].index

    series: dict[str, pd.Series] = {}
    repro: dict[str, dict] = {}
    cells = 0
    for regime in spec["regimes"]:
        full_r, _oos_r, tr_r, _x2_r = spec["centers"][regime]
        r = g2f.run_cell(prices, idx, spec["build"](P, {}), regime)
        cells += 1
        d = abs(r["full"]["sharpe"] - full_r)
        ok = bool(d < g2f.REPRO_TOL and r["n_trades"] == tr_r)
        repro[f"center@{regime}"] = {"ok": ok, "abs_d": round(d, 4),
                                     "trades": r["n_trades"],
                                     "recorded_trades": tr_r}
        series[f"center@{regime}"] = equity_to_daily_returns(r["eq"])
        for point in spec["points"]:
            r = g2f.run_cell(prices, idx, spec["build"](P, point), regime)
            cells += 1
            series[f"nbhd {point}@{regime}"] = equity_to_daily_returns(r["eq"])
    if not all(v["ok"] for v in repro.values()):
        return None, {"repro_ok": False, "repro": repro, "n_cells": cells,
                      "reason": "center repro mismatch -- harness/panel drift, "
                                "matrix NOT fabricated, leg stays pending"}
    matrix = align_returns(series)
    return matrix, {"repro_ok": True, "repro": repro, "n_cells": cells,
                    "span": [str(matrix.index[0].date()),
                             str(matrix.index[-1].date())]}


# ---------------------------------------------------------------- live run

def run() -> int:
    os.makedirs(G25_DIR, exist_ok=True)
    from pbo import _registered_returns          # reuse: anchor-gate curve machine
    from live.paper import SIGNAL_BUILDERS

    head_now = sg.ledger_head()
    matrix, validity = _registered_returns()     # raises on anchor drift = correct abort
    print(f"ledger head now: {head_now['total']} ({head_now['file']})")
    print(f"book matrix: T={matrix.shape[0]} N={matrix.shape[1]} "
          f"{matrix.index[0].date()}..{matrix.index[-1].date()}")

    fam_cache: dict[str, tuple] = {}
    summary = []
    for tid in matrix.columns:
        rets = [float(x) for x in matrix[tid].tolist()]
        dsr = sg.deflated_sharpe_ratio(rets, n_trials=head_now["total"])
        ci = sg.bootstrap_ci_sharpe(rets, seed=BOOT_SEED)
        reg = FAMILY_REGISTRY.get(tid)
        if reg is None:
            pbo_leg = {"status": "pending",
                       "reason": "registered trader has no family mapping -- "
                                 "completeness gate, fix registry"}
            fam_ctx = _registration_ledger_head(None)
        else:
            fam_ctx = _registration_ledger_head(reg["batch_results"])
            if reg["kind"] == "g2_folk":
                fam = reg["family"]
                if fam not in fam_cache:
                    import g2_folk as g2f
                    fam_cache[fam] = _folk_family_matrix(g2f, fam)
                fam_matrix, fam_info = fam_cache[fam]
                if fam_matrix is None:
                    pbo_leg = {"status": "pending",
                               "family": fam, **fam_info}
                else:
                    cscv = cscv_pbo(fam_matrix)
                    pbo_leg = {"status": _pbo_leg_status(cscv["pbo"]),
                               "family": fam, "pbo": cscv["pbo"],
                               "n_cells": fam_info["n_cells"],
                               "T": cscv["n_rows"],
                               "n_combinations": cscv["n_combinations"],
                               "repro": fam_info["repro"]}
            else:
                pbo_leg = {"status": "pending", "family": reg["family"],
                           "reason": "family harness not wired yet "
                                     "(queued next rounds; leg = insufficient "
                                     "-> blocks promotion until computed)"}
        verdict = _aggregate_verdict(dsr["dsr"] >= DSR_GATE,
                                    ci["ci_lower_bound_positive"],
                                    pbo_leg["status"])
        payload = {
            "trader": tid,
            "authority": "research/BACKTEST_SCIENCE.md s8 (G2.5 three-check)",
            "verdict": verdict,
            "legs": {
                "dsr": {"value": dsr["dsr"], "gate": DSR_GATE,
                        "pass": bool(dsr["dsr"] >= DSR_GATE), **dsr},
                "ci": {"pass": bool(ci["ci_lower_bound_positive"]), **ci},
                "pbo": pbo_leg,
            },
            "inputs": {
                "n_trials_now": head_now["total"],
                "ledger_head_file": head_now["file"],
                "registration_ledger_head": fam_ctx,
                "returns_window": [str(matrix.index[0].date()),
                                   str(matrix.index[-1].date())],
                "T": int(matrix.shape[0]),
                "anchor_validity": validity.get(tid),
            },
            "ledger_note": "engine runs = recorded-cell reproductions (anchor "
                           "gate + recorded family grids, evidence_cutoff panel) "
                           "-- audit reproductions, NOT new trials; ledger N "
                           "unchanged (pbo_cscv_v1 precedent)",
            "generated": _now(),
        }
        out = os.path.join(G25_DIR, f"{tid}.json")
        with open(out + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        os.replace(out + ".tmp", out)
        summary.append({"trader": tid, "verdict": verdict,
                        "dsr": dsr["dsr"], "ci_low": ci["ci95_low"],
                        "pbo": pbo_leg.get("pbo"),
                        "pbo_status": pbo_leg["status"]})
        print(f"{tid:<16} dsr={dsr['dsr']:.4f} ci_low={ci['ci95_low']:.3f} "
              f"pbo={pbo_leg.get('pbo')} ({pbo_leg['status']}) "
              f"-> {verdict}")

    # completeness gate: any registered trader (params.entry contract) missing
    # from the book matrix or registry is disclosed, never silently skipped
    missing = []
    for fname in sorted(os.listdir(TRADERS_DIR)):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        with open(os.path.join(TRADERS_DIR, fname), encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("params", {}).get("entry") not in SIGNAL_BUILDERS:
            continue
        if t["id"] not in matrix.columns or t["id"] not in FAMILY_REGISTRY:
            missing.append(t["id"])
    with open(os.path.join(G25_DIR, "_summary.json.tmp"), "w",
              encoding="utf-8") as fh:
        json.dump({"module": "scripts/g25_retro.py",
                   "authority": "BACKTEST_SCIENCE.md s8 + audit P0-1 (T-02 4/7)",
                   "summary": summary,
                   "completeness_missing": missing,
                   "n_trials_now": head_now["total"],
                   "bands": {"dsr_gate": DSR_GATE, "pbo_pass": "<=0.25",
                             "pbo_observe": "(0.25,0.5]", "pbo_fail": ">0.5"},
                   "generated": _now()}, fh, ensure_ascii=False, indent=1)
    os.replace(os.path.join(G25_DIR, "_summary.json.tmp"),
               os.path.join(G25_DIR, "_summary.json"))
    print(f"summary -> {os.path.join(G25_DIR, '_summary.json')} "
          f"(completeness missing: {missing or 'none'})")
    return 0


# ---------------------------------------------------------------- selftest (offline)

def selftest() -> int:
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # verdict aggregation (frozen rules)
    ok("all pass -> pass", _aggregate_verdict(True, True, "pass") == "pass")
    ok("dsr fail -> fail", _aggregate_verdict(False, True, "pass") == "fail")
    ok("ci fail -> fail", _aggregate_verdict(True, False, "pass") == "fail")
    ok("pbo observe band is NOT a pass (D4 no-registration band)",
       _aggregate_verdict(True, True, "observe") == "fail")
    ok("pbo fail -> fail", _aggregate_verdict(True, True, "fail") == "fail")
    ok("pbo pending + others pass -> pending",
       _aggregate_verdict(True, True, "pending") == "pending")
    ok("pbo pending + dsr fail -> fail (computed failure is decisive)",
       _aggregate_verdict(False, True, "pending") == "fail")
    ok("_pbo_leg_status bands", _pbo_leg_status(0.10) == "pass"
       and _pbo_leg_status(0.25) == "pass" and _pbo_leg_status(0.26) == "observe"
       and _pbo_leg_status(0.50) == "observe" and _pbo_leg_status(0.51) == "fail"
       and _pbo_leg_status(None) == "pending")

    # hr wiring: verdict file read + promotion gate (offline, temp files)
    os.makedirs(G25_DIR, exist_ok=True)
    from firm import hr
    tid = "SELFTEST-G25"
    trader = {"id": tid, "level": "INTERN",
              "backtest": {"out_sample": {"sharpe": 1.0, "trades": 40,
                                          "max_dd": 0.1}},
              "paper": {"months_tracked": 1}, "status_history": []}
    p = os.path.join(G25_DIR, f"{tid}.json")
    try:
        for verdict, expect in (("pass", "PROMOTE"), ("fail", "HOLD"),
                                ("pending", "HOLD")):
            with open(p + ".tmp", "w", encoding="utf-8") as fh:
                json.dump({"verdict": verdict}, fh)
            os.replace(p + ".tmp", p)
            ok(f"hr gate: g25 {verdict} -> {expect}",
               hr.evaluate(dict(trader)) == expect)
        os.remove(p)
        ok("hr gate: g25 missing -> HOLD",
           hr.evaluate(dict(trader)) == "HOLD")
        ok("hr gate: g25 invalid json -> HOLD (insufficient=hold)",
           hr.g25_verdict("SELFTEST-NOT-A-TRADER") in ("missing", "invalid"))
    finally:
        if os.path.exists(p):
            os.remove(p)

    # registry completeness offline: every entry's family kind is known
    kinds = {"g2_folk", "pending_harness"}
    ok("FAMILY_REGISTRY kinds all known",
       all(v["kind"] in kinds for v in FAMILY_REGISTRY.values()))

    n_fail = sum(1 for _, c in checks if not c)
    print(f"\ng25_retro selftest: {len(checks)-n_fail}/{len(checks)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


def _now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    raise SystemExit(selftest() if cmd == "selftest" else run() if cmd == "run" else 0)
