# -*- coding: utf-8 -*-
"""R307 bm-a: T-73 ticket closure (all deliverable faces landed, verdict consolidation R264).

Facts verified this round before flip (zero-result-driven edits, pure status/bookkeeping):
- s1 16-school survey: research/digests/DIGEST-20260926-t73-cn-schools-s1.md (16 rows, five-column five-family)
- s2 A-share behavioral laws: slices A-E digests + in-repo empirical faces (policy_cycle/retail_herding/factor-history/style-rot)
- s3 five CN models ALL judged NEGATIVE:
  * matrix 19 cells NEG (4 families: REV-TILT / DIV-LOWVOL-ROT / REGIME-POLICY / CORE-SATELLITE+DDCTL)
    = research/CN_COMBO_VERDICTS.md + results/_r264bma_cn_verdict_matrix.json (R264 closing face)
  * CN-GRID-SLEEVE converged to T-78 per spec anti-dup law: results/grid_sleeve_p1.json
    survivors_science=[] paper_candidates=[] (0/5 survivors, 0 promotion candidates)
- s4 month-boundary combo-pool entry = ZERO INTAKE by construction (0 survivors); first
  month-boundary cross-check 2026-10-01 handed to monthly-round face (pointer in note).
- Honest boundary: zero CN-* paper accounts opened (judged-negative => no promotion => no paper family).
"""
import json, io, sys, datetime

P = r"fleet\tasks\T-2026-09-26-73-P1.json"
d = json.load(open(P, encoding="utf-8"))
assert d["id"] == "T-2026-09-26-73", d["id"]
assert d["status"] == "claimed", d["status"]
assert "bm-a" in (d.get("claimed_by") or ""), d.get("claimed_by")

# artifact preconditions (fail-closed, zero closure without evidence)
m = json.load(open(r"results\_r264bma_cn_verdict_matrix.json", encoding="utf-8"))
fams = list(m)
assert set(fams) == {"CN-REV-TILT", "CN-DIV-LOWVOL-ROT", "CN-REGIME-POLICY", "CN-CORE-SATELLITE", "CN-CORE-DDCTL"}, fams
neg = all((not c["pass_v2"]) for f in fams for c in m[f]["cells"].values())
assert neg, "unexpected pass in matrix"
g = json.load(open(r"results\grid_sleeve_p1.json", encoding="utf-8"))
assert g["survivors_science"] == [] and g["paper_candidates"] == []

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["status"] = "done"
d["done_at"] = now
d["result_ref"] = ("research/CN_COMBO_VERDICTS.md + results/_r264bma_cn_verdict_matrix.json "
                   "(4 matrix families x 19 cells ALL NEG) + results/grid_sleeve_p1.json "
                   "(CN-GRID-SLEEVE via T-78 convergence: 0 science survivors / 0 paper candidates)")
d["progress_r307_bma"] = (
    "r307 closure: all spec faces landed -> ticket done. s1 16-school survey digest; s2 slices A-E "
    "(policy-cycle / retail-herding / size-lowvol-div factor history / style-rotation empirical in-repo faces); "
    "s3 five CN native models prereg->judgment stand ALL NEGATIVE (REV-TILT 4 cells / DIV-LOWVOL-ROT 4 / "
    "REGIME-POLICY 3 / CORE-SATELLITE 4 + CORE-DDCTL 4 = matrix 19 cells NEG; GRID-SLEEVE converged to T-78 "
    "grid family 0 survivors 0 paper candidates); s4 month-boundary combo-pool entry = ZERO INTAKE by "
    "construction (0 survivors) -- first cross-check 2026-10-01 handed to monthly-round face; non-viable "
    "schools recorded-not-modeled honored (microcap 2024 collapse / northbound withdrawn O-1120 / T0 red-line / "
    "zhuang-following compliance). Zero CN-* paper accounts opened (judged-negative => no promotion) honest."
)
with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
# self-verify
d2 = json.load(open(P, encoding="utf-8"))
assert d2["status"] == "done" and d2["result_ref"]
print("T-73 CLOSED ok at", now)
