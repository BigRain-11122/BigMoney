# DIGEST 2026-10-21 — E30/E31 full-universe breadth: the family is closed for real

**Round**: r1101 (bm-b) · **Evidence cutoff**: 2026-09-22 · **Products**: `scripts/e30_readout.py`
(selftest 29/29), `results/e30_full_universe/E30-CONFIRM-20261021.{json,md}`, 7 runner faces.

## What was asked

r1100 closed equity-breadth as "an early-sample artefact" on a small pre-2018 universe
(56 ETFs, so `top50` ≈ the whole universe). The obvious objection: maybe the defect is the
*measurement*, not the idea. E30/E31 re-ran the same comparison on the full 1,221-ETF
universe where N is no longer degenerate.

## What the data says

| leg | universe | years | ladder5 ann% | best width | excess bp/yr | t |
|---|---|---|---|---|---|---|
| all universe, cost x1 | 1221 | 13.82 | 6.24 | all (9999) | +261.8 | 1.73 |
| all universe, cost x3 | 1221 | 13.82 | 6.15 | all | +252.9 | 1.68 |
| all universe, 2018+ | 1231 | 8.40 | 7.08 | all | +158.0 | 0.86 |
| domestic only | 1152 | 13.82 | 6.24 | all | +227.9 | 1.64 |
| N ladder, full | 1221 | 13.82 | 6.24 | top200 | +162.0 | 1.16 |
| N ladder, 2018+ | 1231 | 8.40 | 7.08 | top200 | +28.8 | 0.23 |
| top200, cost x3 | 1221 | 13.82 | 6.15 | top200 | +149.5 | 1.08 |

Two readings, both honest:

1. **Width.** On the full sample the premium grows with the number of names held
   (top10 −102 → top20 −17 → top50 +114 → top100 +84 → top200 +162 bp/yr). So the 5-rung
   ladder is *not* simply "too concentrated"; breadth does pay over the long sample.
2. **Window.** In the 2018+ sample the same ladder is flat to negative at every width
   (top10 −215, top20 −147, top50 +29, top100 −75, top200 +29 bp/yr; all |t| < 0.7), and
   tripled cost does not rescue it (+149.5bp, t=1.08).

## Verdict

The long-sample breadth excess is real in the data but it is a **long-sample artefact a live
book could not have captured**: it does not survive the recent window at any tradeable width,
and it never clears an evidence bar even in the full sample (best t = 1.73 with 1,221 names,
which is not a tradeable book). **Family stays closed.** Practical corollary for the desk:
the 5-rung core48 ladder is not the thing to fix; chasing breadth is.

## Honest limits

- ETF population is today's surviving listing set → listing survivorship inflates breadth
  (the losers that delisted are absent), which is exactly the bias that favours *wide* books.
- `excess_bp_yr` here is the runner's full-precision ann-return difference vs ladder5; the
  `t` values come from the same runner (paired over rebalance windows).
- Cost model 13.041bp/side on turnover; idle share accrues at the GC001 repo close.
- N ladder is a multiple-comparison surface; only the shape across N is read, never one cell.
- Descriptive census only: no gate, no prereg, no trial count consumed.

## Follow-ups seeded (pool, ready 3)

`E31-LIQ-NLADDER-FULL` / `E31-LIQ-NLADDER-2018` / `E31-LIQ-TOP200-X3` — burned this round
and closed; next supply refill = E32 candidates on the *cash-leg* side (GC001 timing), since
breadth is now closed.

## Pit (one line, for CODELY)

E30 pool entries were seeded with an `entered_at` ten minutes *ahead* of the wall clock
(`01:44` written at `01:34`), which surfaced as a `pool_dualrun_reconcile` envelope-only
drift on `updated_at` (streak reset, entries equal). Seed scripts must call the clock once
and use that value for every timestamp field in the same write.