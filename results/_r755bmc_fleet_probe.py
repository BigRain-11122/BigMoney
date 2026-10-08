# -*- coding: utf-8 -*-
"""r755 bm-c FleetLink adoption probe: origin-side roster bm-c entry, ledger
row P-2026-10-08-09 location, Tools inventory (local group tree is behind
origin; read blobs from origin per group-tree fresh-read law)."""
import json
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


rc, out, _ = git(["ls-tree", "--name-only", "origin/main", "Tools/"])
print("=== origin Tools/ ===")
print(out)
rc, out, _ = git(["grep", "-n", "-F", "P-2026-10-08-09", "origin/main"])
print("=== git grep P-2026-10-08-09 (origin/main) rc=%d ===" % rc)
print(out[:2000])
rc, out, _ = git(["show", "origin/main:Tools/fleet-nodes.json"])
try:
    d = json.loads(out)
    for n in d.get("nodes", []):
        if n.get("id") == "bm-c":
            print("=== origin bm-c roster entry ===")
            print(json.dumps(n, indent=1, ensure_ascii=False))
    print("port:", d.get("port"))
except Exception as e:
    print("roster parse err:", e, out[:400])
