# E89 — every churn cell gets a sampling interval: the 2021_2023 gaps clear zero, both published era gaps do not (r1155 bm-b)

Evidence cutoff 2026-10-21. Face: `results/e44_midmonth/CHURNSE-20261021.json`.
Runner: `python scripts/e39_panel_census.py churnse` (4 universes × 2 books, full churn rows, CPU-only, 26 s).
Selftest: `python scripts/e39_panel_census.py selftest` → 223/223 PASS (11 new legs on the interval helpers).

## Question

E85 (median/trim beside the mean), E86 (all n leave-one-out re-reads) and E82/E83
(one transition owns a cell) are three views of the *shape* of a churn cell. None of
them answers the plainest reading question: a cell is published as `+318.8bp` over
27 transitions — how much of that number is sampling noise? This leg adds, on the
same burn and without touching any mean column:

- **jackknife SE** — closed-form for a mean, `sqrt(Σ(x_i − m)² / (n(n−1)))` = `sd/√n`;
  90% band = `mean ± 1.6449·SE`;
- **seeded percentile bootstrap** — 2,000 draws, fixed seed 20261022 (bit-reproducible),
  90% band `p05..p95`, plus the share of resamples whose sign differs from the mean;
- **gap intervals** — mid15 minus me with the two books resampled independently.

## Answer 1 — half the level cells are within one standard error of zero

| reading | count |
|---|---|
| level cells with an interval | 16 / 16 |
| jackknife 90% band clears zero | **8 / 16** |
| jackknife 90% band straddles zero | **8 / 16** |
| bootstrap agrees (clears / straddles) | 8 / 8 (identical set) |
| cells whose \|mean\| exceeds its own SE | 10 / 16 |
| median jackknife SE | **606 bp** |
| median bootstrap sign-flip share | 14.8% |

The split is not random: **every 2021_2023 cell clears zero and every 2024_now cell
straddles it.**

| book / universe | 2021_2023 mean (SE) | band | 2024_now mean (SE) | band |
|---|---|---|---|---|
| me / unscreened | +1866.5 (666.4) | +770 .. +2963 | +87.3 (89.9) | −61 .. +235 |
| me / drop | +1953.1 (685.4) | +826 .. +3081 | +52.1 (87.1) | −91 .. +195 |
| mid15 / unscreened | +2185.4 (606.0) | +1189 .. +3182 | −123.7 (141.0) | −356 .. +108 |
| mid15 / neutralise | +2185.4 (606.0) | +1189 .. +3182 | −364.7 (375.6) | −983 .. +253 |
| mid15 / drop | +2327.3 (635.0) | +1283 .. +3372 | +28.0 (54.4) | −61 .. +117 |

Read against r1153/r1154: the newest-era cells are the ones E85 called right-skewed
and E86 called 1-swap objects, and they are also the cells that cannot be told from
zero. The 2021_2023 cells are large (+1.9k to +2.3k bp) with a matching SE (~600 bp)
— a wide, genuinely positive era, not a lucky print.

## Answer 2 — neither published era gap survives its own sampling noise

| era | gap bp | SE | jackknife 90% | bootstrap 90% | sign-flip share | clears zero |
|---|---|---|---|---|---|---|
| 2021_2023 | +318.8 | 900.8 | −1162.8 .. +1800.5 | −1177.2 .. +1812.7 | **36.8%** | **no** |
| 2024_now | −211.0 | 167.2 | −486.1 .. +64.1 | −499.0 .. +41.1 | 8.9% | **no** |

This is the sharpest result of the leg and it is a correction of emphasis, not of any
published number: E86 showed both gaps keep their sign under almost every single
removal, so they are stable *as magnitudes*; this leg shows the same magnitudes sit
inside a band that crosses zero *as estimates*. The newest-era gap is the tighter of
the two (−211.0 vs SE 167.2, band reaching only +64) but it still crosses.

Two honest qualifications, both recorded in the face's spec:

- the gap band treats the books as independent. They decide on different calendar
  dates (27 me vs 29 mid15 in 2021_2023) so nothing pairs date-to-date, but they hold
  the same names over the same era, which makes the true difference error *smaller*
  than this quadrature sum — the gap band is conservative in the width direction;
- cells are monthly decisions on overlapping holdings, not iid prints, so the band is
  sampling noise of the transition sample, never a p-value. No cell is called positive
  or negative on the strength of a band.

## Answer 3 — the delta cells are tight, and four of them are structurally zero

| book / mode | 2021_2023 mean (SE) | 2024_now mean (SE) | clears zero |
|---|---|---|---|
| me / neutralise(_int) | 0.0 (0.0) | +5.1 (5.1) | 0.0 cells: n/a (no variance) |
| me / drop | +202.1 (158.0) | −35.2 (19.6) | 2024_now clears |
| mid15 / neutralise(_int) | 0.0 (0.0) | −241.0 (245.2) | no |
| mid15 / drop | +24.3 (129.7) | +151.7 (133.1) | no |

12 delta cells, 1 clears zero (me/drop 2024_now, −35.2 against SE 19.6), median SE
19.6 bp. The four exact-zero cells are E85's structural zeros (the repair screen
rewrote no bar in that era) — their SE is exactly 0.0 and `interval_clears_zero` is
`null`, not `true`, because a cell with no variance and no magnitude is not evidence
of anything.

## Same-burn spot check

28 of 28 means in this face are **bit-identical** to `CHURNROBUST-20261021.json`
(16 level + 12 delta cells, zero mismatches). E88 (the formal control face) stays
open — this was an ad-hoc equality read, not its deliverable.

## Honest limits

- Jackknife and bootstrap both price only the transition-sample noise; serial
  overlap between monthly decisions is not modelled (a block/era-clustered arm is the
  natural next cut, see Next).
- Two universes (`neutralise_int`, `neutralise`) are bit-identical here (E84), so the
  16 level cells are effectively 12 independent cells × books.
- The bootstrap seed is a fixed constant by design; changing it shifts p05/p95 by a
  few bp, never the conclusion, because the jackknife band agrees cell-for-cell.
- Descriptive only: no prereg, no judgement, zero ledger booking, no predictor.

## Next

- E87 (robust read at the 2013 start) and E88 (formal burn control) remain ready on
  the same burn; E90 candidate: an era-clustered interval (block bootstrap on the
  decision dates) to see whether overlap shrinks or widens these bands.