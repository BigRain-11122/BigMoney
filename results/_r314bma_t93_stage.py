"""R314 bm-a T-93 sender stage: copy the 30 DATASET files into a TEMP staging
tree mirroring repo-relative names (for transfer_manifest.ps1 -Path root)."""
import os
import shutil

FILES = [
    "results/decision_chain/curves_x2_legacy_LA.jsonl",
    "results/decision_chain/curves_x2_legacy_LD.jsonl",
    "results/decision_chain/curves_x2_deep_DA.jsonl",
    "results/decision_chain/curves_x2_deep_DC.jsonl",
    "results/decision_chain/curves_x2_deep_DD.jsonl",
    "results/decision_chain/curves_x2_deep_DE.jsonl",
    "results/pros_segs/cells_legacy_LA.jsonl",
    "results/pros_segs/cells_legacy_LB.jsonl",
    "results/pros_segs/cells_legacy_LC.jsonl",
    "results/pros_segs/cells_legacy_LD.jsonl",
    "results/pros_segs/cells_deep_DA.jsonl",
    "results/pros_segs/cells_deep_DB.jsonl",
    "results/pros_segs/cells_deep_DC.jsonl",
    "results/pros_segs/cells_deep_DD.jsonl",
    "results/pros_segs/cells_deep_DE.jsonl",
    "results/decision_chain/done_x2_legacy_LA.json",
    "results/decision_chain/done_x2_legacy_LD.json",
    "results/decision_chain/done_x2_deep_DA.json",
    "results/decision_chain/done_x2_deep_DC.json",
    "results/decision_chain/done_x2_deep_DD.json",
    "results/decision_chain/done_x2_deep_DE.json",
    "results/pros_segs/done_legacy_LA.json",
    "results/pros_segs/done_legacy_LB.json",
    "results/pros_segs/done_legacy_LC.json",
    "results/pros_segs/done_legacy_LD.json",
    "results/pros_segs/done_deep_DA.json",
    "results/pros_segs/done_deep_DB.json",
    "results/pros_segs/done_deep_DC.json",
    "results/pros_segs/done_deep_DD.json",
    "results/pros_segs/done_deep_DE.json",
]

STAGE = os.path.join(os.environ.get("TEMP", "."), "t93_stage_r314bma")

if os.path.exists(STAGE):
    shutil.rmtree(STAGE)
n = 0
for f in FILES:
    dst = os.path.join(STAGE, f.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(f, dst)
    n += 1
print(f"staged {n}/30 -> {STAGE}")
