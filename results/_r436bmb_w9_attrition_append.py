"""r436 bm-b W9 wave closeout: attrition two rows (SCREEN+JUDGE) + pool entry ready->done flip.

Mirrors results/_r430bmb_w8_attrition_append.py (W8 precedent) with W9 live-read numbers.
Zero-retro: screen row ts = w9_screen.json generated (17:10:14 r434 finalize),
judge row ts = w9_judge.json generated (17:47:46 judge-finalize landing).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

screen_row = {
 "batch": "TRIAL_LAB_W9_SCREEN",
 "ts": "2026-09-29 17:10:14",
 "kind": "measurement",
 "retro_fill": False,
 "cells_ledger_delta": 2715,
 "ledger_total_after": 343788,
 "gates": {
  "screen_pass": {
   "n_candidates": 2515,
   "n_survivors": 243,
   "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.517200, prereg sec.3 frozen)"
  },
  "null_face": {
   "p50": 0.5116,
   "p95": 0.5172,
   "n": 200,
   "note": "K=200 twelve-tuple axis nulls with amp leg, seed 20310000; p50 0.5116 within prereg sec.5 recalibrated band [0.50,0.52] (fourth consecutive wave >0.50: W6 0.5036 -> W7 0.51 -> W8 0.5116 -> W9 0.5116, drift disclosed); p95 0.5172 within nine-wave band 0.5116-0.5196; screen survival line = program-frozen null p95 (W2-W8 identical law)"
  },
  "amp_face": {
   "segmented_survival": {
    "amp_narrow": {"n_cells": 823, "n_survivors": 59, "survival_rate": 0.071689},
    "amp_wide": {"n_cells": 739, "n_survivors": 79, "survival_rate": 0.106901},
    "none": {"n_cells": 953, "n_survivors": 105, "survival_rate": 0.110178}
   },
   "note": "AMP new face direction intel (W9 true question): ANTI-enrichment ordering narrow 7.17% < wide 10.69% < none 11.02% -- the CEO-named lowamp20 LONG-direction in-repo anchor (intraday_range three-window negative IC) did NOT manifest as screen enrichment; both amp directions survive WORSE than no amp gate (narrow 0.65x vs none); top n>=3 seven-gate interaction cells max 3/3 (small-n, no W8-caliber 5/6 cell); judge face amp three segments all zero G1 (anti-enrichment != registration-grade, and direction intel: amp gates at this caliber subtract, do not add)"
  }
 },
 "eliminated": 2272,
 "refs": {"prereg": "research/TRIAL_LABOR_W9_PREREG.md", "results": "results/trial_labor_w9/w9_screen.json", "ticket": "T-2026-09-29-121"}
}

judge_row = {
 "batch": "TRIAL_LAB_W9_JUDGE",
 "ts": "2026-09-29 17:47:46",
 "kind": "judgment",
 "retro_fill": False,
 "cells_ledger_delta": 243,
 "ledger_total_after": 344031,
 "gates": {
  "g1_prime_v2": {
   "n": 243,
   "n_pass": 0,
   "line": "skill_line_v2 per-cell (ledger_head live read); top cell W9-B-4123 legL sharpe_full=0.9912 vs line=1.1937 (n_eff=346503) -- line_ok false; seven-face total zero (gate/vol/yang/vconf/streak/tstate/amp); 28 cells bootstrap ci_lower_positive but all below skill line",
   "all_face_total_zero": True,
   "faces": {"gate": {"none": 0, "bear": 0, "bull": 0}, "vol": {"wild": 0, "none": 0, "calm": 0}, "yang": {"none": 0, "first_yang": 0}, "vconf": {"none": 0, "volume_dry": 0, "volume_surge": 0}, "streak": {"none": 0, "up_streak2": 0, "down_streak2": 0}, "tstate": {"none": 0, "deep_pullback": 0, "oversold_rsv": 0}, "amp": {"none": 0, "amp_narrow": 0, "amp_wide": 0}}
  },
  "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.802319, "top_dsr_cell": "W9-A-0041", "n_trials": 343788, "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
  "e_fp_nominal_5pct": 12.15,
  "family_pbo": {"patterns": {"pbo": 0.3429, "n_cells": 58}, "ta": {"pbo": 0.6429, "n_cells": 53}, "composite_rotation": {"pbo": None, "n_cells": 6, "note": "insufficient (<8) -- G2 cannot pass"}, "volatility": {"pbo": 0.2857, "n_cells": 13}, "momentum": {"pbo": 0.9571, "n_cells": 20}, "sentiment": {"pbo": 0.7429, "n_cells": 13}, "trend": {"pbo": 0.7143, "n_cells": 18}, "mean_reversion": {"pbo": 0.3857, "n_cells": 26}, "event": {"pbo": 0.8286, "n_cells": 12}, "folk": {"pbo": 0.5714, "n_cells": 15}, "seasonal": {"pbo": None, "n_cells": 4, "note": "insufficient (<8) -- G2 cannot pass"}, "macro": {"pbo": None, "n_cells": 5, "note": "insufficient (<8) -- G2 cannot pass"}}
 },
 "eliminated": 243,
 "refs": {"prereg": "research/TRIAL_LABOR_W9_PREREG.md", "results": "results/trial_labor_w9/w9_judge.json", "intake": "results/trial_labor_w9/w9_intake.json (lawful-zero n_eligible=0, r436)", "ticket": "T-2026-09-29-121"}
}

for fname in ("gate_attrition.json", "gate_attrition.bm-b.json"):
    p = os.path.join(ROOT, "results", fname)
    d = json.load(open(p, encoding="utf-8"))
    hist = d["history"]
    assert not any(r.get("batch") in ("TRIAL_LAB_W9_SCREEN", "TRIAL_LAB_W9_JUDGE") for r in hist), fname + ": W9 rows already present"
    hist.append(screen_row)
    hist.append(judge_row)
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    back = json.load(open(p, encoding="utf-8"))
    print(fname, ": appended -> history", len(back["history"]), "| tail:", [r["batch"] for r in back["history"][-3:]])

# pool entry flip: TRIAL-LABOR-W9-JUDGE ready -> done (W8 entry convention)
pp = os.path.join(ROOT, "results", "runnable_pool.json")
d = json.load(open(pp, encoding="utf-8"))
e = [x for x in d["entries"] if x["id"] == "TRIAL-LABOR-W9-JUDGE"][0]
assert e["status"] == "ready", "unexpected pool status: " + e["status"]
e["status"] = "done"
e["done_at"] = "2026-09-29 17:47:46"
e["result_ref"] = "results/trial_labor_w9/w9_judge.json"
e["done_note"] = ("judge-finalize landed 2026-09-29 17:47:46 exit 0 (detached burn pid20568 submitted bm-b r435, autofill lineage; 243/243 judged cells, zero G1 pass, zero G2 eligible, E[FP]=12.15, 28 cells ci-lower-positive all below skill line 1.1937); intake s4 lawful-zero w9_intake.json r436 (zero TRIAL-* accounts, zero STRATEGY_LIBRARY rows); attrition W9 two rows r436; prereg sec.7/sec.8 backfilled r436; 48h CEO report docs/trial_labor/CEO-REPORT-WAVE9-20260929.md same round r436; wave ticket T-121 done r436; AMP anti-enrichment research fact = W10 supply-line input")
d["updated_at"] = "2026-09-29T18:05:00+08:00"
tmp = pp + ".tmp"
json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.replace(tmp, pp)
back = json.load(open(pp, encoding="utf-8"))
st = [x["status"] for x in back["entries"] if x["id"] == "TRIAL-LABOR-W9-JUDGE"][0]
print("runnable_pool: TRIAL-LABOR-W9-JUDGE ->", st, "| entries done:", sum(1 for x in back["entries"] if x["status"] == "done"), "/", len(back["entries"]))
