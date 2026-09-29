# -*- coding: utf-8 -*-
"""r417 bm-b: backfill 9 missing trial-labor attrition rows (T-118 drift-debt face #2).

Writes shared results/gate_attrition.json + bm-b lane, ts-sorted insert into
'history', original event timestamps, backfill note per row. Idempotent:
rows already present (by batch key) are skipped, so a rerun is a no-op.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"
NOTE = ("r417 bm-b backfill (T-118 drift-debt face #2): attrition row missed in "
        "its landing window across 2026-09-28/29 waves W1-W5; original event ts "
        "preserved; numbers true-source = results/trial_labor_w{N}/*.json "
        "read-only (no re-burn); receipt = TRIAL_LABOR_W{N}_PREREG sec.8")

ROWS = [
    dict(batch="TRIAL_LABOR_W1_SCREEN", ts="2026-09-28 01:21:37", kind="measurement",
         cells_ledger_delta=858, ledger_total_after=288384,
         gates={"screen_pass": {"n_candidates": 658, "n_survivors": 149,
               "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.511572, prereg sec.3 frozen)"},
                "null_face": {"p50": 0.4497, "p95": 0.511572, "n": 200}},
         eliminated=509, n=1),
    dict(batch="TRIAL_LAB_W2_SCREEN", ts="2026-09-28 07:00:27", kind="measurement",
         cells_ledger_delta=3124, ledger_total_after=297428,
         gates={"screen_pass": {"n_candidates": 2924, "n_survivors": 404,
               "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.511572, prereg sec.3 frozen)"},
                "null_face": {"p50": 0.4521, "p95": 0.511572, "n": 200}},
         eliminated=2520, n=2),
    dict(batch="TRIAL_LAB_W4_SCREEN", ts="2026-09-28 13:12:31", kind="measurement",
         cells_ledger_delta=4010, ledger_total_after=305190,
         gates={"screen_pass": {"n_candidates": 3810, "n_survivors": 461,
               "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.516441, prereg sec.3 frozen)"},
                "null_face": {"p50": 0.494, "p95": 0.516441, "n": 200}},
         eliminated=3349, n=4),
    dict(batch="TRIAL_LAB_W2_JUDGE", ts="2026-09-28 14:38:37", kind="judgment",
         cells_ledger_delta=404, ledger_total_after=311214,
         gates={"g1_prime_v2": {"n": 404, "n_pass": 11,
               "line": "skill_line_v2 per-cell (ledger_head live read); top W2-B-1971 box_breakout p12 sharpe_full=1.635 vs line=1.189 -- line_ok true; 11 passers all sample_sufficient verdict=pass"},
                "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.367222, "n_trials": 310810,
               "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
                "e_fp_nominal_5pct": 20.2},
         eliminated=393, n=2),
    dict(batch="TRIAL_LABOR_W1_JUDGE", ts="2026-09-28 14:50:01", kind="judgment",
         cells_ledger_delta=149, ledger_total_after=311363,
         gates={"g1_prime_v2": {"n": 149, "n_pass": 4,
               "line": "skill_line_v2 per-cell (ledger_head live read); top W1-A-0360 sharpe_full=1.6316 vs line=1.1887 (n_eff=312072) -- line_ok true; passers W1-A-0007/0048/0066/0360 all sample_sufficient verdict=pass (backfill-time discovery: CEO-REPORT-WAVE1 carried 0 for wave-1b -- corrected by r417 addendum, zero-hire conclusion unchanged)"},
                "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.462294, "n_trials": 311214,
               "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
                "e_fp_nominal_5pct": 7.45},
         eliminated=145, n=1),
    dict(batch="TRIAL_LAB_W3_JUDGE", ts="2026-09-28 15:51:55", kind="judgment",
         cells_ledger_delta=513, ledger_total_after=311876,
         gates={"g1_prime_v2": {"n": 513, "n_pass": 2,
               "line": "skill_line_v2 per-cell (ledger_head live read); top W3-A-0325 top_n_rotation none 1.3283 vs line=1.1892 -- line_ok true"},
                "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.087752, "n_trials": 311363,
               "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
                "e_fp_nominal_5pct": 25.65},
         eliminated=511, n=3),
    dict(batch="TRIAL_LAB_W4_JUDGE", ts="2026-09-28 20:03:05", kind="judgment",
         cells_ledger_delta=461, ledger_total_after=317859,
         gates={"g1_prime_v2": {"n": 461, "n_pass": 0,
               "line": "skill_line_v2 per-cell (ledger_head live read); top cell W4-A-0174 sharpe_full=1.1059 vs line=1.1901 (n_eff=321408) -- line_ok false; all-face zero"},
                "g2_registration_v2": {"n_eligible": 0, "top_dsr": 3e-06, "n_trials": 317398,
               "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
                "e_fp_nominal_5pct": 23.05},
         eliminated=461, n=4),
    dict(batch="TRIAL_LAB_W5_SCREEN", ts="2026-09-29 02:35:48", kind="measurement",
         cells_ledger_delta=4126, ledger_total_after=328615,
         gates={"screen_pass": {"n_candidates": 3926, "n_survivors": 372,
               "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.516361, prereg sec.3 frozen)"},
                "null_face": {"p50": 0.4972, "p95": 0.516361, "n": 200}},
         eliminated=3554, n=5),
    dict(batch="TRIAL_LAB_W5_JUDGE", ts="2026-09-29 03:48:39", kind="judgment",
         cells_ledger_delta=372, ledger_total_after=328987,
         gates={"g1_prime_v2": {"n": 372, "n_pass": 1,
               "line": "skill_line_v2 per-cell (ledger_head live read); top W5-B-2619 box_breakout none/none/none sharpe_full=1.6861 vs line=1.1918 -- line_ok true"},
                "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.439559, "n_trials": 328615,
               "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
                "e_fp_nominal_5pct": 18.6},
         eliminated=371, n=5),
]


def build(row):
    n = row.pop("n")
    out = {
        "batch": row["batch"], "ts": row["ts"], "kind": row["kind"],
        "cells_ledger_delta": row["cells_ledger_delta"],
        "ledger_total_after": row["ledger_total_after"],
        "gates": row["gates"],
        "eliminated": row["eliminated"],
        "refs": {
            "prereg": f"research/TRIAL_LABOR_W{n}_PREREG.md",
            "results": f"results/trial_labor_w{n}/w{n}_"
                       + ("screen.json" if row["kind"] == "measurement" else "judge.json"),
            "ticket": "T-2026-09-29-118",
        },
        "note": NOTE.replace("{N}", str(n)),
    }
    return out


def apply(path):
    with open(path, encoding="utf-8") as fh:
        ga = json.load(fh)
    have = {r.get("batch") for r in ga.get("history", [])}
    added = 0
    for row in ROWS:
        if row["batch"] in have:
            continue
        ga["history"].append(build(dict(row)))
        added += 1
    ga["history"].sort(key=lambda r: str(r.get("ts", "")))
    if added:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    with open(path, encoding="utf-8") as fh:
        back = json.load(fh)
    assert isinstance(back.get("history"), list)
    return added, len(back["history"])


for p in (os.path.join(ROOT, "results", "gate_attrition.json"),
          os.path.join(ROOT, "results", "gate_attrition.bm-b.json")):
    added, total = apply(p)
    print(f"{os.path.basename(p)}: +{added} rows -> history {total}")
