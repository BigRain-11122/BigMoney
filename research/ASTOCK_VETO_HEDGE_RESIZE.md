# What does it cost to keep the hedge the right size?

`SCHEDULE_COST_IS_BELOW_THE_NOISE_LINE` · `COST_CANNOT_DECIDE_THE_SCHEDULE` · `THE_SCHEDULE_MOVES_RETURN_MORE_THAN_RISK` · `HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT`

Evidence cutoff **2026-11-20** (last period ends **2026-11-11**).  Book and hedge leg come from `results/astock_veto_hedgeable_beta.json`; the betas are r2030's own series (largest difference **0.00e+00** over 57 shared periods).

## 1. The short version

- The busiest schedule (re-fit and trade every period) turns over **29.5%** of book notional a year; never touching the size after entry turns over **20.1%** -- the difference is **9.4%** of notional a year, and it includes the entry trade in both.
- At **1.0 bp per side** that difference costs **0.0029 pp** of return a year -- **17x** below the 0.05 pp noise line (`SCHEDULE_COST_IS_BELOW_THE_NOISE_LINE`).  You would have to pay **53 bp per side** before it reached the line (`COST_CANNOT_DECIDE_THE_SCHEDULE`).
- Risk barely notices the schedule: annualised volatility spans **0.34 pp** across all eight schedules (11.15% .. 11.50%) while annual return spans **1.05 pp** (`THE_SCHEDULE_MOVES_RETURN_MORE_THAN_RISK`).
- The return spread is not the cadence, it is whether the size chases the beta at all: the two schedules that hold **one** size finish at **12.21%** (set once at 0.9082) and **12.06%** (one unit), above every one of the 6 schedules that follow the beta (best **11.79%**) -- `HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT`.
- Chasing the beta costs **0.97 pp** a year in this window, and it is arithmetic, not bad luck: the size trailed from the past is slightly high in the periods the hedge then earns, and that covariance subtracts **0.97 pp** a year (`chase` column below).

Keeping the hedge the right size is almost free: the busiest schedule trades 29.5% of book notional a year and the quietest 20.1%, a difference of 0.094 notional a year, which at 1.0 bp per side costs 0.0029 pp of return a year -- 17 times below the 0.05 pp noise line. You would have to pay 53 bp per side before that difference reached the line. The schedule barely moves risk either: annualised volatility spans 0.34 pp across all eight (11.15%..11.50%) against a 1.05 pp span in annual return. The return spread is not the cadence -- it is whether the size chases the beta at all: the two schedules that hold one size finish at 12.21% and 12.06%, above every one of the 6 schedules that follow the beta (best 11.79%). The chasing itself costs 0.97 pp a year in this window (the arithmetic: the size you trail is slightly high in the periods the hedge then earns, and 0.97 pp a year is what that covariance subtracts).

## 2. The sample

| periods in the parent | evaluated | warm-up | trainings that could not be fitted |
|---|---|---|---|
| 77 | 57 | 20 | 0 |

Every schedule is measured on those same 57 periods.  A schedule that trades less often is not given a kinder window -- it is given the same window and a staler size, which is the cost being measured.

## 3. Eight schedules, one sample, gross

| schedule | what it does | re-sizes | turnover / yr | mean k | staleness (mean / max) | chase pp/yr (positive = paid) | vol | mean / yr | worst dd |
|---|---|---|---|---|---|---|---|---|---|
| `every_period` | refit and trade every 20-bar period (r2030's honest arm) | 56 | 29.5% | 0.9525 | 0.0000 / 0.0000 | 0.97 | 11.38% | 11.17% | -13.39% |
| `cadence_q` | re-size every 3 periods (~60 trading days) | 18 | 25.7% | 0.9531 | 0.0058 / 0.0478 | 0.82 | 11.37% | 11.31% | -13.42% |
| `cadence_1y` | re-size every 13 periods (~one year) | 4 | 23.6% | 0.9539 | 0.0129 / 0.0858 | 0.83 | 11.47% | 11.31% | -13.48% |
| `band_0.02` | trade only when the target has drifted more than 0.02 | 8 | 25.6% | 0.9545 | 0.0070 / 0.0198 | 0.88 | 11.35% | 11.26% | -13.52% |
| `band_0.05` | trade only when the target has drifted more than 0.05 | 1 | 21.6% | 0.9476 | 0.0179 / 0.0438 | 0.35 | 11.30% | 11.79% | -13.38% |
| `band_0.10` | trade only when the target has drifted more than 0.10 | 1 | 22.3% | 0.9602 | 0.0182 / 0.0951 | 0.74 | 11.50% | 11.38% | -13.32% |
| `set_once` | size on the first honest beta and never touch it again | 0 | 20.1% | 0.9082 | 0.0570 / 0.1039 | 0.00 | 11.35% | 12.21% | -13.52% |
| `one_unit` | short exactly one unit of notional, no estimate at all | 0 | 22.1% | 1.0000 | 0.0521 / 0.1356 | 0.00 | 11.15% | 12.06% | -13.34% |

Staleness is the distance between the size held and the beta the period itself would have chosen.  `every_period` is stale by construction zero; `one_unit` is stale on purpose (it is the no-estimate arm).  `chase` is what following the beta costs against holding the mean size: minus the covariance between the size held and the hedge's own return, annualised.  A constant size has no such term by construction, which is why the two constant arms are the only ones that do not pay it.

## 4. What the turnover costs, at five per-side prices

| schedule | 0.5 bp/side | 1.0 bp/side | 2.0 bp/side | 5.0 bp/side | 20.0 bp/side |
|---|---|---|---|---|---|
| `every_period` | 11.16% | 11.16% | 11.16% | 11.15% | 11.11% |
| `cadence_q` | 11.31% | 11.31% | 11.31% | 11.30% | 11.26% |
| `cadence_1y` | 11.30% | 11.30% | 11.30% | 11.29% | 11.26% |
| `band_0.02` | 11.26% | 11.26% | 11.25% | 11.25% | 11.21% |
| `band_0.05` | 11.79% | 11.79% | 11.79% | 11.78% | 11.75% |
| `band_0.10` | 11.38% | 11.38% | 11.38% | 11.37% | 11.34% |
| `set_once` | 12.21% | 12.21% | 12.21% | 12.20% | 12.17% |
| `one_unit` | 12.06% | 12.06% | 12.05% | 12.05% | 12.02% |

Net of the trade, the spread between the busiest and the quietest schedule does not move: **1.05 pp** of annual return at 1.0 bp per side, **1.07 pp** even at 20 bp.

## 5. Is the schedule the thing to optimise?  The random-timing band

| reading | value |
|---|---|
| draws (same 17 re-sizes, random timing, seed 2034) | 500 |
| annual return, 5% / median / 95% | 11.04% / 11.33% / 11.69% |
| annualised vol, 5% / median / 95% | 11.34% / 11.45% / 11.60% |
| sd of annual return across draws | 0.19 pp |
| both constant arms sit above this whole band | 12.21% and 12.06% vs a 11.69% top |

Randomly-timed schedules land in a **0.65 pp**-wide 90% band on annual return -- that is what "when you trade" is worth.  Both schedules that hold one size land **outside** that band, and the busiest real schedule lands at the bottom end of it.  So the thing that moves this book is not the calendar: it is whether the size is allowed to follow the beta at all, and if it is, the covariance printed in the `chase` column is what you pay for it.

## 6. What an operator should do with this

- **Do not pay for re-sizing.**  Any cadence from quarterly to never costs less than 0.003 pp a year at any realistic per-side price.
- **Do not chase the beta either.**  Every schedule that follows the beta pays the chase term; the two that hold one size do not.  In this window that term alone is **0.97 pp** a year -- **330 times** the entire cost of trading the hedge.
- **So the cadence question answers itself: pick any, then stop moving.**  The remaining choice is the level of k, and r2030 already showed the past cannot pick it (beta = 1.00 tied the refitted beta); here the two levels tried differ by **0.15 pp** a year, which is the size of the prize for guessing.
- **Watch the staleness, not the calendar.**  If the size held drifts more than ~0.05 away from the beta the period would choose, the residual exposure is the printed `max_abs_error`; a calendar cadence cannot see that, a drift band can -- but band 0.05 and band 0.10 both sit inside the varying pack here, so treat the band as an operational alarm, not as an alpha.

## 7. What this face does not say

- It does not re-choose a size or a level.  Both constant arms win (0.91 and 1.00 alike), and they differ from each other by 0.15 pp: the level term in this window is worth a tenth of a point.  What pays here is *not drifting*, and the drift costs because of a covariance this face measures but cannot promise to repeat.
- It charges commission and slippage on the hedge turnover only.  Borrow fee on the ETF leg, roll cost on the futures leg and the book's own turnover cost are priced in r2033 and in the parent book respectively.
- It does not model the intraday of the re-size, the margin call a futures position meets, or the availability of the shares to borrow.
- The evaluation sample is one history of 57 periods; the random-timing band is a statement about timing luck inside that history, not a confidence interval for a future window.
- Only the ETF hedge leg is walked.  r2027 showed the IM leg cannot express this beta at small capital, so the schedule question is asked of the leg that can.

## 8. Reproduction

```
python scripts/astock_veto_hedge_resize.py selftest
python scripts/astock_veto_hedge_resize.py run
python scripts/astock_veto_hedge_resize.py check
```
