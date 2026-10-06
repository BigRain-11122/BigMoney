# -*- coding: utf-8 -*-
"""Settle: full pf.py diff of the r775 freeze commit 6957f509e -- what
exactly changed in the W157 block region and what the W158 block looked
like as LANDED (not as derived)."""
import subprocess

d = subprocess.run(["git", "show", "6957f509e", "--", "scripts/perpetual_faces.py"],
                   capture_output=True).stdout.decode("utf-8", errors="replace")
lines = d.splitlines()
print("diff lines:", len(lines))
# print hunk headers
for idx, l in enumerate(lines):
    if l.startswith("@@") or l.startswith("diff") or l.startswith("---") or l.startswith("+++"):
        print(idx, l[:100])
