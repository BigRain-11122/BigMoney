# -*- coding: utf-8 -*-
# r1121 bm-c: full-text read of the 16:04 external-review row + d19 tool interface probe. Read-only.
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"
cur = subprocess.run(["git", "-C", GRP, "show", "origin/main:docs/orders.md"], capture_output=True).stdout
lines = cur.decode("utf-8", "replace").splitlines()
for l in lines:
    if "外部审查报告定谳令" in l or ("16:04" in l and "executed" in l):
        print(l)
        print("=====ROW_END=====")
        break
r = subprocess.run(["python", "scripts/d19_watermark.py", "--help"], capture_output=True, text=True)
print("D19 HELP rc=%d" % r.returncode)
print((r.stdout or r.stderr)[:1500])
