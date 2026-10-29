# ETF book -- does the buffer pay for itself anywhere on the arm grid?

Face: `results/etf_book_hysteresis_paths.json` (evidence cutoff **2026-10-29**, cost 0bp/side)

## Family verdict -- MIXED_NO_SURVIVOR

- 2 of 4 arms read as cost knobs (turnover down, return not settled: k=0.10, 0.20) and 2 fail the return floor outright (median dCAGR below -0.05pp: k=0.05, 0.35); no arm clears the rule, so the knob is not monotone and cannot be tuned into an edge

Return effect monotone in k: **False**

## Arms (20 cells each: 5 books x 4 phases, each cell against its own k=0)

| k | verdict | turnover down | median dCAGR | median dTurn | median dSharpe | breakeven cost (median, q25-q75) |
|---|---|---|---|---|---|---|
| 0.05 | REJECT | 100% | -0.145pp | -0.0303 | -0.0115 | 50.7 (-18.7-67.0) |
| 0.10 | COST_KNOB_ONLY | 100% | +0.040pp | -0.0513 | +0.0090 | -8.8 (-33.6-49.0) |
| 0.20 | COST_KNOB_ONLY | 100% | +0.065pp | -0.1038 | +0.0040 | -5.5 (-14.5-20.8) |
| 0.35 | REJECT | 100% | -0.130pp | -0.1808 | -0.0020 | 5.4 (-15.7-15.7) |

Breakeven cost = the per-side cost at which this cell's turnover saving equals the return it gave away. A cell that gains return has no breakeven (it already pays).

## Phase noise (the ruler these effects must beat)

| book | phases | CAGR min-max (pp) | CAGR IQR (pp) | Sharpe IQR |
|---|---|---|---|---|
| n12_r10 | 4 | 12.81 - 14.37 | 0.420 | 0.062 |
| n12_r20 | 4 | 9.09 - 10.91 | 0.530 | 0.100 |
| n12_r40 | 4 | 3.71 - 10.35 | 3.040 | 0.212 |
| n20_r20 | 4 | 6.81 - 8.93 | 0.703 | 0.102 |
| n8_r20 | 4 | 8.45 - 10.84 | 0.717 | 0.125 |

Median phase CAGR IQR across books: **0.703pp**

## Control

- k=0 production cell reproduces the card: published 0.0970 vs measured 0.0970 (delta 0.00pp, tol 0.005, within=True)

## Honest limits

- exploratory, no preregistration: ADOPT = survives its own path test, not a config change
- 5 books x 4 phases bounds phase luck inside one cycle; it does not sample the future
- survivor ETF pool, one window 2020-01 -> panel edge, one regime (2024+ strong)
- breakeven uses a linear decisions-per-year conversion and the cell's own turnover delta
- the buffer is path-dependent by construction: the grid, not one arm, is the unit
