# -*- coding: utf-8 -*-
"""r966 bm-a: TRIAL_LAB_W17 gate-attrition rows late append (sec.6 closeout heal).

W17 judge-finalize products landed 2026-10-11 06:48 (r964 session) but the
session died pre-attrition-row -- same death pattern as W18 (healed by
r902 bm-b).  This appends the two mandated rows (prereg sec.6:
"attrition 行（SCREEN 1,584+JUDGE 8×n_blocks）") to all four attrition
faces (canonical + three lane mirrors, W18 r902 mirror precedent).

Facts source = frozen wave products (no re-derive):
  SCREEN: results/trial_labor_w17/w17_screen.json trials_ledger
          (prev 864387 + 1584 = 865971); n_survivors 332; null_p95
          0.511572 band [0.5,0.53] hit; control-determinism 25/25;
          sec5.1 prediction accounting predicted 40 vs observed 43 MISS.
  JUDGE : results/trial_labor_w17/w17_judge.json trials_ledger
          (prev 877753 + 344 = 878097); n_judged 344; G1 pass 0;
          G2 eligible 0; E[FP] 17.2; family PBO worst momentum 0.9571.

Idempotent: refuses double-append per (file, batch) single-shot guard.
Guard-safe: attrition_ledger_guard checks key-set supersets only
(append-only), value order not asserted; late rows carry historical
ledger totals with explicit late-append provenance in entries[].
"""
import json
import io

FILES = [
    "results/gate_attrition.json",
    "results/gate_attrition.bm-a.json",
    "results/gate_attrition.bm-b.json",
    "results/gate_attrition.bm-c.json",
]

ROW_SCREEN = {
    "batch": "TRIAL_LAB_W17_SCREEN",
    "ts": "2026-10-10 22:30",
    "kind": "measurement",
    "cells_ledger_delta": 1584,
    "ledger_total_after": 865971,
    "gates": {
        "screen_pass": {
            "n_candidates": 1584,
            "n_nulls": 200,
            "n_survivors": 332,
            "line": "beat6m_rate > null_p95 (prereg sec.4 frozen W2 math, zero hand-picked)",
            "null_p95": 0.511572,
            "null_p95_band": [0.5, 0.53],
            "null_p95_band_hit": True,
            "control_determinism": "25/25 rerun pairs byte-identical (W16 carry-over)",
            "sec51_prediction_accounting": {"predicted": 40, "observed_control_survivors": 43, "verdict": "MISS"},
        }
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W17_PREREG.md (frozen bm-c r788 2026-10-09)",
        "ledger=864387+1584=865971 (trials_ledger block in results/trial_labor_w17/w17_screen.json)",
        "sec.6 closeout row late-appended r966 bm-a (screen landed 10-10 22:30; r963/r964 dead-window debt; heal per r902 bm-b W18 late-append precedent)",
    ],
}

ROW_JUDGE = {
    "batch": "TRIAL_LAB_W17_JUDGE",
    "ts": "2026-10-11 06:48",
    "kind": "measurement",
    "cells_ledger_delta": 344,
    "ledger_total_after": 878097,
    "gates": {
        "g1_prime_v2": {
            "n_judged": 344,
            "n_pass": 0,
            "line": "sharpe_full > skill_line_v2=1.1478 @ n_eff 878097 AND bootstrap CI lower>0 AND trade_gate (n_trades>=30 AND n_entries>=30)",
        },
        "g2_registration_v2": {
            "n_eligible": 0,
            "line": "G1' pass AND DSR>=0.95 AND family PBO<=0.25 CSCV 8 blocks",
            "family_pbo_worst": "momentum 0.9571/64, folk 0.8286/72, sentiment 0.8/16; event/trend/volatility 0.0 at n_cells=8 each = small-cell zeros, not quality evidence",
        },
        "e_fp_nominal": 17.2,
        "paired_deltas": "seven exit-rule faces ratio 0.966-1.0, wilcoxon p 0.98-1.0 = exit-axis zero-migration on judged-negative pool (results/trial_labor_w17/w17_paired_deltas.json)",
    },
    "entries": [
        "prereg=research/TRIAL_LABOR_W17_PREREG.md sec.7/sec.8 backfilled same round (r966)",
        "blocks=43 complete paired blocks x8 exit faces=344",
        "ledger=877753+344=878097 (trials_ledger block in results/trial_labor_w17/w17_judge.json)",
        "products=results/trial_labor_w17/{w17_judge.json,w17_reform_face.json,w17_paired_deltas.json,w17_intake.json (lawful-zero, r966)}",
        "verdict=lawful-zero (0/344 G1, 0 eligible, onboard 0) = honest negative wave; negative-result-report law applies (照报不粉饰)",
        "sec.6 closeout row late-appended r966 bm-a (judge-finalize landed products 10-11 06:48 but r964 session died pre-attrition-row; heal per r902 bm-b W18 late-append precedent)",
    ],
}


def main() -> int:
    for path in FILES:
        with io.open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        entries = d["entries"]
        for row in (ROW_SCREEN, ROW_JUDGE):
            if any(e.get("batch") == row["batch"] for e in entries):
                print(f"SKIP {path}: {row['batch']} already present (single-shot guard)")
                continue
            entries.append(row)
            print(f"APPEND {path}: {row['batch']} (delta {row['cells_ledger_delta']}, after {row['ledger_total_after']})")
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("done: all four faces updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
