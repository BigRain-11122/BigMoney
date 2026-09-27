"""r121 bm-c rebase-conflict resolver (r120/r344/r360/r366 canon).
16 UU faces vs bm-a same-window S6 double-run + T-95 landing:
  - compute_audit.json: rolling history, identity key = ts (r120 frozen
    convention; rows carry no machine field), collision -> new side (mine,
    r366 new-side-wins), scalars = newer top-level ts side.
  - regime_state.json: rolling history, identity key = asof (r366), same
    collision rule, scalars = newer updated side.
  - other 14 = derived snapshot faces -> git checkout --ours (origin side;
    S6 re-derives next round).
Zero-loss asserted: |A u B| == distinct identities, no cap (r360 law).
"""
import json
import subprocess
import sys

UNION_FILES = {
    "results/compute_audit.json": ("history", "ts", "ts", 4),
    "results/regime_state.json": ("history", "asof", "updated", 2),
}
OURS_FILES = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def stage_blob(path, n):
    out = subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                         capture_output=True, check=True).stdout
    return json.loads(out.decode("utf-8-sig"))


for path, (hist_key, ident, scalar_ts, indent) in UNION_FILES.items():
    orig = stage_blob(path, 2)   # HEAD during rebase = origin side
    mine = stage_blob(path, 3)   # replayed commit = my side

    def _scalar(d):
        # compute_audit nests the fresh face under "latest" (ts inside);
        # regime_state carries "updated" at top level.
        if scalar_ts in d:
            return d[scalar_ts]
        return d["latest"][scalar_ts]

    om = {r[ident]: r for r in orig[hist_key]}
    mm = {r[ident]: r for r in mine[hist_key]}
    union = dict(om)
    for k, v in mm.items():
        union[k] = v                       # collision -> new side wins
    merged = [union[k] for k in sorted(union.keys())]
    src = mine if _scalar(mine) > _scalar(orig) else orig
    assert len(merged) == len(set(om) | set(mm)), "union count mismatch"
    out = dict(src)
    out[hist_key] = merged
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")
    print("%s: origin %d | mine %d -> union %d (scalar from %s side, zero-loss ok)"
          % (path, len(om), len(mm), len(merged),
             "mine" if src is mine else "origin"))

for path in OURS_FILES:
    subprocess.run(["git", "checkout", "--ours", "--", path], check=True)
    subprocess.run(["git", "add", "--", path], check=True)
    raw = open(path, "rb").read()
    assert b"<<<<<<<" not in raw and b"=======" not in raw, "marker left in " + path
    print("take-origin: %s (marker-free)" % path)

print("resolver done: 2 union + 14 take-origin, all marker-free")
