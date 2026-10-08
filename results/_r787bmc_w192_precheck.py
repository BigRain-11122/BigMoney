# -*- coding: utf-8 -*-
"""r787 bm-c W192 precheck: machine-read the W191 finalize product + owner-row
counts + dep-chain presence, feeding exact assert values for the W192
pre-seat probe roll (r587 never-transcribe: every number derives here)."""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "research"))
from perpetual_faces import N1_BANDS  # noqa: E402

out = {}
w191 = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                   "n1_w191_results.json"), encoding="utf-8"))
sg = w191.get("science_gates") or {}
out["w191_ledger"] = sg.get("ledger")
out["w191_cutoff_meta"] = sg.get("cutoff_meta")
out["w191_top_keys"] = sorted(w191.keys())
out["w191_batch"] = w191.get("batch")
owners = {}
for w, c in N1_BANDS.items():
    o = c.get("engine_owner")
    owners[o] = owners.get(o, 0) + 1
out["owner_counts"] = owners
out["rows_total"] = len(N1_BANDS)
out["keys_tail"] = sorted(N1_BANDS)[-5:]
out["w191_row"] = N1_BANDS.get(191)
out["w190_row"] = N1_BANDS.get(190)
missing = []
for w in range(17, 192):
    p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{w}_results.json")
    if not os.path.exists(p):
        missing.append(w)
out["dep_missing_W17_W191"] = missing
print(json.dumps(out, ensure_ascii=False, indent=1))
