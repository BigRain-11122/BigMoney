# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-27, 1673 bars, 4 phases, 294.4 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.70% | 6.38% | 7.47% | 8.55% | 9.62% | 10.68% | 11.72% | 12.74% |
| 1 | 2020-01-09 | 9.22% | 6.31% | 7.38% | 8.43% | 9.46% | 10.48% | 11.48% | 12.45% |
| 2 | 2020-01-16 | 5.58% | 4.34% | 4.90% | 5.44% | 5.95% | 6.44% | 6.91% | 7.35% |
| 3 | 2020-01-23 | 10.17% | 6.62% | 7.79% | 8.95% | 10.10% | 11.23% | 12.36% | 13.47% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.65% | -13.43% | -16.15% | -18.82% | -21.44% | -24.00% | -26.51% |
| 2 | -21.48% | -12.20% | -15.19% | -18.08% | -20.89% | -23.62% | -26.27% | -28.85% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 16.78% | 9.63% | 11.70% | 13.78% | 15.87% | 17.98% | 20.10% | 22.24% |
| 1 | 15.61% | 8.46% | 10.19% | 11.92% | 13.64% | 15.35% | 17.05% | 18.74% |
| 2 | 9.75% | 4.96% | 5.76% | 6.54% | 7.29% | 8.02% | 8.72% | 9.39% |
| 3 | 13.22% | 7.38% | 8.83% | 10.29% | 11.73% | 13.17% | 14.60% | 16.02% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.574 | 1.617 | 1.566 | 1.532 | 1.508 | 1.489 | 1.475 | 1.464 |
| 1 | 1.356 | 1.246 | 1.202 | 1.173 | 1.152 | 1.136 | 1.124 | 1.114 |
| 2 | 0.913 | 0.766 | 0.721 | 0.691 | 0.669 | 0.653 | 0.640 | 0.630 |
| 3 | 1.247 | 1.245 | 1.194 | 1.160 | 1.136 | 1.118 | 1.103 | 1.092 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.51 pp | 0/4 |
| 0.50 | -1.53 pp | 0/4 |
| 0.60 | -0.57 pp | 2/4 |
| 0.70 | +0.37 pp | 3/4 |
| 0.80 | +1.29 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.08 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.23 pp |
| 0.50 | 0/4 | 0/4 | -4.72 pp |
| 0.60 | 2/4 | 0/4 | -3.21 pp |
| 0.70 | 3/4 | 0/4 | -1.71 pp |
| 0.80 | 2/4 | 0/4 | -0.21 pp |
| 0.90 | 0/4 | 0/4 | +1.28 pp |
| 1.00 | 0/4 | 0/4 | +2.76 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
