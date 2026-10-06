# r788 bm-b S0 rebase resolver v3 (2026-10-07) — second replay conflict face (460847156 onto b14dd8206)
# Verified semantics (walk diffs recorded 2026-10-07):
#   - results/p1d_gates.json          : only /meta/date + /meta/elapsed_s run metadata differ
#                                       -> take-new by meta.date: :2 (00:10) > :3 (00:04)
#   - results/saturation_engine/state_bm-b.json / face_bm-b.json : daemon live snapshots,
#       worktree already healed by my daemon (ts 00:11:05 > :2 00:10:05 > :3 00:04:05)
#                                       -> ours-live-wins (keep worktree, verify parse+ts newest)
#   - results/saturation_engine/history_bm-b.jsonl : append-only ledger, both machines' engine
#       appends legitimate -> union :2 + :3 + worktree-valid-lines (markers stripped), zero loss
import json
import subprocess
import sys
import time


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read :{n}:{path}")
    return r.stdout


report = []

# 1) p1d_gates.json — take-new by meta.date
p = "results/p1d_gates.json"
a2, a3 = stage(2, p), stage(3, p)
d2, d3 = json.loads(a2.decode("utf-8")), json.loads(a3.decode("utf-8"))
if d2["meta"]["date"] > d3["meta"]["date"]:
    open(p, "wb").write(a2)
    report.append(f"OK take-new-by-meta.date {p} ({d2['meta']['date']} > {d3['meta']['date']})")
else:
    report.append(f"RED unexpected date order {p}")
    print("\n".join(report))
    sys.exit(2)

# 2) state/face — ours-live-wins (worktree = my daemon's live state)
for p in [
    "results/saturation_engine/state_bm-b.json",
    "results/saturation_engine/face_bm-b.json",
]:
    live = open(p, "rb").read()
    d_live = json.loads(live)  # parse-verify (daemon-healed)
    ts_live = d_live.get("ts") or (d_live.get("last_tick") or {}).get("ts")
    ts2 = None
    d2 = json.loads(stage(2, p))
    ts2 = d2.get("ts") or (d2.get("last_tick") or {}).get("ts")
    if ts_live and ts2 and ts_live >= ts2:
        report.append(f"OK ours-live-wins {p} (worktree {ts_live} >= origin {ts2})")
    else:
        # live not newer (or daemon not healed): fall back to newer blob
        open(p, "wb").write(stage(2, p))
        report.append(f"OK fallback-take-:2 {p} (live={ts_live} origin={ts2})")

# 3) history_bm-b.jsonl — union of :2 + :3 + worktree valid lines
p = "results/saturation_engine/history_bm-b.jsonl"
l2 = stage(2, p).decode("utf-8").splitlines()
l3 = stage(3, p).decode("utf-8").splitlines()
lwt = [
    ln
    for ln in open(p, encoding="utf-8", errors="replace").read().splitlines()
    if ln.startswith("{")
]
seen = set()
union = []
for src in (l2, l3, lwt):
    for ln in src:
        if ln not in seen:
            seen.add(ln)
            union.append(ln)
assert len(union) == len(set(l2) | set(l3) | set(lwt)), "union zero-loss assertion failed"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + "\n")
report.append(
    f"OK append-union-3src {p}: |:2|={len(l2)} |:3|={len(l3)} |wt-valid|={len(lwt)} union={len(union)}"
)

print("\n".join(report))
# post-write parse validation (r185 law)
json.load(open("results/p1d_gates.json", encoding="utf-8"))
json.load(open("results/saturation_engine/state_bm-b.json", encoding="utf-8"))
json.load(open("results/saturation_engine/face_bm-b.json", encoding="utf-8"))
print("PARSE-OK 3/3 json")
print("RESOLVE-OK second face written")
