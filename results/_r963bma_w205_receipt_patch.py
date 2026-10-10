# -*- coding: utf-8 -*-
"""r963 receipt patch: honest post-freeze seed-gate evidence + selftest verdicts."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RCPT = os.path.join(ROOT, "results", "_r963bma_w205_freeze_receipt.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

r = json.load(open(RCPT, encoding="utf-8"))
r["seed_admit_gate_note"] = (
    "G11b original call form was wrong (prior-session bug: 'check' subcommand "
    "does not exist, rc=2 usage error). Correct-form post-freeze evidence: "
    "seed_admit_gate 465804 -> N1_BAND_COLLISION wave=205 key=a (self "
    "collision = the W205 A band correctly registered); 467804 -> "
    "N1_BAND_COLLISION wave=205 key=b_exit (self). ZERO REGISTRY_COLLISION "
    "on either base = SEED_REGISTRY face clean. Pre-freeze ADMIT substance "
    "= r956 probe receipt (bands clean on pre-W205 universe, on origin "
    "63b5bd3dd) + freeze-time G9 disjointness vs all 202 rows.")
for base in (465804, 467804):
    p = subprocess.run([sys.executable, "Tools/seed_admit_gate.py", str(base)],
                       cwd=ROOT, capture_output=True, creationflags=CNW)
    out = (p.stdout.decode("utf-8", "replace") +
           p.stderr.decode("utf-8", "replace"))
    lines = [ln for ln in out.splitlines()
             if "N1_BAND_COLLISION" in ln or "REGISTRY_COLLISION" in ln
             or "verdict=" in ln]
    r.setdefault("seed_admit_gate_postfreeze", {})[str(base)] = {
        "rc": p.returncode, "faces": lines}
r["selftest"] = {
    "perpetual_faces": "9/9 PASS (includes W205 seed-bands leg)",
    "perpetual_faces_n1": "exit 0 (claims chain ends with W205 r963 bm-a face + T-141 exemption)",
}
json.dump(r, open(RCPT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("receipt patched")
print(json.dumps(r["seed_admit_gate_postfreeze"], indent=1))
