# r817 bm-a rebase resolver (evidence retention per SKILL.md 三.5)
# Collision: bm-c r667 (09:44) vs bm-a r817 (10:00) same-window S6 regenerable faces.
# 14 UU total. Resolution:
#   - 6 ALL_FACES via scripts/merge_lane_views.py resolve (union recipe, parse-verified)
#     compute_audit / regime_state / update_status / lhb_update_status / futures_update_status / token_usage
#   - fundamental_b_layer_filter.json  : snapshot, deep-ts probe take-new (local 09:59:42 > origin 09:43:54)
#   - _attrition_guard_scan.json       : UNKNOWN->manual snapshot, deep-ts probe take-new (10:00:43 > 09:44:35)
#   - REPORT-2026-10-07 json/md twins   : ts-diffpick side-3 (10:00:09 > 09:44:17), md copied same-side bytes
#   - LIVE-2026-10-07 + LIVE-latest (json/md x4): family side-3 (10:00:11 > 09:44:18), all same side (r439)
# Sequencer env-rejection during continue (3x "You must edit all merge conflicts" with ls-files -u empty):
#   r808 three-step committed pick-2 (37d723304) but sequencer stuck at msgnum 2/3 -> r624 cure:
#   git rebase --quit + symbolic-ref self-check (detached confirmed) + git branch -f main 37d723304
#   + checkout main + churn-absorb tail commit (62bd2959b). No abort, no force-push, pure fast-forward.
# Delivery: push 4d342fd65..62bd2959b, rev-list both directions = 0.
