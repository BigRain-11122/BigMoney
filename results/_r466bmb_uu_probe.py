# r466 bm-b push-collision rebase probe: per-face ts direction from STAGED blobs (:2=origin/bm-a-r475 side, :3=r466-mine)
# Laws: r461 direction-by-ts-probe (never rebase convention), R350 probe staged blob, r100 hardened ts scan
import subprocess, json, re, sys

def stage(stage_n, path):
    r = subprocess.run(["git", "show", f":{stage_n}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?")

def deep_ts(obj, best=None):
    # deep-scan all string values, keep max ts-shaped (with time-of-day, R350)
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        for m in TS_RE.finditer(obj):
            s = m.group(0)
            if best is None or s > best:
                best = s
    return best

def probe_json(raw):
    try:
        return deep_ts(json.loads(raw.decode("utf-8", errors="strict")))
    except Exception:
        return None

def probe_raw(raw):
    if raw is None:
        return None
    hits = TS_RE.findall(raw.decode("utf-8", errors="replace"))
    return max(hits) if hits else None

FACES = [
    ("docs/daily_report/REPORT-2026-09-30.json", "json"),
    ("docs/daily_report/REPORT-2026-09-30.md", "raw"),
    ("docs/live_usage/LIVE-2026-09-30.json", "json"),
    ("docs/live_usage/LIVE-2026-09-30.md", "raw"),
    ("docs/live_usage/LIVE-latest.json", "json"),
    ("docs/live_usage/LIVE-latest.md", "raw"),
    ("results/_attrition_guard_scan.json", "json"),
    ("results/dashboard_status.js", "raw"),
    ("results/dashboard_status.json", "json"),
    ("results/fundamental_b_layer_filter.json", "json"),
    ("results/futures_update_status.json", "json"),
    ("results/lhb_update_status.json", "json"),
    ("results/scorecard_v1.json", "json"),
    ("results/strategy_scorecard.json", "json"),
    ("results/token_usage.json", "json"),
    ("results/update_status.json", "json"),
]
for path, kind in FACES:
    b2, b3 = stage(2, path), stage(3, path)
    f = probe_json if kind == "json" else probe_raw
    t2, t3 = f(b2), f(b3)
    d = "SAME" if t2 == t3 else (":2(origin)" if (t2 or "") > (t3 or "") else ":3(mine)")
    print(f"{path} | :2={t2} | :3={t3} | newer={d}")

# marks jsonl: line counts + set diff
p = "results/paper/marks/marks-20260930.jsonl"
l2 = stage(2, p).decode("utf-8", errors="replace").splitlines()
l3 = stage(3, p).decode("utf-8", errors="replace").splitlines()
s2, s3 = set(l2), set(l3)
print(f"{p} | :2 lines={len(l2)} unique={len(s2)} | :3 lines={len(l3)} unique={len(s3)} | union={len(s2|s3)} | only2={len(s2-s3)} only3={len(s3-s2)}")
# compute_audit history sizes
for p in ["results/compute_audit.json", "results/regime_state.json"]:
    a = json.loads(stage(2, p).decode("utf-8")); b = json.loads(stage(3, p).decode("utf-8"))
    print(f"{p} | :2 hist={len(a.get('history') or [])} trans={len(a.get('transitions') or [])} | :3 hist={len(b.get('history') or [])} trans={len(b.get('transitions') or [])}")
