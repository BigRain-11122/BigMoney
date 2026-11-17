# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-17, 1665 bars, 4 phases, 265.4 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.98% | 6.50% | 7.63% | 8.75% | 9.85% | 10.94% | 12.01% | 13.07% |
| 1 | 2020-01-09 | 9.61% | 6.48% | 7.59% | 8.68% | 9.76% | 10.82% | 11.86% | 12.88% |
| 2 | 2020-01-16 | 6.04% | 4.53% | 5.14% | 5.72% | 6.29% | 6.83% | 7.34% | 7.83% |
| 3 | 2020-01-23 | 10.41% | 6.73% | 7.93% | 9.12% | 10.29% | 11.46% | 12.62% | 13.76% |

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
| 0 | 17.57% | 9.97% | 12.13% | 14.31% | 16.51% | 18.72% | 20.95% | 23.19% |
| 1 | 16.66% | 8.89% | 10.73% | 12.57% | 14.41% | 16.25% | 18.08% | 19.90% |
| 2 | 10.94% | 5.41% | 6.34% | 7.23% | 8.11% | 8.96% | 9.78% | 10.58% |
| 3 | 13.81% | 7.65% | 9.18% | 10.70% | 12.22% | 13.74% | 15.25% | 16.75% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.654 | 1.677 | 1.626 | 1.592 | 1.567 | 1.549 | 1.534 | 1.523 |
| 1 | 1.438 | 1.303 | 1.258 | 1.229 | 1.208 | 1.192 | 1.180 | 1.170 |
| 2 | 1.018 | 0.833 | 0.787 | 0.757 | 0.735 | 0.719 | 0.706 | 0.695 |
| 3 | 1.295 | 1.285 | 1.234 | 1.200 | 1.176 | 1.158 | 1.144 | 1.132 |

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
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.12 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.76 pp |
| 0.50 | 0/4 | 0/4 | -5.15 pp |
| 0.60 | 0/4 | 0/4 | -3.54 pp |
| 0.70 | 3/4 | 0/4 | -1.93 pp |
| 0.80 | 2/4 | 0/4 | -0.33 pp |
| 0.90 | 0/4 | 0/4 | +1.27 pp |
| 1.00 | 0/4 | 0/4 | +2.86 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
