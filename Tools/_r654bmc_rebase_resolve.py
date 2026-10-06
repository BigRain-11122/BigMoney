# -*- coding: utf-8 -*-
"""r654 bm-c rebase UU resolution: 14 S6-regenerable shared faces, deep-ts
newer-wins = stage3 (bm-c r654 S6 04:41-42) beats stage2 (bm-a r808 S6
04:34-36) on ALL 14 faces (dual probe receipts _r654bmc_uupro*).
Discipline: per-face targeted checkout --theirs + reparse/marker verify +
targeted add (NO add -u loop, r794 law) + rebase --continue in the SAME
process (r787 add+continue atomic law)."""
import json
import os
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

UU = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def git(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:3], r.stderr.decode("utf-8", "replace")[:300]))
    return r


# 0) confirm the UU set matches expectation exactly
out = git(["ls-files", "-u"]).stdout.decode("utf-8", "replace")
got = sorted({ln.split("\t")[1] for ln in out.splitlines() if "\t" in ln})
assert got == sorted(UU), "UU set drift: %s" % got

# 1) per-face: checkout --theirs (stage3 = r654 side), verify, targeted add
for f in UU:
    git(["checkout", "--theirs", f])
    data = open(f, "rb").read()
    assert b"<<<<<<<" not in data and b">>>>>>>" not in data, "marker leak in " + f
    if f.endswith(".json"):
        json.loads(data.decode("utf-8-sig"))  # reparse gate (r710B law)
    git(["add", f])
    print("resolved (theirs=newer r654):", f)

# 2) rebase --continue in the SAME process (r787 atomic law), editor disabled
env = dict(os.environ)
env["GIT_EDITOR"] = "true"
r = subprocess.run(["git", "rebase", "--continue"], capture_output=True, env=env,
                   creationflags=CREATE_NO_WINDOW)
print("rebase --continue rc=", r.returncode)
print(r.stdout.decode("utf-8", "replace")[-500:])
print(r.stderr.decode("utf-8", "replace")[-500:])
sys.exit(r.returncode)
