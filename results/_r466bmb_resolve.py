# r466 bm-b push-rejection rebase resolver (19 UU): snapshots/mtwins take-new(:3 newer, probe-verified 14:15-16 vs bm-a 14:10-13)
# + compute_audit union zero-loss + regime_state union + marks :3 strict-superset wholesale (r461 law)
# Laws: r188/R208 union, R216 take-new, r461 ts-direction, R209 js wrapper whole-bytes, r185 parse-validate
import subprocess, json, io, sys

def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"stage read fail {stage} {path}: {r.stderr[:200]}")
    return r.stdout

report = {}

# 1) snapshots + twins: take :3 wholesale (probe: all :3 newer; twins forced same side as json probe)
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in SNAPSHOTS:
    b = stage_bytes(3, p)
    if p.endswith(".json"):
        json.loads(b.decode("utf-8", errors="strict"))  # parse-validate before write (r185)
    with open(p, "wb") as f:
        f.write(b)
    report[p] = f"take-:3 ({len(b)}B)"

# 2) marks-20260930.jsonl: :3 strict superset (only2=0 probe) -> take :3 wholesale (r461 superset law)
p = "results/paper/marks/marks-20260930.jsonl"
l2 = stage_bytes(2, p).decode("utf-8").splitlines()
l3 = stage_bytes(3, p).decode("utf-8").splitlines()
s2, s3 = set(l2), set(l3)
assert not (s2 - s3), f"marks :2 has {len(s2-s3)} lines not in :3 -- NOT superset, abort blind take"
with open(p, "wb") as f:
    f.write(stage_bytes(3, p))
report[p] = f"take-:3 strict-superset (:2 {len(l2)} subset of :3 {len(l3)}, union {len(s2|s3)})"

# 3) compute_audit: union history by ts key (zero row loss), latest snapshot fields take-:3
p = "results/compute_audit.json"
a = json.loads(stage_bytes(2, p).decode("utf-8"))
b = json.loads(stage_bytes(3, p).decode("utf-8"))
ka = {row.get("ts"): row for row in a["history"]}
kb = {row.get("ts"): row for row in b["history"]}
merged = dict(ka); merged.update(kb)
hist = sorted(merged.values(), key=lambda r: r.get("ts", ""))
assert len(hist) == len(set(ka) | set(kb)), f"union assert fail {len(hist)} vs {len(set(ka)|set(kb))}"
assert b["latest"]["ts"] >= a["latest"]["ts"], f"latest direction wrong: {b['latest']['ts']} < {a['latest']['ts']}"
res = dict(b)
res["history"] = hist
out = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
json.loads(out)
io.open(p, "w", encoding="utf-8", newline="\n").write(out)
report[p] = f"union history {len(ka)}+{len(kb)}->{len(hist)} (|A\u222aB|={len(set(ka)|set(kb))} exact), latest take-:3 ts={b['latest']['ts']}"

# 4) regime_state: union history (asof) + transitions (ts), state fields take-:3
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
assert b.get("updated", "") >= a.get("updated", ""), f"regime updated direction wrong"
res = dict(b)
res["history"] = hist
res["transitions"] = trans
out = json.dumps(res, ensure_ascii=False, indent=2) + "\n"
json.loads(out)
io.open(p, "w", encoding="utf-8", newline="\n").write(out)
report[p] = f"union history {len(ha)}+{len(hb)}->{len(hist)}, transitions {len(ta)}+{len(tb)}->{len(trans)}, state take-:3 updated={b.get('updated')}"

for k, v in report.items():
    print(f"[resolved] {k} | {v}")
print(f"ALL 19 RESOLVED ({len(report)} faces), zero-loss asserts PASS")
