# index-futures carry: what it is worth in risk units

Generated 2026-11-25T20:20:53 · evidence cutoff 2026-11-25 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.05% a year compounded, vol 10.35%, Sharpe 1.065, max drawdown -10.56%, worst year -0.21%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 75 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.05 | 8.64 | 5.87 | 1.442 | -5.64 | 174 (14) | -0.82 |
| IF | 8.05 | 3.50 | 4.41 | 0.803 | -6.55 | 300 (14) | -3.15 |
| IM | 4.31 | 9.96 | 6.82 | 1.426 | -5.05 | 122 (15) | 4.44 |
| IH | 8.05 | 2.37 | 4.44 | 0.550 | -7.42 | 479 (11) | -3.63 |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | 8.64 | 2.81 | 9.76 | 6.95 | 106 |
| IF | 3.50 | 1.72 | 5.81 | 4.09 | 110 |
| IM | 9.96 | 5.68 | 11.91 | 6.23 | 42 |
| IH | 2.37 | 1.41 | 5.39 | 3.98 | 106 |

- **IC**: the two published rulers disagree by 6.95 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IF**: the two published rulers disagree by 4.09 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IM**: the two published rulers disagree by 6.23 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IH**: the two published rulers disagree by 3.98 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 11.87 | -7.67 | -0.038 | 0.30 | +0.320 | SLEEVE_CANDIDATE |
| IF | x1.82 | 6.29 | -11.77 | 0.052 | 0.30 | +0.129 | REFUSE |
| IM | x1.17 | 11.73 | -5.90 | -0.063 | 0.30 | +0.379 | SLEEVE_CANDIDATE |
| IH | x1.80 | 4.16 | -13.24 | 0.055 | 0.30 | +0.084 | REFUSE |

- **IC**: carry 11.87% at target risk, corr -0.038, blend Sharpe +0.320
- **IF**: at 8.0% vol the sleeve earns 6.29% against the book's 11.05%
- **IM**: carry 11.73% at target risk, corr -0.063, blend Sharpe +0.379
- **IH**: at 8.0% vol the sleeve earns 4.16% against the book's 11.05%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | 12.68 | 3.07 | +9.60 | 0.88 | +8.72 |
| IF | 5.62 | 2.12 | +3.50 | 1.82 | +1.68 |
| IM | 3.83 | -5.22 | +9.05 | 2.96 | +6.09 |
| IH | 3.24 | - | - | 0.00 | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.
- **IC leg priced, level change disclosed**: 1 share conversion(s) removed (2015-04-15 x3.486); level change is not a return
- **IM leg priced, level change disclosed**: 1 share conversion(s) removed (2022-09-05 x2.763); level change is not a return
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | 12.79 | 3.71 | +9.09 | +9.60 | +8.97 | +6.67 |
| IF | 5.14 | 2.69 | +2.45 | +3.50 | +2.32 | +0.63 |
| IM | 4.78 | -4.25 | +9.03 | +9.05 | +8.95 | +7.53 |
| IH | 2.98 | - | - | - | - | - |
- **IC**: holds at both ends of the cost band: +8.97 pp/yr at the exchange file, +6.67 pp/yr at the measured median (63 rolls, drag 0.12 / 2.42 pp/yr)
- **IF**: holds at both ends of the cost band: +2.32 pp/yr at the exchange file, +0.63 pp/yr at the measured median (74 rolls, drag 0.14 / 1.83 pp/yr)
- **IM**: holds at both ends of the cost band: +8.95 pp/yr at the exchange file, +7.53 pp/yr at the measured median (23 rolls, drag 0.08 / 1.51 pp/yr)
- **IH**: no open-to-open gap is printed because the other leg could not be priced (no ETF is mapped to this index, so there is no other leg to price); that is a missing price, not a zero gap
- **IC leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return
- **IH leg not priced at the open**: no ETF is mapped to this index, so there is no other leg to price

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 55.26% on capital, DD 36.06% | 48.99% on capital, DD 31.97% | 41.87% on capital, DD 27.32% |
| IF | 21.14% on capital, DD 39.57% | 18.86% on capital, DD 35.31% | 16.24% on capital, DD 30.39% |
| IM | 66.23% on capital, DD 33.54% | 58.46% on capital, DD 29.61% | 49.71% on capital, DD 25.18% |
| IH | 13.61% on capital, DD 42.61% | 12.21% on capital, DD 38.22% | 10.57% on capital, DD 33.11% |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | 72.42 | 10.49% on capital, DD 87.87% | 10.24% on capital, DD 85.78% | 9.89% on capital, DD 82.84% |
| IF | 72.30 | 4.25% on capital, DD 87.85% | 4.15% on capital, DD 85.77% | 4.01% on capital, DD 82.82% |
| IM | 72.35 | 12.10% on capital, DD 87.86% | 11.81% on capital, DD 85.77% | 11.41% on capital, DD 82.83% |
| IH | 72.41 | 2.88% on capital, DD 87.86% | 2.81% on capital, DD 85.78% | 2.71% on capital, DD 82.84% |

The four holes sit within 0.11 pp of each other (72.30 to 72.42): these indices fell in the same crisis, so the buffer is one market-wide number, not four independent ones -- holding several products does not shrink it.

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

**IC**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 11.56 | 10.00 | 1.156 | -10.10 |
| 0.20 | x1.20 | 12.62 | 10.00 | 1.262 | -9.90 |
| 0.30 | x1.35 | 13.85 | 10.00 | 1.385 | -9.57 |

**IF**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 11.03 | 10.00 | 1.103 | -10.10 |
| 0.20 | x1.19 | 11.46 | 10.00 | 1.146 | -9.93 |
| 0.30 | x1.35 | 11.94 | 10.00 | 1.194 | -9.67 |

**IM**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x1.02 | 14.69 | 10.00 | 1.469 | -10.77 |
| 0.10 | x1.14 | 15.83 | 10.00 | 1.583 | -10.58 |
| 0.20 | x1.27 | 17.11 | 10.00 | 1.711 | -10.27 |
| 0.30 | x1.42 | 18.48 | 10.00 | 1.848 | -9.76 |

**IH**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 10.91 | 10.00 | 1.091 | -10.12 |
| 0.20 | x1.19 | 11.19 | 10.00 | 1.119 | -9.98 |
| 0.30 | x1.34 | 11.49 | 10.00 | 1.149 | -9.74 |

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

