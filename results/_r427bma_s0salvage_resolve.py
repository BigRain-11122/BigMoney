"""r427 bm-a S0 salvage conflict resolver (stash-pop 17-UU batch, non-ALL_FACES legs).

Canon: bigmoney-conflict-resolve SKILL.md
- twin-regen (REPORT/LIVE json+md, dashboard json+js): probe deep-ts on STAGED blobs
  (:2:=origin/HEAD side, :3:=stash/crashed-round side) -> SAME side whole-bytes both faces
  (md/js never re-serialized; r329 md-not-json law; R209 js-wrapper law)
- snapshot (scorecard_v1 / strategy_scorecard / fundamental_b_layer_filter): take-new via
  hardened deep-ts probe (r100: key normalized strip '_-'; R350: no key-exclude lists,
  wall-clock values require time-of-day; probe STAGED blob not working tree)
- tie -> :2: (HEAD/origin, r140 same-second law)
Audit: prints per-file decision + probe evidence; parse-verify before write.
"""
import subprocess, json, re, sys

TS_RX = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def deep_ts(obj, best=("", "")):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RX.match(v):
                if v > best[0]:
                    best = (v, str(k))
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best

def probe_side(stage, path):
    b = blob(stage, path)
    if b is None:
        return None, None
    d = json.loads(b)
    ts, key = deep_ts(d)
    return (ts, key), d

def resolve_json_take_new(path):
    p2, d2 = probe_side(2, path)
    p3, d3 = probe_side(3, path)
    if p2 is None and p3 is None:
        print(f"[FAIL] {path}: neither side readable"); return None
    if p3 is None or (p2 and p2[0] >= p3[0]):   # tie -> :2: (r140)
        side, rev = p2, 2
    else:
        side, rev = p3, 3
    b = blob(rev, path)
    json.loads(b)  # parse-verify staged bytes before write
    with open(path, "wb") as f:
        f.write(b)
    print(f"[take-new] {path}: side=:{rev}: origin_ts={p2} stash_ts={p3}")
    return rev

def resolve_twin(json_path, byte_path):
    rev = resolve_json_take_new(json_path)
    if rev is None:
        print(f"[SKIP-twin] {byte_path}: json side undetermined"); return
    b = blob(rev, byte_path)
    if b is None:
        print(f"[FAIL] {byte_path}: staged blob missing on :{rev}:"); return
    with open(byte_path, "wb") as f:
        f.write(b)
    print(f"[twin-copy] {byte_path}: whole-bytes from :{rev}: (same-side law)")

PAIRS = [
    ("results/dashboard_status.json", "results/dashboard_status.js"),
    ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
    ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
SNAPSHOTS = [
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
]

if __name__ == "__main__":
    for jp, bp in PAIRS:
        resolve_twin(jp, bp)
    for p in SNAPSHOTS:
        resolve_json_take_new(p)
    # final parse-verify all written faces
    ok = True
    for p in [x for pair in PAIRS for x in pair] + SNAPSHOTS:
        try:
            if p.endswith(".json"):
                json.load(open(p, encoding="utf-8"))
        except Exception as e:
            ok = False
            print(f"[VERIFY-FAIL] {p}: {e}")
    print("ALL-PARSE-OK" if ok else "VERIFY-FAILURES")
    sys.exit(0 if ok else 2)
