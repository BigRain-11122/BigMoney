# DIGEST 2026-10-30 r1353 bm-c — the buffer axis has ends now, and neither end moves the answer

## What was asked

r1352 closed the buffer family on three arms that all sat **inside** their own cell bands
(k=0.05 −0.030pp, k=0.10 +0.072pp, k=0.20 +0.138pp median per-cell vs the 10bp/k=0 baseline) and
stocked three follow-up rows rather than leaving "small k might work" standing. This window
ignited those rows and read them back through the same frozen rule (`judge()` in
`scripts/etf_book_phase_atlas_arms.py`, unchanged constants).

## What the three arms say

Each arm is 280 engine runs (12 cells × every decision origin of one rebalance cycle), 8% vol
target, 2026-10-29 bar, 10bp/side unless stated.

| arm | knob | median per-cell Δ | not-worse share | cells clearing own band | label |
|---|---|---|---|---|---|
| buffer_k02 | k=0.02 | **−0.018pp** | 0.917 | 0/12 | NOT-SEPARABLE |
| buffer_k05 | k=0.05 | −0.030pp | 0.667 | 0/12 | REJECT |
| buffer_k10 | k=0.10 | +0.072pp | 0.833 | 0/12 | NOT-SEPARABLE |
| buffer_k20 | k=0.20 | +0.138pp | 0.917 | 0/12 | NOT-SEPARABLE |
| buffer_k40 | k=0.40 | **+0.318pp** | 0.750 | 0/12 | REJECT |
| cost20 | 20bp/side | −1.410pp | 0.000 | 0/12 | REJECT |
| buffer_k05_cost20 | k=0.05 @ 20bp | **−1.460pp** | 0.000 | 1/12 | REJECT |

Three readings, in the order they matter:

1. **The axis is monotone and unmeasurable at every point.** −0.018 → −0.030 → +0.072 → +0.138 →
   +0.318pp across a 20x sweep of the knob. The direction is clean (more buffering, mildly more
   return) but the whole sweep spans 0.34pp against a per-cell band of ~6.6pp, i.e. **1/20th of
   the ruler**. Zero cells, at any strength, clear their own band.
2. **The far end flips the label for the right reason.** k=0.40 is the only buffer arm whose median
   is *positive* and it is the only one that reads REJECT — because at 8x the arm the dispersion
   grows too (3 of 12 cells fall below the −0.15pp floor, not-worse share 0.750 < 0.80). A knob
   that raises the mean and the spread together is not a knob you can quote.
3. **The buffer is not a toll hedge.** At 20bp/side the no-buffer toll costs −1.410pp; adding
   k=0.05 costs −1.460pp, i.e. the interaction is **−0.05pp on top of the toll**, the same sign and
   the same size as the buffer's own 10bp reading. The 1.41pp loss belongs to the toll; nothing in
   the buffer family buys any of it back.

## Consequence

The buffer family retires with both ends priced: it is a real, monotone, tiny effect that this
design cannot resolve, and it does not interact with the cost axis. The three rows stocked at
r1352 are now burned, flipped done by the pool harvest, and their arms stand in the published
face (9 arms, `--check` green, selftest 50/50).

## Also this window

The three rows could not be ignited when they were entered: they carried **no `shards` array**, so
`Tools/autofill.py` skipped them under "no takeable shard" and published the tick as
`pool_empty_or_busy` while py sat at 5–7% and the watermark read RED. That is the exact shape the
submit gate (r301 law) exists to refuse, re-entered by hand. Fixed two ways: the rows got a real
shard (`atlas-0of1`), and `_ghost_ready_ids()` now names such entries in a
`ghost_ready_no_shards` verdict instead of letting them hide inside an empty-pool reading
(selftest S20g2–S20g5).

Card: E264. Faces: `results/etf_book_phase_atlas_buffer_{k02,k40,k05_cost20}.json`,
`results/etf_book_phase_atlas_arms.json` (9 arms), `research/ETF_BOOK_PHASE_ATLAS_ARMS.md`.