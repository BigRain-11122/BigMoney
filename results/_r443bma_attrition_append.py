import json

p = r'results/gate_attrition.bm-a.json'
d = json.load(open(p, encoding='utf-8'))
assert isinstance(d['entries'], list)
d['entries'].append({
    "batch": "T-101-V4-A11-XSELECT",
    "ts": "2026-09-29T19:4x+08:00",
    "host": "bm-a",
    "n_cells": 24,
    "verdict": "FV_FAIL_0of24",
    "line_action": "ARM_XSECTION_SELECT_CLOSE",
    "legs": {
        "top_sharpe": 0.4994,
        "skill_line": 1.2504,
        "top_dsr": 0.0168,
        "family_pbo": {"U5": 0.8143, "U4": 0.0},
        "best_cell": "U4|f_c2|top2|x1",
        "best_oos_excess_cell": "U4|f_c2|top1|x1 (+10.38% / x2 +8.26%)",
        "d6_reject": 24,
        "d6_reject_face": "vs_bh mirror 0.80-0.97 (structural class beta)",
        "below_null_median_cells": "f_rsv30 U4 both + f_roc20 U4 all 4 (below-random ordering = negative information)",
        "maxdd_floor_breaches": 20,
        "deepest_maxdd": "-0.6002 (U5|f_c2|top1|x2)",
        "null_pool": {"n": 4800, "nan": 0, "mu": 0.1590, "sigma": 0.2161},
        "ledger": "344056->344080 +24 linear, trials_ledger key landed"
    },
    "a11_arm_final_state": "input-feature cross-sectional selection usage CLOSED (0/24): "
        "gate/factor feature differentials among the frozen five carry no "
        "selection information -- f_rsv30/f_roc20 orderings rank BELOW random "
        "(falling-knife / dead intra-class momentum), f_c2 positive-excess "
        "face = high-beta member tilt mirror (d6 0.94-0.97), not skill; "
        "always-invested top-k concentration deepens maxdd (20/24 breach "
        "-35% floor, deepest -60.0%); remaining input-feature route = "
        "predictor/conditional faces (vol/risk conditioning), non-selection "
        "non-timing, future batches need fresh prereg + D6 first",
    "prereg": "research/T-101-V4_A11_XSELECT_PREREG.md",
    "results": "results/t101_v4_a11_xselect.json",
    "burn_disclosure": "burn#1-#3 pre-output engineering wiring failures "
        "(RangeIndex->DatetimeIndex silent all-NaN reindex + OR/AND; string/"
        "datetime key mix empty intersection; numpy scatter broadcast) -- all "
        "crashed BEFORE any JSON write or ledger append, zero partial "
        "products zero double-count; burn#4 final 141.3s, judgment faces "
        "zero-touch (r251/r280 precedent family)",
})
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('attrition entries:', len(d['entries']), 'appended A11 row')
