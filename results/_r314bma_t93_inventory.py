"""R314 bm-a T-93 sender inventory: verify the 30 DATASET files exist locally,
report honest missing list + sizes (no fabrication)."""
import os

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

missing, present = [], []
total = 0
for f in FILES:
    if os.path.exists(f):
        sz = os.path.getsize(f)
        total += sz
        present.append((f, sz))
    else:
        missing.append(f)

print(f"present {len(present)}/{len(FILES)}  total {total/1e6:.1f}MB")
for f, sz in present:
    print(f"  OK  {f}  {sz/1e6:.2f}MB")
for f in missing:
    print(f"  MISSING  {f}")
over = [f for f, sz in present if sz > 95 * 1024 * 1024]
print("over-95MB files:", over or "none")
print("manifest tool exists:", os.path.exists("Tools/transfer_manifest.ps1"))
