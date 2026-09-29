import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

screen_row = {
 "batch": "TRIAL_LAB_W8_SCREEN",
 "ts": "2026-09-29 14:39:00",
 "kind": "measurement",
 "retro_fill": False,
 "cells_ledger_delta": 3034,
 "ledger_total_after": 340654,
 "gates": {
  "screen_pass": {
   "n_candidates": 2834,
   "n_survivors": 408,
   "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.5156, prereg sec.3 frozen)"
  },
  "null_face": {
   "p50": 0.5116,
   "p95": 0.5156,
   "n": 200,
   "note": "K=200 eleven-tuple axis nulls with tstate leg, seed 20307000; p50 0.5116 within prereg sec.5 recalibrated band [0.50,0.52] (third consecutive wave >0.50: W6 0.5036 -> W7 0.51 -> W8 0.5116, drift disclosed); p95 0.5156 within eight-wave band 0.5116-0.5196; screen survival line = program-frozen null p95 (W2-W7 identical law)"
  },
  "tstate_face": {
   "segmented_survival": {
    "none": {"n_cells": 1304, "n_survivors": 145, "survival_rate": 0.111196},
    "deep_pullback": {"n_cells": 684, "n_survivors": 137, "survival_rate": 0.200292},
    "oversold_rsv": {"n_cells": 846, "n_survivors": 126, "survival_rate": 0.148936}
   },
   "top_interaction_cell": {"key": "none|wild|none|volume_surge|none|oversold_rsv", "n_cells": 6, "n_survivors": 5, "survival_rate": 0.8333},
   "note": "TSTATE new face direction intel (W8 true question): deep_pullback (MAD60_q10) 20.03% = 1.80x vs none 11.12%, oversold_rsv (RSV60<0.2) 14.89% = 1.34x vs none -- folk die-deep-buy-the-dip ordering holds at screen caliber; same-direction with census 20d-forward priors (MAD60_q10 median t=+2.255 / RSV60_low t=+2.201) and W7 down_streak2 enrichment (streak confirm -> depth confirm deepening); top n>=5 interaction cells carry a tstate leg in 5 of top 6; judge face all-zero G1 in all tstate segments (enrichment != registration-grade edge); census 20d window vs engine 6m window horizon mismatch disclosed (weak anchor, honest)"
  }
 },
 "eliminated": 2426,
 "refs": {"prereg": "research/TRIAL_LABOR_W8_PREREG.md", "results": "results/trial_labor_w8/w8_screen.json", "ticket": "T-2026-09-29-120"}
}

judge_row = {
 "batch": "TRIAL_LAB_W8_JUDGE",
 "ts": "2026-09-29 15:26:25",
 "kind": "judgment",
 "retro_fill": False,
 "cells_ledger_delta": 408,
 "ledger_total_after": 341063,
 "gates": {
  "g1_prime_v2": {
   "n": 408,
   "n_pass": 0,
   "line": "skill_line_v2 per-cell (ledger_head live read); top cell W8-B-2704 three_soldiers sharpe_full=0.9533 vs line=1.1933 (n_eff=343688) -- line_ok false; six-face total zero (gate/vol/yang/vconf/streak/tstate)",
   "all_face_total_zero": True,
   "faces": {"gate": {"none": 0, "bear": 0, "bull": 0}, "vol": {"wild": 0, "none": 0, "calm": 0}, "yang": {"none": 0, "first_yang": 0}, "vconf": {"none": 0, "volume_dry": 0, "volume_surge": 0}, "streak": {"none": 0, "up_streak2": 0, "down_streak2": 0}, "tstate": {"none": 0, "deep_pullback": 0, "oversold_rsv": 0}}
  },
  "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.685786, "n_trials": 340655, "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
  "e_fp_nominal_5pct": 20.4,
  "family_pbo": {"ta": 0.7571, "composite_rotation": 0.5571, "patterns": 0.7143, "volatility": 0.5571, "sentiment": 0.6286, "trend": 0.9286, "momentum": 0.8571, "event": 0.4143, "folk": 0.6429, "seasonal": 0.7143, "mean_reversion": 0.3857, "macro": 0.3714}
 },
 "eliminated": 408,
 "refs": {"prereg": "research/TRIAL_LABOR_W8_PREREG.md", "results": "results/trial_labor_w8/w8_judge.json", "intake": "results/trial_labor_w8/w8_intake.json (zero-face n_eligible=0)", "ticket": "T-2026-09-29-120"}
}

for fname in ("gate_attrition.json", "gate_attrition.bm-b.json"):
    p = os.path.join(ROOT, "results", fname)
    d = json.load(open(p, encoding="utf-8"))
    hist = d["history"]
    assert not any(r.get("batch") in ("TRIAL_LAB_W8_SCREEN", "TRIAL_LAB_W8_JUDGE") for r in hist), fname + ": W8 rows already present"
    hist.append(screen_row)
    hist.append(judge_row)
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    back = json.load(open(p, encoding="utf-8"))
    print(fname, ": appended -> history", len(back["history"]), "| tail:", [r["batch"] for r in back["history"][-3:]])
