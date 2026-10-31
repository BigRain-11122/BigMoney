# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-10-30, 1653 bars, 4 phases, 164.9 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.12% | 6.56% | 7.70% | 8.83% | 9.95% | 11.05% | 12.14% | 13.21% |
| 1 | 2020-01-09 | 9.67% | 6.51% | 7.63% | 8.74% | 9.82% | 10.89% | 11.94% | 12.97% |
| 2 | 2020-01-16 | 6.22% | 4.61% | 5.24% | 5.84% | 6.42% | 6.98% | 7.52% | 8.02% |
| 3 | 2020-01-23 | 10.11% | 6.62% | 7.79% | 8.94% | 10.09% | 11.22% | 12.34% | 13.45% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.16% | -12.79% | -15.37% | -17.92% | -20.41% | -22.86% | -25.27% |
| 2 | -18.94% | -11.30% | -14.07% | -16.77% | -19.39% | -21.95% | -24.44% | -26.86% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 18.11% | 10.18% | 12.39% | 14.63% | 16.88% | 19.16% | 21.45% | 23.75% |
| 1 | 16.94% | 9.02% | 10.90% | 12.77% | 14.65% | 16.52% | 18.38% | 20.24% |
| 2 | 11.47% | 5.62% | 6.60% | 7.55% | 8.47% | 9.37% | 10.25% | 11.10% |
| 3 | 13.15% | 7.39% | 8.85% | 10.31% | 11.75% | 13.19% | 14.62% | 16.04% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.698 | 1.708 | 1.657 | 1.622 | 1.598 | 1.579 | 1.565 | 1.554 |
| 1 | 1.449 | 1.311 | 1.267 | 1.237 | 1.216 | 1.201 | 1.188 | 1.179 |
| 2 | 1.060 | 0.858 | 0.812 | 0.782 | 0.760 | 0.744 | 0.731 | 0.721 |
| 3 | 1.236 | 1.238 | 1.188 | 1.154 | 1.130 | 1.111 | 1.097 | 1.086 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.70 pp | 0/4 |
| 0.50 | -1.69 pp | 0/4 |
| 0.60 | -0.69 pp | 0/4 |
| 0.70 | +0.29 pp | 3/4 |
| 0.80 | +1.25 pp | 2/4 |
| 0.90 | +2.21 pp | 0/4 |
| 1.00 | +3.13 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.87 pp |
| 0.50 | 0/4 | 0/4 | -5.23 pp |
| 0.60 | 0/4 | 0/4 | -3.60 pp |
| 0.70 | 3/4 | 0/4 | -1.98 pp |
| 0.80 | 2/4 | 0/4 | -0.36 pp |
| 0.90 | 0/4 | 0/4 | +1.26 pp |
| 1.00 | 0/4 | 0/4 | +2.86 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
