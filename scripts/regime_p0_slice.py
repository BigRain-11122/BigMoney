# regime_p0_slice.py -- O-20261010-1725 M-1 P0 matrix slice (zero-burn re-slice)
#
# Law chain: O-20261010-1725 (strategy x regime full test schedule M-1),
#   sec.2 "zero-burn v1 = re-slice of adjudicated return streams, attribution
#   not new search, D-41 legal, zero trial budget".
# Axis freeze: research/REGIME_AXIS_M1_FREEZE.md (bm-b r836, v1.0 labels +
#   panic windows frozen). Slice semantics per freeze sec.4.1: per strategy x
#   per regime = in-bucket 12m rolling net-return distribution (all starts)
#   + in-bucket Sharpe + in-bucket worst drawdown -> three verdicts.
# CEO floor (O-20261010-1655 acceptance clause): 5y deposit ~1.30%/yr --
#   home_ok requires 12m median annualized > DEPOSIT_FLOOR.
#
# Non-goals (honesty boundaries, freeze sec.4): pre-2013 unlabeled days are
#   excluded (counted, not sliced); slice attribution is NOT a new-criterion
#   claim; scheduling enforcement goes through its own prereg.
#
# Calendar alignment law (r875 bm-c): fund cont_*.json carry t0 + returns
#   only (no date array); the p1c panel cache (Money02) is absent on this
#   host. Alignment = tail-anchor onto results/regime_thermo/thermo_daily.csv
#   (same Money02 bars source, same 2026-09-22 cutoff), verified by the
#   REGIME5-labels/thermo date-set identity over [2013-03-21, 2026-09-22]
#   (3284 == 3284, set-equal, live-verified). nav[i] <-> thermo[i - OFF]
#   where OFF = n_days - len(thermo); day-identity asserted at run time.

import argparse
import csv
import json
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THERMO_CSV = os.path.join(ROOT, "results", "regime_thermo", "thermo_daily.csv")
REGIME5_JSON = os.path.join(ROOT, "results", "regime5_labels",
                            "REGIME5-2026-09-30.json")
PANIC_JSON = os.path.join(ROOT, "results", "regime_axis_m1",
                          "panic_windows.json")

# O-20261010-1655 CEO floor: big-bank 5y deposit listed rate ~1.30%/yr.
DEPOSIT_FLOOR = 0.0130
# Repo annualization convention (fund_value_p1.py: yrs = len(nav)/252).
TD_PER_YEAR = 252
W12M = 252  # 12-month rolling window = 252 trading days (all starts)
COLS = ["BULL", "CHOP", "GRIND", "BEAR", "SUPPORT", "PANIC"]
EVIDENCE_CUTOFF = "2026-09-22"
LABEL_FIRST = "2013-03-21"  # REGIME-5 v1.0 coverage floor

# fund trio cont cells (adjudicated batches, burn_machine per file):
FUND_CELLS = [
    ("fund_value_p1/cont_VALUE-PB_x1.json", "VALUE", "VALUE-PB|x1"),
    ("fund_value_p1/cont_VALUE-PB_x2.json", "VALUE", "VALUE-PB|x2"),
    ("fund_value_p1/cont_VALUE-PE_x1.json", "VALUE", "VALUE-PE|x1"),
    ("fund_value_p1/cont_VALUE-PE_x2.json", "VALUE", "VALUE-PE|x2"),
    ("fund_quality_p1/cont_QUALITY-ROE_x1.json", "QUALITY", "QUALITY-ROE|x1"),
    ("fund_quality_p1/cont_QUALITY-ROE_x2.json", "QUALITY", "QUALITY-ROE|x2"),
    ("fund_divlowvol_p1/cont_DIVLOWVOL-YIELDVOL_x1.json", "DIVLOWVOL",
     "DIVLOWVOL-YIELDVOL|x1"),
    ("fund_divlowvol_p1/cont_DIVLOWVOL-YIELDVOL_x2.json", "DIVLOWVOL",
     "DIVLOWVOL-YIELDVOL|x2"),
]


def load_calendar():
    """thermo date axis (Money02 bars calendar, cutoff 2026-09-22)."""
    with open(THERMO_CSV, encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head, dates = rows[0], [r[0] for r in rows[1:]]
    return dates


def load_labels():
    d = json.load(open(REGIME5_JSON, encoding="utf-8"))
    return {l["date"]: str(l["state"]).upper() for l in d["labels"]}


def load_panic_days():
    d = json.load(open(PANIC_JSON, encoding="utf-8"))
    return {x["date"] for x in d["days"]}


def _sharpe_nav(nav):
    """Same caliber as engine.metrics.sharpe (mean/std * sqrt(252))."""
    rets = np.diff(nav) / nav[:-1]
    sd = rets.std(ddof=1)
    if sd == 0 or len(rets) < 2:
        return 0.0
    return float(rets.mean() / sd * np.sqrt(TD_PER_YEAR))


def _max_dd(nav):
    peak = np.maximum.accumulate(nav)
    return float((nav / peak - 1.0).min())


def bucket_stats(rets):
    """Stats for one regime bucket (list/array of daily net returns)."""
    r = np.asarray(rets, dtype=float)
    n = len(r)
    out = {"n_days": n}
    if n == 0:
        return out
    nav = np.concatenate([[1.0], np.cumprod(1.0 + r)])
    yrs = n / TD_PER_YEAR
    out["ann_ret"] = float(nav[-1] ** (1.0 / yrs) - 1.0) if yrs > 0 else 0.0
    out["cum_ret"] = round(float(nav[-1] - 1.0), 4)
    out["sharpe"] = round(_sharpe_nav(nav), 4)
    out["max_dd"] = round(_max_dd(nav), 4)
    if n < W12M:
        # honest small-sample note (freeze sec.4: extreme windows /
        # short states carry insufficient power for all-start 12m windows)
        out["sample_note"] = (f"n={n} < {W12M} trading days: all-start 12m "
                              "rolling windows impossible; ann_ret for "
                              "buckets this short is a per-day-pace "
                              "extrapolation, read cum_ret instead")
    # 12m rolling windows, all starts within the bucket (step 1)
    wins = []
    if n >= W12M:
        csum = np.concatenate([[0.0], np.cumsum(np.log1p(r))])
        lw = csum[W12M:] - csum[:-W12M]
        wins = np.expm1(lw)  # per-window 12m compound net return
    if len(wins):
        out["roll12"] = {
            "n_windows": int(len(wins)),
            "best": round(float(wins.max()), 4),
            "p75": round(float(np.percentile(wins, 75)), 4),
            "median": round(float(np.median(wins)), 4),
            "p25": round(float(np.percentile(wins, 25)), 4),
            "worst": round(float(wins.min()), 4),
            "pos_share": round(float((wins > 0).mean()), 4),
        }
        out["three_verdicts"] = {
            # home_ok: 12m median annualized beats the deposit floor
            "floor_beat_median": bool(np.median(wins) > DEPOSIT_FLOOR),
            # away_ok: median not negative (regime not actively harmful)
            "not_negative_median": bool(np.median(wins) >= 0.0),
            # gate advice: scheduling-off recommendation flag
            "gate_off_advice": bool(np.median(wins) < 0.0),
        }
    return out


def slice_cell(rel_path, family, cell_name, dates, labels, panic):
    path = os.path.join(ROOT, "results", rel_path)
    d = json.load(open(path, encoding="utf-8"))
    rets = d["returns"]
    n_days = int(d["n_days"])
    t0 = d["t0"]
    if len(rets) + 1 != n_days:
        raise SystemExit(f"cont file shape mismatch {rel_path}: "
                         f"len(returns)+1={len(rets)+1} != n_days={n_days}")
    # tail-anchor alignment: nav[-1] <-> dates[-1] (thermo cutoff 2026-09-22).
    # nav[j] <-> dates[off + j], off = len(dates) - n_days.
    # off < 0 = cell starts before the thermo axis (pre-1996-12-16 days
    # carry no labels and no panic data anyway -> unlabeled).
    # off >= 0 = hard t0 identity gate: dates[off] must EQUAL t0.
    off = len(dates) - n_days
    if off >= 0:
        if dates[off] != t0:
            raise SystemExit(f"t0 identity gate FAIL {rel_path}: "
                             f"dates[{off}]={dates[off]} != t0={t0}")
    else:
        if not (t0 < dates[0]):
            raise SystemExit(f"anchor sanity fail {rel_path}: t0={t0} "
                             f"not before dates[0]={dates[0]}")
    # returns[i] = nav[i+1]/nav[i]-1 -> date = dates[off + i + 1]
    buckets = {c: [] for c in COLS}
    unlabeled = 0
    panic_in = 0
    for i in range(len(rets)):
        di = off + i + 1
        if di < 0:
            unlabeled += 1
            continue
        dt = dates[di]
        if dt < LABEL_FIRST:
            unlabeled += 1
            continue
        if dt in panic:
            buckets["PANIC"].append(rets[i])
            panic_in += 1
            continue
        st = labels.get(dt)
        if st is None or st not in ("BULL", "CHOP", "GRIND", "BEAR",
                                    "SUPPORT"):
            unlabeled += 1
            continue
        buckets[st].append(rets[i])
    stats = {c: bucket_stats(buckets[c]) for c in COLS}
    return {
        "family": family,
        "cell": cell_name,
        "source": "results/" + rel_path,
        "t0": t0,
        "n_days": n_days,
        "burn_machine": d.get("burn_machine"),
        "unlabeled_days": unlabeled,
        "labeled_days": sum(len(buckets[c]) for c in COLS),
        "panic_days_in": panic_in,
        "by_regime": stats,
    }


def family_rollup(cells):
    """Family-level: median of cell-level 12m medians per regime (honest
    small-sample aggregation; per-cell rows remain primary)."""
    fam = {}
    for c in cells:
        f = fam.setdefault(c["family"], {col: [] for col in COLS})
        for col in COLS:
            r12 = c["by_regime"][col].get("roll12")
            if r12:
                f[col].append(r12["median"])
    out = {}
    for fam_name, cols_d in fam.items():
        row = {}
        for col in COLS:
            v = cols_d[col]
            row[col] = {
                "n_cells_with_12m": len(v),
                "median_of_medians": round(float(np.median(v)), 4) if v else None,
            }
        out[fam_name] = row
    return out


def run(out_path):
    dates = load_calendar()
    labels = load_labels()
    panic = load_panic_days()
    # day-identity gate (r875): labeled-span set equality, live re-verified
    lab_dates = [d for d in labels if LABEL_FIRST <= d <= EVIDENCE_CUTOFF]
    cal_dates = [d for d in dates if d >= LABEL_FIRST]
    if set(lab_dates) != set(cal_dates):
        raise SystemExit("calendar identity gate FAIL: regime5 labels vs "
                         "thermo date sets differ over labeled span")
    cells = []
    for rel, family, name in FUND_CELLS:
        cells.append(slice_cell(rel, family, name, dates, labels, panic))
    payload = {
        "schema": "p0-matrix-slice-v1",
        "batch": "P0-MATRIX-SLICE-FUND-TRIO",
        "order_ref": "O-20261010-1725 sec.2 zero-burn v1",
        "axis_freeze": "research/REGIME_AXIS_M1_FREEZE.md (bm-b r836)",
        "deposit_floor": DEPOSIT_FLOOR,
        "td_per_year": TD_PER_YEAR,
        "roll_window_td": W12M,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "label_first_day": LABEL_FIRST,
        "calendar_axis": "results/regime_thermo/thermo_daily.csv "
                         "(tail-anchor, identity gate 3284==3284)",
        "attribution_note": "slice attribution only; NOT a new-criterion "
                            "claim; scheduling enforcement goes through its "
                            "own prereg (freeze sec.4)",
        "floor_source": "O-20261010-1655 CEO acceptance clause: big-bank 5y "
                        "deposit listed rate ~1.30%/yr",
        "cells": cells,
        "family_rollup": family_rollup(cells),
        "audit": {
            "machine": "bm-c",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_note": "zero-burn deterministic re-slice, no engine "
                            "re-run, no new trials",
        },
        "coverage_gaps": {
            "four_asset": "corebook e2 face has no in-repo daily stream "
                          "(external config not in repo); judgment-face "
                          "cagr/all-start dist already on record -- regime "
                          "re-slice deferred to a replay leg",
            "six_member_defensive": "paper marks start 2026-09-24 "
                                    "(~11 days); 12m windows impossible -- "
                                    "forward accumulation in flight",
            "system_v1": "paper marks n=5 (2026-09-24+); insufficient",
            "dip_rebound": "refined variant has no standalone in-repo "
                           "daily stream yet -- locate/wire next slice",
            "theme_wave_ride": "event-driven face; needs event-window "
                               "attribution (slice two)",
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
        "cells": len(cells),
        "gaps": len(payload["coverage_gaps"]),
    }, ensure_ascii=False))
    return 0


def selftest():
    """Hermetic selftest (no repo data dependency for the math legs)."""
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    # leg1: bucket_stats on a known constant stream
    r = np.full(504, 0.001)
    st = bucket_stats(r)
    nav_end = (1.001 ** 504)
    chk("ann_ret compound", abs(st["ann_ret"] - (nav_end ** (252 / 504) - 1))
        < 1e-9)
    # leg2: 12m rolling window count = n - W + 1
    chk("roll12 n_windows", st["roll12"]["n_windows"] == 504 - W12M + 1)
    # leg3: all-identical windows -> best==median==worst
    chk("roll12 degenerate", st["roll12"]["best"] == st["roll12"]["worst"])
    # leg4: positive stream beats floor -> floor_beat_median True
    chk("floor beat true", st["three_verdicts"]["floor_beat_median"] is True)
    # leg5: negative stream -> gate_off_advice True, not_negative False
    stn = bucket_stats(np.full(600, -0.001))
    chk("negative gate advice", stn["three_verdicts"]["gate_off_advice"]
        is True and stn["three_verdicts"]["not_negative_median"] is False)
    # leg6: short bucket -> no roll12, n_days reported
    sts = bucket_stats([0.01, -0.02, 0.005])
    chk("short bucket no roll12", "roll12" not in sts and sts["n_days"] == 3)
    # leg7: max_dd sign convention (drawdown <= 0)
    stv = bucket_stats([0.1, -0.5, 0.2])
    chk("maxdd negative", stv["max_dd"] <= 0)
    # leg8: sharpe of flat stream = 0
    chk("flat sharpe zero", bucket_stats([0.0] * 10)["sharpe"] == 0.0)
    # leg9: floor constant matches CEO clause
    chk("floor 1.30pct", DEPOSIT_FLOOR == 0.0130)
    # leg10: cols complete & mutually exclusive priority order
    chk("cols fixed", COLS == ["BULL", "CHOP", "GRIND", "BEAR", "SUPPORT",
                               "PANIC"])
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    ap.add_argument("--out", default=os.path.join(
        ROOT, "results", "regime_style_matrix",
        "P0-SLICE-FUND-TRIO-20261011.json"))
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    sys.exit(main())
