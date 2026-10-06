# -*- coding: utf-8 -*-
"""r650 bm-c resolver fix-leg: 7 faces that fell to the origin default on
empty-ts parse are re-resolved to MINE (stage 3) -- my S6 generation
(03:21-03:24) is provably newer than bm-a r806's S6 (03:03-03:07); twin faces
must converge on the same generation (LIVE md/json, dashboard js/json).
regime_state: content-identical except 'updated' wall-clock (mine 03:21:36 >
origin 03:03:41). Receipt appended to results/_r650bmc_merge_resolve.json."""
import json, os, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def sha(path, stage):
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-u", "--", path],
                       capture_output=True, text=True, encoding="utf-8")
    for line in r.stdout.splitlines():
        p = line.split("\t")
        m = p[0].split()
        if len(p) >= 2 and m[2] == str(stage) and p[1] == path:
            return m[1]
    return None

def blob(s):
    r = subprocess.run(["git", "-C", ROOT, "cat-file", "-p", s], capture_output=True)
    assert r.returncode == 0 and r.stdout, "blob read failed %s" % s
    return r.stdout

FIX = [
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/regime_state.json",
]
report_path = os.path.join(ROOT, "results", "_r650bmc_merge_resolve.json")
rep = json.load(open(report_path, encoding="utf-8"))
for p in FIX:
    s3 = sha(p, 3)
    assert s3, "no stage3 for %s" % p
    b = blob(s3)
    full = os.path.join(ROOT, p.replace("/", os.sep))
    with open(full, "wb") as fh:
        fh.write(b)
    prev = rep["faces"].get(p, "")
    rep["faces"][p] = "mine (fix-leg: empty-ts default overturned -- newer generation 03:21-03:24 wins; prev='%s')" % prev
    print("fix-leg resolved:", p, len(b), "bytes")
rep["fix_leg"] = ("7 faces re-resolved to mine: my S6 generation 03:21-03:24 provably newer than origin 03:03-03:07; "
                  "twin convergence (LIVE md/json + dashboard js/json) + regime_state updated-field only diff")
json.dump(rep, open(report_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("receipt updated")
