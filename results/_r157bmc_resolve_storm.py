"""r157 bm-c push-storm rebase resolver (r154/r155 canon recipe family).

9 UU faces, all S6 derived-snapshot family vs bm-b r376 (10:50 window) +
autofill tick self-commit. Strategies:
- take-new theirs: REPORT json+md (coupled-twin), dashboard_status json+js,
  prospect_paper/_summary, regime_state, t35_open_fill_verify, token_usage
  (delta-snapshot not cumulative ledger; ours r157 delta=0 zero-loss)
- compute_audit: latest=theirs (newer sample) + history ts-key union
"""
import json
import subprocess
import sys

def stage(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show failed: {spec}")
    return r.stdout.decode("utf-8", errors="replace")

TAKE_NEW = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/prospect_paper/_summary.json",
    "results/regime_state.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
]

report = []
for f in TAKE_NEW:
    t = stage(":3:" + f)
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    report.append(f"{f}: take-new theirs")

# compute_audit: latest=theirs + history ts-key union
f = "results/compute_audit.json"
o = json.loads(stage(":2:" + f))
t = json.loads(stage(":3:" + f))
merged = dict(t)  # envelope/latest from newer side
oh = o.get("history", [])
th = t.get("history", [])
seen = {h.get("ts") for h in oh}
union = list(oh) + [h for h in th if h.get("ts") not in seen]
merged["history"] = union
with open(f, "w", encoding="utf-8", newline="") as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
report.append(f"{f}: latest=theirs({t.get('latest', {}).get('ts', '?')}) + history union {len(oh)}+{len(th)}->{len(union)}")

for line in report:
    print(line)
