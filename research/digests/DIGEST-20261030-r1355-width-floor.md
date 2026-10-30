# r1355 — the width ladder is a direction, not a size (and the buffer line survived its first unfitted point)

2026-10-30, bm-c. Faces: `results/etf_book_width_resolution_floor.json`,
`results/etf_book_buffer_floor_readback.json`. Script:
`scripts/etf_book_phase_atlas_arms.py --width` / `--readback` (selftest 60 → 74). Cards E266/E267.

## What was asked

r1354 turned the buffer family's "unmeasurable at every strength" into a size (k = 7.79, past
k = 1.0). The same question was owed to the other knob r1350 refused to quote: is "width is inside
the band" a size or only a direction? And the three rows stocked at r1354 were still in the pool,
so whichever the harvest took first had to be read back.

## Answer 1 — width buys a direction, not a size

The baseline grid (N = 3/5/8/12 × R = 10/20/40, 10 phases per cell, cutoff 2026-10-29) is already
published; the fit needs no engine run.

| width | median CAGR | R10 | R20 | R40 |
|---|---|---|---|---|
| N3 | +8.715pp | 10.93 | 8.71 | 6.78 |
| N5 | +9.130pp | 11.51 | 9.13 | 8.32 |
| N8 | +10.130pp | 12.00 | 10.13 | 8.30 |
| N12 | +9.645pp | 11.63 | 9.64 | 7.55 |

Five of nine adjacent rungs point up (R10 +0.58/+0.50/−0.37, R20 +0.42/+1.00/−0.49,
R40 +1.54/−0.02/−0.76), sign agreement 0.556 against a frozen 0.75 floor. The peak sits at N=8 and
the widest rung tested (N=12) is worse than N=8 **in all three cadences**.

The arithmetic, published beside it and not as the headline: +0.1138pp per name, r2 0.525, so a
full ruler (6.68pp = the baseline median cell band) would need 58.72 names of runway — width 61.7
against the widest rung anyone has priced (N=20, `results/etf_capacity_frontier.json`). The whole
ladder spans 0.93pp = 0.139 of the ruler.

Verdict: **DIRECTION_NOT_A_SIZE**.

## Answer 1b — the second engine will not reproduce the hill

`results/etf_capacity_frontier.json` prices the same width ladder on its own universe (its own
engine, N5..N20). It does **not** replicate the atlas's shape: R20 descends monotonically
(15.56/15.00/14.03/12.64) while R40 ascends monotonically (10.04/10.71/11.28/11.32), and R10
descends (19.72→19.41). Up-direction share 0.429, sign flips between cadences = **true**.

That is the useful half of a negative: the atlas's hill is not a property of width, it is a
property of that panel's selection at that cadence. Width is a trade (CAGR against capacity), and
neither of its two terms has a stable sign across engines.

## Answer 2 — the buffer line's first unfitted point: HOLDS

The pool harvested `E266-ATLAS-BUFFER-K030` first (the midpoint of 0.20→0.40, the widest gap in
r1354's fit), then started the next row.

| reading | value |
|---|---|
| fit at k=0.30 (slope +0.862/k, intercept −0.031) | **+0.228pp** |
| the arm's own 12 cells (median Δ vs baseline) | **+0.260pp** |
| gap | **+0.032pp** |
| tolerance | 0.127pp = 3× the fit's largest in-sample residual (0.042pp), floored at 0.05 |

Verdict: **HOLDS**. The cell spread of that same arm is −0.72 .. +1.24pp, so the median agreeing
with the line is not the book agreeing with the line — which is why both numbers are published.

## What was mechanised

- `--width` / `--width-check`: frozen rule (sign test before slope, priced envelope named with its
  source), gate with the same three states as the other faces (green / inconsistent / stale).
- `--readback` / `--readback-check`: refuses to assess unless the harvested face's own audit
  declares k=0.30, tolerance derived from the fit's own residual scale.
- selftest 60 → 74 legs: the sign test must be able to pass (a monotone ladder reaches), a flat
  ladder must need a width past the priced envelope, a hill must read DIRECTION_NOT_A_SIZE, the
  cross-check must flip only when a ladder disagrees between cadences, and the fit must be able to
  fail the point it never saw.
- chain legs `etf_book_width_floor` + `etf_book_buffer_readback` (both rc0, 0.1s each); one smoke
  leg re-derives both verdicts from the numbers on the published faces.