# Three books, one window, one clock

Window **2020-01-03 .. 2026-11-26** (1671 bars, 244 days/yr). Cutoff 2026-11-26.

| book | what the return is per | cagr | vol | sharpe | max drawdown | total |
|---|---|---|---|---|---|---|
| ETF composite book | capital | 9.94% | 10.47% | 0.950 | -10.11% | 91.27% |
| CB dual-low sleeve | capital | 6.34% | 12.93% | 0.491 | -22.59% | 52.34% |
| index-futures carry (basis arm) | notional | 10.22% | 3.21% | 3.189 | -2.47% | 94.67% |

Year by year, same calendar:

| year | ETF | CB | carry (basis) |
|---|---|---|---|
| 2020 | 4.75% | 10.76% | 16.68% |
| 2021 | 5.17% | 33.25% | 10.37% |
| 2022 | 2.88% | -4.87% | 6.97% |
| 2023 | 2.38% | -2.18% | 5.54% |
| 2024 | 12.41% | 27.79% | 7.22% |
| 2025 | 42.47% | 4.79% | 13.80% |
| 2026 | 0.86% | -20.75% | 9.19% |

## The same leg, three published Sharpes

| arm | sharpe | what it is | window |
|---|---|---|---|
| carry_basis_only | 2.9720 | the basis move net of cost -- no index exposure, no hedge, no account | 2017-01-18..2026-11-25 |
| carry_excess_hedged | 1.4162 | the same day minus the same notional's index return -- the residual a hedge leaves | 2018-10-22..2026-11-20 |
| carry_unhedged | 0.5057 | per-lot daily points on the held contract -- carries the index's own vol | 2018-10-22..2026-11-20 |

## What it takes to hold it

- sizing rule: lots = floor(8% x capital / 91,029 CNY per lot)
- wallet 1,000,000 CNY -> **0 lots**; first executable capital 1,137,862 CNY (gap 137,862 CNY)
- the book's decision on the desk ticket: `WITHDRAW_FROM_TICKET`
- capital-return identity at the 8% target: hedged arm 11.33%, basis arm 23.78%

## Verdict

`THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD`

On one window (2020-01-03..2026-11-26) and one clock the three books print 9.94% / 6.34% / 10.22% (ETF / CB / carry basis). The carry line wins and cannot be bought: it is the basis arm, quoted per notional, and the family's own hedged arm on the same leg is 1.42 Sharpe, not 2.97. At the book's 8.0% vol target one IC lot still needs 1,137,862 CNY of capital against a 1,000,000 CNY wallet, so the executable line is 0 lots.

### Caveats

- the carry arm is a daily excess return on notional; the ETF/CB books are returns on capital
- the carry row's sharpe on this common window is not the family's published 2.97 — that one is the 2017-2026 IC-only window; the two differ because the window differs, not because the rule changed
- 2020-01..2022-07 the carry arm is IC only (IM listed 2022-07-25); after that it is the mean of the two legs
- the ETF book's vol target makes its drawdown a dial, so its return is not a fair 'more risk more return' comparison
- costs: ETF/CB 10bp per side as published, carry 1.5bp per side as published

Generated 2026-11-27T23:13:43+08:00. Inputs are hashed; `--check` says STALE when one of them moves.
