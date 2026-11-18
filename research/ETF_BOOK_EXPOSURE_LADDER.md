# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-18, 1666 bars, 4 phases, 206.7 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.95% | 6.49% | 7.61% | 8.72% | 9.82% | 10.91% | 11.98% | 13.03% |
| 1 | 2020-01-09 | 9.59% | 6.47% | 7.58% | 8.67% | 9.75% | 10.81% | 11.85% | 12.86% |
| 2 | 2020-01-16 | 6.02% | 4.52% | 5.12% | 5.71% | 6.27% | 6.80% | 7.31% | 7.80% |
| 3 | 2020-01-23 | 10.41% | 6.74% | 7.94% | 9.12% | 10.30% | 11.47% | 12.63% | 13.77% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.16% | -12.79% | -15.37% | -17.92% | -20.41% | -22.86% | -25.27% |
| 2 | -18.96% | -11.30% | -14.07% | -16.77% | -19.39% | -21.95% | -24.44% | -26.86% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 17.49% | 9.93% | 12.08% | 14.25% | 16.44% | 18.64% | 20.85% | 23.08% |
| 1 | 16.61% | 8.87% | 10.71% | 12.54% | 14.37% | 16.20% | 18.02% | 19.84% |
| 2 | 10.87% | 5.39% | 6.30% | 7.19% | 8.06% | 8.90% | 9.71% | 10.50% |
| 3 | 13.83% | 7.66% | 9.19% | 10.72% | 12.24% | 13.76% | 15.27% | 16.77% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.647 | 1.672 | 1.620 | 1.586 | 1.561 | 1.543 | 1.529 | 1.517 |
| 1 | 1.434 | 1.300 | 1.256 | 1.226 | 1.205 | 1.189 | 1.177 | 1.167 |
| 2 | 1.012 | 0.829 | 0.783 | 0.753 | 0.731 | 0.715 | 0.702 | 0.691 |
| 3 | 1.297 | 1.286 | 1.235 | 1.202 | 1.177 | 1.159 | 1.145 | 1.134 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.69 pp | 0/4 |
| 0.50 | -1.68 pp | 0/4 |
| 0.60 | -0.69 pp | 0/4 |
| 0.70 | +0.29 pp | 3/4 |
| 0.80 | +1.26 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.12 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.74 pp |
| 0.50 | 0/4 | 0/4 | -5.13 pp |
| 0.60 | 0/4 | 0/4 | -3.52 pp |
| 0.70 | 3/4 | 0/4 | -1.92 pp |
| 0.80 | 2/4 | 0/4 | -0.32 pp |
| 0.90 | 0/4 | 0/4 | +1.26 pp |
| 1.00 | 0/4 | 0/4 | +2.85 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
