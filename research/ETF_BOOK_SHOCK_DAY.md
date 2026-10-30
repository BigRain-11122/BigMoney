# ETF book -- what a market gap actually costs

Evidence cutoff 2026-10-30 · rule beta target 0.20 · rebalance 20 bars · cost 8.0 bp/side

## The answer

the book's realized beta to 510300 is 0.12 over its whole history and 0.21 on the last 250 bars (the ticket trades to 0.20) -- on the 20 worst index days the book averaged -0.47% while the index averaged -3.87%, so an index gap costs that beta's share of the shock, never the deployed share

## Realized beta

| window | bars | beta |
| --- | --- | --- |
| full history | 1525 | 0.1200 |
| last 250 bars | 250 | 0.2090 |

Verdict: **BETA_MATCHED** (band 0.10..0.30).

## The book's own worst days

| face | book | 510300 |
| --- | --- | --- |
| worst day | -4.70% (2025-07-07) | -8.84% |
| 1st percentile | -1.22% | -3.04% |
| 5th percentile | -0.53% | -1.72% |
| daily sd | 0.41% | 1.16% |

**Price quality**: the panel carries 168 unit-change prints and the contamination face calls the effect MATERIAL. On repaired prices the same rule's worst day is -2.88% (2025-04-23) -- so the worst day quoted above is a print, not a market day. Source: results/etf_book_flip_contamination.json.

## On the 20 worst index days (measured, not assumed)

| date | 510300 | book |
| --- | --- | --- |
| 2024-10-09 | -8.84% | -0.35% |
| 2025-04-07 | -6.67% | -1.96% |
| 2022-04-25 | -4.82% | -1.30% |
| 2022-03-15 | -4.77% | -0.57% |
| 2020-07-24 | -4.45% | -1.46% |
| 2021-02-22 | -3.57% | -0.74% |
| 2021-03-08 | -3.53% | -0.07% |
| 2021-07-27 | -3.47% | -0.31% |

Mean on those days: index -3.87% / book -0.47% (ratio 0.121) · book worst -1.96% on 2025-04-07 · book finished up on 15% of them.

## Tomorrow, in money

Priced on results/etf_book_order/TICKET-2026-10-30.json: NAV +1,000,000 CNY, deployed +471,226 CNY (47.1%), cash +528,774 CNY.

| index gaps | book returns | costs you | the naive 'shock x deployed' |
| --- | --- | --- | --- |
| -3% | -0.36% | -3,599 CNY | -14,145 CNY |
| -5% | -0.60% | -5,998 CNY | -23,574 CNY |
| -8% | -0.96% | -9,597 CNY | -37,719 CNY |

The last column is what an operator computes by hand and it overstates the loss by roughly the inverse of the beta scaling.

Descriptive face: no rule is adopted here, nothing is traded, and the shocks are index moves applied through the measured beta, not forecasts.
