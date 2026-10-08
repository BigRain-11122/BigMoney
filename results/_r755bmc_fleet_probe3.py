# -*- coding: utf-8 -*-
"""r755 bm-c FleetLink probe 3: local vs origin blob identity for the three
carrier files (fleet-link.ps1 / InvisibleRunner.vbs / fleet-nodes.json)."""
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


for f in ["Tools/fleet-link.ps1", "Tools/InvisibleRunner.vbs",
          "Tools/fleet-nodes.json", "Tools/register-fleet-link.ps1"]:
    local_path = os.path.join(GROUP, f.replace("/", "\\"))
    if os.path.exists(local_path):
        rc, local_hash, _ = git(["hash-object", local_path])
    else:
        local_hash = "LOCAL-ABSENT"
    rc, origin_hash, _ = git(["rev-parse", "origin/main:" + f])
    verdict = "SAME" if local_hash == origin_hash else "DIFF/ABSENT"
    print("%-32s local=%s origin=%s %s" % (f, local_hash[:12], origin_hash[:12], verdict))
