# What a roll costs when you measure it

The roll book switches both legs at the same close, so the seam itself is free by construction. What is *not* free is crossing the spread twice on the way through. That charge has been `commission + one tick each leg` = **1.5bp per roll** -- an arithmetic composition of the fee and the minimum tick, not a measurement of anything anybody quoted.

This page measures it from the only tape the repo has: each contract's own daily high and low. Corwin-Schultz (2012) effective spread from daily high/low, 20-day rolling median, one-bar lag; imported from etf_book_cost_tape.cs_spread. Per roll the cost is half the incumbent's spread plus half the successor's plus the fee, priced at the roll date with the estimator's own one-bar lag.

Evidence cutoff: `None`  ·  generated 2026-11-17T21:43:19

## §一 The measured cost of one roll (bp, per product)

| product | rolls | rolls/yr | p25 | **median** | mean | p75 | max | rolls at or under 1.5bp | unpriced |
|---|---|---|---|---|---|---|---|---|---|

The last two columns are the honesty of the estimate. `at or under 1.5bp` is the share of rolls whose range implies a spread no wider than the document floor -- a face that only printed the median would hide that the floor is met on a minority of rolls, and would also hide that the rest of the distribution is the estimator saturating rather than the market quoting. `unpriced` counts rolls where the cache could not price a leg; those are filled with that product's own median and the count is printed rather than the roll being dropped.

## §二 What the measured cost does to the carry

| product | discount gross | breakeven bp/roll | net @1.5bp (published) | net @measured median | net @measured p75 |
|---|---|---|---|---|---|

Admission line 3.0%/yr, the same one the basis pages use.

## §三 The verdict

| | products |
|---|---|
| admitted at the published floor | — |
| admitted at the measured median | **—** |
| admitted at the measured 75th pct | — |
| below the line before any cost | — |
| flips, published floor → measured | **—** |

| | products |
|---|---|
| break-even **inside** the unmeasured cost band (no verdict) | **—** |
| break-even above the whole band (admitted whatever the spread) | — |
| below the line whatever the spread (absent) | — |

The cost of one roll is bounded below by the exchange document (fee + one tick each leg = 1.5bp) and above by what the day's range implies. Neither end is a quote, and the upper end is plainly saturated: it returns a number of the same order as the day's own range (0.9-2.6%) on a contract whose tick is 0.5bp, so it cannot resolve a spread two orders of magnitude below the range it reads.

## §四 Is the estimator reading a spread, or a range?

Split the rolls by the day's own range. If the number were a quote, a quiet third and a violent third would imply the same spread. If it rises with the range, the estimator is carrying volatility and only its *ordering* is earned -- which is exactly the difference between "the roll costs 20bp" and "the estimator says 20bp on average and 6bp on the quiet third".

| product | quiet third | middle third | violent third | violent / quiet | flag |
|---|---|---|---|---|---|

## §五 What this face does not know

* the band is the honest form of the number: the p25 column is the quiet-day reading and p75 the violent-day one, printed side by side so no single figure has to carry the argument;
* the estimator clips a negative implied spread to zero. In a trending market the implied serial covariance is negative and the reading becomes 0 -- those rolls are inside the `at or under 1.5bp` column, and they pull the median down;
* the fee is the exchange's published rate, and it is the one input here that is a document rather than a tape.

## Roll ledger (last six per product)
