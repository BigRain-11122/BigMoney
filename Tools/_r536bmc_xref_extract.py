# -*- coding: utf-8 -*-
"""r536 bm-c: extract bm-b r725 merge resolver from origin blob for lineage
reuse (python bytes extraction, r710-A law)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\scratch\_r725bmb_merge_resolve_REF.py"
r = subprocess.run(["git", "show", "origin/main:results/_r725bmb_merge_resolve.py"],
                   capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
if r.returncode != 0 or not r.stdout:
    print("EXTRACT-FAIL rc=%d len=%d" % (r.returncode, len(r.stdout or b"")))
    raise SystemExit(1)
with open(OUT, "wb") as fh:
    fh.write(r.stdout)
print("EXTRACTED %d bytes -> %s" % (len(r.stdout), OUT))
