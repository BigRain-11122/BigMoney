# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-06, 1658 bars, 4 phases, 287.8 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.97% | 6.47% | 7.59% | 8.70% | 9.79% | 10.87% | 11.93% | 12.98% |
| 1 | 2020-01-09 | 9.69% | 6.51% | 7.63% | 8.74% | 9.83% | 10.90% | 11.95% | 12.98% |
| 2 | 2020-01-16 | 6.24% | 4.61% | 5.24% | 5.85% | 6.43% | 6.99% | 7.52% | 8.04% |
| 3 | 2020-01-23 | 10.34% | 6.71% | 7.90% | 9.08% | 10.25% | 11.41% | 12.56% | 13.70% |

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
| 0 | 17.64% | 9.93% | 12.08% | 14.25% | 16.43% | 18.63% | 20.84% | 23.07% |
| 1 | 16.93% | 9.01% | 10.88% | 12.76% | 14.63% | 16.49% | 18.35% | 20.21% |
| 2 | 11.48% | 5.62% | 6.60% | 7.55% | 8.47% | 9.38% | 10.26% | 11.11% |
| 3 | 13.70% | 7.61% | 9.12% | 10.63% | 12.14% | 13.64% | 15.13% | 16.62% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.657 | 1.667 | 1.616 | 1.582 | 1.557 | 1.539 | 1.525 | 1.513 |
| 1 | 1.452 | 1.312 | 1.268 | 1.239 | 1.218 | 1.202 | 1.190 | 1.180 |
| 2 | 1.059 | 0.859 | 0.813 | 0.783 | 0.761 | 0.745 | 0.732 | 0.722 |
| 3 | 1.283 | 1.274 | 1.223 | 1.189 | 1.165 | 1.147 | 1.133 | 1.121 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 1 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.74 pp | 0/4 |
| 0.50 | -1.72 pp | 0/4 |
| 0.60 | -0.72 pp | 0/4 |
| 0.70 | +0.26 pp | 3/4 |
| 0.80 | +1.23 pp | 2/4 |
| 0.90 | +2.18 pp | 0/4 |
| 1.00 | +3.12 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.90 pp |
| 0.50 | 0/4 | 0/4 | -5.27 pp |
| 0.60 | 0/4 | 0/4 | -3.64 pp |
| 0.70 | 3/4 | 0/4 | -2.02 pp |
| 0.80 | 2/4 | 0/4 | -0.40 pp |
| 0.90 | 0/4 | 0/4 | +1.21 pp |
| 1.00 | 0/4 | 0/4 | +2.81 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
