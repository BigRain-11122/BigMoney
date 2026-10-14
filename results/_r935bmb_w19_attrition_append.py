# r935 bm-b: append TRIAL_LAB_W19 SCREEN+JUDGE attrition rows to both ledgers (append-only, W18 r932 pattern mirror)
import json, io, sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
UTC_NOTE = "ts = product-file mtime face (judge finalize 13:49:47 out.log receipt)"

j = json.load(io.open(ROOT + r"\results\trial_labor_w19\w19_judge.json", encoding="utf-8"))
fp = j.get("family_pbo", {})
fp_str = "; ".join(f"{k} {v['pbo']}/{v.get('n_cells')}" if v.get("pbo") is not None else f"{k} None/{v.get('n_cells')} (insufficient<8)" for k, v in fp.items())

screen_row = {
    "batch": "TRIAL_LAB_W19_SCREEN",
    "ts": "2026-10-14 11:12",
    "kind": "measurement",
    "cells_ledger_delta": 546,
    "ledger_total_after": 945735,
    "gates": {
        "screen_pass": {
            "n_candidates": 346,
            "n_nulls": 200,
            "n_survivors": 70,
            "line": "beat6m_rate > null_p95 (W2 frozen math)",
            "null_p95": 0.511572,
            "null_p95_band": [0.5, 0.53],
            "survivors_by_face": {"daily_signal": 47, "weekly_grid": 23},
            "as_burned_identity": "43/173 vs W17 control AND W18 as-burned three-column byte-identical (sec.5.1 hard gate; three-wave determinism chain closed r931)",
        }
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W19_PREREG.md (frozen bm-b r927)",
        "source=W16 frozen 173 cells verbatim reuse x 2 timing faces (tl1.AXIS_TIMING verbatim, zero new timing code)",
        "paired-block design: 346 cells + 200 isomorphic nulls; degenerate 173 pairs disclosed in w19_paired_deltas.json",
        "ledger 945189+546=945735 (results/trial_labor_w19/w19_screen.json trials_ledger)",
    ],
}

judge_row = {
    "batch": "TRIAL_LAB_W19_JUDGE",
    "ts": "2026-10-14 13:49",
    "kind": "measurement",
    "cells_ledger_delta": 112,
    "ledger_total_after": 948047,
    "gates": {
        "g1_prime_v2": {
            "n_judged": 112,
            "n_pass": 0,
            "note": "best sharpe_full_L 0.7515 (W16-B-0730|daily_signal); all below skill line; zero registrations lawful-zero wave",
        },
        "g2_registration_v2": {
            "n_eligible": 0,
            "line": "G1' pass AND DSR>=0.95 AND family PBO<=0.25 CSCV 8 blocks",
            "family_pbo_reading": fp_str,
        },
        "e_fp_nominal": 5.6,
        "paired_deltas": "daily_signal face: informative n=45 (weekly_asburned subgroup), median +0.0942, wilcoxon_p 0.01; weekly_grid face: informative n=128 (daily_asburned subgroup), median -0.2808, wilcoxon_p 0.358; degenerate 173 disclosed",
        "zvx": "8 weekly_grid arms zero-variance excluded (judge members 104 = 112 - 8, disclosed in w19_reform_face.json)",
        "reform_face": "g2_reform_fdr4d eligible_reform=[] onboard_list=[] (reform line parallel negative, E[FP]=5.6 vs 0 observed)",
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W19_PREREG.md sec.0-9 frozen; finalize detached PID 17108 landed 13:49:47 (out.log receipt)",
        "X=template_default (W17 consumer-3) S=as-burned (W18 consumer-2) T=only-tested-axis; execution-side three-axis adjudication chain closed",
        "consumer-2 cashed: T-axis downweight canon basis -- future GENERATE needs entry x filter faces only",
        "ledger 947935+112=948047 (results/trial_labor_w19/w19_judge.json trials_ledger; finalize out.log 'ledger total 948047')",
        UTC_NOTE,
    ],
}

for path in [r"\results\gate_attrition.json", r"\results\gate_attrition.bm-b.json"]:
    full = ROOT + path
    g = json.load(io.open(full, encoding="utf-8"))
    es = g["entries"]
    have = {e.get("batch") for e in es}
    added = []
    for row in (screen_row, judge_row):
        if row["batch"] in have:
            print(f"SKIP already-present {row['batch']} in {path}")
            continue
        es.append(row)
        added.append(row["batch"])
    with io.open(full, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{path}: appended {added} entries_total={len(es)}")

print("family_pbo_reading:", fp_str)
print("ATTRITION_APPEND_DONE")
