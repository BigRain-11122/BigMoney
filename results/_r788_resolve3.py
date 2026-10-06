# r788 bm-b S0 rebase resolver v4 (2026-10-07) — third face: my r787 S6 absorb (b14dd8206) vs bm-c r643 tip
# Verified: :2 (origin) newer on every ts-carrying file (bm-c S6 ran 23:58-00:01 vs mine 23:52-23:55)
# Recipes (R440 two-way split + SKILL.md):
#   - S6 regenerable snapshots  : origin-newer-wins, ts-gated (assert ts2 > ts3 before take :2)
#   - no-ts regenerable (daily_scorecard, dashboard_status.json, LIVE-latest.md, dashboard_status.js,
#     post_review/REPORT-20261007.md AA): take :2 whole (regenerated every round; newer machine run)
#   - rolling ledgers (compute_audit history, regime_state transitions): union dedup + newest-cap + state :2
#   - append logs (post_review.jsonl, x2_watch_log.jsonl): 3-source union (:2 + :3 + worktree valid lines)
#   - CODELY.md: take :2 (post gate-repair skeleton; r786/r798 already flow-sunk by bm-c r643)
#               + insert my r787 entry before '### Reference' + archive zero-loss assertion
import json
import subprocess
import sys


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read :{n}:{path}")
    return r.stdout


def find_ts(d):
    if not isinstance(d, dict):
        return None
    for k in (
        "generated",
        "updated",
        "ts",
        "generated_from_state_updated",
    ):
        v = d.get(k)
        if isinstance(v, str) and ("2026-" in v or ":" in v):
            return v
    return None


report = []

# ---------- 1) ts-gated snapshot take-new (:2) ----------
TS_SNAPSHOTS = [
    "docs/live_usage/LIVE-latest.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in TS_SNAPSHOTS:
    a2, a3 = stage(2, p), stage(3, p)
    d2, d3 = json.loads(a2.decode("utf-8")), json.loads(a3.decode("utf-8"))
    t2, t3 = find_ts(d2), find_ts(d3)
    if t2 is None or t3 is None:
        report.append(f"RED no-ts {p} ({t2} vs {t3})")
        print("\n".join(report))
        sys.exit(2)
    if not (t2 >= t3):
        report.append(f"RED ts-not-newer {p}: :2={t2} :3={t3}")
        print("\n".join(report))
        sys.exit(2)
    open(p, "wb").write(a2)
    report.append(f"OK snap-take-:2 {p} ({t2} >= {t3})")

# ---------- 2) no-ts regenerable: take :2 whole ----------
WHOLE_TAKE2 = [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "docs/live_usage/LIVE-latest.md",
    "results/post_review/REPORT-20261007.md",
]
for p in WHOLE_TAKE2:
    a2 = stage(2, p)
    open(p, "wb").write(a2)
    report.append(f"OK whole-take-:2 {p} ({len(a2)}B)")

# ---------- 3) rolling ledgers ----------
# compute_audit: union history (dedup, ts-sorted, cap to max side len keep newest) + latest from :2
p = "results/compute_audit.json"
d2, d3 = json.loads(stage(2, p)), json.loads(stage(3, p))
h2, h3 = d2["history"], d3["history"]
seen = set()
union = []
for e in h2 + h3:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(e)
if all(isinstance(e, dict) and "ts" in e for e in union):
    union.sort(key=lambda e: str(e.get("ts", "")))
cap = max(len(h2), len(h3))
if len(union) > cap:
    union = union[-cap:]
merged = dict(d2)
merged["history"] = union
open(p, "w", encoding="utf-8", newline="").write(
    json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
)
report.append(f"OK ledger-union {p}: |:2|={len(h2)} |:3|={len(h3)} union={len(union)} cap={cap}")

# regime_state: take :2 state + union transitions with same cap rule
p = "results/regime_state.json"
d2, d3 = json.loads(stage(2, p)), json.loads(stage(3, p))
t2, t3 = d2.get("transitions", []), d3.get("transitions", [])
seen = set()
union = []
for e in t2 + t3:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(e)
cap = max(len(t2), len(t3))
if len(union) > cap:
    union = union[-cap:]
merged = dict(d2)
merged["transitions"] = union
open(p, "w", encoding="utf-8", newline="").write(
    json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
)
report.append(f"OK ledger-union {p}: |:2|={len(t2)} |:3|={len(t3)} union={len(union)} cap={cap}")

# ---------- 4) append logs: 3-source union ----------
for p in ["results/post_review.jsonl", "results/x2_watch_log.jsonl"]:
    l2 = stage(2, p).decode("utf-8").splitlines()
    l3 = stage(3, p).decode("utf-8").splitlines()
    lwt = [
        ln
        for ln in open(p, encoding="utf-8", errors="replace").read().splitlines()
        if ln.startswith("{") and ln.rstrip()
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

# ---------- 5) CODELY.md: :2 skeleton + r787 entry insert + archive zero-loss assertion ----------
p = "CODELY.md"
a2 = stage(2, p).decode("utf-8")
a3 = stage(3, p).decode("utf-8")
r787_line = next(
    (l for l in a3.splitlines() if l.startswith("- [2026-10-06 23:5x r787 bm-b]")), None
)
if r787_line is None:
    report.append("RED r787 entry not found in :3")
    print("\n".join(report))
    sys.exit(2)
r = subprocess.run(
    ["git", "show", "43b8ce97a:research/memory-archive/202610.md"], capture_output=True
)
if r.returncode != 0:
    report.append("RED cannot read archive at onto commit")
    print("\n".join(report))
    sys.exit(2)
arch = r.stdout.decode("utf-8")
needles = ["r786 bm-b", "r798 bm-a"]
missing = [n for n in needles if n not in arch]
if missing:
    report.append(f"RED archive zero-loss failed, missing {missing}")
    print("\n".join(report))
    sys.exit(2)
if r787_line in a2:
    report.append("OK codely r787 already present (no insert)")
    resolved = a2
else:
    lines = a2.splitlines()
    try:
        idx = lines.index("### Reference")
    except ValueError:
        report.append("RED '### Reference' anchor not found in :2")
        print("\n".join(report))
        sys.exit(2)
    lines.insert(idx, r787_line)
    resolved = "\n".join(lines) + ("\n" if a2.endswith("\n") else "")
open(p, "w", encoding="utf-8", newline="").write(resolved)
report.append("OK codely :2-skeleton + r787-insert + archive-assert-pass")

print("\n".join(report))
# ---------- post-write parse validation (r185) ----------
for q in TS_SNAPSHOTS + [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/compute_audit.json",
    "results/regime_state.json",
]:
    json.load(open(q, encoding="utf-8"))
print("PARSE-OK all json faces")
print("RESOLVE-OK third face written")
