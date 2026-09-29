# r424 bm-a push-storm probe: deep-scan ts in stage blobs (:2:=origin/bm-c, :3:=local/bm-a)
import subprocess, json, re

def stage(rel, n):
    raw = subprocess.run(["git", "show", f":{n}:{rel}"], capture_output=True).stdout
    return raw.decode("utf-8", "replace")

def deep_ts(obj, path="", out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "." + str(k)
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v):
                out.append((p, v))
            elif isinstance(v, (dict, list)):
                deep_ts(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            deep_ts(v, path + f"[{i}]", out)
    return out

FACES = [
    ("docs/daily_report/REPORT-2026-09-29.json", "json"),
    ("docs/live_usage/LIVE-2026-09-29.json", "json"),
    ("docs/live_usage/LIVE-latest.json", "json"),
    ("results/dashboard_status.json", "json"),
    ("results/scorecard_v1.json", "json"),
    ("results/strategy_scorecard.json", "json"),
    ("results/prospect_promotion/_summary.json", "json"),
]
for rel, kind in FACES:
    print("==", rel)
    for n, side in ((2, "origin/bm-c"), (3, "local/bm-a")):
        raw = stage(rel, n)
        try:
            d = json.loads(raw)
            ts = deep_ts(d)[:4]
            print(f"  :{n}: ({side})", ts if ts else "(no ts found)")
        except Exception as e:
            print(f"  :{n}: ({side}) PARSE-ERR {e} len={len(raw)}")
# dashboard_status.js: find embedded ts string
raw2 = stage("results/dashboard_status.js", 2)
raw3 = stage("results/dashboard_status.js", 3)
m2 = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", raw2)
m3 = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", raw3)
print("== dashboard_status.js  :2: ts:", m2[:3], " :3: ts:", m3[:3])
