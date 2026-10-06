# r788 bm-b S0 rebase resolver v5 (2026-10-07) — fifth face: final churn-absorb (39a0f40c2) replay
# Roles reversed: :2 (a0015f538 tree) now newer than :3 for lane snapshots.
#   - p1d_gates.json       : take-new by meta.date (either side may be newer)
#   - state/face bm-b      : ours-live-wins (my daemon live state is freshest of all)
#   - history_bm-b.jsonl   : 3-source union (idempotent superset)
import json
import subprocess
import sys


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read :{n}:{path}")
    return r.stdout


report = []

# 1) p1d_gates: take-new by meta.date
p = "results/p1d_gates.json"
a2, a3 = stage(2, p), stage(3, p)
d2, d3 = json.loads(a2.decode("utf-8")), json.loads(a3.decode("utf-8"))
if d2["meta"]["date"] >= d3["meta"]["date"]:
    open(p, "wb").write(a2)
    report.append(f"OK take-:2 {p} ({d2['meta']['date']} >= {d3['meta']['date']})")
else:
    open(p, "wb").write(a3)
    report.append(f"OK take-:3 {p} ({d3['meta']['date']} > {d2['meta']['date']})")

# 2) state/face: ours-live-wins
for p in [
    "results/saturation_engine/state_bm-b.json",
    "results/saturation_engine/face_bm-b.json",
]:
    live = open(p, "rb").read()
    d_live = json.loads(live)
    ts_live = d_live.get("ts") or (d_live.get("last_tick") or {}).get("ts")
    d2 = json.loads(stage(2, p))
    ts2 = d2.get("ts") or (d2.get("last_tick") or {}).get("ts")
    if ts_live and ts2 and ts_live >= ts2:
        report.append(f"OK ours-live-wins {p} (live {ts_live} >= :2 {ts2})")
    else:
        open(p, "wb").write(stage(2, p))
        report.append(f"OK fallback-take-:2 {p} (live={ts_live} :2={ts2})")

# 3) history: 3-source union
p = "results/saturation_engine/history_bm-b.jsonl"
l2 = stage(2, p).decode("utf-8").splitlines()
l3 = stage(3, p).decode("utf-8").splitlines()
lwt = [
    ln
    for ln in open(p, encoding="utf-8", errors="replace").read().splitlines()
    if ln.startswith("{") and ln.strip()
]
seen = set()
union = []
for src in (l2, l3, lwt):
    for ln in src:
        if ln not in seen:
            seen.add(ln)
            union.append(ln)
assert len(union) == len(set(l2) | set(l3) | set(lwt)), "union zero-loss failed"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + "\n")
report.append(
    f"OK append-union-3src {p}: |:2|={len(l2)} |:3|={len(l3)} |wt|={len(lwt)} union={len(union)}"
)

print("\n".join(report))
json.load(open("results/p1d_gates.json", encoding="utf-8"))
json.load(open("results/saturation_engine/state_bm-b.json", encoding="utf-8"))
json.load(open("results/saturation_engine/face_bm-b.json", encoding="utf-8"))
print("PARSE-OK 3/3")
print("RESOLVE-OK fifth face written")
