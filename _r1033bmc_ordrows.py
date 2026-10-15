# -*- coding: utf-8 -*-
# r1033 ORD delta rows: read origin blob tail, list table rows after r1032 consume point (4f5727aa = rows through 17:41 O-1741)
import subprocess, io, sys

GROUP = r"K:\Fluxgroup\FluxGroup"
out = subprocess.run(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"],
                     capture_output=True, timeout=60).stdout.decode("utf-8", errors="replace")
lines = out.splitlines()
rows = [(i, l) for i, l in enumerate(lines) if l.startswith("| ")]
tail = rows[-30:]
for i, l in tail:
    sys.stdout.buffer.write((l[:230] + "\n").encode("utf-8", errors="replace"))
