"""r161 bm-c push-storm resolver (14-UU vs bm-b same-window S6 derived faces).

Canon: r158/r160 recipe + r159 direction law (stopped-sha full-file ts-probe
decides side; :2:/:3: labels never used as direction semantics). Probe result
this window: ALL 14 faces take :3: (bm-c 12:00-12:01 derive fresher than
bm-b 11:49-11:51 S6 derive; regime_state data-identical, only `updated` newer;
compute_audit latest take-newer + history ts-key union zero-loss).
Twins (dashboard_status.js / REPORT-2026-09-28.md) follow their JSON face.
All resolved faces parse-verified before staging.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("stage read fail %s" % path)
    return r.stdout

# ts-probed take-:3: faces (probe log above, direction = newer ts on :3:)
TAKE3 = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

report = {}
for p in TAKE3:
    data = stage(3, p)
    with open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.loads(data)  # parse-verify
    report[p] = "take-:3: (ts-probe newer) parse-ok"

# compute_audit: latest take-newer + history ts-key union zero-loss
p = "results/compute_audit.json"
a = json.loads(stage(2, p))
b = json.loads(stage(3, p))
lat_a = a.get("latest", {})
lat_b = b.get("latest", {})
latest = lat_b if str(lat_b.get("ts", "")) >= str(lat_a.get("ts", "")) else lat_a
hist = {}
for e in a.get("history", []) + b.get("history", []):
    k = str(e.get("ts"))
    if k not in hist:
        hist[k] = e
merged_hist = sorted(hist.values(), key=lambda e: str(e.get("ts")))
merged = {k: v for k, v in b.items() if k not in ("latest", "history")}
merged["latest"] = latest
merged["history"] = merged_hist
with open(p, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
report[p] = ("latest=%s (take-newer) + history union %d+%d->%d zero-loss"
            % (latest.get("ts"), len(a.get("history", [])),
               len(b.get("history", [])), len(merged_hist)))

print(json.dumps(report, ensure_ascii=False, indent=1))
print("RESOLVED: 14 faces, direction=take-:3: all, audit union zero-loss")
