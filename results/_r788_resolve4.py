# r788 bm-b S0 rebase resolver v5 (2026-10-07) — fourth face: churn-absorb commit (d20ae5ace) replay
# 5 UU: my-lane daemon live snapshots (state/face bm-b -> ours-live-wins, ts-gated),
#       my-lane history + shared pool nulls.jsonl x2 (append-only -> 3-source union).
import json
import subprocess
import sys


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read :{n}:{path}")
    return r.stdout


report = []

# 1) state/face: ours-live-wins (worktree = my daemon live state)
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
        report.append(f"OK ours-live-wins {p} (live {ts_live} >= origin {ts2})")
    else:
        open(p, "wb").write(stage(2, p))
        report.append(f"OK fallback-take-:2 {p} (live={ts_live} origin={ts2})")

# 2) append-logs: 3-source union
for p in [
    "results/saturation_engine/history_bm-b.jsonl",
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/fund_quality_p1/nulls.jsonl",
]:
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
    assert len(union) == len(set(l2) | set(l3) | set(lwt)), f"union zero-loss failed {p}"
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(union) + "\n")
    report.append(
        f"OK append-union-3src {p}: |:2|={len(l2)} |:3|={len(l3)} |wt|={len(lwt)} union={len(union)}"
    )

print("\n".join(report))
json.load(open("results/saturation_engine/state_bm-b.json", encoding="utf-8"))
json.load(open("results/saturation_engine/face_bm-b.json", encoding="utf-8"))
print("PARSE-OK 2/2 live snapshots")
print("RESOLVE-OK fourth face written")
