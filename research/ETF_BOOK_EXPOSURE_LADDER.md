# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-25, 1671 bars, 4 phases, 362.3 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.40% | 6.25% | 7.31% | 8.36% | 9.39% | 10.41% | 11.41% | 12.40% |
| 1 | 2020-01-09 | 9.16% | 6.29% | 7.35% | 8.40% | 9.43% | 10.44% | 11.42% | 12.39% |
| 2 | 2020-01-16 | 5.51% | 4.31% | 4.87% | 5.40% | 5.91% | 6.39% | 6.85% | 7.28% |
| 3 | 2020-01-23 | 10.11% | 6.60% | 7.76% | 8.91% | 10.05% | 11.18% | 12.30% | 13.40% |

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
| 0 | 16.03% | 9.32% | 11.30% | 13.30% | 15.30% | 17.32% | 19.35% | 21.38% |
| 1 | 15.48% | 8.41% | 10.13% | 11.84% | 13.55% | 15.24% | 16.93% | 18.61% |
| 2 | 9.59% | 4.90% | 5.68% | 6.45% | 7.18% | 7.89% | 8.57% | 9.23% |
| 3 | 13.07% | 7.31% | 8.76% | 10.19% | 11.62% | 13.04% | 14.45% | 15.86% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.515 | 1.571 | 1.520 | 1.486 | 1.461 | 1.443 | 1.429 | 1.417 |
| 1 | 1.346 | 1.239 | 1.195 | 1.166 | 1.145 | 1.129 | 1.117 | 1.107 |
| 2 | 0.899 | 0.757 | 0.712 | 0.682 | 0.660 | 0.644 | 0.631 | 0.621 |
| 3 | 1.235 | 1.234 | 1.184 | 1.150 | 1.126 | 1.107 | 1.093 | 1.082 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.43 pp | 0/4 |
| 0.50 | -1.47 pp | 0/4 |
| 0.60 | -0.53 pp | 2/4 |
| 0.70 | +0.40 pp | 3/4 |
| 0.80 | +1.31 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.07 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.06 pp |
| 0.50 | 0/4 | 0/4 | -4.58 pp |
| 0.60 | 2/4 | 0/4 | -3.10 pp |
| 0.70 | 3/4 | 0/4 | -1.63 pp |
| 0.80 | 2/4 | 0/4 | -0.17 pp |
| 0.90 | 0/4 | 0/4 | +1.28 pp |
| 1.00 | 0/4 | 0/4 | +2.73 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
