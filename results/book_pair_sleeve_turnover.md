# The sleeve's premium reading: how much of it is which bonds we hold?

generated 2026-11-28T14:14:34+08:00 · evidence cutoff 2026-11-27 · bar 2026-11-27

**THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET**


| what | value |
|---|---|
| swaps seen / priced on both sides | 140 / 139 |
| median turnover per swap | 25.0% |
| membership step: median |churn| | 2.30 pp |
| membership step: p90 |churn| | 5.98 pp |
| membership step: largest |churn| | 13.63 pp |
| ordinary day (not a swap): median |change| | 0.78 pp |
| ordinary day: p90 |change| | 2.71 pp |
| churn median ÷ ordinary-day median | 2.94 |
| biggest swap ÷ ordinary-day p90 | 5.04 |

## Does a swap alone move a label?

- month ends examined: **81**; within 10 bars of a swap: **52**; bucket changed by the swap alone: **16**.
- the edges are the *actual* series' own tertiles, held fixed for both readings, so a change here is the reading moving, not the ruler drifting.


## Today

| what | value |
|---|---|
| reading (2026-11-27) | 11.420% |
| cheap below / rich above | 9.247% / 15.231% |
| distance to nearest edge | 2.17 pp |
| swap step p90 | 5.98 pp |
| reading sits inside the swap step | yes |
| label in force (parent face, read 2026-10-31) | rich |

## Reconciliation with the parent face

`book_pair_sleeve_premium.sleeve_premium` — 3490 days compared, max |diff| **0.0** (tolerance 1e-09).


## The swaps that moved it most

| date | turnover | before | after | churn (pp) |
|---|---|---|---|---|
| 2026-07-17 | 25% | 23.97 | 10.34 | -13.63 |
| 2018-09-11 | 70% | 17.28 | 5.23 | -12.06 |
| 2026-11-16 | 20% | 18.56 | 6.70 | -11.86 |
| 2025-12-16 | 30% | 17.48 | 7.76 | -9.72 |
| 2025-10-21 | 35% | 10.79 | 1.40 | -9.39 |
| 2025-02-24 | 30% | 14.73 | 5.96 | -8.78 |
| 2025-04-22 | 20% | 19.60 | 11.25 | -8.36 |
| 2026-05-21 | 35% | 16.45 | 8.27 | -8.19 |

## What this face does not claim

- membership is rebuilt from the parent's pick formula because neither parent publishes its holdings; the 1e-9 reconciliation only proves the two implementations agree, not that either equals the traded book
- the counterfactual reading drops bonds that delisted since the swap, so a swap that saved a defaulted name flatters the pre-swap side in those months
- a tertile label is a coarse ruler: a reading that moves 3pp inside the mid bucket is invisible to this face even though it is the same 3pp the desk sees
- churn_pp is a median-of-medians: two sets of 20 with the same median can differ in every bond, so this is a lower bound on membership noise
