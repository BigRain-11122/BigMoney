# Is the 60-day vol window load-bearing, or a champion on one calendar?

Face: `results/etf_book_vol_window_phase.json` (evidence cutoff 2026-11-27, 1672 bars, 4 phases, 83.7 s).

## Verdict

**ADOPT_WINDOW** -- best alternative 30d, earned the +0.02 Sharpe bar in 4/4 phases, no worse out of sample in 4/4.

Published window: 60 days (stays).

## Does the difference survive a paired ruler?

The older face on this axis (`results/etf_book_voltarget_phase.json`) calls the same shorter-window win *within noise*, because it compares a +1.50pp paired gain to the control's own 1.81pp CAGR spread across phases -- a between-phase spread applied to a paired effect. Here the two books' own return difference inside each phase is bootstrapped (circular blocks of one rebalance cycle, 1,000 draws, seeded by draw index):

| phase | paired mean | 5%-95% band | share > 0 |
|---|---|---|---|
| 0 | +0.95 pp/yr | [-0.01, +2.10] | 94.7% |
| 1 | +1.84 pp/yr | [+0.78, +3.07] | 100.0% |
| 2 | +1.23 pp/yr | [+0.17, +2.38] | 97.4% |
| 3 | +0.41 pp/yr | [-0.36, +1.22] | 80.1% |

Paired read: **MIXED_ACROSS_PHASES** (arm 30d vs control 60d).

Shipped window stays: yes -- the frozen Sharpe bar says adopt, but the paired band still contains zero in 2 of 4 phases (MIXED_ACROSS_PHASES) -- a production change needs the paired ruler to clear too, so the shipped window stays and the whole ladder is published.

Older face on the same axis (read, not re-derived): window 20d vs 60d control, median **+1.50pp**, median Sharpe +0.12, share up 1.00, its own noise floor **1.81pp** -> `within noise`.

## Sharpe by window and phase (full window)

| phase | start | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 1.006 | 0.993 | 0.925 | 0.785 | 0.765 |
| 1 | 2020-01-09 | 1.049 | 0.944 | 0.902 | 0.852 | 0.841 |
| 2 | 2020-01-16 | 0.947 | 0.897 | 0.838 | 0.727 | 0.704 |
| 3 | 2020-01-23 | 1.184 | 1.097 | 1.134 | 1.029 | 1.005 |

## Out of sample (bars after 2023-12-31)

| phase | 30d | 45d | 60d | 90d | 120d |
|---|---|---|---|---|---|
| 0 | 1.666 | 1.623 | 1.561 | 1.327 | 1.300 |
| 1 | 1.529 | 1.354 | 1.349 | 1.353 | 1.265 |
| 2 | 1.534 | 1.460 | 1.366 | 1.277 | 1.240 |
| 3 | 1.363 | 1.208 | 1.332 | 1.189 | 1.187 |

## Per-window read

| window | phases earned | phases OOS not worse | Sharpe delta range |
|---|---|---|---|
| 30d | 4/4 | 4/4 | +0.050 .. +0.147 |
| 45d | 3/4 | 3/4 | -0.037 .. +0.068 |
| 90d | 0/4 | 0/4 | -0.140 .. -0.050 |
| 120d | 0/4 | 0/4 | -0.160 .. -0.061 |

## What the winning window actually changes (shipped vs best)

| phase | shipped 60d scale / vol / Sharpe | best 30d scale / vol / Sharpe |
|---|---|---|
| 0 | 0.710 / 10.2% / 0.925 | 0.724 / 10.3% / 1.006 |
| 1 | 0.716 / 10.7% / 0.902 | 0.731 / 11.0% / 1.049 |
| 2 | 0.724 / 10.6% / 0.838 | 0.739 / 10.7% / 0.947 |
| 3 | 0.737 / 9.9% / 1.134 | 0.741 / 9.8% / 1.184 |

A shorter estimate reacts faster, so it also holds MORE of the book: the mean scale rises in every phase, and the delivered vol drifts above the 8% label. The Sharpe column is the part that is not just extra exposure.

## Rule (frozen before the first run)

ADOPT_WINDOW iff some window earns >= sharpe_gain over the shipped window on the full calendar AND is no worse out of sample in >= share_min of the phases; PHASE_DEPENDENT iff the best window earns the bar on at least one phase but fewer than share_min (the answer is a property of where the cycle starts); WINDOW_INERT iff no window earns the bar on any phase and every window sits within sharpe_gain of the shipped one everywhere (the axis carries no result, the shipped value is safe); REJECT_WINDOW_CHANGE otherwise (no window earns the bar, but some is further than sharpe_gain away on at least one phase)

Identity: the 60d arm reproduces the published production card in the phase that prices the shipped span = **PASS**.

Rows: `results/etf_book_vol_window_phase.json::phase_rows`.
