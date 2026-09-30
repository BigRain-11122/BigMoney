# r475 bm-a: rebase collision resolver (13 UU faces vs bm-c r272 + bm-a r465
# addenda landed mid-round). Canonical recipes per bigmoney-conflict-resolve
# SKILL: ALL_FACES via merge_lane_views resolve; marks line-union; twin-regen
# same-side ts-diffpick (json probe + md byte copy); snapshots take-new by
# staged-blob ts deep-probe; HANDOVER anchor-insert; _attrition_guard_scan
# manual-classified scan-evidence take-new.
import json
import re
import subprocess
import sys

sys.path.insert(0, ".")

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"no stage {stage} for {path}")
    return r.stdout.decode("utf-8", "replace")

def deep_ts(obj, best=""):
    """Recursively find the newest ISO-like ts string in any nested layer."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", obj):
        if obj > best:
            best = obj
    return best

log = {}

# ---- 1) ALL_FACES via merge_lane_views resolve CLI (canonical, no hand-union)
ALL_FACES = ["results/compute_audit.json", "results/regime_state.json",
             "results/update_status.json", "results/lhb_update_status.json",
             "results/futures_update_status.json", "results/token_usage.json"]
for p in ALL_FACES:
    r = subprocess.run([sys.executable, "scripts/merge_lane_views.py",
                        "resolve", p], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"MLV-RESOLVE FAIL {p}: {r.stdout[-300:]} {r.stderr[-300:]}")
        raise SystemExit(2)
    log[p] = "mlv-resolve OK: " + r.stdout.strip().splitlines()[-1][:80]

# ---- 2) marks jsonl: line-level union (append-log)
P_MARKS = "results/paper/marks/marks-20260930.jsonl"
ours = [l for l in blob(2, P_MARKS).splitlines() if l.strip()]
theirs = [l for l in blob(3, P_MARKS).splitlines() if l.strip()]
seen, union = set(), []
for line in ours + theirs:
    if line not in seen:
        seen.add(line)
        union.append(line)
union.sort(key=lambda l: (json.loads(l).get("ts", "") if l.startswith("{") else ""))
for l in union:
    json.loads(l)
with open(P_MARKS, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(union) + "\n")
log[P_MARKS] = f"union {len(ours)}+{len(theirs)}->{len(union)}"

# ---- 3) twin-regen faces: SAME side by generated ts (json probe; md copies)
def ts_of_json_text(t):
    return deep_ts(json.loads(t))

TWIN_GROUPS = [
    ("docs/daily_report/REPORT-2026-09-30", ["docs/daily_report/REPORT-2026-09-30.json",
                                             "docs/daily_report/REPORT-2026-09-30.md"]),
    ("docs/live_usage/LIVE-2026-09-30", ["docs/live_usage/LIVE-2026-09-30.json",
                                          "docs/live_usage/LIVE-2026-09-30.md"]),
    ("docs/live_usage/LIVE-latest", ["docs/live_usage/LIVE-latest.json",
                                     "docs/live_usage/LIVE-latest.md"]),
]
for name, paths in TWIN_GROUPS:
    jpath = paths[0]
    t2, t3 = ts_of_json_text(blob(2, jpath)), ts_of_json_text(blob(3, jpath))
    side = 3 if t3 >= t2 else 2   # same-second tie -> HEAD law: rebase ours=2 wins ties? r140: tie -> HEAD side = the base side (2)
    if t3 == t2:
        side = 2
    for p in paths:
        data = blob(side, p)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(data)
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8").read())
    log[name] = f"take-:2 origin" if side == 2 else f"take-:3 mine (ts {t2} vs {t3})"

# ---- 4) snapshot take-new by staged-blob deep ts
for p in ["results/fundamental_b_layer_filter.json",
          "results/_attrition_guard_scan.json"]:
    t2 = deep_ts(json.loads(blob(2, p)))
    t3 = deep_ts(json.loads(blob(3, p)))
    side = 3 if t3 > t2 else 2
    data = blob(side, p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    log[p] = f"take-:{side} (ts {t2} vs {t3})"

# ---- 5) HANDOVER anchor-insert: my r475 line goes at the very top of the
# origin side (origin already holds bm-a r465 + bm-c r270 entries below).
P_H = "research/HANDOVER.md"
base = blob(2, P_H)
mine = blob(3, P_H)
header = "# Bigmoney 交接与成果收割指南（HANDOVER）\n\n"
if not base.startswith(header) or not mine.startswith(header):
    raise RuntimeError("HANDOVER header prefix assertion failed")
base_rest = base[len(header):]
mine_rest = mine[len(header):]
my_line = mine_rest.split("\n", 1)[0]          # my new r475 entry line
if "round 475" not in my_line:
    raise RuntimeError("my HANDOVER first line is not the r475 entry")
merged = header + my_line + "\n" + base_rest
with open(P_H, "w", encoding="utf-8", newline="") as f:
    f.write(merged)
log[P_H] = f"anchor-insert mine-at-top ({len(my_line)}B line; base kept {len(base_rest)}B)"

print(json.dumps(log, ensure_ascii=False, indent=1))
