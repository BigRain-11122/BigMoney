# Is the 60-day vol window load-bearing, or a champion on one calendar?

Face: `results/etf_book_vol_window_phase.json` (evidence cutoff 2026-11-16, 1663 bars, 4 phases, 94.1 s).

## Verdict

**ADOPT_WINDOW** -- best alternative 30d, earned the +0.02 Sharpe bar in 4/4 phases, no worse out of sample in 4/4.

Published window: 60 days (stays).

## Does the difference survive a paired ruler?

The older face on this axis (`results/etf_book_voltarget_phase.json`) calls the same shorter-window win *within noise*, because it compares a +1.50pp paired gain to the control's own 1.81pp CAGR spread across phases -- a between-phase spread applied to a paired effect. Here the two books' own return difference inside each phase is bootstrapped (circular blocks of one rebalance cycle, 1,000 draws, seeded by draw index):

| phase | paired mean | 5%-95% band | share > 0 |
|---|---|---|---|
| 0 | +0.86 pp/yr | [-0.09, +1.95] | 92.6% |
| 1 | +1.81 pp/yr | [+0.69, +3.04] | 99.9% |
| 2 | +1.19 pp/yr | [+0.13, +2.42] | 96.7% |
| 3 | +0.41 pp/yr | [-0.36, +1.19] | 82.0% |

Paired read: **MIXED_ACROSS_PHASES** (arm 30d vs control 60d).

Shipped window stays: yes -- the frozen Sharpe bar says adopt, but the paired band still contains zero in 2 of 4 phases (MIXED_ACROSS_PHASES) -- a production change needs the paired ruler to clear too, so the shipped window stays and the whole ladder is published.

Older face on the same axis (read, not re-derived): window 20d vs 60d control, median **+1.50pp**, median Sharpe +0.12, share up 1.00, its own noise floor **1.81pp** -> `within noise`.

## Sharpe by window and phase (full window)

| phase | start | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 1.049 | 1.043 | 0.980 | 0.842 | 0.820 |
| 1 | 2020-01-09 | 1.071 | 0.969 | 0.929 | 0.876 | 0.862 |
| 2 | 2020-01-16 | 0.993 | 0.948 | 0.889 | 0.779 | 0.752 |
| 3 | 2020-01-23 | 1.189 | 1.102 | 1.139 | 1.033 | 1.009 |

## Out of sample (bars after 2023-12-31)

| phase | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|
| 0 | 1.777 | 1.750 | 1.702 | 1.479 | 1.444 |
| 1 | 1.582 | 1.414 | 1.411 | 1.410 | 1.315 |
| 2 | 1.647 | 1.586 | 1.490 | 1.403 | 1.358 |
| 3 | 1.376 | 1.220 | 1.345 | 1.199 | 1.197 |

## Per-window read

| window | phases earned | phases OOS not worse | Sharpe delta range |
|---|---|---|---|
| 30d | 4/4 | 4/4 | +0.050 .. +0.142 |
| 45d | 3/4 | 3/4 | -0.037 .. +0.063 |
| 90d | 0/4 | 0/4 | -0.138 .. -0.053 |
| 120d | 0/4 | 0/4 | -0.160 .. -0.067 |

## What the winning window actually changes (shipped vs best)

| phase | shipped 60d scale / vol / Sharpe | best 30d scale / vol / Sharpe |
|---|---|---|
| 0 | 0.710 / 10.2% / 0.980 | 0.724 / 10.3% / 1.049 |
| 1 | 0.713 / 10.8% / 0.929 | 0.730 / 11.0% / 1.071 |
| 2 | 0.723 / 10.6% / 0.889 | 0.739 / 10.6% / 0.993 |
| 3 | 0.737 / 9.9% / 1.139 | 0.741 / 9.8% / 1.189 |

A shorter estimate reacts faster, so it also holds MORE of the book: the mean scale rises in every phase, and the delivered vol drifts above the 8% label. The Sharpe column is the part that is not just extra exposure.

## Rule (frozen before the first run)

ADOPT_WINDOW iff some window earns >= sharpe_gain over the shipped window on the full calendar AND is no worse out of sample in >= share_min of the phases; PHASE_DEPENDENT iff the best window earns the bar on at least one phase but fewer than share_min (the answer is a property of where the cycle starts); WINDOW_INERT iff no window earns the bar on any phase and every window sits within sharpe_gain of the shipped one everywhere (the axis carries no result, the shipped value is safe); REJECT_WINDOW_CHANGE otherwise (no window earns the bar, but some is further than sharpe_gain away on at least one phase)

Identity: the 60d arm reproduces the published production card in the phase that prices the shipped span = **PASS**.

Rows: `results/etf_book_vol_window_phase.json::phase_rows`.
