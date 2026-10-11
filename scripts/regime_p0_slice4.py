# regime_p0_slice4.py -- O-20261010-1725 M-1 P0 matrix slice FOUR (zero-burn)
#
# Face: grid_harvest family = GRID-SLEEVE-P1 frozen 5 live cells (T-78,
#   batch results/grid_sleeve_p1.json, evidence_cutoff 2026-09-24).
#   Deterministic replay via engine.run_grid_sleeve with the batch's own
#   frozen params (n_grids 10 / band_win 250 / nav0 1e6 / cost 13.0bp x1
#   frozen declared caliber) -> daily NAV stream -> identity gate vs the
#   stored batch stats (sharpe_full/ann/mdd, full-precision anchors) ->
#   regime buckets (REGIME-5 label per day, PANIC priority).
#
# Law chain: O-20261010-1725 sec.2 "zero-burn v1 = re-slice of adjudicated
#   return streams, attribution not new search, D-41 legal, zero trial
#   budget". Axis freeze: research/REGIME_AXIS_M1_FREEZE.md (bm-b r836).
#   Slice3 replay-stream precedent (deterministic replay of a frozen
#   config is zero-burn re-derivation, not a new trial).
#
# Reuse law (no-reimplementation): shared machinery imported from
#   scripts/regime_p0_slice.py (v1, r875 selftest 10/10); slice2/slice3
#   precedent pattern. The engine is consumed verbatim -- no grid math
#   re-implemented here.

import argparse
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PATHS  # noqa: E402
from engine.grid_sleeve import run_grid_sleeve  # noqa: E402
from regime_p0_slice import (  # noqa: E402
    COLS, DEPOSIT_FLOOR, LABEL_FIRST, TD_PER_YEAR, W12M,
    bucket_stats, load_labels, load_panic_days,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_JSON = os.path.join(ROOT, "results", "grid_sleeve_p1.json")
COST_BP_X1 = 13.0          # knowledge/cost_spec.GRID_LEGACY_COST_BP_X1 (frozen)
XCHK_ATOL = 5e-9           # full-precision anchors; deterministic engine -> near-exact
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")


def _load_instrument(code, cutoff):
    """data/daily single-instrument OHLCV at the batch's own cutoff
    (verbatim convention of the batch runner, scripts/grid_sleeve_p1.py)."""
    path = os.path.join(PATHS.daily_dir, f"{code}.csv")
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df[df.index <= pd.Timestamp(cutoff)]
    for col in ("open", "close"):
        if col not in df.columns or df[col].isna().any():
            raise SystemExit(f"face gate FAIL {code}: {col} missing/NaN")
    if len(df) < 252:
        raise SystemExit(f"face gate FAIL {code}: {len(df)} bars too short")
    return df


def slice_grid(labels, panic):
    """Replay the frozen grid cells and bucket daily net returns by regime."""
    batch = json.load(open(BATCH_JSON, encoding="utf-8"))
    frozen = batch["grid_params"]          # n_grids/band_win/nav0 (frozen)
    live = batch["universe"]["live"]       # 5 frozen cells
    cutoff = batch["evidence_cutoff"]      # batch's own lockbox face
    stored = {c["code"]: c for c in batch["candidates"]}
    if sorted(live) != sorted(stored):
        raise SystemExit("config gate FAIL: live universe vs candidates "
                         "mismatch")
    cells = {}
    for code in live:
        df = _load_instrument(code, cutoff)
        r = run_grid_sleeve(df["open"], df["close"], df.index,
                            cost_bp=COST_BP_X1, **frozen)
        st = stored[code]
        # identity gate: replay must reproduce the frozen batch stats
        if (abs(r["sharpe"] - st["sharpe_full"]) > XCHK_ATOL
                or abs(r["ann"] - st["ann"]) > XCHK_ATOL
                or abs(r["mdd"] - st["mdd"]) > XCHK_ATOL):
            raise SystemExit(
                f"identity gate FAIL {code}: replayed s={r['sharpe']} "
                f"ann={r['ann']} mdd={r['mdd']} vs stored "
                f"s={st['sharpe_full']} ann={st['ann']} mdd={st['mdd']}")
        nav = r["nav"]
        rets = nav.pct_change().dropna()
        rdates = [str(d.date()) for d in nav.index[1:]]
        if len(rets) != len(rdates):
            raise SystemExit(f"shape gate FAIL {code}: rets/dates")
        buckets = {c: [] for c in COLS}
        unlabeled = 0
        panic_in = 0
        for i, dt in enumerate(rdates):
            if dt < LABEL_FIRST:
                unlabeled += 1
                continue
            if dt in panic:
                buckets["PANIC"].append(float(rets.iloc[i]))
                panic_in += 1
                continue
            s = labels.get(dt)
            if s is None or s not in STATES:
                unlabeled += 1
                continue
            buckets[s].append(float(rets.iloc[i]))
        cells[code] = {
            "n_bars": int(len(df)),
            "date_first": str(df.index[0].date()),
            "date_last": str(df.index[-1].date()),
            "identity_stored": {
                "sharpe_full": st["sharpe_full"], "ann": st["ann"],
                "mdd": st["mdd"]},
            "identity_replayed": {
                "sharpe": r["sharpe"], "ann": r["ann"], "mdd": r["mdd"]},
            "n_round_trips": r["n_round_trips"],
            "n_entries": r["n_entries"],
            "unlabeled_days": unlabeled,
            "labeled_days": sum(len(buckets[c]) for c in COLS),
            "panic_days_in": panic_in,
            "active_days_nonzero": int(sum(1 for x in rets if x != 0.0)),
            "by_regime": {c: bucket_stats(buckets[c]) for c in COLS},
        }
    return {
        "family": "grid_harvest",
        "three_piece": "10-grid in-band harvest on 250d band, frozen "
                       "GRID-SLEEVE-P1 params (T-78 batch verbatim)",
        "source": "results/grid_sleeve_p1.json (frozen batch) + "
                 "data/daily/<code>.csv replay at batch cutoff",
        "provenance": {
            "batch": batch["batch"], "ticket": batch["ticket"],
            "prereg": batch["prereg"], "prereg_sha256_16":
                batch["prereg_sha256_16"], "generated": batch["generated"],
            "cost": "V1 legacy 13.0bp x1 (frozen declared caliber)",
        },
        "declared_home": "CHOP (O-1725 P0 declared chop-market weapon; "
                         "style matrix grid row)",
        "cells": cells,
    }


def run(out_path):
    labels = load_labels()
    panic = load_panic_days()
    grid = slice_grid(labels, panic)
    payload = {
        "schema": "p0-matrix-slice4",
        "batch": "P0-MATRIX-SLICE4-GRID",
        "order_ref": "O-20261010-1725 sec.2 zero-burn v1 (P0 row: grid "
                     "family home-ground verify)",
        "axis_freeze": "research/REGIME_AXIS_M1_FREEZE.md (bm-b r836)",
        "deposit_floor": DEPOSIT_FLOOR,
        "td_per_year": TD_PER_YEAR,
        "roll_window_td": W12M,
        "evidence_cutoff": "2026-09-22",
        "batch_cutoff_note": "grid cells replayed at the batch's own "
                             "evidence_cutoff 2026-09-24 (identity anchor "
                             "face); regime bucketing uses REGIME-5 labels "
                             "which cover through 2026-09-30",
        "label_first_day": LABEL_FIRST,
        "calendar_axis": "cell-own explicit dates array (NAV index), "
                         "identity-gated vs frozen batch stats",
        "attribution_note": "slice attribution only; NOT a new-criterion "
                            "claim; scheduling enforcement goes through its "
                            "own prereg (freeze sec.4)",
        "grid_harvest": grid,
        "coverage_gaps_update": {
            "grid_family": "RESOLVED this slice: 5 frozen cells replayed "
                           "identity-clean and wired into the matrix",
            "six_member_defensive_and_system_v1": "unchanged: forward paper "
                                                  "marks too short for 12m "
                                                  "windows",
        },
        "audit": {
            "machine": "bm-c",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_note": "zero-burn deterministic replay of the frozen "
                            "T-78 batch config, no new trials, no engine "
                            "re-tuning",
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print(json.dumps({
        "ok": True,
        "out": out_path,
        "cells": list(grid["cells"].keys()),
    }, ensure_ascii=False))
    return 0


def selftest():
    """Hermetic selftest (no repo data dependency)."""
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    # leg1: v1 import face (reuse law)
    chk("v1 import", callable(bucket_stats) and COLS[0] == "BULL"
        and DEPOSIT_FLOOR == 0.0130 and W12M == 252)
    # leg2: engine import face (verbatim consumption, no re-implementation)
    chk("engine import", callable(run_grid_sleeve))
    # leg3: frozen constants (cost caliber + module constants)
    chk("cost x1", COST_BP_X1 == 13.0)
    chk("cutoffs", LABEL_FIRST == "2013-03-21" and TD_PER_YEAR == 252)
    # leg4: NAV -> net returns alignment (first day drops, dates shift 1)
    nav = pd.Series([1.0, 1.1, 0.99, 1.0],
                    index=pd.to_datetime(["2024-01-01", "2024-01-02",
                                          "2024-01-03", "2024-01-04"]))
    rets = nav.pct_change().dropna()
    rdates = [str(d.date()) for d in nav.index[1:]]
    chk("rets align", len(rets) == 3 and abs(rets.iloc[0] - 0.1) < 1e-12
        and rdates[0] == "2024-01-02")
    # leg5: identity gate math (pass + fail paths on synthetic anchors)
    a = {"sharpe_full": 0.5, "ann": 0.02, "mdd": -0.1}
    b = {"sharpe": 0.5 + 1e-12, "ann": 0.02, "mdd": -0.1}
    chk("ident pass", all(abs(b[k2] - a[k1]) <= XCHK_ATOL for k1, k2 in
                          (("sharpe_full", "sharpe"), ("ann", "ann"),
                           ("mdd", "mdd"))))
    c = {"sharpe": 0.5 + 1e-6, "ann": 0.02, "mdd": -0.1}
    chk("ident fail", abs(c["sharpe"] - a["sharpe_full"]) > XCHK_ATOL)
    # leg6: bucket priority law (panic day wins over state label)
    labels = {"2024-01-02": "BULL"}
    panic = {"2024-01-02"}
    buckets = {c: [] for c in COLS}
    dt = "2024-01-02"
    if dt in panic:
        buckets["PANIC"].append(0.01)
    else:
        buckets[labels.get(dt, "CHOP")].append(0.01)
    chk("panic priority", len(buckets["PANIC"]) == 1
        and len(buckets["BULL"]) == 0)
    # leg7: unlabeled floor (pre-2013 span honest)
    chk("label floor", "2013-03-20" < LABEL_FIRST)
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    ap.add_argument("--out", default=os.path.join(
        ROOT, "results", "regime_style_matrix",
        "P0-SLICE4-GRID-20261011.json"))
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    sys.exit(main())
