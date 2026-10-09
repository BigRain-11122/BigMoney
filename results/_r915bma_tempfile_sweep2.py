# -*- coding: utf-8 -*-
"""r915 bm-a council-dispatch temp-file sweep EXTENSION (C-20261009-02
@BigMoney item-1 清临时件): the remaining 227 root _r* scratch files
(historical per-round probes/resolvers/closeout writers/commitmsg
variants from the r767-r806 era, all machines) -- prescan + quarantine
via the legal path. Zero hard deletes."""
import glob
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
files = sorted(set(glob.glob(os.path.join(ROOT, "_r*"))))
files = [f for f in files if os.path.isfile(f)]
print("sweep candidates:", len(files))
if not files:
    print("NOTHING TO SWEEP")
    sys.exit(0)

for cmd in ("prescan", "quarantine"):
    argv = [sys.executable, os.path.join(ROOT, "Tools", "treasure_guard.py"), cmd] \
        + [os.path.relpath(f, ROOT) for f in files] \
        + (["--reason", "C-20261009-02 @BigMoney dispatch item-1 "
            "clean-root-temp-files extension: remaining historical "
            "per-round scratch (probes/resolvers/closeout/commitmsg "
            "variants, r767-r806 era) quarantine sweep"] if cmd == "quarantine" else [])
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, creationflags=CNW)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    print("== %s rc=%d" % (cmd, p.returncode))
    print(out[-800:])
    if p.returncode != 0:
        print("ABORT at %s" % cmd)
        sys.exit(p.returncode)

left = [f for f in files if os.path.exists(f)]
assert not left, "files still present: %d" % len(left)
print("POST-SWEEP ASSERT PASS: root _r* leftovers=0 (swept %d)" % len(files))
