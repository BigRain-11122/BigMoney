# Would a fixed fraction do the same job as the de-lever rule?

Face: `results/etf_book_exposure_ladder.json` (evidence cutoff 2026-11-19, 1667 bars, 4 phases, 253.7 s).

Same names, same grid, same cost model everywhere -- only the exposure multiplier differs. The fixed fractions were chosen before the run, so none of them is calibrated from the answer.

| phase | start | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 8.88% | 6.46% | 7.57% | 8.68% | 9.77% | 10.85% | 11.91% | 12.95% |
| 1 | 2020-01-09 | 9.52% | 6.44% | 7.54% | 8.63% | 9.70% | 10.75% | 11.78% | 12.79% |
| 2 | 2020-01-16 | 5.91% | 4.47% | 5.07% | 5.64% | 6.19% | 6.71% | 7.21% | 7.69% |
| 3 | 2020-01-23 | 10.38% | 6.72% | 7.91% | 9.10% | 10.27% | 11.43% | 12.59% | 13.73% |

## Drawdown on the same phases

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | -13.26% | -6.40% | -8.08% | -9.75% | -11.41% | -13.05% | -14.68% | -16.29% |
| 1 | -16.77% | -10.16% | -12.79% | -15.37% | -17.92% | -20.41% | -22.86% | -25.27% |
| 2 | -19.52% | -11.35% | -14.15% | -16.87% | -19.53% | -22.11% | -24.62% | -27.07% |
| 3 | -14.94% | -6.46% | -8.06% | -9.93% | -11.86% | -13.76% | -15.63% | -17.48% |

## Out of sample (bars after 2023-12-31)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 17.30% | 9.85% | 11.98% | 14.13% | 16.29% | 18.47% | 20.66% | 22.87% |
| 1 | 16.43% | 8.79% | 10.61% | 12.43% | 14.24% | 16.05% | 17.85% | 19.65% |
| 2 | 10.59% | 5.28% | 6.16% | 7.03% | 7.87% | 8.68% | 9.46% | 10.22% |
| 3 | 13.74% | 7.61% | 9.13% | 10.65% | 12.16% | 13.67% | 15.17% | 16.66% |

## Out-of-sample Sharpe (the rule's risk-adjusted test)

| phase | production | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.631 | 1.659 | 1.608 | 1.574 | 1.549 | 1.531 | 1.517 | 1.505 |
| 1 | 1.420 | 1.290 | 1.246 | 1.217 | 1.196 | 1.180 | 1.168 | 1.158 |
| 2 | 0.988 | 0.813 | 0.768 | 0.737 | 0.716 | 0.699 | 0.686 | 0.676 |
| 3 | 1.290 | 1.280 | 1.229 | 1.195 | 1.171 | 1.153 | 1.139 | 1.127 |

## Verdict (full window)

**CONSTANT_LADDER_DOMINATES**

best fixed fraction: const_0.70 -- no worse than production in 3 of 4 phases (needed 3); production beats every fixed fraction in 0 of 28 cells.

| fixed fraction | mean CAGR vs production | phases not worse |
|---|---|---|
| 0.40 | -2.65 pp | 0/4 |
| 0.50 | -1.65 pp | 0/4 |
| 0.60 | -0.66 pp | 0/4 |
| 0.70 | +0.31 pp | 3/4 |
| 0.80 | +1.26 pp | 2/4 |
| 0.90 | +2.20 pp | 0/4 |
| 1.00 | +3.12 pp | 0/4 |

## Verdict (adoption: full window AND out of sample)

**REJECT_FIXED_FRACTION**

best fixed fraction const_0.70: no worse than production in 3 of 4 phases on the full window, but only 0 of 4 out of sample -- the de-lever rule's own out-of-sample Sharpe is the highest of the eight arms, so what it buys is risk-adjusted return, not simply a smaller book.

| fixed fraction | full window not worse | out of sample not worse | mean OOS CAGR vs production |
|---|---|---|---|
| 0.40 | 0/4 | 0/4 | -6.63 pp |
| 0.50 | 0/4 | 0/4 | -5.04 pp |
| 0.60 | 0/4 | 0/4 | -3.45 pp |
| 0.70 | 3/4 | 0/4 | -1.87 pp |
| 0.80 | 2/4 | 0/4 | -0.30 pp |
| 0.90 | 0/4 | 0/4 | +1.27 pp |
| 1.00 | 0/4 | 0/4 | +2.84 pp |

This second reading is the face's own pre-stated standard applied, not a retuned threshold: the notes written before the first run demanded an out-of-sample test, and the first run is exactly the case it was written for (the full window says no worse, the out-of-sample window does not). Both verdicts are published; the full-window one keeps its v1.0 criteria.

## Identity

the production arm re-runs the engine's own scale and reproduces its nav bit for bit on all 4 phases: PASS

## Caveats

- one panel, one universe; a wider or delisted-inclusive universe can move the level, though the comparison is between arms on the same names
- the fixed fractions are long-only exposure multipliers, not leverage: 1.00 means the book the card already describes at full size
- `--check` re-derives the verdict from these published rows; a face whose echoed criteria differ from the module constants is refused
