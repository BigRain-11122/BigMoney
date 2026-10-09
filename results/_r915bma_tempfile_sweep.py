# -*- coding: utf-8 -*-
"""r915 bm-a council-dispatch temp-file sweep (C-20261009-02 @BigMoney
item-1 清临时件): prescan the 157 root _r*msg/_r*pathspec scratch files,
then quarantine-move them via the TREASURE_PROTECTION_LAW sec.2 legal
path (Tools/treasure_guard.py quarantine -- 7-day observation window,
manifest asserted). Zero hard deletes."""
import glob
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
patterns = ["_r*msg.txt", "_r*pathspec.txt"]
files = sorted(set(sum([glob.glob(os.path.join(ROOT, p)) for p in patterns], [])))
files = [f for f in files if os.path.isfile(f)]
print("sweep candidates:", len(files))

rc, out = None, None
for cmd in ("prescan", "quarantine"):
    argv = [sys.executable, os.path.join(ROOT, "Tools", "treasure_guard.py"), cmd] \
        + [os.path.relpath(f, ROOT) for f in files] \
        + (["--reason", "C-20261009-02 @BigMoney dispatch item-1 "
            "clean-root-temp-files: r915 quarantine sweep of commitmsg/"
            "pathspec scratch files (157, council audit face)"] if cmd == "quarantine" else [])
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, creationflags=CNW)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    print("== %s rc=%d" % (cmd, p.returncode))
    print(out[-1200:])
    rc = p.returncode
    if rc != 0:
        print("ABORT at %s -- zero further action" % cmd)
        sys.exit(rc)

# post-sweep assert: root clean of the patterns, manifest present
left = [f for f in files if os.path.exists(f)]
assert not left, "files still present after quarantine: %d" % len(left)
qdirs = sorted(glob.glob(os.path.join(ROOT, "results", "_quarantine", "2026-10-09*")))
assert qdirs, "no quarantine dir created"
man = [p for p in glob.glob(os.path.join(qdirs[-1], "*")) if "manifest" in p.lower()]
assert man, "manifest missing in %s" % qdirs[-1]
mjson = json.load(open(man[0], encoding="utf-8"))
n_in_dir = len([p for p in glob.glob(os.path.join(qdirs[-1], "*")) if os.path.isfile(p)]) - 1
print("POST-SWEEP ASSERT PASS: root leftovers=0, quarantine dir=%s, manifest "
      "entries=%s, files-in-dir=%d" % (os.path.basename(qdirs[-1]),
                                        len(mjson) if hasattr(mjson, "__len__") else "?",
                                        n_in_dir))
