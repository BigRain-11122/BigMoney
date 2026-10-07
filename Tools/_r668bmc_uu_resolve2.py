# -*- coding: utf-8 -*-
"""r668 bm-c rebase resolver v2: extract FULL side versions from the rebase
index stages (:2 = HEAD/origin-bm-a-r817, :3 = mine/36c67bb57), no hunk
parsing (v1 off-by-one self-pit: group(2)=merge-base not mine -- 17 faces
rewritten with stale base content, caught by compute_audit residue assert;
recovery = stage-extract + overwrite with correct winner side).
Rules: 17 ts-newer faces -> :3 (mine, verified newer per probe); compute_audit
-> latest ts-newer(mine) + history/samples row-union (r667/r528 precedent)."""
import io
import json
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = "K:/Fluxgroup/FluxGroup/quant/bigmoney/"
CREATE_NO_WINDOW = 0x08000000

TS_FILES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
CA = "results/compute_audit.json"


def stage(stage_no, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage_no, path)], cwd=ROOT,
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    assert r.returncode == 0, "stage %d read fail %s: %s" % (stage_no, path, r.stderr[:100])
    return r.stdout.decode("utf-8-sig", errors="replace") if r.stdout else ""


# sanity anchors before any write (r419 needle law)
probe = stage(2, "results/update_status.json")
assert '"updated": "2026-10-07 09:58:33"' in probe, "stage2 anchor (bm-a side ts) missing"
probe3 = stage(3, "results/update_status.json")
assert '"updated": "2026-10-07 09:59:32"' in probe3, "stage3 anchor (mine ts) missing"

for f in TS_FILES:
    mine = stage(3, f)
    assert mine, "empty stage3 %s" % f
    assert "<<<<<<<" not in mine, "marker in stage3 %s" % f
    if f.endswith(".json"):
        json.loads(mine)                     # strict reparse
    with open(ROOT + f, "wb") as fh:
        fh.write(mine.encode("utf-8"))
    print("RESOLVED v2 mine-side:", f)

head_j = json.loads(stage(2, CA))
mine_j = json.loads(stage(3, CA))


def union_rows(a, b):
    seen, out = set(), []
    for row in list(a) + list(b):
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


merged = dict(mine_j)
union_summary = {}
for key in ("history", "samples", "runs", "rows"):
    ha, mb = head_j.get(key), mine_j.get(key)
    if isinstance(ha, list) or isinstance(mb, list):
        ha, mb = ha or [], mb or []
        u = union_rows(ha, mb)
        merged[key] = u
        union_summary[key] = (len(ha), len(mb), len(u))
for key in head_j:
    if key not in merged:
        merged[key] = head_j[key]
json.dump({"head_latest_ts": head_j.get("latest", {}).get("ts"),
           "mine_latest_ts": mine_j.get("latest", {}).get("ts"),
           "union": union_summary,
           "note": "latest=ts-newer(mine); list fields row-union; head-only keys carried"},
          open(ROOT + "results/_r668bmc_ca_union_receipt.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
with open(ROOT + CA, "wb") as fh:
    fh.write(json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8"))
print("RESOLVED v2 compute_audit:", union_summary,
      "latest head=%s mine=%s -> mine" % (head_j.get("latest", {}).get("ts"), mine_j.get("latest", {}).get("ts")))
print("ALL RESOLVED V2")
