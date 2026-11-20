# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-20, 1668 bars, 4 phases, 275.0 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.59% | 6.33% | 7.42% | 8.49% | 9.54% | 10.58% | 11.61% | 12.62% |
| 1 | 2020-01-09 | 9.32% | 6.36% | 7.44% | 8.50% | 9.55% | 10.57% | 11.58% | 12.57% |
| 2 | 2020-01-16 | 5.65% | 4.37% | 4.94% | 5.49% | 6.01% | 6.50% | 6.98% | 7.43% |
| 3 | 2020-01-23 | 10.32% | 6.69% | 7.88% | 9.06% | 10.22% | 11.38% | 12.53% | 13.66% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.34% | -13.04% | -15.70% | -18.31% | -20.87% | -23.37% | -25.83% |
| 2 | -20.84% | -11.93% | -14.85% | -17.69% | -20.45% | -23.13% | -25.73% | -28.26% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 16.55% | 9.54% | 11.59% | 13.64% | 15.71% | 17.80% | 19.89% | 21.99% |
| 1 | 15.91% | 8.59% | 10.35% | 12.11% | 13.87% | 15.61% | 17.35% | 19.08% |
| 2 | 9.95% | 5.03% | 5.86% | 6.66% | 7.43% | 8.17% | 8.89% | 9.59% |
| 3 | 13.60% | 7.55% | 9.05% | 10.55% | 12.05% | 13.54% | 15.02% | 16.49% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.559 | 1.605 | 1.554 | 1.520 | 1.495 | 1.477 | 1.463 | 1.451 |
| 1 | 1.377 | 1.261 | 1.217 | 1.187 | 1.166 | 1.151 | 1.138 | 1.129 |
| 2 | 0.931 | 0.777 | 0.732 | 0.701 | 0.680 | 0.663 | 0.650 | 0.640 |
| 3 | 1.278 | 1.270 | 1.219 | 1.185 | 1.161 | 1.143 | 1.129 | 1.117 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.53 pp | 0/4 |
| 0.50 | -1.55 pp | 0/4 |
| 0.60 | -0.59 pp | 1/4 |
| 0.70 | +0.36 pp | 3/4 |
| 0.80 | +1.29 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.10 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.33 pp |
| 0.50 | 0/4 | 0/4 | -4.79 pp |
| 0.60 | 1/4 | 0/4 | -3.26 pp |
| 0.70 | 3/4 | 0/4 | -1.74 pp |
| 0.80 | 2/4 | 0/4 | -0.22 pp |
| 0.90 | 0/4 | 0/4 | +1.28 pp |
| 1.00 | 0/4 | 0/4 | +2.78 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
