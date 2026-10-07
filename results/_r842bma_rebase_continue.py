# -*- coding: utf-8 -*-
"""r842 bm-a: finish rebase (add resolved + continue with GIT_EDITOR=true per
r356 PS env law), then same-window reconcile closeout (r376), then push."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CREATE_NO_WINDOW = 0x08000000

def run(args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=e,
                       creationflags=CREATE_NO_WINDOW)
    return r

resolved = [
    "docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/regime_state.json",
    "results/token_usage.json", "results/update_status.json",
]
r = run(["git", "add"] + resolved)
print("add rc", r.returncode, (r.stderr or "")[:200])

# any remaining UU?
s = run(["git", "status", "--porcelain"])
uu = [l for l in s.stdout.splitlines() if l.startswith("UU") or l.startswith("AA")]
print("remaining UU/AA:", uu if uu else "none")
assert not uu, uu

r = run(["git", "rebase", "--continue"], env={"GIT_EDITOR": "true", "GIT_SEQUENCE_EDITOR": "true"})
print("rebase continue rc", r.returncode)
print((r.stdout or "").strip()[-400:])
if r.returncode != 0:
    print("STDERR:", (r.stderr or "").strip()[-400:])
    s2 = run(["git", "status", "--porcelain"])
    print("status now:")
    for l in s2.stdout.splitlines()[:20]:
        print("  ", l)
else:
    lg = run(["git", "log", "--oneline", "-4"])
    print(lg.stdout)
