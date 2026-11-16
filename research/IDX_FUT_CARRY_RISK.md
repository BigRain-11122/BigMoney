# index-futures carry: what it is worth in risk units

Generated 2026-11-16T20:48:09 · evidence cutoff 2026-11-16 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.56% a year compounded, vol 10.33%, Sharpe 1.111, max drawdown -10.56%, worst year 3.08%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 68 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.02 | 8.76 | 5.87 | 1.461 | -5.64 | 174 (6) | -0.82 |
| IF | 8.02 | 3.57 | 4.38 | 0.823 | -6.55 | 300 (6) | -3.15 |
| IM | 4.28 | 10.20 | 6.82 | 1.459 | -5.05 | 122 (7) | 4.44 |
| IH | 8.02 | 2.39 | 4.40 | 0.559 | -7.42 | 479 (3) | -3.63 |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | 8.76 | 2.88 | 9.79 | 6.91 | 105 |
| IF | 3.57 | 1.88 | 5.79 | 3.92 | 109 |
| IM | 10.20 | 5.86 | 11.95 | 6.09 | 41 |
| IH | 2.39 | 1.55 | 5.32 | 3.77 | 105 |

- **IC**: the two published rulers disagree by 6.91 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IF**: the two published rulers disagree by 3.92 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IM**: the two published rulers disagree by 6.09 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IH**: the two published rulers disagree by 3.77 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 12.04 | -7.67 | -0.039 | 0.30 | +0.325 | SLEEVE_CANDIDATE |
| IF | x1.83 | 6.46 | -11.84 | 0.053 | 0.30 | +0.131 | REFUSE |
| IM | x1.17 | 12.02 | -5.91 | -0.064 | 0.30 | +0.387 | SLEEVE_CANDIDATE |
| IH | x1.82 | 4.24 | -13.36 | 0.056 | 0.30 | +0.084 | REFUSE |

- **IC**: carry 12.04% at target risk, corr -0.039, blend Sharpe +0.325
- **IF**: at 8.0% vol the sleeve earns 6.46% against the book's 11.56%
- **IM**: carry 12.02% at target risk, corr -0.064, blend Sharpe +0.387
- **IH**: at 8.0% vol the sleeve earns 4.24% against the book's 11.56%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | 14.14 | 4.28 | +9.87 | 0.88 | +8.98 |
| IF | 6.09 | 2.49 | +3.61 | 1.77 | +1.84 |
| IM | 7.41 | -2.20 | +9.62 | 2.96 | +6.66 |
| IH | 3.37 | - | - | 0.00 | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.
- **IC leg priced, level change disclosed**: 1 share conversion(s) removed (2015-04-15 x3.486); level change is not a return
- **IM leg priced, level change disclosed**: 1 share conversion(s) removed (2022-09-05 x2.763); level change is not a return
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | 14.27 | 4.99 | +9.28 | +9.87 | +9.16 | +6.86 |
| IF | 5.56 | 3.08 | +2.48 | +3.61 | +2.35 | +0.65 |
| IM | 8.41 | -1.18 | +9.59 | +9.62 | +9.51 | +8.07 |
| IH | 3.08 | - | - | - | - | - |
- **IC**: holds at both ends of the cost band: +9.16 pp/yr at the exchange file, +6.86 pp/yr at the measured median (63 rolls, drag 0.12 / 2.42 pp/yr)
- **IF**: holds at both ends of the cost band: +2.35 pp/yr at the exchange file, +0.65 pp/yr at the measured median (74 rolls, drag 0.14 / 1.83 pp/yr)
- **IM**: holds at both ends of the cost band: +9.51 pp/yr at the exchange file, +8.07 pp/yr at the measured median (23 rolls, drag 0.08 / 1.52 pp/yr)
- **IH**: no open-to-open gap is printed because the other leg could not be priced (no ETF is mapped to this index, so there is no other leg to price); that is a missing price, not a zero gap
- **IC leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return
- **IH leg not priced at the open**: no ETF is mapped to this index, so there is no other leg to price

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 56.03% on capital, DD 36.06% | 49.68% on capital, DD 31.97% | 42.46% on capital, DD 27.32% |
| IF | 21.55% on capital, DD 39.57% | 19.23% on capital, DD 35.31% | 16.55% on capital, DD 30.39% |
| IM | 67.77% on capital, DD 33.54% | 59.82% on capital, DD 29.61% | 50.87% on capital, DD 25.18% |
| IH | 13.73% on capital, DD 42.61% | 12.31% on capital, DD 38.22% | 10.67% on capital, DD 33.11% |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | 72.42 | 10.63% on capital, DD 87.87% | 10.38% on capital, DD 85.78% | 10.02% on capital, DD 82.84% |
| IF | 72.30 | 4.33% on capital, DD 87.85% | 4.23% on capital, DD 85.77% | 4.09% on capital, DD 82.82% |
| IM | 72.35 | 12.38% on capital, DD 87.86% | 12.09% on capital, DD 85.77% | 11.68% on capital, DD 82.83% |
| IH | 72.41 | 2.90% on capital, DD 87.86% | 2.83% on capital, DD 85.78% | 2.74% on capital, DD 82.84% |

The four holes sit within 0.11 pp of each other (72.30 to 72.42): these indices fell in the same crisis, so the buffer is one market-wide number, not four independent ones -- holding several products does not shrink it.

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

