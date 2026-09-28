"""r393 resolve #9: five files whose :2: stage blob is ITSELF poisoned
(marker text committed into the 4/6 intermediate replay). Recovery: read
the CLEAN upstream tip (origin/main) as the 'ours' side, combine with :3:
(my part-1 clean latest). Zero-loss ledger union preserved via origin/main.
"""
import json
import re
import subprocess

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def bb(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"],
                           capture_output=True).stdout


def bj(rev, path):
    return json.loads(bb(rev, path))


def probe(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = probe(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe(v, best)
    elif isinstance(obj, str) and TS_SHAPE.match(obj):
        best = max(best, obj)
    return best


def union_rows(ha, hb):
    seen, union = set(), []
    for row in ha + hb:
        k = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            union.append(row)
    union.sort(key=lambda r: r.get("ts", r.get("date", "")))
    return union


log = []

# ---- compute_audit: union mine(:3) + origin/main histories ---------------
P = "results/compute_audit.json"
A, B = bj("origin/main", P), bj(":3", P)
union = union_rows(A.get("history", []), B.get("history", []))
la = (A.get("latest") or {}).get("ts") or ""
lb = (B.get("latest") or {}).get("ts") or ""
merged = {"history": union, "latest": (A if lb <= la else B).get("latest")}
json.loads(json.dumps(merged))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
log.append(f"compute_audit: union {len(A['history'])}+{len(B['history'])}"
           f"->{len(union)} latest={max(la, lb)}")

# ---- regime_state: union + state take-new ---------------------------------
P = "results/regime_state.json"
A, B = bj("origin/main", P), bj(":3", P)
merged = {}
for key in ("history", "transitions"):
    if key in A or key in B:
        merged[key] = union_rows(A.get(key, []), B.get(key, []))
state_side = A if probe(B) <= probe(A) else B
for k, v in state_side.items():
    if k not in merged:
        merged[k] = v
json.loads(json.dumps(merged))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
log.append("regime_state: union + state take-new "
           f"{'origin' if state_side is A else 'mine'}")

# ---- snapshots: take-new between origin/main and mine(:3) -----------------
for P in ["results/token_usage.json", "results/update_status.json",
          "docs/live_usage/LIVE-2026-09-28.json"]:
    a, b = bj("origin/main", P), bj(":3", P)
    ta, tb = probe(a), probe(b)
    pick = a if tb <= ta else b
    json.loads(json.dumps(pick))
    open(P, "w", encoding="utf-8").write(json.dumps(
        pick, ensure_ascii=False, indent=1))
    log.append(f"{P}: take-{'origin' if pick is a else 'mine'}"
                f" ({ta or '-'} vs {tb or '-'})")

# live_usage md twin follows its json pick side
P = "docs/live_usage/LIVE-2026-09-28.json"
a, b = bj("origin/main", P), bj(":3", P)
side = "origin/main" if probe(b) <= probe(a) else ":3"
open("docs/live_usage/LIVE-2026-09-28.md", "wb").write(
    bb(side, "docs/live_usage/LIVE-2026-09-28.md"))
log.append(f"live_usage md twin <- {side}")

# ---- final zero-marker + parse assertion over all 15 stop files ----------
FILES = [
    "docs/daily_report/REPORT-2026-09-28.json", "docs/daily_report/REPORT-2026-09-28.md",
    "docs/live_usage/LIVE-2026-09-28.json", "docs/live_usage/LIVE-2026-09-28.md",
    "results/compute_audit.json", "results/dashboard_status.js",
    "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json", "results/prospect_promotion/_summary.json",
    "results/regime_state.json", "results/scorecard_v1.json",
    "results/strategy_scorecard.json", "results/token_usage.json",
    "results/update_status.json",
]
bad = []
for f in FILES:
    txt = open(f, "rb").read().decode("utf-8", errors="replace")
    if txt.lstrip().startswith("<<<<<<<") or "\n<<<<<<< " in txt \
            or "\n>>>>>>> " in txt:
        bad.append(f + ":MARKERS")
    elif f.endswith(".json"):
        try:
            json.loads(txt)
        except Exception as e:
            bad.append(f + f":PARSE:{e}")
for d in log:
    print(" ", d)
print("FINAL CHECK:", "PASS all 15 clean+parse" if not bad else f"FAIL {bad}")
raise SystemExit(1 if bad else 0)
