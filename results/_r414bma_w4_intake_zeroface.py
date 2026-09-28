"""r414 bm-a: TRIAL_LABOR_W4 intake zero-face product (prereg sec.6 s4 actual-count clause).

W4 judge landed 2026-09-28 20:03 (bm-b r396 harvest: 461 judged, E[FP]=23.05
nominal 5%, G2 eligible 0) but the intake face product never landed -- the W4
runner was built half-by-design (intake subcommand gated on judge products,
never registered). Zero G2-eligible survivors makes the registration path dead
code, so the lawful closure is the zero-face product mirroring the r407 W5
precedent (w5_intake.json schema, one-off generator, no runner overbuild).

Fail-closed: refuses to write anything if w4_judge.json is missing, unreadable,
or carries ANY non-empty eligible_g2 list (that path belongs to the real D6
binding machinery, W2 runner cmd_intake precedent).
"""
from __future__ import annotations

import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUDGE_PATH = os.path.join(ROOT, "results", "trial_labor_w4", "w4_judge.json")
OUT_PATH = os.path.join(ROOT, "results", "trial_labor_w4", "w4_intake.json")


def main() -> int:
    if not os.path.exists(JUDGE_PATH):
        print("REFUSE: w4_judge.json not found -- judge face must land first")
        return 2
    if os.path.exists(OUT_PATH):
        print("NO-OP: w4_intake.json already exists (single-shot guard)")
        return 0
    with open(JUDGE_PATH, encoding="utf-8") as f:
        judge = json.load(f)
    eligible = judge.get("eligible_g2")
    if eligible:
        print(f"REFUSE: {len(eligible)} G2-eligible survivors -- real D6 binding "
              f"path required (W2 runner cmd_intake precedent), zero-face refuses")
        return 2
    vol_face = judge.get("vol_face_judgment", {})
    parts = ", ".join(
        f"{k} {v.get('n_g1_pass')}/{v.get('n_cells')}"
        for k, v in sorted(vol_face.items())
    )
    n_judged = judge.get("n_judged_cells")
    disclosure = judge.get("n_wave_disclosure", {})
    e_fp = disclosure.get("E_FP_nominal_5pct")
    product = {
        "wave": "TRIAL_LABOR_W4",
        "stage": "intake",
        "prereg": "research/TRIAL_LABOR_W4_PREREG.md",
        "evidence_cutoff": judge.get("evidence_cutoff"),
        "grammar_sha256": judge.get("grammar_sha256"),
        "n_eligible": 0,
        "admitted": [],
        "rejected": [],
        "d6_binding": {},
        "intake": [],
        "note": (
            "zero G2-eligible survivors = lawful outcome, reported as-is "
            "(prereg sec.6 s4 actual-count clause; vol-face G1 passes "
            f"{parts} -> zero G1 passes wave-wide, no cell reached G2)"
        ),
        "audit": {
            "n_engine_runs": 0,
            "ledger_trials_added": 0,
            "note": (
                "intake = judgment face, zero ledger rows; zero eligible -> D6 "
                "binding / STRATEGY_LIBRARY registration / TRIAL-* paper-desk "
                "onboarding / smoke anchor re-run all zero-surface per prereg "
                "sec.6 s4 (dead path this wave); runner cmd_intake subcommand "
                "not built this wave -- zero survivors made the registration "
                "path dead code; W2 runner cmd_intake (scripts/trial_labor_w2.py) "
                "is the reusable precedent for any wave with survivors; 48h CEO "
                "report clock discharged by merged report "
                "docs/trial_labor/CEO-REPORT-WAVE2-5-20260929.md (bm-b r408, "
                "34.5h ahead of earliest deadline)"
            ),
            "judge_receipt": (
                f"results/trial_labor_w4/w4_judge.json ({n_judged} judged, "
                f"E[FP]={e_fp} nominal 5%, n_eligible_g2=0)"
            ),
        },
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(product, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT_PATH)
    # self-verify: reload and check the load-bearing fields
    with open(OUT_PATH, encoding="utf-8") as f:
        back = json.load(f)
    assert back["n_eligible"] == 0 and back["admitted"] == [] and back["d6_binding"] == {}
    assert back["evidence_cutoff"] == judge.get("evidence_cutoff")
    print(f"OK: w4_intake.json zero-face landed ({n_judged} judged, "
          f"E[FP]={e_fp}, n_eligible=0 lawful-zero, cutoff {back['evidence_cutoff']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
