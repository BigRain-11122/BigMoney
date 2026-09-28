# -*- coding: utf-8 -*-
"""r405 bm-b: MASS_TRIAL_W1_JUDGE gate-attrition row append (wave-1a judge stage closure, W1b r388 precedent).

Appends one measurement row to results/gate_attrition.json entries (append-only):
166 judged -> G1'v2 0 pass -> G2 0 eligible. Ledger total after = 312,042 (live head read from w1_judge.json).
Idempotent: refuses double-append if a MASS_TRIAL_W1_JUDGE row already exists.
"""
import json
import io

PATH = "results/gate_attrition.json"
BATCH = "MASS_TRIAL_W1_JUDGE"

with io.open(PATH, "r", encoding="utf-8") as f:
    d = json.load(f)

if any(e.get("batch") == BATCH for e in d["entries"]):
    print("REFUSE: batch row already present (single-shot guard)")
    raise SystemExit(0)

j = json.load(open("results/mass_trial/w1_judge.json", encoding="utf-8"))
cells = j["cells"]
n_cells = len(cells)
n_g1 = sum(1 for c in cells if c.get("g1_pass"))
n_g2 = sum(1 for c in cells if (c.get("g2_registration_v2") or {}).get("pass"))
ledger = j["trials_ledger"]["total"]
skill_line = cells[0]["g1_prime_v2"]["skill_line"]["line"]
dsr_max = max(c["dsr"]["dsr"] for c in cells if isinstance(c.get("dsr"), dict))

row = {
    "batch": BATCH,
    "ts": "2026-09-29 03:1x",
    "kind": "measurement",
    "cells_ledger_delta": n_cells,
    "ledger_total_after": ledger,
    "gates": {
        "g1_prime_v2": {
            "n_judged": n_cells,
            "n_pass": n_g1,
            "line": "sharpe_full > skill_line_v2=%.4f AND bootstrap CI lower>0 AND entries>=30" % skill_line,
        },
        "g2_registration_v2": {
            "n_eligible": n_g2,
            "line": "G1' pass AND DSR>=0.95 (n_trials=%d cumulative deflation) AND family PBO<=0.25" % ledger,
        },
        "dsr_face": {
            "max_dsr": round(dsr_max, 5),
            "note": "max DSR 0.077 << 0.95 gate; cumulative N~312k deflation dominates",
        },
        "wave_multiplicity": {
            "screen_cells": 975,
            "judged_cells": n_cells,
            "E_FP_nominal_5pct": j["n_wave_disclosure"]["E_FP_nominal_5pct"],
        },
        "family_pbo": {
            "n_sufficient_families": sum(1 for v in j["family_pbo"].values() if v.get("pbo") is not None),
            "note": "families with <8 cells = insufficient -> G2 cannot pass (honest n/a); mean_reversion pbo=0.4143",
        },
    },
    "verdict": "judged-negative 0/%d registrations; prediction sec.9.1 modal-zero hit" % n_cells,
    "prereg": "research/MASS_TRIAL_W1_PREREG.md sec.9.1 FROZEN (commit deb3b1f4, seed 20285000)",
    "results": "results/mass_trial/w1_judge.json",
}

d["entries"].append(row)
with io.open(PATH, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("APPENDED: %s row (delta=%d, ledger_after=%d, g1_pass=%d, g2_eligible=%d, dsr_max=%.5f)"
      % (BATCH, n_cells, ledger, n_g1, n_g2, dsr_max))
