# r427 bm-a push-storm wave-2 resolver (rebase replay of round-427 commit, 31 UU)
# Pairs/snapshots via hardened deep-ts probe on STAGED blobs (:2:=origin, :3:=local commit);
# x2_watch_log.jsonl = multiset line union (r426 pattern). ALL_FACES handled by merge_lane_views separately.
import subprocess, json, sys
from collections import Counter

TS_RX = __import__('re').compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

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

def resolve_json_take_new(path):
    b2, b3 = blob(2, path), blob(3, path)
    if b2 is None and b3 is None:
        print(f"[FAIL] {path}"); return None
    p2 = deep_ts(json.loads(b2))[0] if b2 else ""
    p3 = deep_ts(json.loads(b3))[0] if b3 else ""
    stage = 2 if (not p3 or p2 >= p3) else 3   # tie -> :2: origin (r140)
    json.loads(blob(stage, path))
    with open(path, "wb") as f:
        f.write(blob(stage, path))
    print(f"[take-new] {path}: :{stage}: origin={p2} local={p3}")
    return stage

def resolve_twin(jp, bp):
    s = resolve_json_take_new(jp)
    if s is None:
        return
    b = blob(s, bp)
    if b is None:
        print(f"[FAIL-twin] {bp}"); return
    with open(bp, "wb") as f:
        f.write(b)
    print(f"[twin-copy] {bp}: whole-bytes :{s}:")

def union_jsonl(path):
    b2, b3 = blob(2, path), blob(3, path)
    l2 = b2.decode('utf-8').splitlines() if b2 else []
    l3 = b3.decode('utf-8').splitlines() if b3 else []
    # r426 law: multiset UNION (common lines once) = Counter | Counter (max), NOT + (sum)
    cnt = Counter(l2) | Counter(l3)
    out = sorted(cnt.elements())
    assert len(out) == len(l2) + len(l3) - sum((Counter(l2) & Counter(l3)).values()), \
        f"multiset-union mismatch {len(out)}"
    with open(path, "wb") as f:
        f.write(("\n".join(out) + "\n").encode('utf-8'))
    print(f"[union] {path}: {len(l2)}+{len(l3)} -> {len(out)} multiset-verified")

if __name__ == "__main__":
    PAIRS = [
        ("results/dashboard_status.json", "results/dashboard_status.js"),
        ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
        ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
        ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
    ]
    SNAPS = [
        "results/scorecard_v1.json", "results/strategy_scorecard.json",
        "results/fundamental_b_layer_filter.json", "results/daily_scorecard.json",
        "results/t35_open_fill_verify.json",
        "results/paper_export/export-2026-09-28.json", "results/paper_export/latest.json",
        "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
        "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
        "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
        "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
    ]
    for jp, bp in PAIRS:
        resolve_twin(jp, bp)
    for p in SNAPS:
        resolve_json_take_new(p)
    union_jsonl("results/x2_watch_log.jsonl")
    ok = True
    for p in [x for pair in PAIRS for x in pair] + SNAPS:
        if p.endswith(".json"):
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:
                ok = False
                print(f"[VERIFY-FAIL] {p}: {e}")
    print("ALL-PARSE-OK" if ok else "VERIFY-FAILURES")
    sys.exit(0 if ok else 2)
