<!-- BEGIN:IDX-FUT-CARRY-HEDGE-BETA-LOTS -->

# the hedge is a whole number of lots

generated 2026-11-23T19:56:27+08:00 | evidence_cutoff **2026-11-20** | verdict **THE_WHOLE_LOT_COUNT_DEPENDS_ON_THE_WINDOW_AND_IT_COSTS_MONEY**

The r2006 face priced one IC long lot hedged with beta x IF lots and then had
to buy a whole number of them. This page asks whether that integer came from
the pair or from the 242 days it was measured on, and what the rounding costs.

## IC_vs_IF

full-sample beta **0.9466** | last-year beta **1.5567** | 1961 aligned days 2018-10-23..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 381 | 0.356 | 0.476 | 0.948 | 1.534 | 1.834 | [1, 2] | 62.7% |
| 120d | 369 | 0.385 | 0.488 | 0.933 | 1.482 | 1.714 | [1, 2] | 64.5% |
| 242d | 344 | 0.426 | 0.605 | 0.944 | 1.363 | 1.548 | [1, 2] | 70.3% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 1.5567 | 95,884 | 225,664 | 2,820,795 |
| whole_ceil | 2 | 143,280 | 251,552 | 3,144,400 |
| whole_round | 2 | 143,280 | 251,552 | 3,144,400 |
| beta_one | 1.0000 | 36,360 | 265,558 | 3,319,474 |

rounding up to whole lots moves P&L by **+47,396 CNY** and sigma by **+25,888 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.4433` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IC_vs_IH

full-sample beta **1.1569** | last-year beta **2.2520** | 1961 aligned days 2018-10-23..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 381 | 0.130 | 0.570 | 1.206 | 2.199 | 2.831 | [1, 2, 3] | 85.8% |
| 120d | 369 | 0.336 | 0.554 | 1.222 | 2.155 | 2.358 | [1, 2, 3] | 85.9% |
| 242d | 344 | 0.455 | 0.721 | 1.166 | 1.827 | 2.245 | [1, 2, 3] | 91.3% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 2.2520 | 31,996 | 334,216 | 4,177,702 |
| whole_ceil | 3 | 66,060 | 349,085 | 4,363,557 |
| whole_round | 2 | 20,520 | 335,943 | 4,199,291 |
| beta_one | 1.0000 | -25,020 | 374,441 | 4,680,518 |

rounding up to whole lots moves P&L by **+34,064 CNY** and sigma by **+14,868 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.7480` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IC_vs_IM

full-sample beta **0.8757** | last-year beta **1.0056** | 1049 aligned days 2022-07-25..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 198 | 0.645 | 0.710 | 0.815 | 1.050 | 1.100 | [1, 2] | 78.3% |
| 120d | 186 | 0.694 | 0.732 | 0.812 | 1.038 | 1.063 | [1, 2] | 74.2% |
| 242d | 162 | 0.736 | 0.746 | 0.786 | 1.028 | 1.049 | [1, 2] | 80.9% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 1.0056 | 86,799 | 113,471 | 1,418,385 |
| whole_ceil | 2 | 242,400 | 446,573 | 5,582,167 |
| whole_round | 1 | 85,920 | 113,500 | 1,418,750 |
| beta_one | 1.0000 | 85,920 | 113,500 | 1,418,750 |

rounding up to whole lots moves P&L by **+155,601 CNY** and sigma by **+333,103 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.9944` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IH_vs_IC

full-sample beta **0.3939** | last-year beta **0.2008** | 1961 aligned days 2018-10-23..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 381 | 0.073 | 0.221 | 0.486 | 0.642 | 1.013 | [1, 2] | 0.3% |
| 120d | 369 | 0.196 | 0.228 | 0.484 | 0.623 | 0.819 | [1] | 0.0% |
| 242d | 344 | 0.203 | 0.270 | 0.472 | 0.592 | 0.696 | [1] | 0.0% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 0.2008 | -31,371 | 99,782 | 1,247,280 |
| whole_ceil | 1 | 25,020 | 374,441 | 4,680,518 |
| whole_round | 1 | 25,020 | 374,441 | 4,680,518 |
| beta_one | 1.0000 | 25,020 | 374,441 | 4,680,518 |

rounding up to whole lots moves P&L by **+56,391 CNY** and sigma by **+274,659 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.7992` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IH_vs_IF

full-sample beta **0.6339** | last-year beta **0.4753** | 1961 aligned days 2018-10-23..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 381 | 0.394 | 0.513 | 0.659 | 0.713 | 0.803 | [1] | 0.0% |
| 120d | 369 | 0.442 | 0.518 | 0.666 | 0.702 | 0.732 | [1] | 0.0% |
| 242d | 344 | 0.477 | 0.549 | 0.667 | 0.692 | 0.711 | [1] | 0.0% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 0.4753 | 5,281 | 62,638 | 782,972 |
| whole_ceil | 1 | 61,380 | 145,889 | 1,823,618 |
| whole_round | 1 | 61,380 | 145,889 | 1,823,618 |
| beta_one | 1.0000 | 61,380 | 145,889 | 1,823,618 |

rounding up to whole lots moves P&L by **+56,099 CNY** and sigma by **+83,252 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.5247` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IH_vs_IM

full-sample beta **0.2465** | last-year beta **0.1828** | 1049 aligned days 2022-07-25..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 198 | 0.133 | 0.162 | 0.286 | 0.406 | 0.477 | [1] | 0.0% |
| 120d | 186 | 0.144 | 0.174 | 0.307 | 0.377 | 0.436 | [1] | 0.0% |
| 242d | 162 | 0.186 | 0.201 | 0.271 | 0.361 | 0.398 | [1] | 0.0% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 0.1828 | -16,938 | 108,959 | 1,361,993 |
| whole_ceil | 1 | 110,940 | 371,441 | 4,643,017 |
| whole_round | 1 | 110,940 | 371,441 | 4,643,017 |
| beta_one | 1.0000 | 110,940 | 371,441 | 4,643,017 |

rounding up to whole lots moves P&L by **+127,878 CNY** and sigma by **+262,482 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.8172` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IM_vs_IC

full-sample beta **1.0330** | last-year beta **0.9315** | 1049 aligned days 2022-07-25..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 198 | 0.821 | 0.887 | 1.129 | 1.258 | 1.328 | [1, 2] | 71.2% |
| 120d | 186 | 0.873 | 0.904 | 1.144 | 1.215 | 1.297 | [1, 2] | 71.0% |
| 242d | 162 | 0.886 | 0.908 | 1.155 | 1.187 | 1.218 | [1, 2] | 74.7% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 0.9315 | -90,756 | 109,182 | 1,364,780 |
| whole_ceil | 1 | -85,920 | 113,500 | 1,418,750 |
| whole_round | 1 | -85,920 | 113,500 | 1,418,750 |
| beta_one | 1.0000 | -85,920 | 113,500 | 1,418,750 |

rounding up to whole lots moves P&L by **+4,836 CNY** and sigma by **+4,318 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.0685` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IM_vs_IF

full-sample beta **1.1730** | last-year beta **1.3939** | 1049 aligned days 2022-07-25..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 198 | 0.577 | 0.734 | 1.098 | 1.627 | 2.255 | [1, 2, 3] | 30.3% |
| 120d | 186 | 0.679 | 0.741 | 1.094 | 1.721 | 2.051 | [1, 2, 3] | 28.0% |
| 242d | 162 | 0.748 | 0.809 | 1.164 | 1.393 | 1.656 | [1, 2] | 16.1% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 1.3939 | -7,447 | 257,400 | 3,217,498 |
| whole_ceil | 2 | 57,360 | 299,049 | 3,738,118 |
| whole_round | 1 | -49,560 | 275,747 | 3,446,840 |
| beta_one | 1.0000 | -49,560 | 275,747 | 3,446,840 |

rounding up to whole lots moves P&L by **+64,807 CNY** and sigma by **+41,650 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.6061` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## IM_vs_IH

full-sample beta **1.4629** | last-year beta **1.8987** | 1049 aligned days 2022-07-25..2026-11-20

| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |
|---|---|---|---|---|---|---|---|---|
| 60d | 198 | 0.492 | 0.769 | 1.537 | 2.275 | 3.040 | [1, 2, 3, 4] | 38.4% |
| 120d | 186 | 0.657 | 0.776 | 1.574 | 2.131 | 2.626 | [1, 2, 3] | 36.0% |
| 242d | 162 | 0.753 | 0.852 | 1.589 | 1.837 | 2.033 | [1, 2, 3] | 19.1% |

last year 2025-11-21..2026-11-20, per one long lot:

| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |
|---|---|---|---|---|
| exact_beta | 1.8987 | -70,014 | 351,161 | 4,389,517 |
| whole_ceil | 2 | -65,400 | 351,431 | 4,392,885 |
| whole_round | 2 | -65,400 | 351,431 | 4,392,885 |
| beta_one | 1.0000 | -110,940 | 371,441 | 4,643,017 |

rounding up to whole lots moves P&L by **+4,614 CNY** and sigma by **+269 CNY** against the exact beta.

Read the sign before the number: rounding 1.5567 up to 2 buys `0.1013` of extra
hedge, and extra hedge is a position in the hedge leg's own carry. A positive
difference means that bet paid last year; it is not a saving, and it reverses
whenever the hedge leg's carry turns positive.

## what this does not settle

* the whole-lot convention itself is a desk rule, not a measurement: both `ceil`
  and `round` rows are printed and no row is recommended;
* the sample is one roll walk over the history this repo holds; a pair whose
  beta sits far from a lot boundary cannot show this effect at all, which is
  the honest reading of a single-lot-count spread.

<!-- END:IDX-FUT-CARRY-HEDGE-BETA-LOTS -->
