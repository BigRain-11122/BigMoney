import json

p = r'results/gate_attrition.bm-a.json'
d = json.load(open(p, encoding='utf-8'))
assert isinstance(d['entries'], list)
d['entries'].append({
    "batch": "T-101-V4-A12-PREDCOND",
    "ts": "2026-09-29T20:4x+08:00",
    "host": "bm-a",
    "n_cells": 12,
    "verdict": "FV_FAIL_0of12",
    "line_action": "ARM_CONDITIONAL_SLEEVE_CLOSE",
    "legs": {
        "top_sharpe": 0.4316,
        "skill_line": 1.0889,
        "top_dsr": 0.001,
        "family_pbo": {"U5": 0.1714, "U4": 0.4286},
        "best_cell": "U5|c_vtar|x1",
        "c_vtar_oos_excess": "U5 +0.86%/x2 +0.65% ; U4 +0.29%/x2 +0.08% (small positive both universes, x2-stable)",
        "c_volinv_oos_excess": "U5 -2.04%/x2 -2.25% ; U4 -0.74%/x2 -0.92% (negative both = A11 mirror closed)",
        "d6_reject": 12,
        "d6_reject_face": "vs_a11 dominant 0.847-0.933 (c_vtar max pair U4|f_c2|top2 0.8958; vs_bh 0.57-0.83)",
        "maxdd_floor_breaches": 0,
        "descriptive_positive_finding": "exposure conditioning structurally caps maxdd (0/12 breach vs A11 always-invested 20/24, deepest -60%) -- descriptive face only, far below Sharpe line",
        "entries_ok": "all 12 pass (35-98 OOS trade events; sec.5 thin-event risk for c_volinv did not materialize)",
        "null_pool": {"n": 2400, "nan": 0, "mu": 0.2390, "sigma": 0.1683},
        "ledger": "346270->346282 +12 linear, trials_ledger key landed; head file=w10_screen.json (fleet in-flight advanced N_eff +2,190 since A11)"
    },
    "a12_arm_final_state": "vol/risk-conditioned continuous position usage CLOSED (0/12): "
        "input-feature route now five-subline closed (A2/A9/A10 timing + "
        "A11 selection + A12 conditioning); c_volinv negative OOS excess "
        "both universes = A11 high-vol-tilt mirror evidence closed-loop "
        "(same information opposite sign); c_vtar small positive crash-"
        "avoidance tilt far below registration (top cell 40% of line); "
        "exposure conditioning caps drawdown depth descriptively (input "
        "note for future risk-budget lines, not a strategy claim); "
        "remaining input-feature route = pure predictor (forecast, "
        "walk-forward) face only, future batches need fresh prereg + "
        "D6 first",
    "prereg": "research/T-101-V4_A12_PREDCOND_PREREG.md",
    "results": "results/t101_v4_a12_predcond.json",
    "burn_disclosure": "zero-correction burn (single 61.0s run); selftest "
        "legs 3/4/8 stride-20 caliber errors caught and fixed PRE-freeze "
        "(judgment faces zero-touch, r251/r280 precedent family); "
        "dual-nulls base wiring: fv.UNC_BASE rebound to batch key 20316500 "
        "pre-call -- A10/A11 inherited fv module base 20313500 while "
        "declaring their own keys in prereg metadata (seed-arbitrary face, "
        "zero verdict impact, disclosure note in prereg sec.8)",
})
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('attrition entries:', len(d['entries']), 'appended A12 row')
