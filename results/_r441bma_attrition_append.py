# r441 bm-a: append gate_attrition history row for T-101-V4-A158-FULLVERDICT
import json
import time

path = 'results/gate_attrition.json'
with open(path, encoding='utf-8') as f:
    d = json.load(f)

row = {
    "batch": "T-101-V4-A158-FULLVERDICT",
    "kind": "judgment",
    "cells_ledger_delta": 9,
    "eliminated": 9,
    "gates": {
        "e_fp_nominal_5pct": 0.45,
        "family_pbo": {
            "module_grid_note": "canonical CSCV over 17 tried gate configs per member "
                                 "(own-calendar complete matrix, n=17>=8)",
            "510300": {"n_cells": 2, "pbo": 0.3714, "verdict": "observe"},
            "510500": {"n_cells": 4, "pbo": 0.5571, "verdict": "fail"},
            "588000": {"n_cells": 3, "pbo": 0.1857, "verdict": "register_eligible",
                       "judged_subgrid_insufficient": True},
        },
        "g1_prime_v2": {
            "n": 9, "n_pass": 0,
            "line": "skill_line_v2=1.7201 batch-own null pool (mu=-0.0162 sigma=0.3438 "
                    "N_eff=344040); top cell 588000|VSUMD30 sharpe_full=0.8055 -- "
                    "line_ok false; 3 cells bootstrap ci_lower_positive (below line)",
        },
        "g2_registration_v2": {
            "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25",
            "n_eligible": 0, "n_trials": 344040,
            "top_dsr": 0.024749, "top_dsr_cell": "510300|RANK30_q90",
        },
    },
    "collapse": {
        "accept13_to_9": True,
        "dropped_redundant": ["588000|RESI60_q90", "588000|SUMN10_q10",
                              "588000|VSUMD10_q90", "588000|VSUMD20_q90"],
        "rule": "connected components |corr|>=0.7 per member; keep max oos_excess_vs_bh",
    },
    "ledger_total_after": 344040,
    "refs": {
        "prereg": "research/T-101-V4_A158_FULLVERDICT_PREREG.md",
        "results": "results/t101_v4_a158_fv.json",
        "upstream": "results/gate_timing_prescreen_a158.json (bm-c r231)",
    },
    "retro_fill": False,
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
}
d["history"].append(row)
with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("appended row; history len =", len(d["history"]))
