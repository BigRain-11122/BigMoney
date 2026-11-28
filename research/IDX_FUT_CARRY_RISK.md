# index-futures carry: what it is worth in risk units

Generated 2026-11-28T09:06:26 · evidence cutoff 2026-11-27 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.03% a year compounded, vol 10.34%, Sharpe 1.063, max drawdown -10.56%, worst year -0.30%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 77 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.06 | 8.95 | 5.90 | 1.484 | -5.64 | 174 (0) | -0.82 |
| IF | 8.06 | 3.79 | 4.45 | 0.859 | -6.55 | 300 (0) | -3.15 |
| IM | 4.32 | 10.36 | 6.84 | 1.476 | -5.05 | 122 (0) | 4.44 |
| IH | 8.06 | 2.58 | 4.47 | 0.593 | -7.42 | 479 (0) | -3.63 |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | 8.95 | 3.05 | 10.00 | 6.95 | 106 |
| IF | 3.79 | 1.78 | 6.05 | 4.27 | 110 |
| IM | 10.36 | 6.05 | 12.28 | 6.23 | 42 |
| IH | 2.58 | 1.43 | 5.56 | 4.14 | 106 |

- **IC**: the two published rulers disagree by 6.95 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IF**: the two published rulers disagree by 4.27 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IM**: the two published rulers disagree by 6.23 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IH**: the two published rulers disagree by 4.14 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 12.24 | -7.63 | -0.038 | 0.30 | +0.333 | SLEEVE_CANDIDATE |
| IF | x1.80 | 6.76 | -11.66 | 0.052 | 0.30 | +0.142 | REFUSE |
| IM | x1.17 | 12.17 | -5.89 | -0.064 | 0.30 | +0.395 | SLEEVE_CANDIDATE |
| IH | x1.79 | 4.52 | -13.16 | 0.055 | 0.30 | +0.093 | REFUSE |

- **IC**: carry 12.24% at target risk, corr -0.038, blend Sharpe +0.333
- **IF**: at 8.0% vol the sleeve earns 6.76% against the book's 11.03%
- **IM**: carry 12.17% at target risk, corr -0.064, blend Sharpe +0.395
- **IH**: at 8.0% vol the sleeve earns 4.52% against the book's 11.03%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | 13.96 | 4.07 | +9.88 | 0.88 | +9.00 |
| IF | 6.45 | 2.72 | +3.73 | 1.82 | +1.91 |
| IM | 6.06 | -3.24 | +9.30 | 2.96 | +6.33 |
| IH | 3.83 | - | - | 0.00 | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.
- **IC leg priced, level change disclosed**: 1 share conversion(s) removed (2015-04-15 x3.486); level change is not a return
- **IM leg priced, level change disclosed**: 1 share conversion(s) removed (2022-09-05 x2.763); level change is not a return
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | 12.47 | 3.40 | +9.07 | +9.88 | +8.96 | +6.66 |
| IF | 5.04 | 2.59 | +2.45 | +3.73 | +2.31 | +0.63 |
| IM | 4.23 | -4.92 | +9.14 | +9.30 | +9.06 | +7.64 |
| IH | 2.95 | - | - | - | - | - |
- **IC**: holds at both ends of the cost band: +8.96 pp/yr at the exchange file, +6.66 pp/yr at the measured median (63 rolls, drag 0.12 / 2.41 pp/yr)
- **IF**: holds at both ends of the cost band: +2.31 pp/yr at the exchange file, +0.63 pp/yr at the measured median (74 rolls, drag 0.14 / 1.83 pp/yr)
- **IM**: holds at both ends of the cost band: +9.06 pp/yr at the exchange file, +7.64 pp/yr at the measured median (23 rolls, drag 0.08 / 1.50 pp/yr)
- **IH**: no open-to-open gap is printed because the other leg could not be priced (no ETF is mapped to this index, so there is no other leg to price); that is a missing price, not a zero gap
- **IC leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return
- **IH leg not priced at the open**: no ETF is mapped to this index, so there is no other leg to price

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 57.25% on capital, DD 36.06% | 50.76% on capital, DD 31.97% | 43.38% on capital, DD 27.32% |
| IF | 22.90% on capital, DD 39.57% | 20.43% on capital, DD 35.31% | 17.58% on capital, DD 30.39% |
| IM | 68.82% on capital, DD 33.54% | 60.75% on capital, DD 29.61% | 51.66% on capital, DD 25.18% |
| IH | 14.82% on capital, DD 42.61% | 13.30% on capital, DD 38.22% | 11.52% on capital, DD 33.11% |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | 72.42 | 10.86% on capital, DD 87.87% | 10.61% on capital, DD 85.78% | 10.24% on capital, DD 82.84% |
| IF | 72.30 | 4.60% on capital, DD 87.85% | 4.49% on capital, DD 85.77% | 4.34% on capital, DD 82.82% |
| IM | 72.35 | 12.58% on capital, DD 87.86% | 12.28% on capital, DD 85.77% | 11.86% on capital, DD 82.83% |
| IH | 72.41 | 3.13% on capital, DD 87.86% | 3.06% on capital, DD 85.78% | 2.96% on capital, DD 82.84% |

The four holes sit within 0.11 pp of each other (72.30 to 72.42): these indices fell in the same crisis, so the buffer is one market-wide number, not four independent ones -- holding several products does not shrink it.

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

**IC**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.63 | 10.00 | 1.063 | -10.22 |
| 0.10 | x1.07 | 11.57 | 10.00 | 1.157 | -10.10 |
| 0.20 | x1.20 | 12.68 | 10.00 | 1.268 | -9.91 |
| 0.30 | x1.35 | 13.96 | 10.00 | 1.396 | -9.57 |

**IF**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.63 | 10.00 | 1.063 | -10.22 |
| 0.10 | x1.07 | 11.04 | 10.00 | 1.104 | -10.11 |
| 0.20 | x1.19 | 11.51 | 10.00 | 1.151 | -9.93 |
| 0.30 | x1.35 | 12.05 | 10.00 | 1.205 | -9.67 |

**IM**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x1.02 | 14.65 | 10.00 | 1.465 | -10.77 |
| 0.10 | x1.14 | 15.83 | 10.00 | 1.583 | -10.59 |
| 0.20 | x1.27 | 17.16 | 10.00 | 1.716 | -10.28 |
| 0.30 | x1.42 | 18.59 | 10.00 | 1.860 | -9.76 |

**IH**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.63 | 10.00 | 1.063 | -10.22 |
| 0.10 | x1.07 | 10.91 | 10.00 | 1.091 | -10.13 |
| 0.20 | x1.19 | 11.23 | 10.00 | 1.123 | -9.98 |
| 0.30 | x1.34 | 11.56 | 10.00 | 1.156 | -9.74 |

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

