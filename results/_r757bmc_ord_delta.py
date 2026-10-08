# -*- coding: utf-8 -*-
"""r757 bm-c ORD delta probe v2: query ORIGIN/MAIN history (v1 wrongly used
local HEAD; group tree chronically behind origin per fresh-read law), show
commits touching docs/orders.md and the 10-08 rows in the current blob."""
import json
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


out = {"round": 757}
rc, o, e = git(["log", "origin/main", "-8", "--format=%h|%ci|%s", "--",
                "docs/orders.md"])
out["origin_log"] = o.strip().splitlines()

rc, blob, _ = git(["show", "origin/main:docs/orders.md"])
lines = blob.splitlines()
rows08 = [ln for ln in lines if ln.startswith("| 10-08")]
out["rows_1008"] = rows08
tail_rows = [ln for ln in lines if ln.startswith("| 10-07 2") or ln.startswith("| 10-08")]
out["tail_rows_count"] = len(tail_rows)

with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r757bmc_ord_delta.json",
          "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print("ORIGIN_LOG_LINES=%d ROWS_1008=%d TAIL=%d (receipt in json)"
      % (len(out["origin_log"]), len(rows08), len(tail_rows)))
for ln in out["origin_log"]:
    print(ln)
