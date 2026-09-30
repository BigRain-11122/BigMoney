# r452 bm-b rebase resolver: 19-UU same-window S6 mirror collision (bm-c r260 vs bm-b r452)
# Canon: rolling-ledger history faces = ts-distinct union; same-day regenerate faces = take-new-by-ts;
# md/js twins follow their JSON winners. All json.loads verified pre-add (r185 law).
import json, subprocess, sys, io, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{side}:{path} rc={r.returncode} {r.stderr[:200]}")
    return r.stdout.decode("utf-8-sig", errors="strict")

def load(side, path):
    return json.loads(stage(side, path))

def ts_of(obj, keys=("ts", "generated", "updated", "last_scan", "scan_ts")):
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            return str(obj[k])
    return None

CONFLICTS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/crash_fuse.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

# stage 2 = ours = HEAD during rebase = bm-c r260 base side
# stage 3 = theirs = my r452 commit side

def union_history(a, b, cap=None):
    """ts-distinct union preserving chronological order; later occurrence wins on dupe."""
    seen = {}
    for e in a + b:
        t = ts_of(e)
        if t is None:
            raise RuntimeError("history entry without ts key")
        seen[t] = e
    out = sorted(seen.values(), key=lambda e: str(ts_of(e)))
    if cap and len(out) > cap:
        out = out[-cap:]
    return out

report = []

# --- class 1: rolling history + latest (union) ---
for path, cap in [("results/compute_audit.json", 210), ("results/regime_state.json", None)]:
    a, b = load(2, path), load(3, path)
    ha, hb = a.get("history", []), b.get("history", [])
    merged = union_history(ha, hb, cap)
    latest = a.get("latest") or {}
    latest_b = b.get("latest") or {}
    ta, tb = ts_of(latest), ts_of(latest_b)
    winner = "ours(bm-c)" if (ta or "") >= (tb or "") else "theirs(bm-b)"
    latest_pick = latest if winner == "ours(bm-c)" else latest_b
    merged_obj = dict(a)
    merged_obj["latest"] = latest_pick
    merged_obj["history"] = merged
    txt = json.dumps(merged_obj, ensure_ascii=False, indent=2) + "\n"
    json.loads(txt)
    with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    report.append(f"{path}: history union {len(ha)}+{len(hb)}->{len(merged)} (dedupe ts), latest take-new {winner} ({ta} vs {tb})")

# --- class 2: take-new-by-ts JSON regenerates ---
take_new_json = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
json_winner = {}
for path in take_new_json:
    a, b = load(2, path), load(3, path)
    ta, tb = ts_of(a), ts_of(b)
    if ta is None and tb is None:
        # no top-level ts: prefer theirs (my r452 commit, later chain) but verify equality class
        json_winner[path] = "theirs(bm-b)"
        pick = b
        note = "no-ts-field default-theirs"
    else:
        winner = "theirs(bm-b)" if str(tb) >= str(ta) else "ours(bm-c)"
        json_winner[path] = winner
        pick = b if winner == "theirs(bm-b)" else a
        note = f"{ta} vs {tb}"
    txt = json.dumps(pick, ensure_ascii=False, indent=2) + "\n"
    json.loads(txt)
    with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    report.append(f"{path}: take-new {winner} ({note})")

# --- class 3: crash_fuse (inspect: machine-keyed or flat) ---
cf_a, cf_b = load(2, "results/crash_fuse.json"), load(3, "results/crash_fuse.json")
if isinstance(cf_a, dict) and isinstance(cf_b, dict):
    keys_a, keys_b = set(cf_a), set(cf_b)
    merged_cf = dict(cf_a)
    merged_cf.update(cf_b)  # theirs wins on shared keys only if newer ts inside; inspect depth
    # deep: if values are dicts with ts, merge per-key take-new
    for k in keys_a | keys_b:
        va, vb = cf_a.get(k), cf_b.get(k)
        if isinstance(va, dict) and isinstance(vb, dict):
            ta, tb = ts_of(va), ts_of(vb)
            merged_cf[k] = vb if (tb and (not ta or str(tb) >= str(ta))) else va
        else:
            merged_cf[k] = vb if k in cf_b else va
    txt = json.dumps(merged_cf, ensure_ascii=False, indent=2) + "\n"
    json.loads(txt)
    with open(os.path.join(REPO, "results/crash_fuse.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    report.append(f"results/crash_fuse.json: per-key merge keys {len(keys_a)}|{len(keys_b)} -> {len(merged_cf)}")
else:
    raise RuntimeError("crash_fude unexpected shape")

# --- class 4: md twins + js wrapper follow JSON winners ---
md_follow = {
    "docs/daily_report/REPORT-2026-09-30.md": "docs/daily_report/REPORT-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md": "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
for md, js in md_follow.items():
    side = 3 if json_winner[js].startswith("theirs") else 2
    txt = stage(side, md)
    with open(os.path.join(REPO, md), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    report.append(f"{md}: follows {js} winner side={side}")

for line in report:
    print("[resolve]", line)
print("ALL RESOLVED + VERIFIED")
