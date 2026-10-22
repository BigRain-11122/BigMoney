# E87 + E88 — the churn premium has no typical month before 2021, and both faces sit on the same burn

- date: 2026-10-22T23:4x (r1156 bm-b)
- evidence cutoffs: 2026-10-21 (re-read; panel bar 2026-10-22 has advanced since)
- faces: `results/e44_midmonth/CHURNROBUST-20261022-s2013.json`,
  `results/e44_midmonth/CHURNROBUST-CONTROL-20261021.json`
- runner: `python scripts/e39_panel_census.py robustchurn --start 2013-01-01` (37s),
  `python scripts/e39_panel_census.py burncontrol` (2s, pure file join)

## E87 — re-reading the churn cells at the 2013 start

Two answers, one of them a correction of emphasis.

1. **The published newest-era cells are start-invariant.** The 2013-start burn
   reproduces every 2021_2023 and 2024_now cell bit-for-bit (mid15 unscreened
   mean -123.7, 2021_2023 +2185.4, neutralise -364.7 — identical to E85). The
   earlier start does not change the burn; it only adds the two older eras, so
   the cell count goes 16 → 32 and nothing published moves.
2. **The two older eras have no typical month at all.** That is the new content:

| cell (level, churn_alpha_bp) | mean | median | trim10 | median keeps | top-3 share |
|---|---|---|---|---|---|
| me pre2017 unscreened | +209.1 | **-10.7** | 209.1 | -5.1% (flips) | 108.5% |
| me 2017_2020 unscreened | +1265.3 | 113.0 | 878.3 | 8.9% | 101.6% |
| mid15 pre2017 unscreened | +120.8 | **-34.9** | 1.1 | -28.9% (flips) | 149.1% |
| mid15 2017_2020 unscreened | +1130.5 | 221.6 | 677.5 | 19.6% | 84.1% |
| mid15 2021_2023 unscreened | +2185.4 | 284.6 | 2001.9 | 13.0% | 40.0% |
| mid15 2024_now unscreened | -123.7 | 18.1 | 2.7 | -14.6% (flips) | 151.6% |

- Both books' pre2017 medians flip sign against their means, and the three
  largest transitions exceed the whole signed total (top-3 share 108.5% /
  149.1%). The 2017_2020 medians keep 4-23% of the mean.
- The trimmed mean is the tell that these are right-skewed cells rather than
  one-outlier cells: only 7 of 32 level cells lose half their magnitude under a
  10% trim, against 29 of 32 under the median.
- Delta cells (screen effect) look different at this start: 14 of 14 lose half
  under the median, 10 of 14 under the trim, zero sign flips, and the trimmed
  deltas are exactly 0.0 in most older cells — the screen rewrote no bar there
  (the r1153 structural-zero reading, now visible forward of 2020 as well).

**Reading**: the "churn premium" is a 2021-onward object. Before 2021 it is a
handful of transitions dressed as an era-level number, and quoting a per-era
mean from those years is quoting three swaps. E85's era-shape conclusion stands
and now extends backward: the shape is not just different between 2021_2023 and
2024_now, the two older eras have no centre of mass to speak of.

## E88 — burn control

`burncontrol` joins the interval face (CHURNSE-20261021), the robust face
(CHURNROBUST-20261021) and the new 2013 face on `(book, universe|mode, era)`
and compares `mean_bp` by exact equality:

- SE vs robust (2020): 16 level + 12 delta cells, **28/28 matched, 0 mismatch**.
- SE vs robust (2013): the same 28 shared cells, **28/28 matched, 0 mismatch**,
  and exactly 16 cells exist only in the 2013 face (the two older eras).

So every face in this chain (E80/E82 gap → E85 robust → E89 intervals → E87
re-read) is read off one burn; no number in the chain can move by re-deriving
it. The control is now a leg, re-runnable in 2s, so a future re-derivation is
caught the round it happens.

## Pits

- A cell that is era-local is start-invariant by construction: re-reading at an
  earlier start is NOT a robustness test for the newer eras, it is only a way to
  add the older ones. Say which of the two you got.
- `n=0` cells are dropped, so a face's cell count (16 vs 32) is the only signal
  that the older eras were absent at all — print the spec's start beside every
  cell count.
- The variant filename must carry the start (r1135 pit, applied here: the face
  is `CHURNROBUST-<cutoff>-s2013.json` and the 2020 face was left untouched).

## Pool

- E87 closed (result_ref above). E88 closed (control face above).
- Seeded E91-CHURN-TOP-TRANSITION-NAMES: publish the identity, date and size of
  the three transitions that carry each older-era cell, so the concentration is
  auditable by name instead of quoted as a share.