# -*- coding: utf-8 -*-
# r852 D19 cross-machine contradiction check (r779 three-step law):
# step1 fresh fetch of the GROUP tree, step2 raw-blob sha1 of decisions+orders at origin/main
import subprocess, hashlib, os

GROUPS = [r"C:\Fluxgroup\FluxGroup", r"K:\Fluxgroup\FluxGroup"]
for g in GROUPS:
    if not os.path.isdir(g):
        print(g, "-> absent")
        continue
    r = subprocess.run(["git", "-C", g, "fetch", "origin"], capture_output=True, text=True, timeout=120)
    print(g, "fetch rc:", r.returncode, (r.stderr or r.stdout).strip()[:120])
    for doc in ("docs/decisions.md", "docs/orders.md"):
        s = subprocess.run(["git", "-C", g, "show", f"origin/main:{doc}"], capture_output=True)
        if s.returncode != 0:
            print("  ", doc, "-> show rc", s.returncode, s.stderr.decode(errors="replace")[:80])
            continue
        h = hashlib.sha1(s.stdout).hexdigest()
        print("  ", doc, "origin/main sha1:", h, f"({len(s.stdout)} bytes)")
    break
