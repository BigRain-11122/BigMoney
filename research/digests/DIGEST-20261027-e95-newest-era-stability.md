# DIGEST 2026-10-27 · E95: the newest-era tilt cell is re-derived, not re-measured

**Leg**: `python scripts\e39_panel_census.py tiltstable` (mode added this round)
**Face**: `results/e42_tilt_era/NEWESTERA-STABILITY-20261026.json`
**Untouched twins**: `results/e42_tilt_era/TILT-ERA-20261020.json` (published), `TILT-ERA-20261026-screened.json`
**Selftest**: `python scripts\e39_panel_census.py selftest` → 266/266 (was 262, +4 legs)

## Why this leg exists

The E42 tilt face's newest-era cell was published twice: **+748.1 bp** (cutoff 2026-10-20) and
**+697.6 bp** (cutoff 2026-10-26). Six sessions of new data moved the headline by 50.5 bp, and
nothing in the repo said whether that was a *level change* or the cell simply being re-derived.
Both faces carry `months=34`, i.e. **the same window length** — so the move cannot be blamed on
a longer window. This leg measures the cell's own end-choice sensitivity on one panel and puts
the two spreads side by side.

## What the grid does

One `_monthly_core()` pass (one panel, one loader, one cutoff = 2026-10-26), then the cell is
recomputed with the evaluation end moved across the last 12 month-ends of the era. Nothing but
the end moves: same months-prefix, same code path, same corporate-action guard.

| window end | months | tilt bp | positive share | beta | R² |
|---|---|---|---|---|---|
| 2025-11 | 23 | 448.6 | 43.5% | 1.173 | 0.569 |
| 2025-12 | 24 | 570.1 | 45.8% | 1.166 | 0.567 |
| 2026-01 | 25 | 1029.4 | 48.0% | 1.068 | 0.546 |
| 2026-02 | 26 | 1089.1 | 50.0% | 1.064 | 0.543 |
| 2026-03 | 27 | 757.5 | 48.1% | 1.108 | 0.577 |
| 2026-04 | 28 | 1079.5 | 50.0% | 1.127 | 0.603 |
| 2026-05 | 29 | 1213.0 | 51.7% | 1.115 | 0.598 |
| 2026-06 | 30 | **1632.7** | 53.3% | 1.066 | 0.604 |
| 2026-07 | 31 | 918.6 | 51.6% | 1.023 | 0.659 |
| 2026-08 | 32 | 1109.7 | 53.1% | 1.013 | 0.657 |
| 2026-09 | 33 | 982.2 | 51.5% | 1.024 | 0.659 |
| 2026-10 | 34 | **697.6** | 50.0% | 1.032 | 0.673 |

Span **1184.1 bp** (min 448.6 / max 1632.7), sd 316.3 bp, on 34 months of a series whose own
monthly sd is 621.4 bp.

## The comparison the item asked for

| quantity | value |
|---|---|
| published readings on disk | 2 (`TILT-ERA-20261020` 748.1, current 697.6) |
| spread of published readings | **50.5 bp** |
| spread from moving the end alone | **1184.1 bp** (23× larger) |
| verdict | `inside_end_choice_span` |

So: the 50.5 bp that separated two publications is *far inside* the noise that a single month of
end choice produces. Two further readings of the same table:

- Both publications report `months=34` but different levels, so the 50.5 bp is **panel revision**
  (restated prints / data arrival), not window length. The cell is not reproducible across panel
  arrivals even when the window is unchanged.
- The cell's sign is stable (positive at every end) and its beta on the ladder stays in
  1.01–1.17, so the *mechanism* (ladder ≈ size tilt) survives; it is the **level in bp** that
  cannot be quoted.

## What may and may not be said

- MAY: "the newest era's tilt is positive at every one of 12 window ends, beta ≈ 1.03–1.17".
- MAY NOT: "the newest-era tilt is +697.6 bp" (or +748.1 bp) as a level, and MAY NOT treat a
  later publication as evidence the level "rose" or "fell".
- Consequence for the E41/E42 ratio claims ("4.7× decay", "748 bp vs peak"): those are ratios of
  two era levels, and the newest-era leg alone carries ±592 bp of end-choice slack. Any ratio
  quoted off this cell must publish its window end beside it.

## Honest limits

- End-choice grid only: it cannot see universe changes or panel-arrival effects (r1110 register);
  the 50.5 bp panel-revision read is an inference from equal month counts, not a controlled test.
- The newest era is the shortest (34 months) and open-ended, so its mean carries the widest error
  by construction; 50.0% positive share means the head-line is a mean of an almost symmetric,
  very noisy series.
- Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count.