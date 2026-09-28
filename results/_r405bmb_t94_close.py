# -*- coding: utf-8 -*-
"""r405 bm-b: T-94 ticket closure (MASS W1 wave-1a judge harvest + dual-wave first-mass-trial close).

Sets status=done + result_ref + done_at + progress_r405. Append-only on progress fields.
"""
import json
import io

PATH = "fleet/tasks/T-2026-09-27-94-P1.json"
with io.open(PATH, "r", encoding="utf-8") as f:
    t = json.load(f)

if t.get("status") == "done":
    print("REFUSE: ticket already done (single-shot guard)")
    raise SystemExit(0)

t["progress_r405"] = (
    "r405 bm-b (T-94 owner, wave close per pool MASS-W1-JUDGE done_note 'r386 receipt precedent'): "
    "(1) w1_judge.json receipt harvest VERIFIED -- 166/166 judged cells (evidence_cutoff 2026-09-22), "
    "G1'v2 pass 0/166 (best sharpe_full 0.19 vs skill_line_v2 1.19), G2 eligible 0/166 (max DSR 0.077 << 0.95 "
    "under cumulative n_trials=312,042 deflation), E[FP] nominal 8.3 disclosed, family PBO honest faces "
    "(<8-cell families insufficient n/a), ledger 311,876+166=312,042 linear append verified; "
    "(2) sec.9.1 pre-registered prediction reconciliation ALL FOUR IN-RANGE: collapse 0 in [0,15]; G1' 0 in [0,20] "
    "('most screen survivors should die' honored); G2 0 in [0,3] modal-zero HIT; family-enrichment direction HIT "
    "(reversal/pattern/folk/seasonal 68 cells vs trend/momentum 10 cells); "
    "(3) zero G2-eligible -> lawful-zero closure face: NO STRATEGY_LIBRARY registrations, NO TRIAL-* paper accounts "
    "(prereg sec.10 terminal-survivor path vacuous; 'zero survivors = lawful outcome, report as-is, no verdict-flip' "
    "sec.9.1 pred.3 verbatim); "
    "(4) gate_attrition.json MASS_TRIAL_W1_JUDGE measurement row appended (delta 166, ledger_after 312042); "
    "(5) O-2245 48h CEO clock discharged IN-WINDOW: docs/trial_labor/CEO-REPORT-WAVE1-20260929.md one-pager "
    "(dual-wave funnel 1,833 generated -> 315 judged -> 0 registered; deadline 2026-09-29 22:45, landed 03:1x); "
    "(6) MSG receipt to ALL fleet/inbox/MSG-20260929-0315-bmb-all-mass-w1-wave-close.json; "
    "(7) sibling wave-1b (TRIAL_LABOR_W1) closed r388 same lawful-zero face -- T-94 umbrella fully closed; "
    "supply line continues per TRIAL_LABOR_LAW sec.1 standing law (W5-JUDGE burning bm-b, W6 prereg draft bm-a r410)."
)
t["result_ref"] = (
    "results/mass_trial/w1_judge.json (166 judged, G2 0, ledger 312,042) + results/mass_trial/w1_screen_summary.json "
    "(975->166) + results/gate_attrition.json MASS_TRIAL_W1 + MASS_TRIAL_W1_JUDGE rows + "
    "docs/trial_labor/CEO-REPORT-WAVE1-20260929.md (O-2245 48h CEO report, in-window) + "
    "results/trial_labor_w1/w1_judge.json + w1_intake.json (sibling wave-1b lawful-zero r388) -- "
    "dual-wave first mass trial: 1,833 candidates -> 315 judged -> 0 registrations lawful-zero"
)
t["status"] = "done"
t["done_at"] = "2026-09-29 03:1x"

with io.open(PATH, "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("T-94 CLOSED: status=done, result_ref set, progress_r405 appended")
