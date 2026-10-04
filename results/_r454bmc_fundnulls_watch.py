"""r454 bm-c FUND trio NULLS continuity watch (read-only, bm-b canonical burn
lane per r622/r629 division law). Replicates r453 probe form, delta vs r453
evidence file. Zero-action unless a family hits nulls_cap=2000 (finalize
window opens 10-05 10:30)."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

FAMILIES = ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]
NULLS_CAP = 2000
CELLS_PER_FAMILY = 802  # x1+x2 across all cells_* files
SENS_PER_FAMILY = 500

prev_path = os.path.join(ROOT, "_r453bmc_fundnulls_watch.json")
with open(prev_path, encoding="utf-8") as f:
    prev = json.load(f)

fam_out = {}
delta_out = {}
for fam in FAMILIES:
    d = os.path.join(ROOT, fam)
    files = {}
    for name in os.listdir(d):
        if not name.endswith(".jsonl"):
            continue
        p = os.path.join(d, name)
        with open(p, "rb") as fh:
            rows = sum(1 for _ in fh)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(p))\
            .strftime("%m-%d %H:%M")
        files[name] = {"rows": rows, "mtime": mtime}
    fam_out[fam] = files
    prev_nulls = prev["families"][fam]["nulls.jsonl"]["rows"]
    now_nulls = files["nulls.jsonl"]["rows"]
    delta_out[fam] = now_nulls - prev_nulls

evidence = {
    "probe": "r454bmc fund NULLS watch (bm-b canonical burn, read-only)",
    "probe_time": NOW,
    "families": fam_out,
    "expected": {
        "cells_per_family": CELLS_PER_FAMILY,
        "sens_per_family": SENS_PER_FAMILY,
        "nulls_cap": NULLS_CAP,
    },
    "delta_vs_r453": {
        "nulls_rows": {f: fam_out[f]["nulls.jsonl"]["rows"] for f in FAMILIES},
        "delta": delta_out,
        "note": "rows " + "/".join(
            f"{fam_out[f]['nulls.jsonl']['rows']}" for f in FAMILIES) +
        " vs r453; finalize window opens 10-05 10:30 (D ETA per bm-b r652)",
    },
}
out_path = os.path.join(ROOT, "_r454bmc_fundnulls_watch.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(evidence, f, ensure_ascii=False, indent=1)
print("WROTE " + out_path)
print("nulls rows:", {f: fam_out[f]["nulls.jsonl"]["rows"] for f in FAMILIES})
print("delta vs r453:", delta_out)
