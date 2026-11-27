# One wallet, two books -- the order list

generated 2026-11-27T13:37:26+08:00 | priced on bar 2026-11-26 | split 30% CB / 70% ETF (from the blend face)

> with one wallet and the 30/70 split the blend face calls best, what exactly do I buy -- lots, fees, and the cash that is left?

## What the two sleeves are on this bar

* ETF sleeve -- 5 names 159207, 159549, 515300, 562060, 513690, vol-target scale 0.7507, so 24.9% of *its own* budget sits in cash by design
* CB sleeve -- 20 names, one board lot each costs 86167 CNY of wallet before the sleeve fits at all

## Wallet ladder

| wallet CNY | verdict | ETF names | CB names | invested | cash | of which design cash | of which lot-grid cash |
|---|---|---|---|---|---|---|---|
| 50,000 | CB_SLEEVE_TOO_SMALL | 5/5 | 0/20 | 26,096 | 47.8% | 8725 | 30.4% |
| 86,167 | PARTIAL | 5/5 | 19/20 | 65,151 | 24.4% | 15036 | 6.9% |
| 86,168 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 66,443 | 22.9% | 15036 | 5.4% |
| 100,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 73,911 | 26.1% | 17449 | 8.6% |
| 200,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 152,502 | 23.7% | 34899 | 6.3% |
| 500,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 400,980 | 19.8% | 87246 | 2.4% |
| 1,000,000 | HOLDS_THE_BLEND | 5/5 | 20/20 | 814,111 | 18.6% | 174493 | 1.1% |

### The published minimum is one yuan short

`book_pair_blend` prints a minimum wallet of **86,167.00 CNY** (25850.20 / 0.30, rounded to the yuan). At that wallet the CB sleeve budgets 25,850.10 CNY against a 25,850.20 CNY lot rung, so **19 of 20 names are held** -- the book is not the backtested book. At **86,168 CNY** all 20 hold. The difference is 1 CNY, and it is the whole point of printing a ticket instead of a ratio.

## How this page can be wrong

* prices are each parent's as-of close; a real order pays the next open plus impact
* the CB parent prices no broker bill, so this ticket's fee line is the ETF sleeve only
* the 30/70 split is sample-in optimal on the overlap (2020-01..2026-11) -- it is the blend face's best, not a law
* cash between the two sleeves is not rebalanced here; the blend face's own note says it models no transfer cost
* the CB sleeve's twenty names are chosen on one bar; names that leave the pool before the next rebalance are the book's problem, not the ticket's
