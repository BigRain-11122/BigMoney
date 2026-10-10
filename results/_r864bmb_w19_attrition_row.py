"""r864 bm-b PERPETUAL-N2-W19 slice-4 judged-burn attrition row append.

W18 row precedent (r861, kind=search-refusal) + LHB_THERMO_IC_P1 judged
precedent (kind=ic_judgment). This batch is JUDGEABLE (pooled 336>=300),
so kind=ic_judgment with the full decomposition face. Round-trip
fidelity pre-verified (json.dumps indent=1 ensure_ascii=False byte-
identical) so the append preserves the file format exactly.
"""
import json

PATH = "results/gate_attrition.json"

row = {
    "batch": "PERPETUAL-N2-W19",
    "ts": "2026-10-11 06:0x",
    "kind": "ic_judgment",
    "cells_ledger_delta": 496,
    "ledger_total_after": 877227,
    "gates": {
        "face": "family-level V1 (T23 census calibration law) + per-survivor "
                "M1 t>=3.0 positive-direction; per-cell full chain = "
                "h1_ok survivor AND M1; registration chain NOT in batch "
                "scope (material pool only, prereg sec.0)",
        "v1_pass": 1,
        "v1_unjudgeable": 0,
        "m1_pass": 9,
        "full_chain_pass": 9
    },
    "entries": [
        "freeze_window=r864_bm-b_f5426c419",
        "pooled_nulls=336>=300_frozen_sufficiency_line->first_judgeable_burn"
        "_of_the_feedback_lever",
        "attrition=6_t84s3+5_in_batch_dup->11_excluded;51_enrolled;"
        "3_h1_skip(5.9%<10%_guard);48_ok;48*7=336",
        "v1_family_max|ICIR|=0.38>pooled_null_p95=0.086->HOLDS",
        "d1_leverage=0.38_vs_census_random_0.353->positive_signal"
        "(descriptive_non-gating;K=62_vs_64_parity_disclosed)",
        "m1_t>=3.0_positive_direction=9/48_survivors",
        "material_pool_only;zero_registration;zero_engine_runs"
    ]
}

with open(PATH, encoding="utf-8") as f:
    raw = f.read()
d = json.loads(raw)
rt = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
assert rt == raw, "round-trip fidelity broken, abort"
assert not any(e.get("batch") == "PERPETUAL-N2-W19"
              for e in d["entries"]), "row already present"
d["entries"].append(row)
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("appended PERPETUAL-N2-W19 row; entries n =", len(d["entries"]))
