"""r158 bm-c push-storm rebase resolver (r155/r157 canon recipe family).

26 UU faces, all S6 derived-snapshot family vs bm-b r377 (11:0x window) +
autofill tick self-commit. Canon (r155/r376 paradigm):
- pure derived snapshots: take-new by generated ts (tie -> theirs=landed);
  coupled twins (REPORT json+md, dashboard json+js, paper_export export+latest)
  take the same side.
- update_status/lhb/futures status faces: max-cutoff then newer ts.
- compute_audit.json: latest=ts-newer side + history ts-key union.
- x2_watch_log.jsonl: append-only line union (exact-dup dedupe).
- token_usage.json: delta-snapshot -> take-new by ts (r157 canon).
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
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
]

MAX_CUTOFF = [
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
]

for f in TAKE_NEW_BY_TS:
    o, t = stage(":2:" + f), stage(":3:" + f)
    ots, tts = probe_ts(o), probe_ts(t)
    # coupled-twin pairing handled by identical ts probing -> same side wins
    side = "theirs" if tts >= ots else "ours"
    content = t if side == "theirs" else o
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    report.append(f"{f}: take-new {side} (ours {ots!r} vs theirs {tts!r})")

for f in MAX_CUTOFF:
    o, t = stage(":2:" + f), stage(":3:" + f)
    oc, tc = probe_cutoff(o), probe_cutoff(t)
    ots, tts = probe_ts(o), probe_ts(t)
    if tc > oc or (tc == oc and tts >= ots):
        side, content = "theirs", t
    else:
        side, content = "ours", o
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    report.append(f"{f}: max-cutoff {side} (cutoff ours {oc!r} vs theirs {tc!r})")

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

# x2_watch_log.jsonl: append-only line union
f = "results/x2_watch_log.jsonl"
o_lines = stage(":2:" + f).splitlines()
t_lines = stage(":3:" + f).splitlines()
seen = set(o_lines)
union = o_lines + [ln for ln in t_lines if ln not in seen]
with open(f, "w", encoding="utf-8", newline="") as fh:
    fh.write("\n".join(union) + ("\n" if union else ""))
report.append(f"{f}: line union {len(o_lines)}+{len(t_lines)}->{len(union)} (exact-dup dedupe)")

for line in report:
    print(line)
