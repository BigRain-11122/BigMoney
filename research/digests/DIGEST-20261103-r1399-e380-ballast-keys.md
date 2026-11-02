# DIGEST 2026-11-03 r1399 (bm-b) -- E380: the unwritten counter has two terms

Card: `knowledge/METHODOLOGY_ASSETS.md` E380. Face: `results/state_tilt/BALLASTKEYS-2026-11-03.json`
(+ `ballastkeys_latest.json`). Script: `scripts/e380_ballast_keys_and_readers.py` (selftest 13/13,
verify problems=[]). Smoke leg: `scripts/run_e380_smoke_leg.py` (1/1, execs the suite's block verbatim).

## What the window found

The 04:20 window claimed E380, drafted the script and published a face, then died without a closeout.
This window inherited the products (r1005 dead-window rule), re-derived them, and repaired two
things the draft had left open:

1. **The unaccounted key.** The draft published `delta_fields_with_no_writer 25` against
   `new_keys_without_a_writer 26` and wrote "1 key(s) unaccounted". The counter has a second term:
   a store member that writes an *old* unwritten cell lowers it. Measured exactly one such write --
   `Tools/_r1234bmb_pool.py` writing `results/runnable_pool.json::entries` -- so 25 = 26 - 1 and the
   face now publishes the closing cell by name instead of a gap sentence. A per-key predicate audit
   over all 42 added keys found 0 disagreements with the write set the arm actually used.
2. **A stale replay number.** The draft face printed E378's guard headline as 230 (published 131) and
   `equal: false`. That number was written before the script's own fix landed at 05:38: the code on
   disk reproduces 131/2306/1712 exactly. The face now carries `equal: true` and the smoke leg refuses
   an arm that does not reproduce the published headline.

## Readings

42 new (face, field) cells from 19 store members: read by two or more members 5 (3 with no writer),
read by one member 37 (23 with no writer, 14 with), written at all 16 of which 3 are written by a pin
source that never reads them. The five shared keys are `bm-b.json::{heartbeat_epoch_utc, round_no}`,
`state-bm-b.json::{last_decisions_sha, r1334, round_no}` -- the round-closeout scripts reading each
other's heartbeat/state fields. So the "channel between files no commit holds" that gives this study
its verdict is the closeout machinery, not a payload contract: 88% of the added keys are read by the
single member that also adds them.

## Rules worth carrying

- An "unwritten field" delta is `+new unwritten keys -old unwritten cells a store writer closes`. A
  face that publishes only the first term produces a permanent unexplained off-by-N.
- A number quoted from an upstream face must be recomputed in the quoting face and published with an
  equality flag; a stale draft can disagree with its own script and nothing catches it but a leg.
- 42 added keys moving a counter is not 42 keys in use: the reader axis has to be published next to
  the writer axis or the count reads as usefulness.