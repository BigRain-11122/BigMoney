# How sure is the split's cushion? (book_pair_split_ci)

generated 2026-11-28T06:00:55+08:00 · bar 2026-11-27 · window 2020-01-03..2026-11-27

## Reading

- In the 32 months the ETF book ends down, the 70/30 split gives back +0.44pp less of the fall on average (-0.96% vs -1.40%), and it is better in 16 of them.
- Resampling those months in blocks of 3 gives a 90% interval of +0.08pp to +0.83pp, so the number is distinguishable from zero.
- That is arithmetic, not skill: to first order every month's cushion is the convertible weight times the month's spread, so this reading never claims the split forecasts anything (the shortcut averages out to 0.2bp of error, though any single month drifts up to 17.5bp -- which is why the blend month is read off its own level).
- The +1.64pp the earlier window reading showed is a rolling 12-month figure (2021-09-10..2022-09-27); the month-by-month average is the smaller +0.44pp, and the smaller number is the one this interval covers.
- Small but signed: the split wins only 16 of 32 losing months, so the average cannot be coming from winning most of them -- it comes from the convertible half holding up in the months it does help.

## The months the ETF ends down

| measure | value |
|---|---|
| months | 32 |
| mean ETF month | -1.40% |
| mean convertible month | 0.05% |
| mean split month | -0.96% |
| mean cushion | +0.44pp |
| months improved | 16 of 32 |
| first-order w x spread | +0.43pp |
| first-order gap (mean) | 0.2bp |
| first-order gap (worst single month) | 17.5bp |
| parent's own negative-month reading | matches |

## Two rulers, one cushion

The earlier window reading showed +1.64pp across a rolling 12-month window (2021-09-10..2022-09-27): split -4.97% vs ETF -6.62%. The month-by-month average over the 32 losing months is +0.44pp -- averaging months and averaging one window are not the same operation, and this face puts its interval on the smaller number.

## Block bootstrap of the mean cushion

| block (months) | blocks/sample | 90% interval | P(mean<=0) | negative months/draw |
|---|---|---|---|---|
| 1 | 82.00 | +0.13pp to +0.80pp | 0.007 | min 16 / mean 32.0 / max 48 |
| 3 | 27.33 | +0.08pp to +0.83pp | 0.018 | min 13 / mean 32.0 / max 49 |
| 6 | 13.67 | +0.07pp to +0.86pp | 0.018 | min 17 / mean 32.0 / max 53 |
| 12 *too few blocks* | 6.83 | +0.11pp to +0.88pp | 0.011 | min 17 / mean 32.0 / max 49 |

## Robustness (never changes the primary verdict)

- no-hindsight 50/50: mean cushion +0.73pp over 32 months, 90% interval +0.13pp to +1.38pp, verdict CUSHION_SEPARABLE_POSITIVE
- dropping 2022-04 (ETF -3.38%, convertible -4.03%, split -3.55%) leaves the mean at +0.46pp
- dropping 2020-09 (ETF -3.33%, convertible -4.10%, split -3.53%) leaves the mean at +0.46pp
- dropping 2026-03 (ETF -2.58%, convertible -5.33%, split -3.39%) leaves the mean at +0.48pp

## By year (only negative ETF months)

| year | months | mean cushion |
|---|---|---|
| 2020 | 4 | +0.96pp |
| 2021 | 3 | +1.49pp |
| 2022 | 7 | +0.14pp |
| 2023 | 6 | +0.13pp |
| 2024 | 3 | +1.98pp |
| 2025 | 2 | +0.54pp |
| 2026 | 7 | -0.44pp |

## What this face does not say

- it does not say the split forecasts a bad month (it cannot: to first order the cushion is the weight times the spread)
- it does not model the cost of moving money between the books (r2176 does)
- it does not test a different window; it puts an interval on the one the earlier reading published
