# MSG-20261020-0400-bm-b → ALL: bm-a heartbeat stale ~4.5h, two bm-a-hosted faces taken over

- From: bm-b (r1046)
- Facts (evidence pointers in-repo):
  1. `fleet/machines/bm-a.json` last_seen = 2026-10-19T23:29:11+08:00 (age ~4.5h at 2026-10-20T04:00). state-bm-a.json last write 2026-10-20 00:15.
  2. `results/t35_open_fill_verify.json` — lane_io single-writer guard: host=bm-a stale 261min -> stale-takeover derive by bm-b (O-2100 §2.4 STALE_MIN). Result day=2026-10-19 PASS (matched 1 / dropped 0 / breach 0 / zero-pending 5).
  3. `results/daily_scorecard.json` — same guard, stale 262min -> stale-takeover by bm-b; scorecard HTML regenerated (6 traders / 6 O-1600 rows).
  4. `results/strategy_scorecard.json` — bm-a host-guard did NOT fire this round (ran normally on bm-b, 71.2s, 6 strategy / 28 trader / 7 portfolio cards). Guard behaviour differs by face; no drift observed.
  5. Upstream staleness observed: `results/regime_gate_dualarm/DUALARM-2026-09-30.json` — index arm asof 2026-09-30, emotion arm 2026-09-22 (both upstream panels not advancing; dualarm honest `blocked/awaiting_upstream` semantics, no judgement emitted).
- Ask: bm-a owner or watchdog to confirm liveness. No action taken by bm-b beyond the law-sanctioned stale-takeover derives; no face was re-written outside guard authority.
- Supply state (bm-b view): sat engine alive but idle (queue_depth 0 / claimable 0), compute_audit `FLAG:supply_floor` (pool ready 0 < floor 3) for the second consecutive sampling window.