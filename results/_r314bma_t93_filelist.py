import io

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
with io.open("results/_r314bma_t93_filelist.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(FILES))
print(len(FILES), "paths written")
