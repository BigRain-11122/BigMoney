"""r866 bm-b PERPETUAL-N2-W20 slice-3 judged-burn attrition row append.

W19 row precedent (r864, kind=ic_judgment). This batch is JUDGEABLE
(pooled 336>=300), so kind=ic_judgment with the full decomposition
face. Round-trip fidelity pre-verified (json.dumps indent=1
ensure_ascii=False byte-identical) so the append preserves the file
format exactly.
"""
import json

PATH = "results/gate_attrition.json"

row = {
    "batch": "PERPETUAL-N2-W20",
    "ts": "2026-10-11 06:5x",
    "kind": "ic_judgment",
    "cells_ledger_delta": 496,
    "ledger_total_after": 877723,
    "gates": {
        "face": "family-level V1 (T23 census calibration law) + per-survivor "
                "M1 t>=3.0 positive-direction; per-cell full chain = "
                "h1_ok survivor AND M1; registration chain NOT in batch "
                "scope (material pool only, prereg sec.0)",
        "v1_pass": 1,
        "v1_unjudgeable": 0,
        "m1_pass": 0,
        "full_chain_pass": 0
    },
    "entries": [
        "freeze_window=r866_bm-b_526f3d4d3",
        "pooled_nulls=336>=300_frozen_sufficiency_line->second_judgeable"
        "_burn_of_the_feedback_lever(replication_wave)",
        "attrition=10_t84s3+3_in_batch_dup->13_excluded;49_enrolled;"
        "1_h1_skip(2.0%<10%_guard);48_ok;48*7=336",
        "v1_family_max|ICIR|=0.478>pooled_null_p95=0.087->HOLDS",
        "rp1_band[0.20,0.45]=0.478_above_band->band_replication_FAILS"
        "(disclosed_per_prereg_law_no_re-tune)",
        "rp2_leverage=0.478>=census_random_0.353->2/2_independent_readings"
        "->leverage_claim_UPGRADED_citable(descriptive_non-gating)",
        "m1_t>=3.0_positive_direction=0/48_survivors"
        "(negative_direction|t|>=3=27/48_descriptive_disclosure)",
        "material_pool_only;zero_registration;zero_engine_runs"
    ]
}

with open(PATH, encoding="utf-8") as f:
    raw = f.read()
d = json.loads(raw)
rt = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
assert rt == raw, "round-trip fidelity broken, abort"
assert not any(e.get("batch") == "PERPETUAL-N2-W20"
              for e in d["entries"]), "row already present"
d["entries"].append(row)
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("appended PERPETUAL-N2-W20 row; entries n =", len(d["entries"]))
