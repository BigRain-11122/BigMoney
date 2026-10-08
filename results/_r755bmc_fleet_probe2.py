# -*- coding: utf-8 -*-
"""r755 bm-c FleetLink probe 2: origin blobs for register-fleet-link.ps1 (full),
evolution-ledger.md P-09/P-10 row context, recent origin log."""
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


print("=== origin register-fleet-link.ps1 ===")
rc, out, _ = git(["show", "origin/main:Tools/register-fleet-link.ps1"])
print(out)
print("=== origin evolution-ledger.md L112-140 ===")
rc, out, _ = git(["show", "origin/main:cph4/evolution-ledger.md"])
lines = out.splitlines()
for i, ln in enumerate(lines[111:140], start=112):
    print("%d: %s" % (i, ln[:600]))
print("=== origin log -5 ===")
rc, out, _ = git(["log", "-5", "--format=%h|%ci|%s", "origin/main"])
print(out)
