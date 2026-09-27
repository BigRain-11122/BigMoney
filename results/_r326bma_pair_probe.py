# -*- coding: utf-8 -*-
"""r326: probe dashboard pair generated_at per rebase stage + pair-fix."""
import json
import re
import subprocess


def sb(p, n):
    return subprocess.run(["git", "show", ":%d:%s" % (n, p)],
                          capture_output=True).stdout


PAT = re.compile(rb'"generated_at":\s*"([^"]+)"')

for p in ("results/dashboard_status.js", "results/dashboard_status.json"):
    for n in (2, 3):
        b = sb(p, n)
        m = PAT.search(b)
        print("stage :%d %-36s generated_at=%s len=%d"
              % (n, p.split("/")[-1], m.group(1).decode() if m else None, len(b)))
    print("  identical:", sb(p, 2) == sb(p, 3))
