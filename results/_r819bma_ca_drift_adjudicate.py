# -*- coding: utf-8 -*-
"""r819 bm-a compute_audit reconcile-drift adjudication per r85 law:
rolling-window truncation != row loss. Directional key-set survival core."""
import json, sys, io
sys.path.insert(0, "scripts")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import merge_lane_views as mlv

shared = json.load(open(r"results/compute_audit.json", encoding="utf-8"))
merged, _notes = mlv.merge_face("compute_audit", mlv.load_sources("compute_audit"))
sh_keys = {json.dumps(r, sort_keys=True) for r in shared.get("history", [])}
mg_keys = {json.dumps(r, sort_keys=True) for r in merged.get("history", [])}
shared_only = sh_keys - mg_keys
merged_only = mg_keys - sh_keys
print("shared history rows:", len(sh_keys), "merged view rows:", len(mg_keys))
print("shared-only (would-be-LOST rows):", len(shared_only))
print("merged-only (rows newer than shared window):", len(merged_only))
for r in sorted(shared_only)[:3]:
    print("SHARED_ONLY_SAMPLE:", r[:160])
for r in sorted(merged_only)[:3]:
    print("MERGED_ONLY_SAMPLE:", r[:160])
# r85 adjudication: shared-only MUST be 0 (zero loss); merged-only = producer window fresher rows
verdict = "ZERO-LOSS (r85 rolling-window observation phase)" if not shared_only else "ACTIVE LOSS - STOP"
print("VERDICT:", verdict)
