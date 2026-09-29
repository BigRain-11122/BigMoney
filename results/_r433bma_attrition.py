import json

p = "results/gate_attrition.json"
d = json.load(open(p, encoding="utf-8"))
entries = d["entries"] if isinstance(d, dict) and "entries" in d else None
if entries is None:
    raise SystemExit("FACE ERROR: entries list not found (r248 law)")
entries.append({
    "batch": "T-101-V4-A2-PRESCREEN",
    "ts": "2026-09-29T15:2x+08:00",
    "host": "bm-a",
    "n_cells": 10,
    "survive": 1,
    "kill": 9,
    "kill_reasons": {"oos_excess<=0": 9, "maxdd<-35%": 5, "sharpe<=null_med": 6},
    "d6": {"max_abs_corr": 0.9424, "verdict": "REJECT_corr>=0.7_beta_same_source"},
    "evidence_cutoff": "2026-09-28",
    "prereg": "research/T-101-V4_PREREG.md",
    "note": "same-gate usage-flip falsified: gate_verify 20d-forward PASS != continuous regime-timing (9/10 kill); lone survivor 510050|RSV30 deferred behind D6 correlation-source prereg",
})
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("gate_attrition appended, total entries:", len(entries))
