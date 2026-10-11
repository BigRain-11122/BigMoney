# regime_p0_slice2.py -- O-20261010-1725 M-1 P0 matrix slice TWO (zero-burn)
#
# Faces (P0 declared-weapon home-ground verification, O-1725 sec.2 P0 rows):
#   A. dip_rebound  = REV-OSC refined sleeve FY_BG_TP8 (first-yang entry +
#      bear gate + TP8, REFINE-BENCH-20260926-P1 refined) -- located stream:
#      results/rev_osc/daily_series_FY_BG_TP8.json (DECISION_CHAIN_V2_P1
#      sleeve-daily-series, judged frozen config rev_osc_stock_p1.sim_cell,
#      deterministic zero-rng, cutoff 2026-09-22). P0_MATRIX_SLICE_V1 sec.4
#      said "no standalone daily stream in-repo" -> LOCATED, this slice wires
#      it (sec.4 row superseded).
#   B. theme_wave   = theme judge p1/p2 episodes.csv event-window attribution
#      (regime label at episode ignition_date; PANIC day priority).
#
# Law chain: O-20261010-1725 sec.2 "zero-burn v1 = re-slice of adjudicated
#   return streams, attribution not new search, D-41 legal, zero trial
#   budget". Axis freeze: research/REGIME_AXIS_M1_FREEZE.md (bm-b r836).
#   Attribution is NOT a new-criterion claim; scheduling enforcement goes
#   through its own prereg (freeze sec.4).
#
# Reuse law (no-reimplementation): bucket_stats / loaders / constants are
#   imported from scripts/regime_p0_slice.py (v1, r875 selftest 10/10).

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regime_p0_slice import (  # noqa: E402
    COLS, DEPOSIT_FLOOR, EVIDENCE_CUTOFF, LABEL_FIRST, TD_PER_YEAR, W12M,
    bucket_stats, load_calendar, load_labels, load_panic_days,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV_OSC_SERIES = os.path.join(ROOT, "results", "rev_osc",
                              "daily_series_FY_BG_TP8.json")
THEME_EPISODES = [
    ("TJ", os.path.join(ROOT, "results", "theme_judge_p1", "episodes.csv")),
    ("TJ2", os.path.join(ROOT, "results", "theme_judge_p2", "episodes.csv")),
]
# stored stats are rounded (sharpe 3dp / ann & dd 5-6dp) -- cross-check gate
# tolerances absorb the rounding, not a re-definition of the stats.
XCHK = {"sharpe_atol": 2e-3, "ann_atol": 2e-4, "mdd_atol": 2e-4}
SYS_NET_RANGE = (-0.99, 5.0)  # honest sanity band for episode net returns


def _full_span_stats(series):
    """Full-span face recomputation (drop the initial 0.0 day, same as the
    artifact's own stats convention; cross-checked against stored stats)."""
    rets = np.asarray(series[1:], dtype=float)
    nav = np.concatenate([[1.0], np.cumprod(1.0 + rets)])
    sd = rets.std(ddof=1)
    sharpe = float(rets.mean() / sd * np.sqrt(TD_PER_YEAR)) if sd > 0 else 0.0
    yrs = len(rets) / TD_PER_YEAR
    ann = float(nav[-1] ** (1.0 / yrs) - 1.0) if yrs > 0 else 0.0
    peak = np.maximum.accumulate(nav)
    mdd = float((nav / peak - 1.0).min())
    return {"sharpe_full": round(sharpe, 6), "ann_ret": round(ann, 6),
            "max_dd": round(mdd, 6)}


def slice_dip_rebound(labels, panic):
    """Leg A: FY_BG_TP8 sleeve daily series x regime buckets.

    Alignment: artifact carries explicit parallel arrays -- series[i] is the
    net return realized ON dates[i] (verified by full-span stats cross-check
    vs the artifact's stored stats). No tail-anchor needed (unlike fund trio
    cont files which carry t0+returns only).
    """
    d = json.load(open(REV_OSC_SERIES, encoding="utf-8"))
    faces = {}
    for f in ("x1", "x2"):
        fc = d["faces"][f]
        series, dates = fc["series"], fc["dates"]
        if len(series) != len(dates):
            raise SystemExit(f"shape gate FAIL {f}: len mismatch")
        if any(dates[i] >= dates[i + 1] for i in range(len(dates) - 1)):
            raise SystemExit(f"date order gate FAIL {f}: not strictly rising")
        # integrity: full-span recomputation == stored stats (rounding tol)
        rec = _full_span_stats(series)
        st = fc["stats"]
        if (abs(rec["sharpe_full"] - st["sharpe_full"]) > XCHK["sharpe_atol"]
                or abs(rec["ann_ret"] - st["ann_ret"]) > XCHK["ann_atol"]
                or abs(rec["max_dd"] - st["max_dd"]) > XCHK["mdd_atol"]):
            raise SystemExit(
                f"full-span cross-check FAIL {f}: recomputed {rec} vs stored "
                f"sharpe={st['sharpe_full']} ann={st['ann_ret']} "
                f"mdd={st['max_dd']}")
        buckets = {c: [] for c in COLS}
        unlabeled = 0
        panic_in = 0
        for i in range(len(series)):
            dt = dates[i]
            if dt < LABEL_FIRST:
                unlabeled += 1
                continue
            if dt in panic:
                buckets["PANIC"].append(series[i])
                panic_in += 1
                continue
            s = labels.get(dt)
            if s is None or s not in ("BULL", "CHOP", "GRIND", "BEAR",
                                      "SUPPORT"):
                unlabeled += 1
                continue
            buckets[s].append(series[i])
        faces[f] = {
            "n_days": len(series),
            "date_first": dates[0],
            "date_last": dates[-1],
            "sha256_series_stored": fc.get("sha256_series"),
            "full_span_stored": st,
            "full_span_recomputed": rec,
            "unlabeled_days": unlabeled,
            "labeled_days": sum(len(buckets[c]) for c in COLS),
            "panic_days_in": panic_in,
            "active_days_nonzero": int(sum(1 for x in series if x != 0.0)),
            "counters_stored": fc.get("counters"),
            "by_regime": {c: bucket_stats(buckets[c]) for c in COLS},
        }
    return {
        "family": "dip_rebound",
        "three_piece": "FY first-yang entry + BG bear gate + TP8 take-profit "
                       "(REFINE-BENCH-20260926-P1 refined sleeve)",
        "source": "results/rev_osc/daily_series_FY_BG_TP8.json",
        "provenance": d["provenance"],
        "declared_home": "BEAR (style matrix dip_rebound sleeve row)",
        "faces": faces,
    }


def episode_stats(nets, excess):
    """Event-window stats face for one regime bucket of episodes.

    Episodes are short event windows (wlen days), so the 12m all-start
    rolling machinery does not apply -- the honest stats face is the
    per-episode net/excess distribution.
    """
    r = np.asarray(nets, dtype=float)
    e = np.asarray(excess, dtype=float)
    n = len(r)
    out = {"n_episodes": n}
    if n == 0:
        return out
    out.update({
        "median_sys_net": round(float(np.median(r)), 4),
        "p25": round(float(np.percentile(r, 25)), 4),
        "p75": round(float(np.percentile(r, 75)), 4),
        "best": round(float(r.max()), 4),
        "worst": round(float(r.min()), 4),
        "pos_share": round(float((r > 0).mean()), 4),
        "median_excess_vs_bh": round(float(np.median(e)), 4),
        # e = net - bh, so e > 0 <=> net > bh (beat the buy-and-hold window)
        "beat_bh_share": round(float((e > 0).mean()), 4),
    })
    if n < 30:
        out["sample_note"] = (f"n={n} < 30 episodes: small-sample bucket, "
                              "read distribution shape not verdicts")
    return out


def slice_theme(labels, panic):
    """Leg B: theme episodes x regime label at ignition_date."""
    batches = {}
    for tag, path in THEME_EPISODES:
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        strata = {}
        for stratum in sorted(set(r["stratum"] for r in rows)):
            srows = [r for r in rows if r["stratum"] == stratum]
            sfaces = {}
            for face in ("x1", "x2"):
                buckets = {c: {"net": [], "exc": []} for c in COLS}
                unlabeled = 0
                panic_in = 0
                for r in srows:
                    dt = r["ignition_date"]
                    net = float(r[f"sys_net_{face}"])
                    bh = float(r[f"bh_net_{face}"])
                    if not (SYS_NET_RANGE[0] <= net <= SYS_NET_RANGE[1]):
                        raise SystemExit(
                            f"sys_net sanity gate FAIL {tag}/{stratum}/"
                            f"{face}: {net} out of honest range")
                    if dt < LABEL_FIRST:
                        unlabeled += 1
                        continue
                    if dt in panic:
                        buckets["PANIC"]["net"].append(net)
                        buckets["PANIC"]["exc"].append(net - bh)
                        panic_in += 1
                        continue
                    st = labels.get(dt)
                    if st is None or st not in ("BULL", "CHOP", "GRIND",
                                                "BEAR", "SUPPORT"):
                        unlabeled += 1
                        continue
                    buckets[st]["net"].append(net)
                    buckets[st]["exc"].append(net - bh)
                sfaces[face] = {
                    "n_episodes": len(srows),
                    "unlabeled_episodes": unlabeled,
                    "panic_ignitions": panic_in,
                    "by_regime": {
                        c: episode_stats(buckets[c]["net"],
                                         buckets[c]["exc"])
                        for c in COLS
                    },
                }
            strata[stratum] = sfaces
        batches[tag] = {
            "source": "results/theme_judge_p1/episodes.csv"
                      if tag == "TJ" else
                      "results/theme_judge_p2/episodes.csv",
            "n_episodes_total": len(rows),
            "ignition_date_range": [min(r["ignition_date"] for r in rows),
                                    max(r["ignition_date"] for r in rows)],
            "strata": strata,
        }
    return {
        "family": "theme_wave_ride",
        "declared_home": "BULL (style matrix cta/theme row, O-1725 P0 "
                         "declared bull weapon)",
        "window_semantics": "episode = theme ignition event window (wlen "
                            "days, stratum FULL/SOLO); regime = REGIME-5 "
                            "label at ignition_date; panic-day ignitions "
                            "bucket to PANIC with priority",
        "batches": batches,
    }


def run(out_path):
    # calendar identity gate (same as slice v1, r875 law)
    dates = load_calendar()
    labels = load_labels()
    panic = load_panic_days()
    lab_dates = [x for x in labels if LABEL_FIRST <= x <= EVIDENCE_CUTOFF]
    cal_dates = [x for x in dates if x >= LABEL_FIRST]
    if set(lab_dates) != set(cal_dates):
        raise SystemExit("calendar identity gate FAIL: regime5 labels vs "
                         "thermo date sets differ over labeled span")
    dip = slice_dip_rebound(labels, panic)
    theme = slice_theme(labels, panic)
    payload = {
        "schema": "p0-matrix-slice2",
        "batch": "P0-MATRIX-SLICE2-DIPREBOUND-THEME",
        "order_ref": "O-20261010-1725 sec.2 zero-burn v1 (P0 rows: dip "
                     "rebound home-ground verify + theme event-window)",
        "axis_freeze": "research/REGIME_AXIS_M1_FREEZE.md (bm-b r836)",
        "deposit_floor": DEPOSIT_FLOOR,
        "td_per_year": TD_PER_YEAR,
        "roll_window_td": W12M,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "label_first_day": LABEL_FIRST,
        "calendar_axis": "results/regime_thermo/thermo_daily.csv (identity "
                         "gate); dip series aligned by its own explicit "
                         "dates array (cross-checked vs stored stats)",
        "attribution_note": "slice attribution only; NOT a new-criterion "
                            "claim; scheduling enforcement goes through its "
                            "own prereg (freeze sec.4)",
        "dip_rebound": dip,
        "theme_wave": theme,
        "coverage_gaps_update": {
            "four_asset": "unchanged from slice v1: no in-repo daily stream "
                          "(replay leg)",
            "six_member_defensive_and_system_v1": "unchanged: forward paper "
                                                  "marks too short for 12m "
                                                  "windows",
            "dip_rebound": "RESOLVED this slice: located stream "
                           "(DECISION_CHAIN_V2_P1 sleeve-daily-series) and "
                           "wired into the matrix -- slice v1 sec.4 row "
                           "superseded",
            "theme_wave": "RESOLVED this slice: event-window attribution "
                          "landed (ignition-date regime bucketing)",
        },
        "audit": {
            "machine": "bm-c",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_note": "zero-burn deterministic re-slice, no engine "
                            "re-run, no new trials",
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
        "dip_faces": list(dip["faces"].keys()),
        "theme_batches": list(theme["batches"].keys()),
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
        and DEPOSIT_FLOOR == 0.0130)
    # leg2: episode_stats math on a known synthetic set
    st = episode_stats([0.01, 0.03], [-0.02, 0.01])
    chk("ep median", st["median_sys_net"] == 0.02)
    chk("ep pos_share", st["pos_share"] == 1.0)
    chk("ep beat_bh_share", st["beat_bh_share"] == 0.5)
    chk("ep excess median", st["median_excess_vs_bh"] == -0.005)
    # leg3: empty bucket honest
    st0 = episode_stats([], [])
    chk("ep empty", st0 == {"n_episodes": 0})
    # leg4: small-sample note
    chk("ep small note", "sample_note" in episode_stats([0.01] * 5,
                                                        [0.0] * 5))
    # leg5: bucket_stats passthrough (v1 machinery intact via import)
    stb = bucket_stats(np.full(504, 0.001))
    chk("bucket_stats reuse", stb["roll12"]["n_windows"] == 504 - W12M + 1)
    # leg6: full-span stats convention (drop initial 0.0 day; 6dp rounding)
    fs = _full_span_stats([0.0] + [0.001] * 503)
    chk("fullspan drop-first", abs(fs["ann_ret"] - (1.001 ** 252 - 1))
        < 2e-6)
    # leg7: sys-net sanity band constant
    chk("sanity band", SYS_NET_RANGE == (-0.99, 5.0))
    # leg8: slice constants inherited unchanged
    chk("constants", W12M == 252 and TD_PER_YEAR == 252
        and LABEL_FIRST == "2013-03-21")
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    ap.add_argument("--out", default=os.path.join(
        ROOT, "results", "regime_style_matrix",
        "P0-SLICE2-DIPREBOUND-THEME-20261011.json"))
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    sys.exit(main())
