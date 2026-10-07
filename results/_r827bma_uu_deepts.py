# r827 deep-ts freshest-side resolver for snapshot/twin UU faces
# (r819/r825 lineage; rebase stage law r351: :2:=origin/base, :3:=replay/local)
import subprocess, re, sys, os

FACES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/pool_core_samples.jsonl",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

def blob(stage, rel):
    r = subprocess.run(["git", "show", f":{stage}:{rel}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def freshest_ts(raw):
    hits = TS_RE.findall(raw.decode("utf-8", "replace"))
    return max(hits) if hits else None

def resolve(rel, forced=None):
    b2, b3 = blob(2, rel), blob(3, rel)
    if b2 is None or b3 is None:
        print(f"SKIP {rel}: stage blob missing"); return None
    if b2 == b3:
        print(f"EQUAL {rel}: both sides identical -> keep :2:"); 
        open(rel, "wb").write(b2); return ":2:"
    t2, t3 = freshest_ts(b2), freshest_ts(b3)
    if forced:
        side = forced
    elif t2 and t3:
        side = ":2:" if t2 >= t3 else ":3:"
    elif t2: side = ":2:"
    elif t3: side = ":3:"
    else: side = ":2:"  # no ts anywhere: origin canon (r140)
    open(rel, "wb").write(b2 if side == ":2:" else b3)
    print(f"RESOLVED {rel}: origin_ts={t2} replay_ts={t3} -> {side}")
    return side

if __name__ == "__main__":
    forced = sys.argv[1] if len(sys.argv) > 1 else None
    for f in FACES:
        resolve(f, forced if forced != "auto" else None)
