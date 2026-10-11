"""P0 matrix slice THREE -- corebook four-asset replay leg (regime re-slicing).

Order source: O-20261010-1725 sec.2 zero-burn re-slicing (attribution, no new
search). research/P0_MATRIX_SLICE_V1.md sec.4 declared this face as
"四资产核心仓: 判决面在册但日流不在仓(外部配置) -> 政体重切=重放腿(后续切片)".

What this slice does:
  1. Loads the JUDGED corebook config from the frozen verdict face
     results/corebook_closeout_p1/corebook_closeout_p1.json
     faces.e2_four_asset_allocation (verdict "retained"): cell A-EQW,
     rule "monthly", w [0.25, 0.25, 0.25, 0.25] over stock/bond/gold/cash.
  2. Replays that EXACT frozen config through the ALLOC-POLICY-SCAN-P1
     engine (load_faces + simulate_with_dates + _path_metrics, zero
     re-implementation) and cross-checks the replayed path metrics against
     the frozen e2 criteria_reads (same pipeline -> exact float equality
     expected within 1e-9; any drift = fail-closed).
  3. Persists the replayed daily net-return stream in the continuation
     schema consumed by regime_p0_slice.slice_cell, then re-slices it by
     the SAME frozen regime axis (identity gates re-verified live).

Zero-burn nature: replay of one judged config; no grid, no search, no new
trials, no ledger marks, no prereg (attribution under O-1725 sec.2).
Exit-axis nature (TRL law sec.4 disclosure): permanent allocation,
always-invested with monthly rebalance; no engine exit stack involved.

Usage:
    python scripts/regime_p0_slice3.py run
    python scripts/regime_p0_slice3.py selftest
"""
import argparse
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# GBK console reconfigure entry law (r236 family)
if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8",
                                                                 "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np  # noqa: E402

from regime_p0_slice import (  # noqa: E402  (v1 reuse law)
    ROOT, load_calendar, load_labels, load_panic_days, slice_cell,
    bucket_stats, COLS, LABEL_FIRST, DEPOSIT_FLOOR, TD_PER_YEAR, W12M,
)
import allocation_policy_scan as aps  # noqa: E402  (engine reuse law)

VERDICT_FACE = os.path.join(ROOT, "results", "corebook_closeout_p1",
                            "corebook_closeout_p1.json")
STREAM_REL = "regime_style_matrix/corebook_replay_stream_A-EQW-monthly.json"
FAMILY = "COREBOOK"
CELL_NAME = "A-EQW|x1"
XCHECK_TOL = 1e-9
XCHECK_KEYS = ("cagr", "vol", "sharpe", "maxdd", "worst5y",
               "p_dd20_1y", "n_dd_windows")


def _config_gate(e2):
    """Fail-closed gate: the judged cell must be exactly A-EQW/monthly/25x4."""
    if e2.get("verdict") != "retained":
        raise SystemExit(f"config gate FAIL: e2 verdict drift {e2.get('verdict')!r}"
                         " != 'retained'")
    cr = e2["criteria_reads"]
    if cr.get("cell_id") != "A-EQW" or cr.get("rule") != "monthly" \
            or cr.get("w") != [0.25, 0.25, 0.25, 0.25]:
        raise SystemExit(f"config gate FAIL: judged cell drift "
                         f"{cr.get('cell_id')}/{cr.get('rule')}/{cr.get('w')}")
    return cr


def load_frozen_config():
    d = json.load(open(VERDICT_FACE, encoding="utf-8"))
    e2 = d["faces"]["e2_four_asset_allocation"]
    cr = _config_gate(e2)
    return d, e2, cr


def _xcheck(pm, cr, tol=XCHECK_TOL):
    """Cross-check replayed path metrics vs frozen e2 reads; fail-closed."""
    table = {}
    for k in XCHECK_KEYS:
        rep, frz = pm[k], cr[k]
        diff = abs(float(rep) - float(frz))
        table[k] = {"replay": rep, "frozen_e2": frz, "abs_diff": diff}
        if diff > tol:
            raise SystemExit(f"replay xcheck FAIL {k}: replay={rep} "
                             f"frozen={frz} abs_diff={diff} > {tol}")
    return table


def _calendar_gates(master, thermo):
    """Live re-verified identity gates: tail anchor + set equality."""
    if master[-1] != thermo[-1]:
        raise SystemExit(f"tail identity gate FAIL: master[-1]={master[-1]} "
                         f"!= thermo[-1]={thermo[-1]}")
    if thermo[-1] != aps.EVIDENCE_CUTOFF:
        raise SystemExit(f"tail identity gate FAIL: thermo[-1]={thermo[-1]} "
                         f"!= EVIDENCE_CUTOFF={aps.EVIDENCE_CUTOFF}")
    tset = {d for d in thermo if d >= master[0]}
    mset = set(master)
    if tset != mset:
        only_t = sorted(tset - mset)[:3]
        only_m = sorted(mset - tset)[:3]
        raise SystemExit("calendar set-equality gate FAIL "
                         f"(thermo_only={only_t} master_only={only_m})")


def _stream_from_path(path, master, cr, facts):
    """Continuation-schema stream dict from a replayed value path."""
    p = np.asarray(path, dtype=float)
    daily = p[1:] / p[:-1] - 1.0
    return {
        "schema": "corebook-replay-stream-v1",
        "cell_id": cr["cell_id"],
        "rule": cr["rule"],
        "w": list(cr["w"]),
        "adjudication_nature": ("zero-burn replay of judged corebook config "
                                "(attribution slice; no new trials)"),
        "n_days": int(len(master)),
        "t0": str(master[0]),
        "returns": [float(x) for x in daily],
        "burn_machine": None,
        "replay_machine": "bm-c",
        "faces_facts": facts,
        "note": ("entry cost at t0 is embedded in path[0] and therefore NOT "
                 "in the daily returns array (one-time ~7.8bp on ETF legs); "
                 "rebalance costs ARE embedded in daily returns"),
    }


def replay_stream():
    """Replay A-EQW/monthly over the frozen four-asset joint window."""
    _d, e2, cr = load_frozen_config()
    aps._cost_check()  # Face A cost anchor (engine's own gate)
    master, rets, facts = aps.load_faces()
    thermo = load_calendar()
    _calendar_gates(master, thermo)
    targets = np.array([list(cr["w"])], dtype=float)
    res = aps.simulate_with_dates(master, rets, targets, [0], cr["rule"],
                                  store_path=True)
    path = res["path"][0]
    pm = aps._path_metrics(path)
    xtab = _xcheck(pm, cr)
    n_reb = int(res["n_reb"][0])
    if n_reb != int(cr["n_rebalances"]):
        raise SystemExit(f"replay xcheck FAIL n_rebalances: {n_reb} "
                         f"!= {cr['n_rebalances']}")
    stream = _stream_from_path(path, master, cr, facts)
    stream["xcheck_summary"] = {k: v["abs_diff"] for k, v in xtab.items()}
    return stream, e2, cr, pm, res, facts, xtab


def run(out_path):
    stream, e2, cr, pm, res, facts, xtab = replay_stream()
    stream_path = os.path.join(ROOT, "results", STREAM_REL)
    os.makedirs(os.path.dirname(stream_path), exist_ok=True)
    with open(stream_path, "w", encoding="utf-8") as fh:
        json.dump(stream, fh, ensure_ascii=False)
    dates = load_calendar()
    labels = load_labels()
    panic = load_panic_days()
    cell = slice_cell(STREAM_REL, FAMILY, CELL_NAME, dates, labels, panic)
    envelope = {
        "schema": "p0-matrix-slice3",
        "batch": "P0-MATRIX-SLICE3-COREBOOK",
        "order_ref": ("O-20261010-1725 sec.2 zero-burn replay leg "
                      "(P0_MATRIX_SLICE_V1.md sec.4 declared face: "
                      "corebook four-asset, external config, replay not "
                      "re-slice)"),
        "axis_freeze": "research/REGIME_AXIS_M1_FREEZE.md (bm-b r836)",
        "deposit_floor": DEPOSIT_FLOOR,
        "td_per_year": TD_PER_YEAR,
        "roll_window_td": W12M,
        "evidence_cutoff": aps.EVIDENCE_CUTOFF,
        "label_first_day": LABEL_FIRST,
        "calendar_axis": ("results/regime_thermo/thermo_daily.csv "
                          "(identity gates live re-verified: tail anchor + "
                          "set equality replay window)"),
        "attribution_note": ("slice attribution only; NOT a new-criterion "
                             "claim; scheduling enforcement goes through "
                             "its own prereg (freeze sec.4)"),
        "exit_axis_nature": ("permanent allocation (always-invested, monthly "
                             "rebalance); no engine exit stack involved"),
        "replay": {
            "config": {"cell_id": cr["cell_id"], "rule": cr["rule"],
                       "w": cr["w"],
                       "legs": list(aps.LEG_ORDER)},
            "verdict_face": ("results/corebook_closeout_p1/"
                             "corebook_closeout_p1.json#faces."
                             "e2_four_asset_allocation (verdict retained)"),
            "stream_rel": "results/" + STREAM_REL,
            "faces_facts": facts,
            "path_metrics_replay": pm,
            "xcheck_vs_frozen_e2": xtab,
            "n_rebalances": int(res["n_reb"][0]),
            "entry_cost_frac": float(res["entry_cost"][0]),
            "tot_rebalance_cost_frac": float(res["tot_cost"][0]),
            "claim_anchor_distinction": (
                "ORDER conclusion A anchor cagr 0.0587 refers to the "
                "external regime-adaptive variant (config NOT in repo); "
                "this slice replays the in-repo judged A-EQW/monthly face "
                f"(cagr {cr['cagr']:.4f}) -- the two are distinct faces, "
                "reported separately, no conflation"),
        },
        "cells": [cell],
        "coverage_gaps_update": {
            "defense_six_and_system_v1": ("forward paper marks accumulating "
                                           "since 2026-09-24; 12m all-start "
                                           "windows impossible until ~2027-09 "
                                           "(honest accumulation, unchanged)"),
        },
        "audit": {"deterministic": True, "zero_burn": True,
                  "n_new_trials": 0, "seed": None, "machine": "bm-c"},
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=1)
    print("stream:", stream_path)
    print("envelope:", out_path)
    for col in COLS:
        b = cell["by_regime"][col]
        r12 = b.get("roll12")
        if r12:
            tv = b["three_verdicts"]
            print(f"{col}: n={b['n_days']} 12m_med={r12['median']*100:.2f}% "
                  f"pos_share={r12['pos_share']*100:.1f}% "
                  f"floor_beat={tv['floor_beat_median']} "
                  f"gate_off={tv['gate_off_advice']}")
        else:
            print(f"{col}: n={b['n_days']} (short bucket; "
                  f"{b.get('sample_note', 'no 12m windows')})")
    print("xcheck vs frozen e2: ALL PASS (max abs_diff "
          f"{max(v['abs_diff'] for v in xtab.values()):.2e})")
    return 0


def selftest():
    """Hermetic selftest (no repo data dependency)."""
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    # leg1: v1 + engine import face (reuse law)
    chk("v1 import", callable(slice_cell) and callable(bucket_stats)
        and COLS == ["BULL", "CHOP", "GRIND", "BEAR", "SUPPORT", "PANIC"]
        and DEPOSIT_FLOOR == 0.0130 and W12M == 252
        and LABEL_FIRST == "2013-03-21")
    chk("engine import", callable(aps.load_faces)
        and callable(aps.simulate_with_dates)
        and aps.JOINT_START == "2013-07-29"
        and aps.LEG_ORDER == ["stock", "bond", "gold", "cash"])
    # leg2: config gate fail-closed on drift
    good_e2 = {"verdict": "retained", "criteria_reads": {
        "cell_id": "A-EQW", "rule": "monthly",
        "w": [0.25, 0.25, 0.25, 0.25]}}
    chk("config gate pass", _config_gate(good_e2)["cell_id"] == "A-EQW")
    for bad in ({"verdict": "downgraded", "criteria_reads": good_e2[
        "criteria_reads"]},
        {"verdict": "retained", "criteria_reads": {
            "cell_id": "S60C10", "rule": "monthly", "w": [0.6, 0.16, 0.16,
                                                           0.08]}},
        {"verdict": "retained", "criteria_reads": {
            "cell_id": "A-EQW", "rule": "annual", "w": [0.25] * 4}}):
        try:
            _config_gate(bad)
            chk("config gate fail-closed", False)
        except SystemExit:
            chk("config gate fail-closed", True)
    # leg3: engine simulate math on a synthetic 3-day monthly rebalance
    saved_cost = aps.COST_PER_SIDE
    aps.COST_PER_SIDE = 1e-4
    try:
        # engine semantics: rets[0] is never consumed (t=0 = entry day);
        # calendar rules rebalance at the close of the period's first day.
        dates = ["2020-01-02", "2020-02-03", "2020-02-04"]
        rets = np.array([[0.0, 0.0, 0.0, 0.0],      # t=0 (unused by engine)
                         [0.01, 0.0, 0.0, 0.0],     # t=1 drift + monthly reb
                         [0.0, -0.01, 0.0, 0.0]])  # t=2 drift only
        res = aps.simulate_with_dates(dates, rets, np.array([[0.25] * 4]),
                                      [0], "monthly", store_path=True)
        p = res["path"][0]
        c = 1e-4
        v0 = 1.0 - 0.75 * c
        pr1 = 0.25 * 0.01
        v1 = v0 * (1.0 + pr1)
        ws = 0.25 * 1.01 / (1.0 + pr1)
        wo = 0.25 / (1.0 + pr1)
        cost1 = (abs(0.25 - ws) + abs(0.25 - wo) * 2) * c
        v1c = v1 * (1.0 - cost1)
        v2 = v1c * (1.0 + 0.25 * (-0.01))
        chk("sim path math", np.allclose(p, [v0, v1c, v2], rtol=0,
                                         atol=1e-14))
        chk("sim n_reb", int(res["n_reb"][0]) == 1)
    finally:
        aps.COST_PER_SIDE = saved_cost
    # leg4: stream schema (continuation contract len(returns)+1 == n_days)
    st = _stream_from_path(np.array([0.99, 1.0, 1.01]),
                           ["2020-01-02", "2020-01-03", "2020-01-06"],
                           good_e2["criteria_reads"], {"n_days": 3})
    chk("stream schema", len(st["returns"]) + 1 == st["n_days"]
        and st["t0"] == "2020-01-02"
        and abs(st["returns"][0] - (1.0 / 0.99 - 1.0)) < 1e-15)
    # leg5: bucket_stats verdicts (v1 machinery via import)
    stb = bucket_stats(np.full(504, 0.001))
    chk("bucket floor beat", stb["three_verdicts"]["floor_beat_median"]
        and not stb["three_verdicts"]["gate_off_advice"])
    stn = bucket_stats(np.full(504, -0.001))
    chk("bucket gate off", stn["three_verdicts"]["gate_off_advice"]
        and not stn["three_verdicts"]["not_negative_median"])
    chk("bucket small note", "sample_note" in bucket_stats(np.full(50, 0.01)))
    # leg6: xcheck pass/fail-closed behavior
    pm_good = {"cagr": 0.05, "vol": 0.07, "sharpe": 0.8, "maxdd": -0.12,
               "worst5y": 0.02, "p_dd20_1y": 0.0, "n_dd_windows": 100}
    cr_ref = {"cagr": 0.05, "vol": 0.07, "sharpe": 0.8, "maxdd": -0.12,
              "worst5y": 0.02, "p_dd20_1y": 0.0, "n_dd_windows": 100}
    chk("xcheck pass", _xcheck(pm_good, cr_ref)["cagr"]["abs_diff"] == 0.0)
    try:
        _xcheck(dict(pm_good, cagr=0.06), cr_ref)
        chk("xcheck fail-closed", False)
    except SystemExit:
        chk("xcheck fail-closed", True)
    # leg7: calendar gates fail-closed behavior
    try:
        _calendar_gates(["2020-01-02", "2020-01-03"],
                        ["2020-01-02", "2020-01-04"])
        chk("calendar gate fail-closed", False)
    except SystemExit:
        chk("calendar gate fail-closed", True)
    chk("calendar gate pass", _calendar_gates(
        ["2026-09-21", "2026-09-22"],
        ["2019-12-31", "2026-09-21", "2026-09-22"]) is None)
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    ap.add_argument("--out", default=os.path.join(
        ROOT, "results", "regime_style_matrix",
        "P0-SLICE3-COREBOOK-20261011.json"))
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    sys.exit(main())
