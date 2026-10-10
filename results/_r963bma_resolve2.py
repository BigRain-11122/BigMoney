# r963 resolver: snapshot take-new (hardened deep-ts probe r100/R350) + twin-regen-md coupling + js-wrapper same-side byte-take
# Staged blobs only (:2:=origin/HEAD side, :3:=replay/ours side); tie -> :2: (r140 law)
import json, re, subprocess, sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def stage_blob(path, stage):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout

def deep_ts(obj, best=""):
    # R350: no key-EXCLUDE lists; value-shape adjudication only; wall-clock values require time-of-day
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best:
            best = obj
    return best

def take_new(path):
    b2, b3 = stage_blob(path, 2), stage_blob(path, 3)
    try:
        j2, j3 = json.loads(b2), json.loads(b3)
    except Exception as e:
        print(f"[FATAL] {path}: parse fail {e}"); sys.exit(2)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if t3 > t2 else 2  # tie -> :2: (r140)
    picked = b3 if side == 3 else b2
    json.loads(picked)  # parse-verify before write (r185)
    with open(path, "wb") as f:
        f.write(picked)
    print(f"[take-new] {path}: :{side}: picked (origin={t2 or 'none'} vs replay={t3 or 'none'})")
    return side

SNAPSHOTS = [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
sides = {}
for p in SNAPSHOTS:
    sides[p] = take_new(p)

# js-wrapper: whole-byte take from the SAME side as dashboard_status.json (twin coupling, R209: no json.dumps strip)
dash_side = sides["results/dashboard_status.json"]
js = "results/dashboard_status.js"
picked = stage_blob(js, dash_side)
with open(js, "wb") as f:
    f.write(picked)
print(f"[js-wrapper] {js}: byte-taken from :{dash_side}: (same side as dashboard_status.json)")

# twin-regen-md: json side by generated ts, md side = same-side blob byte copy (r327/r329: no hybrid twins)
def twin(json_path, md_path, label):
    b2, b3 = stage_blob(json_path, 2), stage_blob(json_path, 3)
    j2, j3 = json.loads(b2), json.loads(b3)
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if t3 > t2 else 2
    jb = b3 if side == 3 else b2
    json.loads(jb)
    mb = stage_blob(md_path, side)
    with open(json_path, "wb") as f: f.write(jb)
    with open(md_path, "wb") as f: f.write(mb)
    print(f"[twin] {label}: :{side}: picked (origin={t2 or 'none'} vs replay={t3 or 'none'}), json+md same-side")

twin("docs/daily_report/REPORT-2026-10-11.json", "docs/daily_report/REPORT-2026-10-11.md", "REPORT-2026-10-11")
# LIVE-latest faces mirror LIVE-2026-10-11 doc family -> decide on LIVE-2026-10-11, apply to all 4 faces
b2, b3 = stage_blob("docs/live_usage/LIVE-2026-10-11.json", 2), stage_blob("docs/live_usage/LIVE-2026-10-11.json", 3)
t2, t3 = deep_ts(json.loads(b2)), deep_ts(json.loads(b3))
lside = 3 if t3 > t2 else 2
for p in ["docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    picked = stage_blob(p, lside)
    if p.endswith(".json"):
        json.loads(picked)
    with open(p, "wb") as f: f.write(picked)
print(f"[twin] LIVE family: :{lside}: picked (origin={t2 or 'none'} vs replay={t3 or 'none'}), all 4 faces same-side")
print("ALL 13 resolved")
