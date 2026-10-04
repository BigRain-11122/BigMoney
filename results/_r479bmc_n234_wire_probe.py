# -*- coding: utf-8 -*-
"""r479 bm-c O-1440 sec.2 N2-N4 wiring-state probe (read-only evidence):
per-face runner-landed state via module subcommand selftest + generator
status + pool waiting-entry identity + engine py face. ASCII stdout."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CREATE = 0x08000000
PY = sys.executable
OUT = {"probe": "r479bmc_n234_wire", "machine": "bm-c"}


def run(args, timeout=300):
    try:
        p = subprocess.run([PY] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=CREATE)
        return {"rc": p.returncode,
                "tail": (p.stdout or "").strip().splitlines()[-6:],
                "err_tail": (p.stderr or "").strip().splitlines()[-3:]}
    except subprocess.TimeoutExpired:
        return {"rc": 99, "err_tail": ["TIMEOUT %ds" % timeout]}


# 1) per-face selftests (hermetic offline)
for mod, face in (("perpetual_faces_n2", "N2"),
                  ("perpetual_faces_n3", "N3"),
                  ("perpetual_faces_n4", "N4")):
    OUT[face + "_selftest"] = run(["scripts/" + mod + ".py", "selftest"])

# 2) generator status (pool-hunger + face registration + flags)
OUT["generator_status"] = run(["scripts/perpetual_faces.py", "status"])

# 3) pool waiting entry identity
with open(r"results\runnable_pool.json", encoding="utf-8") as f:
    pool = json.load(f)
OUT["pool_waiting"] = [
    {"id": e.get("id"), "status": e.get("status"),
     "lane_owner": e.get("lane_owner"), "priority": e.get("priority"),
     "prereg_ref": e.get("prereg_ref"), "runner": e.get("runner")}
    for e in pool.get("entries", []) if e.get("status") == "waiting"]

# 4) N3-R1 burn evidence (ledger row) + N2/N4 prereg file states
import glob as g
for fam, pat in (("n3_r1_products", r"results\perpetual_faces\*n3*"),
                 ("n2_products", r"results\perpetual_faces\*n2*"),
                 ("n4_products", r"results\perpetual_faces\*n4*")):
    OUT[fam] = sorted(os.path.basename(x) for x in g.glob(pat))[:12]
OUT["prereg_files"] = {
    "n2_w15": os.path.exists(r"research\PERPETUAL_N2_W15_PREREG.md"),
    "n3_r1": os.path.exists(r"research\PERPETUAL_N3_R1_PREREG.md"),
    "n4_b1": os.path.exists(r"research\PERPETUAL_N4_B1_PREREG.md"),
}

print(json.dumps(OUT, indent=1, ensure_ascii=True))
