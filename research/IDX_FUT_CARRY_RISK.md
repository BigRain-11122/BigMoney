# index-futures carry: what it is worth in risk units

Generated 2026-11-19T20:35:12 · evidence cutoff 2026-11-19 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.47% a year compounded, vol 10.32%, Sharpe 1.104, max drawdown -10.56%, worst year 2.56%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 71 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.03 | 8.75 | 5.86 | 1.460 | -5.64 | 174 (9) | -0.82 |
| IF | 8.03 | 3.57 | 4.38 | 0.824 | -6.55 | 300 (9) | -3.15 |
| IM | 4.29 | 10.21 | 6.81 | 1.463 | -5.05 | 122 (10) | 4.44 |
| IH | 8.03 | 2.43 | 4.41 | 0.566 | -7.42 | 479 (6) | -3.63 |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | 8.75 | 2.88 | 9.80 | 6.93 | 106 |
| IF | 3.57 | 1.88 | 5.85 | 3.96 | 110 |
| IM | 10.21 | 5.89 | 12.02 | 6.13 | 42 |
| IH | 2.43 | 1.58 | 5.41 | 3.83 | 106 |

- **IC**: the two published rulers disagree by 6.93 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IF**: the two published rulers disagree by 3.96 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IM**: the two published rulers disagree by 6.13 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IH**: the two published rulers disagree by 3.83 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 12.03 | -7.68 | -0.039 | 0.30 | +0.324 | SLEEVE_CANDIDATE |
| IF | x1.83 | 6.47 | -11.84 | 0.052 | 0.30 | +0.131 | REFUSE |
| IM | x1.18 | 12.06 | -5.91 | -0.064 | 0.30 | +0.388 | SLEEVE_CANDIDATE |
| IH | x1.82 | 4.30 | -13.34 | 0.056 | 0.30 | +0.085 | REFUSE |

- **IC**: carry 12.03% at target risk, corr -0.039, blend Sharpe +0.324
- **IF**: at 8.0% vol the sleeve earns 6.47% against the book's 11.47%
- **IM**: carry 12.06% at target risk, corr -0.064, blend Sharpe +0.388
- **IH**: at 8.0% vol the sleeve earns 4.30% against the book's 11.47%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | 13.71 | 3.90 | +9.82 | 0.88 | +8.94 |
| IF | 5.99 | 2.40 | +3.59 | 1.79 | +1.79 |
| IM | 6.22 | -3.27 | +9.48 | 3.02 | +6.47 |
| IH | 3.35 | - | - | 0.00 | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.
- **IC leg priced, level change disclosed**: 1 share conversion(s) removed (2015-04-15 x3.486); level change is not a return
- **IM leg priced, level change disclosed**: 1 share conversion(s) removed (2022-09-05 x2.763); level change is not a return
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | 13.41 | 4.30 | +9.11 | +9.82 | +8.99 | +6.68 |
| IF | 5.28 | 2.87 | +2.41 | +3.59 | +2.27 | +0.58 |
| IM | 6.52 | -2.77 | +9.29 | +9.48 | +9.21 | +7.78 |
| IH | 3.02 | - | - | - | - | - |
- **IC**: holds at both ends of the cost band: +8.99 pp/yr at the exchange file, +6.68 pp/yr at the measured median (63 rolls, drag 0.12 / 2.42 pp/yr)
- **IF**: holds at both ends of the cost band: +2.27 pp/yr at the exchange file, +0.58 pp/yr at the measured median (74 rolls, drag 0.14 / 1.83 pp/yr)
- **IM**: holds at both ends of the cost band: +9.21 pp/yr at the exchange file, +7.78 pp/yr at the measured median (23 rolls, drag 0.08 / 1.51 pp/yr)
- **IH**: no open-to-open gap is printed because the other leg could not be priced (no ETF is mapped to this index, so there is no other leg to price); that is a missing price, not a zero gap
- **IC leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return
- **IH leg not priced at the open**: no ETF is mapped to this index, so there is no other leg to price

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 55.94% on capital, DD 36.06% | 49.59% on capital, DD 31.97% | 42.39% on capital, DD 27.32% |
| IF | 21.59% on capital, DD 39.57% | 19.26% on capital, DD 35.31% | 16.58% on capital, DD 30.39% |
| IM | 67.88% on capital, DD 33.54% | 59.92% on capital, DD 29.61% | 50.95% on capital, DD 25.18% |
| IH | 13.92% on capital, DD 42.61% | 12.49% on capital, DD 38.22% | 10.82% on capital, DD 33.11% |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | 72.42 | 10.61% on capital, DD 87.87% | 10.36% on capital, DD 85.78% | 10.01% on capital, DD 82.84% |
| IF | 72.30 | 4.34% on capital, DD 87.85% | 4.24% on capital, DD 85.77% | 4.09% on capital, DD 82.82% |
| IM | 72.35 | 12.40% on capital, DD 87.86% | 12.11% on capital, DD 85.77% | 11.69% on capital, DD 82.83% |
| IH | 72.41 | 2.94% on capital, DD 87.86% | 2.87% on capital, DD 85.78% | 2.78% on capital, DD 82.84% |

The four holes sit within 0.11 pp of each other (72.30 to 72.42): these indices fell in the same crisis, so the buffer is one market-wide number, not four independent ones -- holding several products does not shrink it.

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

**IC**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.06 | 10.00 | 1.107 | -10.24 |
| 0.10 | x1.08 | 11.98 | 10.00 | 1.198 | -10.12 |
| 0.20 | x1.21 | 13.06 | 10.00 | 1.306 | -9.93 |
| 0.30 | x1.36 | 14.31 | 10.00 | 1.431 | -9.60 |

**IF**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.06 | 10.00 | 1.107 | -10.24 |
| 0.10 | x1.07 | 11.45 | 10.00 | 1.145 | -10.12 |
| 0.20 | x1.20 | 11.89 | 10.00 | 1.189 | -9.95 |
| 0.30 | x1.35 | 12.38 | 10.00 | 1.238 | -9.69 |

**IM**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x1.02 | 15.43 | 10.00 | 1.543 | -10.81 |
| 0.10 | x1.14 | 16.59 | 10.00 | 1.659 | -10.63 |
| 0.20 | x1.28 | 17.91 | 10.00 | 1.791 | -10.31 |
| 0.30 | x1.43 | 19.31 | 10.00 | 1.931 | -9.79 |

**IH**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 11.06 | 10.00 | 1.107 | -10.24 |
| 0.10 | x1.07 | 11.33 | 10.00 | 1.133 | -10.14 |
| 0.20 | x1.20 | 11.62 | 10.00 | 1.162 | -10.00 |
| 0.30 | x1.35 | 11.92 | 10.00 | 1.192 | -9.76 |

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

