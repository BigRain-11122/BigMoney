# -*- coding: utf-8 -*-
"""r776 resolver: 13 take-ours faces + compute_audit history union.
Rebase semantics: --theirs = stage3 = OUR replayed commit (bm-a r776)."""
import json
import subprocess

TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/daily_report/REPORT-2026-10-06.md",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for f in TAKE_OURS:
    r = subprocess.run(["git", "checkout", "--theirs", f], capture_output=True)
    assert r.returncode == 0, (f, r.stderr.decode()[:200])
print("13 faces -> ours(bm-a) checked out")

# compute_audit.json: history ts-keyed union (r773 law), latest = ours
def blob(stage):
    r = subprocess.run(["git", "show", f":{stage}:results/compute_audit.json"],
                       capture_output=True)
    return json.loads(r.stdout)

o2, o3 = blob(2), blob(3)
h2, h3 = o2["history"], o3["history"]
by_ts = {}
for row in h2 + h3:
    by_ts[(row.get("ts"), row.get("machine"), len(by_ts))] = row
# ts-keyed dedup: same ts+machine = same row
seen = {}
for row in h2 + h3:
    key = (row.get("ts"), row.get("machine"))
    if key not in seen:
        seen[key] = row
merged = sorted(seen.values(), key=lambda r: str(r.get("ts")))
cap = max(len(h2), len(h3))
merged = merged[-cap:]
out = dict(o3)          # ours as base (latest newer)
out["history"] = merged
json.dump(out, open("results/compute_audit.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"compute_audit union: {len(h2)}+{len(h3)} -> {len(merged)} (cap {cap})")

# stage all 14
r = subprocess.run(["git", "add"] + TAKE_OURS + ["results/compute_audit.json"],
                   capture_output=True)
assert r.returncode == 0, r.stderr.decode()[:200]

# marker scan on staged blobs (r609 law three: independent scan, --check filtered)
MARKERS = (b"<<<<<<< ", b"=======", b">>>>>>>> ")
bad = []
r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                   capture_output=True)
for f in r.stdout.decode().splitlines():
    rb = subprocess.run(["git", "show", f":{f}"], capture_output=True)
    if any(m in rb.stdout for m in MARKERS):
        bad.append(f)
assert not bad, f"conflict markers in staged: {bad}"
print("marker scan: CLEAN")
