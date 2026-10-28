# DIGEST 2026-10-29 · E205 — the first durable reader is a blocking event

Round r1233 (bm-b), dept: research + engineering.
Face: `results/e79/SIGNGROWTH-2026-10-27.json`, baseline
`results/e79/SIGNGROWTH-BASELINE.json`, code `scripts/e97_routing.py` mode `signgrowth`
(selftest 77 -> 87, smoke leg `product: e97 sign-growth gate`), method card E205.

## The trigger

E204 (r1232) published: 14 of 14 decomposition delta faces are `producer_only`, zero traps,
so E201's fourteen "write this line" items are prose hygiene rather than hazards. That is a
snapshot of one instant.

## What re-running the identical code found one round later

```
reader class                       published r1232     re-run r1233
producer_only                             14                    8
read_outside_the_producer                  0                    6
```

All six were read by exactly one file: `Tools/_r1232bmb_card.py` — the scratch script that
r1232 itself wrote to author its card. So the byte answer was correct when measured and stale
before the round ended, and the "reader" was never a consumer at all.

Two defects, one root: the reader class did not distinguish a durable consumer from a
round-local helper, and a single snapshot cannot see the crossing that matters.

## The fix

1. New reader class `read_by_a_round_scratch_script` for underscore-prefixed helpers
   (`Tools/_r*.py`, `_tmp_*.py`) — house convention for throwaway round scripts. Only a
   durable reader can make a silent face a trap (`durable_readers` / `scratch_readers` both
   published).
2. `signgrowth` gate: the current map is written once as an explicit baseline, then rc 3 on
   exactly two events — (a) a baseline face leaving a clean class for a durable external read
   while it still needs its sign line, (b) a face born already read by a durable consumer.
   Vanished faces are reported as `retired`, never failed.
3. The leg is wired into smoke (124/124) so the crossing actually fails the build.

## Current reading (seed state, honest)

- faces 14: 8 producer-only, 6 scratch-only, 0 durable external readers, 0 traps.
- baseline seeded at cutoff 2026-10-27; `crossings=0`, `born_traps=0`, `newly_declaring=0`,
  `retired=0`.
- The baseline is a ratchet, not a verdict: it blesses today's map including the 6 faces that
  only a throwaway script touches. A re-seed is a deliberate act (`--seed`).

## Limits (published in the face)

- in-repo reader scan only: prose, figures files and out-of-repo consumers are invisible.
- growth is detected between two runs; a reader added and removed inside one interval is lost.
- the scratch/durable split is a naming convention, not a semantic analysis: a durable file
  given an underscore name would be misclassed as scratch (`spec` says so).