# r963 resolver wave-2: fundamental_b_layer_filter snapshot + docs twin families (13-face second rebase)
import json, re, subprocess, sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def stage_blob(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        print(f"[FATAL] {path} :{stage}: missing"); sys.exit(2)
    return r.stdout

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values(): best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj: best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best: best = obj
    return best

# snapshot take-new
p = "results/fundamental_b_layer_filter.json"
b2, b3 = stage_blob(p, 2), stage_blob(p, 3)
t2, t3 = deep_ts(json.loads(b2)), deep_ts(json.loads(b3))
side = 3 if t3 > t2 else 2
picked = b3 if side == 3 else b2
json.loads(picked)
open(p, "wb").write(picked)
print(f"[take-new] {p}: :{side}: (origin={t2 or 'none'} vs replay={t3 or 'none'})")

# twins: REPORT pair + LIVE family (4 faces, single side decision on LIVE-2026-10-11)
def twin_pair(jp, mp, label):
    b2, b3 = stage_blob(jp, 2), stage_blob(jp, 3)
    t2, t3 = deep_ts(json.loads(b2)), deep_ts(json.loads(b3))
    side = 3 if t3 > t2 else 2
    jb = b3 if side == 3 else b2
    json.loads(jb)
    open(jp, "wb").write(jb)
    open(mp, "wb").write(stage_blob(mp, side))
    print(f"[twin] {label}: :{side}: (origin={t2 or 'none'} vs replay={t3 or 'none'})")

twin_pair("docs/daily_report/REPORT-2026-10-11.json", "docs/daily_report/REPORT-2026-10-11.md", "REPORT")
jp = "docs/live_usage/LIVE-2026-10-11.json"
b2, b3 = stage_blob(jp, 2), stage_blob(jp, 3)
t2, t3 = deep_ts(json.loads(b2)), deep_ts(json.loads(b3))
lside = 3 if t3 > t2 else 2
for q in ["docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    blob = stage_blob(q, lside)
    if q.endswith(".json"): json.loads(blob)
    open(q, "wb").write(blob)
print(f"[twin] LIVE family: :{lside}: (origin={t2 or 'none'} vs replay={t3 or 'none'})")
print("WAVE2 done")
