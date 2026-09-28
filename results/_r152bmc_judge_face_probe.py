# r152 bm-c probe: _tl_judge_face helper + wave-block wiring verification for
# build_status trial_labor judge/intake display faces (J12-line, my r146/r151
# lineage). Hermetic on the helper (tempdir fixtures, zero writes to real
# results/); read-only on the real-dir derive (judge products not landed =
# honest-null assertion; W1 judge_state wiring check).
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor import build_status as bs  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
    if not cond:
        fails.append(name)


# --- unit: helper on temp fixtures (never touches real results/) ---
tmp = tempfile.mkdtemp(prefix="tljf_")
try:
    # u1: empty dir -> None (zero judgment claims pre-landing)
    check("u1 empty-dir -> None", bs._tl_judge_face(tmp, "w3_judge.json") is None)
    # u2: tl-lineage judged product (n_judged_cells) + intake
    with open(os.path.join(tmp, "w3_judge.json"), "w", encoding="utf-8") as f:
        json.dump({"wave": "TRIAL_LABOR_W3", "n_judged_cells": 513,
                   "n_eligible_g2": 7,
                   "n_wave_disclosure": {"E_FP_nominal_5pct": 25.65}}, f)
    check("u2 judge absent intake -> judge-only",
          bs._tl_judge_face(tmp, "w3_judge.json") ==
          {"n_judged": 513, "n_eligible_g2": 7, "e_fp": 25.65})
    with open(os.path.join(tmp, "w3_intake.json"), "w", encoding="utf-8") as f:
        json.dump({"wave": "TRIAL_LABOR_W3", "n_eligible": 7,
                   "intake": ["TRIAL-W3-001", "TRIAL-W3-002"]}, f)
    face = bs._tl_judge_face(tmp, "w3_judge.json", "w3_intake.json")
    check("u3 judge+intake -> full face",
          face == {"n_judged": 513, "n_eligible_g2": 7, "e_fp": 25.65,
                   "intake_n_eligible": 7, "intake_n": 2}, str(face))
    # u4: mass-lineage key n_judge_cells + verdicts carried
    tmp2 = tempfile.mkdtemp(prefix="tljf2_")
    with open(os.path.join(tmp2, "w1_judge.json"), "w", encoding="utf-8") as f:
        json.dump({"batch": "MASS-TRIAL-W1-JUDGE", "n_judge_cells": 149,
                   "n_eligible_g2": 0,
                   "n_wave_disclosure": {"E_FP_nominal_5pct": 7.45},
                   "verdicts": {"pass": 0, "fail": 140,
                                "insufficient-sample": 9}}, f)
    face2 = bs._tl_judge_face(tmp2, "w1_judge.json")
    check("u4 mass n_judge_cells + verdicts",
          face2 == {"n_judged": 149, "n_eligible_g2": 0, "e_fp": 7.45,
                    "verdicts": {"pass": 0, "fail": 140,
                                 "insufficient-sample": 9}}, str(face2))
    shutil.rmtree(tmp2, ignore_errors=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --- real-dir readback: judge products NOT landed -> judge key absent ---
st = bs._trial_labor_state()
waves = {w.get("wave"): w for w in st.get("waves", [])}
check("real: 4 wave rows", len(st.get("waves", [])) == 4,
      "/".join(sorted(waves)))
for wn in ("MASS_TRIAL_W1", "TRIAL_LABOR_W1", "TRIAL_LABOR_W2",
           "TRIAL_LABOR_W3"):
    check(f"real {wn}: judge face absent (product not landed)",
          "judge" not in waves.get(wn, {}))
# W3 screen row unchanged by this edit (r151 face intact)
w3 = waves.get("TRIAL_LABOR_W3", {})
check("real W3 row intact (513/3752 p95 0.511572 ledger 301180)",
      w3.get("candidates") == 3752 and w3.get("survivors_stage1") == 513
      and abs((w3.get("null_p95") or 0) - 0.511572) < 1e-9
      and w3.get("ledger_total") == 301180, str(w3.get("candidates")))
# W1 judge_state.json = older prep schema with NO count key (judge cells ==
# survivors_stage1, already displayed) -- judge_prep must stay None, not a
# misleading empty-count row
w1 = waves.get("TRIAL_LABOR_W1", {})
check("real W1 judge_prep stays None (old prep schema, no count key)",
      w1.get("judge_prep") is None, str(w1.get("judge_prep")))
# pool face intact
pe = {e.get("id"): e.get("status") for e in st.get("pool_entries", [])}
check("real pool face: TRIAL-LABOR-W3-JUDGE waiting",
      pe.get("TRIAL-LABOR-W3-JUDGE") == "waiting", str(pe))

print(f"probe summary: {len(fails)} FAIL")
sys.exit(1 if fails else 0)
