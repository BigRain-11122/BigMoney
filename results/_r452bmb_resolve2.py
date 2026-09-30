# r452 bm-b resolver part-2: regime_state (asof-keyed history + top-level take-new-by-updated)
# + crash_fuse/token_usage inspect-merge + take-new-by-ts set + md/js twins.
# compute_audit.json already resolved by part-1 first iteration (history union 201+201, latest take-new).
import json, subprocess, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], cwd=REPO, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{side}:{path} rc={r.returncode}")
    return r.stdout.decode("utf-8-sig", errors="strict")

def load(side, path):
    return json.loads(stage(side, path))

def write_json(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    json.loads(txt)  # r185 verify pre-add
    with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)

report = []

# --- regime_state: history union by 'asof' (cap 3), top-level take-new by 'updated' ---
p = "results/regime_state.json"
a, b = load(2, p), load(3, p)
seen = {}
for e in a["history"] + b["history"]:
    seen[str(e["asof"])] = e
hist = sorted(seen.values(), key=lambda e: str(e["asof"]))[-3:]
base = a if str(a.get("updated", "")) >= str(b.get("updated", "")) else b
merged = dict(base)
merged["history"] = hist
write_json(p, merged)
report.append(f"{p}: history asof-union {len(a['history'])}+{len(b['history'])}->{len(hist)}, top-level take-new updated={base.get('updated')} (side {'ours' if base is a else 'theirs'})")

# --- crash_fuse + token_usage: inspect then merge ---
def inspect(path):
    a, b = load(2, path), load(3, path)
    return a, b

for p in ("results/crash_fuse.json", "results/token_usage.json"):
    a, b = inspect(p)
    if not (isinstance(a, dict) and isinstance(b, dict)):
        raise RuntimeError(f"{p} unexpected shape: {type(a)}")
    merged = {}
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k), b.get(k)
        if isinstance(va, dict) and isinstance(vb, dict):
            ta, tb = str(va.get("ts", "")), str(vb.get("ts", ""))
            merged[k] = vb if tb >= ta else va
        elif isinstance(va, list) and isinstance(vb, list):
            # append-type lists: union by json identity preserving order a-then-b-new
            seenl = []
            for e in va + vb:
                if e not in seenl:
                    seenl.append(e)
            merged[k] = seenl
        else:
            merged[k] = vb if k in b else va
    write_json(p, merged)
    report.append(f"{p}: per-key merge {sorted(set(a)|set(b))[:6]}... -> {len(merged)} keys")

# --- take-new-by-ts regenerates ---
take_new = [
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
    "results/update_status.json",
]
def ts_of(obj, keys=("ts", "generated", "updated", "last_scan", "scan_ts", "asof")):
    for k in keys:
        if isinstance(obj, dict) and k in obj and obj[k] is not None:
            return str(obj[k])
    return None

json_winner = {}
for p in take_new:
    a, b = load(2, p), load(3, p)
    ta, tb = ts_of(a), ts_of(b)
    if ta is None and tb is None:
        winner, pick, note = "theirs(bm-b)", b, "no-ts default-theirs(r452 later chain)"
    else:
        winner = "theirs(bm-b)" if str(tb or "") >= str(ta or "") else "ours(bm-c)"
        pick = b if winner == "theirs(bm-b)" else a
        note = f"{ta} vs {tb}"
    json_winner[p] = winner
    write_json(p, pick)
    report.append(f"{p}: take-new {winner} ({note})")

# --- md/js twins follow JSON winners ---
follow = {
    "docs/daily_report/REPORT-2026-09-30.md": "docs/daily_report/REPORT-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md": "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
for md, js in follow.items():
    side = 3 if json_winner[js].startswith("theirs") else 2
    txt = stage(side, md)
    with open(os.path.join(REPO, md), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    report.append(f"{md}: follows JSON winner side={side}")

for line in report:
    print("[resolve2]", line)
print("PART-2 ALL RESOLVED + VERIFIED")
