# index-futures carry: what it is worth in risk units

Generated 2026-11-15T05:54:22 · evidence cutoff 2026-11-13 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.65% a year compounded, vol 10.33%, Sharpe 1.118, max drawdown -10.56%, worst year 3.14%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 67 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.02 | 8.76 | 5.87 | 1.461 | -5.64 | 174 (6) | -0.82 |
| IF | 8.02 | 3.57 | 4.38 | 0.823 | -6.55 | 300 (6) | -3.15 |
| IM | 4.28 | 10.20 | 6.82 | 1.459 | -5.05 | 122 (7) | 4.44 |
| IH | 8.02 | 2.39 | 4.40 | 0.559 | -7.42 | 479 (3) | -3.63 |

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 12.04 | -7.67 | -0.039 | 0.30 | +0.325 | SLEEVE_CANDIDATE |
| IF | x1.83 | 6.46 | -11.84 | 0.053 | 0.30 | +0.131 | REFUSE |
| IM | x1.17 | 12.02 | -5.91 | -0.064 | 0.30 | +0.387 | SLEEVE_CANDIDATE |
| IH | x1.82 | 4.24 | -13.36 | 0.056 | 0.30 | +0.084 | REFUSE |

- **IC**: carry 12.04% at target risk, corr -0.039, blend Sharpe +0.325
- **IF**: at 8.0% vol the sleeve earns 6.46% against the book's 11.65%
- **IM**: carry 12.02% at target risk, corr -0.064, blend Sharpe +0.387
- **IH**: at 8.0% vol the sleeve earns 4.24% against the book's 11.65%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp |
|---|---|---|---|
| IC | 14.14 | 4.28 | +9.87 |
| IF | 6.09 | 2.49 | +3.61 |
| IM | 7.41 | - | - |
| IH | 3.37 | - | - |
- **IM leg not priced**: 1 day(s) move more than 35% in the ETF leg; gap not printed -- an unread leg is printed as a refusal, not as a zero gap
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 56.03% on capital, DD 36.06% | 49.68% on capital, DD 31.97% | 42.46% on capital, DD 27.32% |
| IF | 21.55% on capital, DD 39.57% | 19.23% on capital, DD 35.31% | 16.55% on capital, DD 30.39% |
| IM | 67.77% on capital, DD 33.54% | 59.82% on capital, DD 29.61% | 50.87% on capital, DD 25.18% |
| IH | 13.73% on capital, DD 42.61% | 12.31% on capital, DD 38.22% | 10.67% on capital, DD 33.11% |

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

**IC**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.18 | 10.00 | 1.118 | -10.23 |
| 0.10 | x1.08 | 12.10 | 10.00 | 1.210 | -10.12 |
| 0.20 | x1.20 | 13.18 | 10.00 | 1.318 | -9.92 |
| 0.30 | x1.36 | 14.43 | 10.00 | 1.443 | -9.59 |

**IF**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.18 | 10.00 | 1.118 | -10.23 |
| 0.10 | x1.07 | 11.56 | 10.00 | 1.156 | -10.12 |
| 0.20 | x1.20 | 12.00 | 10.00 | 1.200 | -9.95 |
| 0.30 | x1.35 | 12.49 | 10.00 | 1.249 | -9.68 |

**IM**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x1.02 | 15.63 | 10.00 | 1.563 | -10.80 |
| 0.10 | x1.14 | 16.80 | 10.00 | 1.680 | -10.62 |
| 0.20 | x1.27 | 18.11 | 10.00 | 1.810 | -10.31 |
| 0.30 | x1.43 | 19.50 | 10.00 | 1.950 | -9.79 |

**IH**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.18 | 10.00 | 1.118 | -10.23 |
| 0.10 | x1.07 | 11.44 | 10.00 | 1.144 | -10.14 |
| 0.20 | x1.20 | 11.72 | 10.00 | 1.172 | -9.99 |
| 0.30 | x1.35 | 12.02 | 10.00 | 1.202 | -9.76 |

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

