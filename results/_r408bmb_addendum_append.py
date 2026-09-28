import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
line = (
 "2026-09-29T04:2x | r408 bm-b addendum | push-time origin movement (bm-c r197 x3 landed during-round: dispatcher preflight + r197 main [T-116 dualrun quota MET streak 3/3 + orders_diff v2 fix] + r197 addendum) -> first push rejected -> rebase hit 28-UU same-window S6 twins -> "
 "classifier 26 classified + 2 UNKNOWN (live_usage LIVE twins manual-classified snapshot same-day idempotent regen, r404 precedent) -> "
 "resolver _r408bmb_resolve.py direction-agnostic take-NEW (pit-law 75/76: probe BOTH stages, newer wins, tie->stage2; rebase stage-inversion noted stage2=bm-c base stage3=mine replay) -> "
 "unions zero-loss: compute_audit history 167+168->169 (state take-NEW mine 04:10:39 vs 04:01:04), regime_state 2+2->2, x2_watch_log SUPERSET 1506 verbatim + 6 l3-new -> 1512 (intra-side multiplicity preserved; first-run count-based assert false-red caught by assert -> superset law, pit-law batch-82 to CODELY) -> "
 "24 snapshot faces all take-NEW stage3 (mine 04:10-04:11 vs bm-c 04:01, twins REPORT/LIVE both took same side via single json probe) + dashboard_status.js wrapper preserved raw-bytes R209 -> "
 "rebase continue hit dumb-terminal GIT_EDITOR unset -> $env:GIT_EDITOR='true' override -> push LANDED 89668ed85 (1afe7c379..89668ed85) | "
 "evidence: resolver output 26 rows + union assertions + push receipt | next: astock repull ~04:30 -> rev_osc unlock next round S6; T-116 flip gate waits 3-machine streak (bm-c 3/3, bm-b 1/3) [r408 bm-b addendum]"
)
with open(r'logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as fh:
    fh.write(line + '\n')
print('addendum line appended, %d chars' % len(line))
