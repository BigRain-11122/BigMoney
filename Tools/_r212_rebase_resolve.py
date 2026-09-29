"""r212 rebase UU resolver probe + resolve (pit-93 canon three-face).

Union faces -> merge_lane_views resolve (recipe canon).
Snapshot/twin faces -> deep-ts probe take-newer; twins forced same side.
Rebase orientation (r351): :2: = base-side = origin, :3: = replay-side = ours.
"""
import subprocess
import sys
import os
import re
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

UNION = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]

# twin groups: resolve the leader by deep-ts, force followers to same side
TWIN_GROUPS = [
    ["docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"],
    ["docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md",
     "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"],
    ["results/dashboard_status.json", "results/dashboard_status.js"],
]

LONE_SNAPSHOTS = [
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]


def stage(stage_id, rel):
    r = subprocess.run(["git", "show", f":{stage_id}:{rel}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")


def deep_ts(txt):
    """Extract the freshest embedded timestamp from a face blob."""
    if txt is None:
        return None
    pats = [
        r'"(?:generated|updated|updated_at|ts|asof|written_at)"\s*:\s*"([^"]+)"',
    ]
    ts = []
    for p in pats:
        ts.extend(m.group(1) for m in re.finditer(p, txt))
    if not ts:
        ts.extend(m.group(0) for m in
                   re.finditer(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d",
                               txt[:4000]))
    ts = [t for t in ts if "20" in t]
    return max(ts) if ts else None


def take_side(rel, side):
    """Write stage blob of `side` (2 or 3) to the working tree file."""
    txt = stage(side, rel)
    assert txt is not None, f"no stage {side} for {rel}"
    with open(rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)
    print(f"  take :{side}: -> {rel}")


def resolve_snapshot(rel):
    a = stage(2, rel)
    b = stage(3, rel)
    ta, tb = deep_ts(a), deep_ts(b)
    print(f"[snapshot] {rel}\n  :2:origin ts={ta}\n  :3:replay ts={tb}")
    if ta is None and tb is None:
        raise SystemExit(f"no probe ts on either side for {rel} -- manual")
    if tb is not None and (ta is None or tb > ta):
        take_side(rel, 3)
        return 3
    if ta is not None and (tb is None or ta > tb):
        take_side(rel, 2)
        return 2
    # tie -> :2: canon (r140 tie takes HEAD; in rebase :2: = origin)
    print("  tie -> :2: origin (r140 canon)")
    take_side(rel, 2)
    return 2


def resolve_union(rel):
    import merge_lane_views as mlv
    stem = rel[len("results/"):-len(".json")]
    blobs = {}
    for key, sid in (("base_side", 2), ("replay_side", 3), ("base", 1)):
        txt = stage(sid, rel)
        if txt is not None:
            try:
                blobs[key] = json.loads(txt)
            except json.JSONDecodeError:
                pass
    merged, notes = mlv.resolve_face_from_blobs(stem, blobs)
    out = json.dumps(merged, ensure_ascii=False, indent=1,
                     sort_keys=False) + "\n"
    with open(rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print(f"[union] {rel}: {'; '.join(notes)}")


def main():
    for rel in UNION:
        resolve_union(rel)
    for group in TWIN_GROUPS:
        leader = group[0]
        side = resolve_snapshot(leader)
        for follower in group[1:]:
            take_side(follower, side)
    for rel in LONE_SNAPSHOTS:
        resolve_snapshot(rel)
    print("ALL-RESOLVED")


if __name__ == "__main__":
    main()
