# ETF book -- the sell half of the ticket

generated 2026-11-22T12:06:35+0800 | ticket `results/etf_book_order/TICKET-2026-11-20.json` (ticket generated 2026-11-22T11:07:49+08:00) | cutoff 2026-11-20

## What this answers

when the sizing dial goes down, what has to be SOLD -- which whole lots, how many CNY, and what does it cost.

The ticket only ever looked up: every row carried `next_lot_dk_pp`, the k rise needed to ADD a lot. When the dial goes down -- which is what happens when the book's beta to the market rises -- the reader had a percentage and no lots. This is that mirror.

## The sell ladder

| k | beta_hat required | beta rise | lots sold | names moving | CNY freed | % NAV | cost CNY |
|---|---|---|---|---|---|---|---|
| 0.3850 | 0.519 | 13.0% | 369 | 5 | 50,100 | 5.010 | 40.08 |
| 0.3350 | 0.597 | 29.9% | 737 | 5 | 100,092 | 10.009 | 80.07 |
| 0.2850 | 0.702 | 52.6% | 1106 | 5 | 150,192 | 15.019 | 120.15 |
| 0.2350 | 0.851 | 85.1% | 1473 | 5 | 200,014 | 20.001 | 160.01 |
| 0.2000 | 1.000 | 117.5% | 1731 | 5 | 235,048 | 23.505 | 188.04 |

## What it takes to sell the FIRST lot of each name

| name | lots held | k fall needed | one lot is | beta_hat at that point |
|---|---|---|---|---|
| 510760 | 708 | 0.0291 pp | 122.80 | 0.460 |
| 512040 | 735 | 0.0250 pp | 118.30 | 0.460 |
| 159655 | 469 | 0.0240 pp | 185.40 | 0.460 |
| 513690 | 779 | 0.0321 pp | 111.60 | 0.460 |
| 159519 | 511 | 0.0142 pp | 170.20 | 0.460 |

## Verdict

`DE_RISK_COSTS_LESS_THAN_ONE_TURN`

If the sizing dial goes from 0.4350 to 0.3850 (beta_hat 0.460 -> 0.519), the sheet sells 369 lots across 5 names for 50,100 CNY, which frees 5.01% of NAV and costs 40.08 CNY at 8.0 bp per side; going all the way to 0.20 sells 235,048 CNY for 188.04 CNY, against 348 CNY for one ordinary turn.

## What this face does not say

- same book re-sized, not a new ranking: a real de-risk executes on a decision bar at that bar's prices, so every CNY here is today's price
- k moves only when beta_hat moves; beta_hat is the engine's expanding slope, not a number this face estimates
- whole lots only: each name floors separately, so the freed CNY differs from (k_now - k_target) * nav by at most one lot per name, in either direction
- this face does not decide that a de-risk is due -- it prices the action once the sizing rule has already said so

Next decision bar: `2026-12-09`.
