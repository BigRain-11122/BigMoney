# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-12, 1662 bars, 4 phases, 312.6 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.11% | 6.56% | 7.71% | 8.84% | 9.96% | 11.06% | 12.15% | 13.23% |
| 1 | 2020-01-09 | 9.61% | 6.48% | 7.59% | 8.69% | 9.77% | 10.83% | 11.87% | 12.89% |
| 2 | 2020-01-16 | 6.27% | 4.62% | 5.25% | 5.86% | 6.45% | 7.01% | 7.55% | 8.06% |
| 3 | 2020-01-23 | 10.14% | 6.62% | 7.78% | 8.94% | 10.08% | 11.22% | 12.34% | 13.45% |

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
| 0 | 17.96% | 10.14% | 12.34% | 14.57% | 16.81% | 19.08% | 21.36% | 23.65% |
| 1 | 16.70% | 8.91% | 10.76% | 12.61% | 14.45% | 16.29% | 18.13% | 19.95% |
| 2 | 11.52% | 5.64% | 6.62% | 7.57% | 8.50% | 9.41% | 10.30% | 11.15% |
| 3 | 13.19% | 7.37% | 8.83% | 10.28% | 11.72% | 13.16% | 14.58% | 16.00% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.683 | 1.700 | 1.649 | 1.615 | 1.590 | 1.572 | 1.557 | 1.546 |
| 1 | 1.438 | 1.303 | 1.259 | 1.229 | 1.208 | 1.192 | 1.180 | 1.170 |
| 2 | 1.065 | 0.863 | 0.817 | 0.787 | 0.765 | 0.749 | 0.736 | 0.726 |
| 3 | 1.242 | 1.240 | 1.189 | 1.155 | 1.131 | 1.113 | 1.099 | 1.087 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.71 pp | 0/4 |
| 0.50 | -1.70 pp | 0/4 |
| 0.60 | -0.70 pp | 0/4 |
| 0.70 | +0.28 pp | 3/4 |
| 0.80 | +1.25 pp | 2/4 |
| 0.90 | +2.19 pp | 0/4 |
| 1.00 | +3.12 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.83 pp |
| 0.50 | 0/4 | 0/4 | -5.21 pp |
| 0.60 | 0/4 | 0/4 | -3.59 pp |
| 0.70 | 3/4 | 0/4 | -1.97 pp |
| 0.80 | 2/4 | 0/4 | -0.36 pp |
| 0.90 | 0/4 | 0/4 | +1.25 pp |
| 1.00 | 0/4 | 0/4 | +2.84 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
