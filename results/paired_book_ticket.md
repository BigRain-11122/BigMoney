# One wallet, two books -- the order list

generated 2026-11-28T12:03:14+08:00 | priced on bar 2026-11-27 | split 30% CB / 70% ETF (from the blend face)

> with one wallet and the 30/70 split the blend face calls best, what exactly do I buy -- lots, fees, and the cash that is left?

## What the two sleeves are on this bar

* ETF sleeve -- 5 names 515020, 512820, 515290, 515300, 159887, vol-target scale 0.5215, so 47.9% of *its own* budget sits in cash by design
* CB sleeve -- 20 names, one board lot each costs 86253 CNY of wallet before the sleeve fits at all

## Wallet ladder

| wallet CNY | verdict | ETF names | CB names | invested | cash | of which design cash | of which lot-grid cash |
|---|---|---|---|---|---|---|---|
| 50,000 | CB_SLEEVE_TOO_SMALL | 5/5 | 0/20 | 17,803 | 64.3% | 16748 | 30.9% |
| 86,253 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 52,662 | 38.9% | 28892 | 5.4% |
| 100,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 57,479 | 42.5% | 33496 | 9.0% |
| 200,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 119,808 | 40.1% | 66992 | 6.6% |
| 500,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 320,500 | 35.9% | 167481 | 2.4% |
| 1,000,000 | HOLDS_THE_BLEND | 5/5 | 20/20 | 654,760 | 34.5% | 334962 | 1.0% |

### The published minimum is one yuan short

`book_pair_blend` prints a minimum wallet of **86,253.00 CNY** (25875.80 / 0.30, rounded to the yuan). At that wallet the CB sleeve budgets 25,875.90 CNY against a 25,875.80 CNY lot rung, so **20 of 20 names are held** -- the book is not the backtested book. At **86,253 CNY** all 20 hold. The difference is 0 CNY, and it is the whole point of printing a ticket instead of a ratio.

## How this page can be wrong

* prices are each parent's as-of close; a real order pays the next open plus impact
* the CB parent prices no broker bill, so this ticket's fee line is the ETF sleeve only
* the 30/70 split is sample-in optimal on the overlap (2020-01..2026-11) -- it is the blend face's best, not a law
* cash between the two sleeves is not rebalanced here; the blend face's own note says it models no transfer cost
* the CB sleeve's twenty names are chosen on one bar; names that leave the pool before the next rebalance are the book's problem, not the ticket's
