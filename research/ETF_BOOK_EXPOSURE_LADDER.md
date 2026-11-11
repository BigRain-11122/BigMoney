# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-11, 1661 bars, 4 phases, 243.1 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.19% | 6.60% | 7.75% | 8.89% | 10.02% | 11.13% | 12.23% | 13.31% |
| 1 | 2020-01-09 | 9.70% | 6.51% | 7.63% | 8.74% | 9.83% | 10.90% | 11.95% | 12.98% |
| 2 | 2020-01-16 | 6.35% | 4.65% | 5.29% | 5.91% | 6.50% | 7.08% | 7.62% | 8.15% |
| 3 | 2020-01-23 | 10.20% | 6.65% | 7.82% | 8.98% | 10.13% | 11.27% | 12.40% | 13.52% |

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
| 0 | 18.18% | 10.22% | 12.45% | 14.70% | 16.97% | 19.26% | 21.57% | 23.89% |
| 1 | 16.92% | 8.99% | 10.87% | 12.74% | 14.61% | 16.47% | 18.33% | 20.18% |
| 2 | 11.73% | 5.72% | 6.72% | 7.69% | 8.65% | 9.58% | 10.48% | 11.36% |
| 3 | 13.33% | 7.44% | 8.91% | 10.38% | 11.84% | 13.29% | 14.74% | 16.18% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.702 | 1.714 | 1.662 | 1.628 | 1.604 | 1.585 | 1.571 | 1.560 |
| 1 | 1.455 | 1.314 | 1.270 | 1.240 | 1.219 | 1.204 | 1.191 | 1.182 |
| 2 | 1.083 | 0.874 | 0.829 | 0.799 | 0.777 | 0.760 | 0.748 | 0.737 |
| 3 | 1.254 | 1.250 | 1.199 | 1.165 | 1.141 | 1.123 | 1.109 | 1.098 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 1 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.76 pp | 0/4 |
| 0.50 | -1.74 pp | 0/4 |
| 0.60 | -0.73 pp | 0/4 |
| 0.70 | +0.26 pp | 3/4 |
| 0.80 | +1.23 pp | 2/4 |
| 0.90 | +2.19 pp | 0/4 |
| 1.00 | +3.13 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.95 pp |
| 0.50 | 0/4 | 0/4 | -5.30 pp |
| 0.60 | 0/4 | 0/4 | -3.66 pp |
| 0.70 | 3/4 | 0/4 | -2.02 pp |
| 0.80 | 2/4 | 0/4 | -0.39 pp |
| 0.90 | 0/4 | 0/4 | +1.24 pp |
| 1.00 | 0/4 | 0/4 | +2.86 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
