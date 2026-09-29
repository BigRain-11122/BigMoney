"""r238 bm-c rebase-collision resolver (14-UU vs origin/main bm-a r445 push).

Per r444 canon + bigmoney-conflict-resolve skill sec.2/3: twins same-side byte-copy,
snapshot deep-ts take-new (probe STAGED blobs :2:/:3:, tie -> :2: = onto side),
js-wrapper twin follows the .json side. A/B-family lane faces (compute_audit /
regime_state / update_status / lhb_update_status / futures_update_status /
token_usage) are resolved by scripts/merge_lane_views.py resolve (built-in recipes,
run separately). No CODELY/archive conflicts this round. Trail law: this script is
the evidence.
"""
import json, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}")
    return r.stdout

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEYP = ("generated", "updated", "asof", "ts", "lastseen", "cutoff", "timestamp")

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in KEYP) and WALL.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def probe(side, path):
    try:
        return deep_ts(json.loads(blob(f":{side}:{path}").decode("utf-8")))
    except Exception:
        return ""

def take(side, path):
    data = blob(f":{side}:{path}")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def resolve_snapshot(path):
    t2, t3 = probe("2", path), probe("3", path)
    side = "2" if t2 >= t3 else "3"
    n = take(side, path)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify
    print(f"[snapshot] {path}: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side} ({n}B)")

def resolve_twin(json_path, md_paths):
    t2, t3 = probe("2", json_path), probe("3", json_path)
    side = "2" if t2 >= t3 else "3"
    for p in [json_path] + md_paths:
        take(side, p)
    if json_path.endswith(".json"):
        json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"[twin] {json_path}+{len(md_paths)}md: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side}")

if __name__ == "__main__":
    for p in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
              "results/scorecard_v1.json", "results/strategy_scorecard.json"]:
        resolve_snapshot(p)
    resolve_twin("docs/daily_report/REPORT-2026-09-29.json", ["docs/daily_report/REPORT-2026-09-29.md"])
    resolve_twin("docs/live_usage/LIVE-2026-09-29.json", ["docs/live_usage/LIVE-2026-09-29.md"])
    resolve_twin("docs/live_usage/LIVE-latest.json", ["docs/live_usage/LIVE-latest.md"])
    # js-wrapper twin follows the .json side
    t2, t3 = probe("2", "results/dashboard_status.json"), probe("3", "results/dashboard_status.json")
    side = "2" if t2 >= t3 else "3"
    take(side, "results/dashboard_status.js")
    print(f"[js-twin] dashboard_status.js follows json side {side}")
    print("resolver done")
