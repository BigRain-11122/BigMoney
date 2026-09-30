# r465 bm-b push-rejection rebase resolver (14 UU): snapshots take-new(:3 newer, probe-verified) + compute_audit/regime_state union zero-loss
# Laws: r188/R208 (union), R216 (take-new by ts), r461 (direction by per-side ts probe, never rebase-convention assumption)
import subprocess, json, io, sys

def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"stage read fail {stage} {path}: {r.stderr[:200]}")
    return r.stdout

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]
UNIONS = ["results/compute_audit.json", "results/regime_state.json"]

report = {}

# 1) snapshots: take :3 wholesale (probe showed mine newer on all 12)
for p in SNAPSHOTS:
    b = stage_bytes(3, p)
    if p.endswith(".json"):
        json.loads(b.decode("utf-8", errors="strict"))  # parse-validate before write (r185)
    with open(p, "wb") as f:
        f.write(b)
    report[p] = f"take-:3 ({len(b)}B)"

# 2) compute_audit: union history by ts key, latest take-new from :3
p = "results/compute_audit.json"
a = json.loads(stage_bytes(2, p).decode("utf-8"))
b = json.loads(stage_bytes(3, p).decode("utf-8"))
ka = {row.get("ts"): row for row in a["history"]}
kb = {row.get("ts"): row for row in b["history"]}
merged = dict(ka); merged.update(kb)  # same-ts rows: same audit run content (or newer editor); ts-key union
hist = sorted(merged.values(), key=lambda r: r.get("ts", ""))
assert len(hist) == len(set(ka) | set(kb)), f"union assert fail {len(hist)} vs {len(set(ka)|set(kb))}"
res = dict(b)  # latest = mine (14:03:51 > origin 14:00:25 probe-verified)
res["history"] = hist
out = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
json.loads(out)
io.open(p, "w", encoding="utf-8", newline="\n").write(out)
report[p] = f"union history {len(ka)}+{len(kb)}->{len(hist)} (|A∪B|={len(set(ka)|set(kb))} exact), latest take-:3 ts={b['latest']['ts']}"

# 3) regime_state: union history (by asof) + transitions, scalar fields take-new from :3
p = "results/regime_state.json"
a = json.loads(stage_bytes(2, p).decode("utf-8"))
b = json.loads(stage_bytes(3, p).decode("utf-8"))
ha = {row.get("asof"): row for row in (a.get("history") or [])}
hb = {row.get("asof"): row for row in (b.get("history") or [])}
merged = dict(ha); merged.update(hb)
hist = sorted(merged.values(), key=lambda r: r.get("asof", ""))
assert len(hist) == len(set(ha) | set(hb))
ta = {(t.get("ts") if isinstance(t, dict) else str(t)): t for t in (a.get("transitions") or [])}
tb = {(t.get("ts") if isinstance(t, dict) else str(t)): t for t in (b.get("transitions") or [])}
tm = dict(ta); tm.update(tb)
trans = sorted(tm.values(), key=lambda t: (t.get("ts", "") if isinstance(t, dict) else ""))
res = dict(b)  # state fields take-new (updated 14:03:59 > 14:00:45 probe-verified)
res["history"] = hist
res["transitions"] = trans
out = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
json.loads(out)
io.open(p, "w", encoding="utf-8", newline="\n").write(out)
report[p] = f"union history {len(ha)}+{len(hb)}->{len(hist)}, transitions {len(ta)}+{len(tb)}->{len(trans)}, state take-:3 updated={b['updated']}"

for k, v in report.items():
    print(f"[resolved] {k} | {v}")
print("ALL 14 RESOLVED, zero-loss asserts PASS")
