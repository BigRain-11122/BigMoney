import json

p = r'results\gate_attrition.json'
d = json.load(open(p, encoding='utf-8'))
hist = d['history']

screen_row = {
 "batch": "TRIAL_LAB_W6_SCREEN",
 "ts": "2026-09-29 06:48:25",
 "kind": "measurement",
 "cells_ledger_delta": 4152,
 "ledger_total_after": 333139,
 "gates": {
  "screen_pass": {
   "n_candidates": 3952,
   "n_survivors": 293,
   "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.5196, prereg sec.3 frozen)"
  },
  "null_face": {
   "p50": 0.5036,
   "p95": 0.5196,
   "n": 200,
   "note": "K=200 nine-tuple axis nulls with vconf leg, seed 20304000; screen survival line = program-frozen null p95 (W2-W5 identical law); p50 0.5036 > 0.50 = prereg sec.5 null-bottom prediction first-wave miss, disclosed"
  },
  "vconf_face": {
   "segmented_survival": {
    "volume_surge": {"n_cells": 1356, "n_survivors": 119, "survival_rate": 0.087758},
    "none": {"n_cells": 1320, "n_survivors": 96, "survival_rate": 0.072727},
    "volume_dry": {"n_cells": 1276, "n_survivors": 78, "survival_rate": 0.061129}
   },
   "top_interaction_cell": {"key": "bear|wild|none|volume_surge", "n_cells": 68, "n_survivors": 30, "survival_rate": 0.441176},
   "note": "VCONF new face direction intel: surge > none > dry (folk-saying liang-zeng-jia-zhang ordering holds at screen caliber); judge face all-zero G1 in all segments"
  }
 },
 "eliminated": 3659,
 "refs": {"prereg": "research/TRIAL_LABOR_W6_PREREG.md", "ticket": "T-2026-09-29-117"}
}

judge_row = {
 "batch": "TRIAL_LAB_W6_JUDGE",
 "ts": "2026-09-29 08:14:22",
 "kind": "judgment",
 "cells_ledger_delta": 293,
 "ledger_total_after": 333432,
 "gates": {
  "g1_prime_v2": {
   "n": 293,
   "n_pass": 0,
   "line": "skill_line_v2 per-cell (ledger_head live read); top cell W6-B-1894 sharpe_full=1.0213 vs line=1.1924 (n_eff=337291) -- line_ok false",
   "all_face_total_zero": True,
   "faces": {"gate": {"none": 0, "bear": 0, "bull": 0}, "vol": {"wild": 0, "none": 0, "calm": 0}, "yang": {"none": 0, "first_yang": 0}, "vconf": {"none": 0, "volume_dry": 0, "volume_surge": 0}}
  },
  "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.091456, "n_trials": 333139, "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
  "e_fp_nominal_5pct": 14.65,
  "family_pbo": {"patterns": 0.7429, "ta": 0.4571, "composite_rotation": 0.5, "volatility": 0.4714, "folk": 0.5286, "momentum": 0.1857, "trend": "insufficient (<8)", "mean_reversion": 0.6714}
 },
 "eliminated": 293,
 "refs": {"prereg": "research/TRIAL_LABOR_W6_PREREG.md", "results": "results/trial_labor_w6/w6_judge.json", "intake": "results/trial_labor_w6/w6_intake.json (zero-face n_eligible=0)", "ticket": "T-2026-09-29-117"}
}

assert not any(r.get('batch') in ('TRIAL_LAB_W6_SCREEN', 'TRIAL_LAB_W6_JUDGE') for r in hist), 'W6 rows already present'
hist.append(screen_row)
hist.append(judge_row)
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('appended. history rows:', len(hist))
print('verify tail batches:', [r['batch'] for r in hist[-3:]])
