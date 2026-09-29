"""r440 bm-b W10 wave closeout: attrition two rows (SCREEN+JUDGE) + pool entry ready->done flip.

Mirrors results/_r436bmb_w9_attrition_append.py (W9 precedent) with W10 live-read numbers.
Zero-retro: screen row ts = w10_screen.json generated (19:54:28 r439 finalize),
judge row ts = w10_judge.json generated (20:31:29 judge-finalize landing).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

screen_row = {
 "batch": "TRIAL_LAB_W10_SCREEN",
 "ts": "2026-09-29 19:54:28",
 "kind": "measurement",
 "retro_fill": False,
 "cells_ledger_delta": 2214,
 "ledger_total_after": 346270,
 "gates": {
  "screen_pass": {
   "n_candidates": 2014,
   "n_survivors": 283,
   "line": "beat6m_rate > null_p95 strictly-greater (null_p95=0.516361, prereg sec.3 frozen)"
  },
  "null_face": {
   "p50": 0.5116,
   "p95": 0.5164,
   "n": 200,
   "note": "K=200 thirteen-tuple axis nulls with mom leg, seed 20311500; p50 0.5116 within prereg sec.5.2 recalibrated band [0.50,0.52] (fifth consecutive wave >0.50: W6 0.5036 -> W7 0.51 -> W8 0.5116 -> W9 0.5116 -> W10 0.5116, drift disclosed); p95 0.5164 within ten-wave band 0.5116-0.5196; screen survival line = program-frozen null p95 (W2-W9 identical law)"
  },
  "mom_face": {
   "segmented_survival": {
    "none": {"n_cells": 1278, "n_survivors": 136, "survival_rate": 0.106416},
    "mom_oversold": {"n_cells": 736, "n_survivors": 147, "survival_rate": 0.199728}
   },
   "note": "MOM new face direction intel (W10 true question, adopted from bm-c r228 package): POSITIVE-axis enrichment 1.88x (mom_oversold 19.97% vs none 10.64%) -- first gate face since W8 TSTATE deep_pullback 1.80x to enrich at screen, opposite of W9 AMP anti-enrichment; but judge face mom two segments both zero G1 (screen enrichment != registration-grade; W8 tstate precedent: enrichment face, zero registration)"
  }
 },
 "eliminated": 1731,
 "refs": {"prereg": "research/TRIAL_LABOR_W10_PREREG.md", "results": "results/trial_labor_w10/w10_screen.json", "ticket": "T-2026-09-29-122"}
}

judge_row = {
 "batch": "TRIAL_LAB_W10_JUDGE",
 "ts": "2026-09-29 20:31:29",
 "kind": "judgment",
 "retro_fill": False,
 "cells_ledger_delta": 283,
 "ledger_total_after": 346553,
 "gates": {
  "g1_prime_v2": {
   "n": 283,
   "n_pass": 0,
   "line": "skill_line_v2 per-cell (ledger_head live read); top cell W10-B-0125 cci_revert legL sharpe_full=0.9905 vs line=1.194 (n_eff=348484) -- line_ok false; eight-face total zero (gate/vol/yang/vconf/streak/tstate/amp/mom); 22 cells bootstrap ci_lower_positive but all below skill line",
   "all_face_total_zero": True,
   "faces": {"gate": {"none": 0, "bear": 0, "bull": 0}, "vol": {"wild": 0, "none": 0, "calm": 0}, "yang": {"none": 0, "first_yang": 0}, "vconf": {"none": 0, "volume_dry": 0, "volume_surge": 0}, "streak": {"none": 0, "up_streak2": 0, "down_streak2": 0}, "tstate": {"none": 0, "deep_pullback": 0, "oversold_rsv": 0}, "amp": {"none": 0, "amp_narrow": 0, "amp_wide": 0}, "mom": {"none": 0, "mom_oversold": 0}}
  },
  "g2_registration_v2": {"n_eligible": 0, "top_dsr": 0.565398, "top_dsr_cell": "JUDGE|W10-B-2010", "n_trials": 346270, "line": "G1 pass AND DSR>=0.95 AND PBO<=0.25"},
  "e_fp_nominal_5pct": 14.15,
  "family_pbo": {"ta": {"pbo": 0.2143, "n_cells": 56}, "folk": {"pbo": 0.2571, "n_cells": 23}, "composite_rotation": {"pbo": 0.4714, "n_cells": 12}, "momentum": {"pbo": 0.4714, "n_cells": 20}, "volatility": {"pbo": 0.5, "n_cells": 12}, "macro": {"pbo": 0.5, "n_cells": 16}, "trend": {"pbo": 0.5429, "n_cells": 19}, "sentiment": {"pbo": 0.6571, "n_cells": 27}, "patterns": {"pbo": 0.7857, "n_cells": 56}, "mean_reversion": {"pbo": 0.7857, "n_cells": 30}, "event": {"pbo": None, "n_cells": 7, "note": "insufficient (<8) -- G2 cannot pass"}, "seasonal": {"pbo": None, "n_cells": 5, "note": "insufficient (<8) -- G2 cannot pass"}}
 },
 "eliminated": 283,
 "refs": {"prereg": "research/TRIAL_LABOR_W10_PREREG.md", "results": "results/trial_labor_w10/w10_judge.json", "intake": "results/trial_labor_w10/w10_intake.json (lawful-zero n_eligible=0, r440)", "ticket": "T-2026-09-29-122"}
}

for fname in ("gate_attrition.json", "gate_attrition.bm-b.json"):
    p = os.path.join(ROOT, "results", fname)
    d = json.load(open(p, encoding="utf-8"))
    hist = d["history"]
    assert not any(r.get("batch") in ("TRIAL_LAB_W10_SCREEN", "TRIAL_LAB_W10_JUDGE") for r in hist), fname + ": W10 rows already present"
    hist.append(screen_row)
    hist.append(judge_row)
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)
    back = json.load(open(p, encoding="utf-8"))
    print(fname, ": appended -> history", len(back["history"]), "| tail:", [r["batch"] for r in back["history"][-3:]])

# pool entry flip: TRIAL-LABOR-W10-JUDGE ready -> done (W9 entry convention)
pp = os.path.join(ROOT, "results", "runnable_pool.json")
d = json.load(open(pp, encoding="utf-8"))
e = [x for x in d["entries"] if x["id"] == "TRIAL-LABOR-W10-JUDGE"][0]
assert e["status"] == "ready", "unexpected pool status: " + e["status"]
e["status"] = "done"
e["done_at"] = "2026-09-29 20:31:29"
e["result_ref"] = "results/trial_labor_w10/w10_judge.json"
e["done_note"] = ("judge-finalize landed 2026-09-29 20:31:29 exit 0 (autofill lineage; 283/283 judged cells, zero G1 pass, zero G2 eligible, E[FP]=14.15, 22 cells ci-lower-positive all below skill line 1.194); intake s4 lawful-zero w10_intake.json r440 (zero TRIAL-* accounts, zero STRATEGY_LIBRARY rows); attrition W10 two rows r440; prereg sec.7/sec.8 backfilled r440; 48h CEO report docs/trial_labor/CEO-REPORT-WAVE10-20260929.md same round r440; wave ticket T-122 done r440; MOM 1.88x screen enrichment + judge zero-G1 = W11 supply-line input (enrichment-face-not-registration precedent W8 tstate)")
d["updated_at"] = "2026-09-29T20:45:00+08:00"
tmp = pp + ".tmp"
json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.replace(tmp, pp)
back = json.load(open(pp, encoding="utf-8"))
st = [x["status"] for x in back["entries"] if x["id"] == "TRIAL-LABOR-W10-JUDGE"][0]
print("runnable_pool: TRIAL-LABOR-W10-JUDGE ->", st, "| entries done:", sum(1 for x in back["entries"] if x["status"] == "done"), "/", len(back["entries"]))
