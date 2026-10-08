# -*- coding: utf-8 -*-
"""r756 bm-c ORD hop-2 tail extraction: dump last lines of origin orders.md
blob to identify rows added between sweep-1 (77C9BC92) and sweep-2
(6BE4D833). Zero tree touch."""
import json
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000

p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"],
                   capture_output=True, creationflags=CF)
assert p.returncode == 0
txt = p.stdout.decode("utf-8", "replace")
lines = txt.splitlines()
probe = {"total_lines": len(lines), "tail": [l for l in lines[-14:]]}
out = os.path.join(ROOT, "results", "_r756bmc_ord_hop2.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(probe, fh, indent=1, ensure_ascii=False)
for l in probe["tail"]:
    print(l[:200])
