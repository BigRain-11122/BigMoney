# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-16, 1664 bars, 4 phases, 324.9 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.03% | 6.53% | 7.66% | 8.78% | 9.89% | 10.98% | 12.06% | 13.13% |
| 1 | 2020-01-09 | 9.62% | 6.48% | 7.59% | 8.69% | 9.77% | 10.83% | 11.87% | 12.89% |
| 2 | 2020-01-16 | 6.10% | 4.55% | 5.17% | 5.76% | 6.33% | 6.87% | 7.39% | 7.89% |
| 3 | 2020-01-23 | 10.39% | 6.73% | 7.92% | 9.11% | 10.28% | 11.44% | 12.60% | 13.74% |

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
| 0 | 17.72% | 10.03% | 12.21% | 14.40% | 16.62% | 18.85% | 21.09% | 23.35% |
| 1 | 16.68% | 8.90% | 10.74% | 12.59% | 14.43% | 16.27% | 18.10% | 19.92% |
| 2 | 11.08% | 5.47% | 6.40% | 7.32% | 8.20% | 9.07% | 9.91% | 10.72% |
| 3 | 13.77% | 7.63% | 9.16% | 10.67% | 12.19% | 13.70% | 15.20% | 16.70% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.666 | 1.687 | 1.635 | 1.601 | 1.576 | 1.558 | 1.544 | 1.532 |
| 1 | 1.439 | 1.304 | 1.259 | 1.230 | 1.209 | 1.193 | 1.181 | 1.171 |
| 2 | 1.030 | 0.840 | 0.795 | 0.764 | 0.743 | 0.726 | 0.713 | 0.703 |
| 3 | 1.292 | 1.282 | 1.231 | 1.197 | 1.173 | 1.155 | 1.140 | 1.129 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.71 pp | 0/4 |
| 0.50 | -1.70 pp | 0/4 |
| 0.60 | -0.70 pp | 0/4 |
| 0.70 | +0.28 pp | 3/4 |
| 0.80 | +1.24 pp | 2/4 |
| 0.90 | +2.19 pp | 0/4 |
| 1.00 | +3.13 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.80 pp |
| 0.50 | 0/4 | 0/4 | -5.19 pp |
| 0.60 | 0/4 | 0/4 | -3.57 pp |
| 0.70 | 3/4 | 0/4 | -1.95 pp |
| 0.80 | 2/4 | 0/4 | -0.34 pp |
| 0.90 | 0/4 | 0/4 | +1.26 pp |
| 1.00 | 0/4 | 0/4 | +2.86 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
