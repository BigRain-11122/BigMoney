import io

line = (
    "2026-09-30T17:1x+08:00 | r481 push-log addendum | "
    "D-15: push first-reject (bm-b r471 W14 FREEZE landed mid-round 16:49) -> runtime-state commit (autofill writer in-flight, r277 law) -> pull --rebase 14-UU storm (all shared S6 regen faces) -> "
    "classifier 13 classified + 1 UNKNOWN (fail-closed): 6 ALL_FACES via merge_lane_views resolve (compute_audit history union 203 rows parse-verified / regime_state triggers+history union / futures+lhb+token+update_status max-cutoff take-new all from :3:) + "
    "3 twin pairs (REPORT-20260930 / LIVE-20260930 / LIVE-latest: json generated_ts deep-probe -> all mine-newer 16:54:41-42 vs 16:51:03-04 -> md byte-copy SAME side, r327/r329 law) + "
    "2 snapshots (fundamental_b_layer_filter updated-ts mine-newer 16:53:30 vs 16:50:59; _attrition_guard_scan UNKNOWN -> manual classify = snapshot, top-level ts probe 16:58:02 vs 16:52:21 mine-newer confirmed) -> "
    "rebase --continue clean (GIT_EDITOR=true r356) -> post-resolve reconcile: 12 faces ZERO-DRIFT, 2 drift recorded as-is per law (compute_audit = bm-b lane rows 16:09/16:29 pending shared settle, producer-window r85 + 1 historical lane-mirror gap, my union = strict superset of both 201-row parents zero-loss; gate_attrition = pre-existing lane-mirror lag, 9 old judged batches in lane files absent from shared view, not touched this round, guard scan CLEAN, D-03 full-diff gate applies only before pool flip = none during RW-5 freeze) -> push landed [via bm-a]\n"
)

with io.open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)

t = io.open('round_reports-bm-a.md', encoding='utf-8').read()
assert 'r481 push-log addendum' in t.splitlines()[-1]
print('addendum appended, total lines:', len(t.splitlines()))
