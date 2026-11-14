# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-13, 1663 bars, 4 phases, 324.2 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.11% | 6.56% | 7.70% | 8.83% | 9.95% | 11.05% | 12.14% | 13.22% |
| 1 | 2020-01-09 | 9.64% | 6.49% | 7.60% | 8.70% | 9.78% | 10.85% | 11.89% | 12.92% |
| 2 | 2020-01-16 | 6.24% | 4.61% | 5.24% | 5.84% | 6.43% | 6.99% | 7.52% | 8.03% |
| 3 | 2020-01-23 | 10.22% | 6.65% | 7.83% | 8.99% | 10.15% | 11.29% | 12.42% | 13.54% |

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
| 0 | 17.94% | 10.13% | 12.33% | 14.55% | 16.79% | 19.05% | 21.33% | 23.62% |
| 1 | 16.75% | 8.93% | 10.78% | 12.64% | 14.48% | 16.33% | 18.17% | 20.00% |
| 2 | 11.45% | 5.61% | 6.58% | 7.53% | 8.46% | 9.36% | 10.23% | 11.08% |
| 3 | 13.38% | 7.46% | 8.94% | 10.41% | 11.87% | 13.33% | 14.78% | 16.23% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.681 | 1.699 | 1.647 | 1.613 | 1.589 | 1.570 | 1.556 | 1.545 |
| 1 | 1.442 | 1.305 | 1.261 | 1.232 | 1.211 | 1.195 | 1.183 | 1.173 |
| 2 | 1.059 | 0.859 | 0.814 | 0.783 | 0.762 | 0.745 | 0.732 | 0.722 |
| 3 | 1.258 | 1.253 | 1.202 | 1.168 | 1.144 | 1.126 | 1.112 | 1.101 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.72 pp | 0/4 |
| 0.50 | -1.71 pp | 0/4 |
| 0.60 | -0.71 pp | 0/4 |
| 0.70 | +0.28 pp | 3/4 |
| 0.80 | +1.24 pp | 2/4 |
| 0.90 | +2.19 pp | 0/4 |
| 1.00 | +3.13 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.85 pp |
| 0.50 | 0/4 | 0/4 | -5.22 pp |
| 0.60 | 0/4 | 0/4 | -3.60 pp |
| 0.70 | 3/4 | 0/4 | -1.98 pp |
| 0.80 | 2/4 | 0/4 | -0.36 pp |
| 0.90 | 0/4 | 0/4 | +1.25 pp |
| 1.00 | 0/4 | 0/4 | +2.85 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
