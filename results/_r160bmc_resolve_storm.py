"""r160 bm-c push-storm rebase resolver (r155/r158 canon recipe family).

13 UU faces, all S6 derived-snapshot family vs bm-b r379/r380 (11:4x window:
W4 false-crash fix round + autofill tick keepalive/claim self-commits).
Canon (r155/r158 paradigm):
- pure derived snapshots: take-new by generated ts (tie -> :3: = replayed-local);
  coupled twins (REPORT json+md, dashboard json+js) take the same side via
  identical ts probing.
- update_status/lhb/futures status faces: max-cutoff then newer ts.
- compute_audit.json: latest=ts-newer side + history ts-key union.
Stage semantics per r159 pitlaw: :2: = onto(origin) side, :3: = replayed
local commit side; direction decided by ts/cutoff probes, never by label.
"""
import json
import re
import subprocess
import sys


def stage(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show failed: {spec}")
    return r.stdout.decode("utf-8", errors="replace")


def probe_ts(s):
    m = re.findall(r'"(?:generated|ts|updated_at|written_at|asof)"\s*:\s*"?([^",\n}]+)', s[:3000])
    return m[0] if m else ""


def probe_cutoff(s):
    m = re.findall(r'"cutoff[^"]*"\s*:\s*"?([^",\n}]+)', s[:3000])
    return m[0] if m else ""


report = []

TAKE_NEW_BY_TS = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-24.md",  # placeholder-skip if absent
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/token_usage.json",
]
TAKE_NEW_BY_TS = [f for f in TAKE_NEW_BY_TS if f != "docs/daily_report/REPORT-2026-09-24.md"]
TAKE_NEW_BY_TS.append("docs/daily_report/REPORT-2026-09-28.md")

MAX_CUTOFF = [
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
]

for f in TAKE_NEW_BY_TS:
    o, t = stage(":2:" + f), stage(":3:" + f)
    ots, tts = probe_ts(o), probe_ts(t)
    # coupled-twin pairing handled by identical ts probing -> same side wins
    side = "local-replayed" if tts >= ots else "origin"
    content = t if tts >= ots else o
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    report.append(f"{f}: take-new {side} (origin {ots!r} vs local {tts!r})")

for f in MAX_CUTOFF:
    o, t = stage(":2:" + f), stage(":3:" + f)
    oc, tc = probe_cutoff(o), probe_cutoff(t)
    ots, tts = probe_ts(o), probe_ts(t)
    if tc > oc or (tc == oc and tts >= ots):
        side, content = "local-replayed", t
    else:
        side, content = "origin", o
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    report.append(f"{f}: max-cutoff {side} (cutoff origin {oc!r} vs local {tc!r})")

# compute_audit: latest=ts-newer + history ts-key union
f = "results/compute_audit.json"
o, t = json.loads(stage(":2:" + f)), json.loads(stage(":3:" + f))
ol, tl = o.get("latest", o), t.get("latest", t)
newer = t if probe_ts(json.dumps(tl)) >= probe_ts(json.dumps(ol)) else o
merged = dict(newer)
oh, th = o.get("history", []), t.get("history", [])
seen = {h.get("ts") for h in oh}
union = list(oh) + [h for h in th if h.get("ts") not in seen]
merged["history"] = union
with open(f, "w", encoding="utf-8", newline="") as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
report.append(f"{f}: latest=ts-newer({probe_ts(json.dumps(newer))!r}) + history union {len(oh)}+{len(th)}->{len(union)}")

# parse-verify every resolved JSON face (fail-closed)
for f in TAKE_NEW_BY_TS + MAX_CUTOFF + ["results/compute_audit.json"]:
    if f.endswith(".json"):
        json.loads(open(f, encoding="utf-8").read())
report.append("parse-verify: all resolved JSON faces OK")

for line in report:
    print(line)
