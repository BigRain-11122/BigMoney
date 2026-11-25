# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-24, 1670 bars, 4 phases, 265.9 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.59% | 6.33% | 7.41% | 8.48% | 9.54% | 10.58% | 11.61% | 12.62% |
| 1 | 2020-01-09 | 9.23% | 6.32% | 7.39% | 8.44% | 9.48% | 10.49% | 11.49% | 12.47% |
| 2 | 2020-01-16 | 5.77% | 4.42% | 5.00% | 5.55% | 6.09% | 6.60% | 7.08% | 7.55% |
| 3 | 2020-01-23 | 10.17% | 6.62% | 7.79% | 8.95% | 10.10% | 11.23% | 12.36% | 13.47% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.58% | -13.34% | -16.05% | -18.70% | -21.30% | -23.85% | -26.35% |
| 2 | -20.84% | -11.93% | -14.85% | -17.69% | -20.45% | -23.13% | -25.73% | -28.26% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 16.52% | 9.52% | 11.56% | 13.62% | 15.68% | 17.76% | 19.85% | 21.95% |
| 1 | 15.66% | 8.49% | 10.22% | 11.95% | 13.68% | 15.40% | 17.11% | 18.80% |
| 2 | 10.22% | 5.14% | 5.99% | 6.82% | 7.62% | 8.39% | 9.14% | 9.87% |
| 3 | 13.22% | 7.38% | 8.84% | 10.29% | 11.73% | 13.17% | 14.60% | 16.03% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.560 | 1.605 | 1.554 | 1.520 | 1.496 | 1.477 | 1.463 | 1.452 |
| 1 | 1.360 | 1.249 | 1.205 | 1.176 | 1.155 | 1.139 | 1.126 | 1.117 |
| 2 | 0.956 | 0.794 | 0.748 | 0.718 | 0.696 | 0.680 | 0.667 | 0.657 |
| 3 | 1.247 | 1.244 | 1.194 | 1.160 | 1.136 | 1.117 | 1.103 | 1.092 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.52 pp | 0/4 |
| 0.50 | -1.54 pp | 0/4 |
| 0.60 | -0.58 pp | 1/4 |
| 0.70 | +0.36 pp | 3/4 |
| 0.80 | +1.28 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.09 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.27 pp |
| 0.50 | 0/4 | 0/4 | -4.75 pp |
| 0.60 | 1/4 | 0/4 | -3.24 pp |
| 0.70 | 3/4 | 0/4 | -1.73 pp |
| 0.80 | 2/4 | 0/4 | -0.22 pp |
| 0.90 | 0/4 | 0/4 | +1.27 pp |
| 1.00 | 0/4 | 0/4 | +2.76 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
