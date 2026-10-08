# -*- coding: utf-8 -*-
"""r755 bm-c silence-order probe: origin Tools silence inventory + full
silence-enforce.ps1 body + local presence check (O-20261008-1240-bm-c)."""
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


print("=== origin Tools/ silence* ===")
rc, out, _ = git(["ls-tree", "--name-only", "origin/main", "Tools/"])
for ln in out.splitlines():
    if "silence" in ln.lower() or "guard" in ln.lower():
        print(ln)
print("=== local presence ===")
for name in ["silence-enforce.ps1"]:
    p = os.path.join(GROUP, "Tools", name)
    print(name, "local exists:", os.path.exists(p))
print("=== origin silence-enforce.ps1 (full) ===")
rc, out, _ = git(["show", "origin/main:Tools/silence-enforce.ps1"])
print(out)
