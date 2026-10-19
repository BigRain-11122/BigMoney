# -*- coding: utf-8 -*-
# r1121 bm-c: full-text of the NATS dispatch row + daily-output-report row. Read-only.
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"
cur = subprocess.run(["git", "-C", GRP, "show", "origin/main:docs/orders.md"], capture_output=True).stdout
lines = cur.decode("utf-8", "replace").splitlines()
for l in lines:
    if "机队实时通信总线铺装收口行" in l:
        print("=== NATS ROW FULL ===")
        print(l)
        print("=== END ===")
    if "每日产出汇报令" in l and "executed" in l:
        print("=== DAILY-REPORT ROW FULL ===")
        print(l)
        print("=== END ===")
