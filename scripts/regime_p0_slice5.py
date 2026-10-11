# regime_p0_slice5.py -- O-20261010-1725 M-1 P0 matrix slice FIVE (zero-burn)
#
# Face: lowamp_defensive_etf family (低波防御族 ETF) = LOWAMP-P3 adjudicated
#   16 continuous cells (LA-EQ/LA-EDGE/LA-REP/LA-T3 x legacy/deep x base/x2,
#   batch results/lowamp_p3/cont_*.json, evidence_cutoff 2026-09-22).
#   LOWAMP-P3 family verdict = judged-negative (dual-axis beat 642/1380
#   pass=false; exit-census PASS; D6 0.1868 ADMIT) -- this slice attributes
#   the ADJUDICATED stream by regime; it is NOT a rescue claim.
#
# Law chain: O-20261010-1725 sec.2 "zero-burn v1 = re-slice of adjudicated
#   return streams, attribution not new search, D-41 legal, zero trial
#   budget". Axis freeze: research/REGIME_AXIS_M1_FREEZE.md (bm-b r836).
#   Slice3/slice4 replay-stream precedent (deterministic replay of a frozen
#   config is zero-burn re-derivation, not a new trial).
#
# Reuse law (no-reimplementation): the batch's own runner machinery is
#   consumed verbatim -- scripts/lowamp_p3.py load_axis/_cont_task (engine
#   face, CELLS frozen specs, CostPatch x2) + shared slice machinery from
#   scripts/regime_p0_slice.py (v1, r875). No grid/selection math
#   re-implemented here. Date axis = the replay's own panel index (the
#   cont files carry no t0; calendar recoverability verified by probe:
#   legacy 1631 days 2020-01-02..2026-09-22, deep 3230 days
#   2013-06-17..2026-09-22, REGIME-5 label coverage 100%/100%,
#   residue 0/0 -- results/_r889bmc_slice5_probe2.txt).

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from regime_p0_slice import (  # noqa: E402
    COLS, DEPOSIT_FLOOR, LABEL_FIRST, TD_PER_YEAR, W12M,
    bucket_stats, family_rollup, load_labels, load_panic_days,
)

CONT_DIR = os.path.join(ROOT, "results", "lowamp_p3")
OUT_DEFAULT = os.path.join(ROOT, "results", "regime_style_matrix",
                           "P0-SLICE5-LOWAMP-ETL-20261011.json")
CELLS = ("LA-EQ", "LA-EDGE", "LA-REP", "LA-T3")
AXES = ("legacy", "deep")
FACES = ("base", "x2")
STAT_ATOL = 1.5e-6   # both faces round(...,6); deterministic engine -> <=1e-6
NAV_ATOL = 0.05      # nav_last stored round 2
RET_ARR_ATOL = 1e-12  # same floats rounded 8dp on both faces -> exact equal
PANEL_END = "2026-09-22"
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")


def _load_lp3():
    """Import the batch runner verbatim (module name has digits; file load)."""
    spec = importlib.util.spec_from_file_location(
        "lp3_slice5", os.path.join(ROOT, "scripts", "lowamp_p3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cont_filename(cell, axis, face):
    return f"cont_{cell}_{axis}_{face}.json"


def _init_axis(lp3, axis):
    """Worker-globals init for one axis (verbatim of _init_worker data face;
    the regime face is not consumed by _cont_task)."""
    from live.paper import build_panels
    prices = lp3.load_axis(axis)
    P = build_panels(prices)
    close = P["close"]
    lp3._G.update(prices=prices, P=P, close=close, idx=close.index,
                  axis=axis, regime=None, _sig={})
    return close


def _identity_gates(cell, axis, face, replay, stored, close):
    """Replay must reproduce the stored cont face (deterministic engine)."""
    if int(replay["n_days"]) != int(stored["n_days"]):
        raise SystemExit(f"identity gate FAIL {cell}|{axis}|{face}: n_days "
                         f"{replay['n_days']} != {stored['n_days']}")
    if int(replay["n_days"]) != len(close.index):
        raise SystemExit(f"panel gate FAIL {cell}|{axis}|{face}: n_days "
                         f"{replay['n_days']} != panel {len(close.index)}")
    for k in ("sharpe_full", "ret_full", "max_dd"):
        if abs(float(replay[k]) - float(stored[k])) > STAT_ATOL:
            raise SystemExit(f"identity gate FAIL {cell}|{axis}|{face}: "
                             f"{k} {replay[k]} vs stored {stored[k]}")
    for k in ("n_trades", "n_entries"):
        if int(replay[k]) != int(stored[k]):
            raise SystemExit(f"identity gate FAIL {cell}|{axis}|{face}: "
                             f"{k} {replay[k]} vs stored {stored[k]}")
    if abs(float(replay["nav_last"]) - float(stored["nav_last"])) > NAV_ATOL:
        raise SystemExit(f"identity gate FAIL {cell}|{axis}|{face}: nav_last "
                         f"{replay['nav_last']} vs {stored['nav_last']}")
    r_rep, r_st = replay["returns"], stored["returns"]
    if len(r_rep) != len(r_st) or len(r_rep) != len(close.index) - 1:
        raise SystemExit(f"shape gate FAIL {cell}|{axis}|{face}: "
                         f"returns {len(r_rep)} vs stored {len(r_st)} "
                         f"vs panel-1 {len(close.index) - 1}")
    maxdiff = float(np.max(np.abs(np.asarray(r_rep) - np.asarray(r_st))))
    if maxdiff > RET_ARR_ATOL:
        raise SystemExit(f"returns identity FAIL {cell}|{axis}|{face}: "
                         f"max|diff|={maxdiff}")


def _bucket(rets, dates, labels, panic):
    """returns[i] <-> dates[i] (dates = panel index offset 1). PANIC wins."""
    buckets = {c: [] for c in COLS}
    unlabeled = 0
    panic_in = 0
    if len(rets) != len(dates):
        raise SystemExit("bucket shape gate FAIL: rets/dates")
    for i, dt in enumerate(dates):
        if dt in panic:
            buckets["PANIC"].append(float(rets[i]))
            panic_in += 1
            continue
        st = labels.get(dt)
        if st is None or st not in STATES:
            unlabeled += 1
            continue
        buckets[st].append(float(rets[i]))
    return buckets, unlabeled, panic_in


def run(out_path):
    lp3 = _load_lp3()
    labels = load_labels()
    panic = load_panic_days()
    cells_out = []
    for axis in AXES:
        close = _init_axis(lp3, axis)
        panel_dates = [str(d.date()) for d in close.index]
        if panel_dates[-1] != PANEL_END:
            raise SystemExit(f"panel end gate FAIL {axis}: "
                             f"{panel_dates[-1]} != {PANEL_END}")
        ret_dates = panel_dates[1:]
        for cell in CELLS:
            for face in FACES:
                stored = json.load(open(
                    os.path.join(CONT_DIR, _cont_filename(cell, axis, face)),
                    encoding="utf-8"))
                replay = lp3._cont_task({"cell": cell, "face": face})
                _identity_gates(cell, axis, face, replay, stored, close)
                buckets, unlabeled, panic_in = _bucket(
                    replay["returns"], ret_dates, labels, panic)
                if unlabeled:
                    raise SystemExit(
                        f"unlabeled gate FAIL {cell}|{axis}|{face}: "
                        f"{unlabeled} days outside labels (probe said 0)")
                cells_out.append({
                    "family": axis,   # rollup key = axis window face
                    "cell": f"{cell}|{axis}|{face}",
                    "spec": dict(lp3.CELLS[cell]),
                    "source": f"results/lowamp_p3/{_cont_filename(cell, axis, face)}",
                    "axis_window": [panel_dates[0], panel_dates[-1]],
                    "n_days": int(replay["n_days"]),
                    "identity_stored": {
                        k: stored[k] for k in ("sharpe_full", "ret_full",
                                               "max_dd", "n_trades",
                                               "n_entries", "nav_last")},
                    "identity_replayed": {
                        k: replay[k] for k in ("sharpe_full", "ret_full",
                                               "max_dd", "n_trades",
                                               "n_entries", "nav_last")},
                    "returns_max_abs_diff_vs_stored": round(float(np.max(
                        np.abs(np.asarray(replay["returns"])
                               - np.asarray(stored["returns"])))), 12),
                    "unlabeled_days": unlabeled,
                    "labeled_days": sum(len(buckets[c]) for c in COLS),
                    "panic_days_in": panic_in,
                    "active_days_nonzero": int(sum(
                        1 for x in replay["returns"] if x != 0.0)),
                    "by_regime": {c: bucket_stats(buckets[c]) for c in COLS},
                })
    rollup = family_rollup(cells_out)
    payload = {
        "schema": "p0-matrix-slice5",
        "batch": "P0-MATRIX-SLICE5-LOWAMP-ETL",
        "order_ref": "O-20261010-1725 sec.2 zero-burn v1 (P0 row: "
                     "低波防御族 ETF home-ground verify)",
        "axis_freeze": "research/REGIME_AXIS_M1_FREEZE.md (bm-b r836)",
        "deposit_floor": DEPOSIT_FLOOR,
        "td_per_year": TD_PER_YEAR,
        "roll_window_td": W12M,
        "evidence_cutoff": "2026-09-22",
        "batch_cutoff_note": "cells replayed at the batch's own cutoff "
                             "2026-09-22 via its own runner (load_axis/"
                             "_cont_task verbatim); regime bucketing uses "
                             "REGIME-5 labels through 2026-09-30",
        "label_first_day": LABEL_FIRST,
        "calendar_axis": "replay panel index (legacy 2020-01-02.., deep "
                         "2013-06-17.., both end 2026-09-22; label coverage "
                         "100% residue 0 per probe)",
        "family": "lowamp_defensive_etf",
        "family_verdict": "judged-negative (LOWAMP-P3 dual-axis beat "
                          "642/1380=46.5% pass=false; exit-census PASS; "
                          "D6 0.1868 ADMIT) -- attribution of the "
                          "adjudicated stream, not a rescue claim",
        "declared_home": "defensive all-weather claim (matrix v1 lowvol "
                         "sleeve row, BEAR/SUPPORT-weighted) -- home-ground "
                         "verify face",
        "attribution_note": "slice attribution only; NOT a new-criterion "
                            "claim; scheduling enforcement goes through its "
                            "own prereg (freeze sec.4)",
        "lowamp_defensive_etf": {
            "family": "lowamp_defensive_etf",
            "three_piece": "W-bar low-amplitude rank Top-N defensive-ETF "
                           "rotation (LA-REP invvol / LA-EQ eq / LA-T3 N3 / "
                           "LA-EDGE W104), LOWAMP-P3 frozen specs, T+1 "
                           "engine-canonical",
            "source": "results/lowamp_p3/cont_*.json (16 frozen continuous "
                      "cells) replayed via scripts/lowamp_p3.py verbatim",
            "provenance": {
                "batch": "LOWAMP-P3", "ticket": "T-2026-10-01-140",
                "cost": "base=x1 (13.041bp/side frozen), x2=CostPatch(2.0)",
                "panel": "legacy=core48 adj face 2020-01-02.., "
                         "deep=t18_deep_panel 2013-06-17..",
            },
            "cells": cells_out,
        },
        "family_rollup_by_axis_window": rollup,
        "coverage_gaps_update": {
            "lowamp_defensive_etf": "RESOLVED this slice: 16 adjudicated "
                                    "cells replayed identity-clean and "
                                    "wired into the matrix (P0 row 低波防御"
                                    "族 ETF)",
            "six_member_defensive_and_system_v1": "unchanged: forward paper "
                                                  "marks too short for 12m "
                                                  "windows",
        },
        "audit": {
            "machine": "bm-c",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_note": "zero-burn deterministic replay of the frozen "
                            "LOWAMP-P3 continuous configs (batch runner "
                            "verbatim), no new trials, no engine re-tuning",
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print(json.dumps({"ok": True, "out": out_path,
                      "cells": [c["cell"] for c in cells_out]},
                     ensure_ascii=False))
    return 0


def selftest():
    """Hermetic selftest (no repo data dependency)."""
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    # leg1: v1 import face (reuse law)
    chk("v1 import", callable(bucket_stats) and callable(family_rollup)
        and COLS[0] == "BULL" and DEPOSIT_FLOOR == 0.0130 and W12M == 252)
    # leg2: batch-runner import face (verbatim consumption)
    lp3 = _load_lp3()
    chk("runner import", callable(lp3.load_axis)
        and callable(lp3._cont_task)
        and set(lp3.CELLS) == {"LA-EQ", "LA-EDGE", "LA-REP", "LA-T3"})
    # leg3: frozen constants
    chk("cutoffs", LABEL_FIRST == "2013-03-21" and TD_PER_YEAR == 252
        and PANEL_END == "2026-09-22")
    # leg4: NAV -> net returns alignment (first day drops, dates shift 1)
    nav = pd.Series([1.0, 1.1, 0.99, 1.0],
                    index=pd.to_datetime(["2024-01-01", "2024-01-02",
                                          "2024-01-03", "2024-01-04"]))
    rets = nav.pct_change().dropna()
    chk("rets align", len(rets) == 3 and abs(rets.iloc[0] - 0.1) < 1e-12
        and str(rets.index[0].date()) == "2024-01-02")
    # leg5: identity tolerance law (round-6 stored vs deterministic replay)
    a = {"sharpe_full": 1.158046, "ret_full": 0.158756, "max_dd": -0.037083}
    b = {k: a[k] + 1e-6 for k in a}
    chk("ident pass", all(abs(b[k] - a[k]) <= STAT_ATOL for k in a))
    c = {k: a[k] + 5e-6 for k in a}
    chk("ident fail", any(abs(c[k] - a[k]) > STAT_ATOL for k in a))
    # leg6: returns-array exact gate (same floats rounded 8dp)
    r = [round(v, 8) for v in (0.001, -0.002, 0.000000005)]
    chk("arr pass", float(np.max(np.abs(np.asarray(r) - np.asarray(r))))
        <= RET_ARR_ATOL)
    r2 = list(r); r2[0] += 1e-10
    chk("arr fail", float(np.max(np.abs(np.asarray(r2) - np.asarray(r))))
        > RET_ARR_ATOL)
    # leg7: bucket priority law (panic day wins over state label)
    labels = {"2024-01-02": "BULL"}
    panic = {"2024-01-02"}
    buckets, unl, pin = _bucket([0.01], ["2024-01-02"], labels, panic)
    chk("panic priority", len(buckets["PANIC"]) == 1
        and len(buckets["BULL"]) == 0 and pin == 1 and unl == 0)
    # leg8: unlabeled floor (pre-2013 span excluded by axis windows)
    chk("label floor", "2013-06-17" > LABEL_FIRST)
    # leg9: cont filename round-trip
    chk("filename rt", _cont_filename("LA-REP", "legacy", "x2")
        == "cont_LA-REP_legacy_x2.json"
        and _cont_filename("LA-T3", "deep", "base")
        == "cont_LA-T3_deep_base.json")
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    sys.exit(main())
