"""r668 bm-a merge UU resolver (22 faces, r652/r656/r139 recipe).

Orientation: MERGE in progress -> HEAD = ours (local), MERGE_HEAD = theirs
(origin). Registered faces (7) go through merge_lane_views resolve with the
r351 mapping the tool expects: --stage2 = ORIGIN side blob, --stage3 =
LOCAL side blob. Out-of-registry faces (15): take-newer by the ts census
(r668 _r668bma_ts_census.py: HEAD strictly newer on every face), twins
byte-copied from the json side's decision, all writes RAW BYTES verbatim
(r509 law: no re-serialization on take-side faces)."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTERED = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
]
MANUAL_TAKE_MINE = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]


def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"git show {ref}:{path} failed"
    return r.stdout


def resolve_registered(path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f2, \
            tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f3:
        f2.write(blob("MERGE_HEAD", path))   # origin side -> --stage2 (r351)
        f3.write(blob("HEAD", path))          # local side  -> --stage3
        p2, p3 = f2.name, f3.name
    try:
        r = subprocess.run(
            [sys.executable, "scripts/merge_lane_views.py", "resolve", path,
             "--stage2", p2, "--stage3", p3],
            capture_output=True, cwd=ROOT)
        out = r.stdout.decode("utf-8", "replace")
        assert r.returncode == 0, f"resolve {path} rc={r.returncode}: {out[-400:]}"
        print(f"[registered] {path}: {out.strip().splitlines()[0][:120]}")
    finally:
        os.unlink(p2)
        os.unlink(p3)


def take_mine(path):
    raw = blob("HEAD", path)
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
    open(os.path.join(ROOT, os.path.normpath(path)), "wb").write(raw)
    print(f"[take-mine] {path}: {len(raw)}B verbatim (HEAD newer per census)")


def main():
    for p in REGISTERED:
        resolve_registered(p)
    for p in MANUAL_TAKE_MINE:
        take_mine(p)
    # post gates: parse every json face + marker sweep + pool entry survival
    all_faces = REGISTERED + MANUAL_TAKE_MINE
    for p in all_faces:
        if p.endswith(".json"):
            json.load(open(os.path.join(ROOT, os.path.normpath(p)),
                           encoding="utf-8"))
    pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"),
                          encoding="utf-8"))
    ids = {e.get("id") for e in pool["entries"]}
    assert "THEME-JUDGE-P1" in ids, "pool union lost THEME-JUDGE-P1 entry!"
    tj = [e for e in pool["entries"] if e.get("id") == "THEME-JUDGE-P1"][0]
    q = [e for e in pool["entries"] if e.get("id") == "FUND-QUALITY-P1-NULLS"][0]
    print(json.dumps({
        "pool_entries": len(pool["entries"]),
        "theme_judge_shard": {k: tj["shards"][0].get(k)
                              for k in ("status", "owner", "owner_since")},
        "quality_shard": {k: q["shards"][0].get(k)
                          for k in ("status", "owner", "owner_since")},
    }, ensure_ascii=False))
    for p in all_faces:
        raw = open(os.path.join(ROOT, os.path.normpath(p)), "rb").read()
        assert b"<<<<<<<" not in raw, f"marker leak in {p}"
    print(f"resolver: {len(all_faces)} faces done, parse+marker gates PASS")


if __name__ == "__main__":
    sys.exit(main())
