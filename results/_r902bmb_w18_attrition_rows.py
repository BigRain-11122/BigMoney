# -*- coding: utf-8 -*-
"""r902 bm-b TRIAL_LABOR_W18 finalize-closeout attrition rows (prereg sec.6 deliverable).

MASS_TRIAL_W1/_W1_JUDGE schema precedent (kind=measurement, gates face) +
W20 append mechanics (round-trip fidelity + already-present guard).
Fills the sec.6 face the dead finalize (PID25060) left unwritten; r900
had started probing this gap (results/_r900bmb_attrition_check.py).
"""
import json

PATH = "results/gate_attrition.json"

row_screen = {
    "batch": "TRIAL_LAB_W18_SCREEN",
    "ts": "2026-10-11 19:10",
    "kind": "measurement",
    "cells_ledger_delta": 892,
    "ledger_total_after": 879189,
    "gates": {
        "screen_pass": {
            "n_candidates": 692,
            "n_nulls": 200,
            "n_survivors": 152,
            "line": "beat6m_rate > null_p95 (W2 frozen math)",
            "null_p95": 0.511572,
            "null_p95_band": [0.5, 0.53],
            "survivors_by_face": {"equal_weight": 41, "cap20": 37, "inverse_vol": 35, "regime_delever": 39},
            "as_burned_identity": "43/173 vs W17 control three-column byte-identical (sec.5.1 hard gate)"
        }
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W18_PREREG.md (frozen bm-c r879)",
        "source=W16 frozen 173 candidates verbatim (zero new generation; gen seed 20630000 held)",
        "dedup_face=NA (verbatim reuse, T-84s3 no-op by construction)",
        "ledger=878297+892=879189 (trials_ledger block in w18_screen.json)",
        "sec.6 closeout row appended r902 bm-b (finalize process PID25060 landed products 00:44 but died pre-attrition-row)"
    ]
}

row_judge = {
    "batch": "TRIAL_LAB_W18_JUDGE",
    "ts": "2026-10-12 00:44",
    "kind": "measurement",
    "cells_ledger_delta": 188,
    "ledger_total_after": 885977,
    "gates": {
        "g1_prime_v2": {
            "n_judged": 188,
            "n_pass": 0,
            "line": "sharpe_full > skill_line_v2=1.1481 @ n_eff 883777 (fork-branch reading) AND bootstrap CI lower>0 AND entries>=0"
        },
        "g2_registration_v2": {
            "n_eligible": 0,
            "line": "G1' pass AND DSR>=0.95 AND family PBO<=0.25 CSCV 8 blocks",
            "family_pbo_worst": "momentum 0.9143/32, folk 0.8429/36; best ta 0.3857/28 (all families fail <=0.25)"
        },
        "e_fp_nominal": 9.4,
        "paired_deltas": "four-face median delta ~0 (eq +0.0001/cap20 0.0/inv -0.0005/del 0.0; IQR 0.029-0.081) = sizing axis zero-median-migration on judged-negative pool"
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W18_PREREG.md sec.7/sec.8 backfilled r902 (one-shot definitive)",
        "blocks=47 complete paired blocks x4 faces=188 (152 surviving legs over 47 cells + 36 non-surviving sibling legs for paired reading)",
        "ledger_fork=prev 883589 captured at judge-prep 19:11 pre-W210; W210 landed 23:2x from same prev (885789) -> judge block 883777 sub-head",
        "reanchor=r902 append-only re-anchor row 885789+188=885977 on live chain (results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json; r807 pre-push fork window catch; superseded branch 883777 must never be re-added)",
        "verdict_stability=looser-side (line at n_eff 883777 < live 885977-derived; all-fail stays all-fail; r638 single-read)",
        "sec.0 consumer (2) fulfilled: negative reading -> X (sizing) axis de-weight justification live-fire; zero onboard; same-grammar rerun FORBIDDEN"
    ]
}

with open(PATH, encoding="utf-8") as f:
    raw = f.read()
d = json.loads(raw)
rt = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
assert rt == raw, "round-trip fidelity broken, abort"
for row in (row_screen, row_judge):
    assert not any(e.get("batch") == row["batch"] for e in d["entries"]), "row already present: " + row["batch"]
    d["entries"].append(row)
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("appended TRIAL_LAB_W18_SCREEN + TRIAL_LAB_W18_JUDGE rows; entries n =", len(d["entries"]))
