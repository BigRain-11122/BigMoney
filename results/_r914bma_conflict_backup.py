# -*- coding: utf-8 -*-
"""r914 bm-a rebase conflict backup + compute_audit structure probe."""
import io
import json
import os
import shutil

TMP = r"C:\Users\sjs20\.codely-cli\tmp\r914-rebase"
FACES = ["results/compute_audit.json", "results/regime_state.json",
         "results/scorecard_v1.json", "results/strategy_scorecard.json",
         "results/update_status.json"]

os.makedirs(TMP, exist_ok=True)
for f in FACES:
    dst = os.path.join(TMP, os.path.basename(f))
    shutil.copyfile(f, dst)
    print("backed up", f, "->", dst)

d = json.load(io.open("results/compute_audit.json", encoding="utf-8"))
print("compute_audit top type:", type(d).__name__)
if isinstance(d, dict):
    print("keys:", list(d.keys())[:12])
    for k, v in list(d.items())[:3]:
        print("  %s: %s len=%s" % (k, type(v).__name__,
                                   len(v) if hasattr(v, "__len__") else "-"))
elif isinstance(d, list):
    print("list len=", len(d))
    print("entry keys:", list(d[-1].keys()) if d else "-")
    print("tail ts:", d[-1].get("ts") if d else "-")
