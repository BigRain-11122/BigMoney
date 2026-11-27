# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-26, 1672 bars, 4 phases, 312.2 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.47% | 6.28% | 7.34% | 8.40% | 9.44% | 10.47% | 11.48% | 12.47% |
| 1 | 2020-01-09 | 9.20% | 6.30% | 7.37% | 8.42% | 9.45% | 10.46% | 11.46% | 12.43% |
| 2 | 2020-01-16 | 5.59% | 4.35% | 4.91% | 5.45% | 5.97% | 6.46% | 6.92% | 7.37% |
| 3 | 2020-01-23 | 10.16% | 6.62% | 7.78% | 8.94% | 10.09% | 11.22% | 12.34% | 13.46% |

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
| 0 | 16.19% | 9.38% | 11.39% | 13.40% | 15.42% | 17.46% | 19.50% | 21.56% |
| 1 | 15.56% | 8.44% | 10.17% | 11.89% | 13.60% | 15.31% | 17.01% | 18.69% |
| 2 | 9.79% | 4.97% | 5.78% | 6.56% | 7.32% | 8.05% | 8.75% | 9.43% |
| 3 | 13.18% | 7.36% | 8.82% | 10.26% | 11.71% | 13.14% | 14.57% | 15.98% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.528 | 1.581 | 1.530 | 1.496 | 1.472 | 1.453 | 1.439 | 1.428 |
| 1 | 1.352 | 1.244 | 1.200 | 1.170 | 1.149 | 1.133 | 1.121 | 1.111 |
| 2 | 0.916 | 0.769 | 0.723 | 0.693 | 0.671 | 0.655 | 0.642 | 0.632 |
| 3 | 1.244 | 1.242 | 1.191 | 1.158 | 1.133 | 1.115 | 1.101 | 1.090 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.47 pp | 0/4 |
| 0.50 | -1.50 pp | 0/4 |
| 0.60 | -0.55 pp | 2/4 |
| 0.70 | +0.38 pp | 3/4 |
| 0.80 | +1.30 pp | 2/4 |
| 0.90 | +2.19 pp | 0/4 |
| 1.00 | +3.08 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.14 pp |
| 0.50 | 0/4 | 0/4 | -4.64 pp |
| 0.60 | 2/4 | 0/4 | -3.15 pp |
| 0.70 | 3/4 | 0/4 | -1.67 pp |
| 0.80 | 2/4 | 0/4 | -0.19 pp |
| 0.90 | 0/4 | 0/4 | +1.28 pp |
| 1.00 | 0/4 | 0/4 | +2.74 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
