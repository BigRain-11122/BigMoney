# index-futures carry: what it is worth in risk units

Generated 2026-11-25T09:09:26 · evidence cutoff 2026-11-24 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.20% a year compounded, vol 10.35%, Sharpe 1.079, max drawdown -10.56%, worst year 0.80%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 74 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | 8.04 | 8.77 | 5.87 | 1.463 | -5.64 | 174 (12) | -0.82 |
| IF | 8.04 | 3.61 | 4.40 | 0.828 | -6.55 | 300 (12) | -3.15 |
| IM | 4.3 | 10.23 | 6.82 | 1.462 | -5.05 | 122 (13) | 4.44 |
| IH | 8.04 | 2.44 | 4.44 | 0.566 | -7.42 | 479 (9) | -3.63 |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | 8.77 | 2.90 | 9.86 | 6.96 | 106 |
| IF | 3.61 | 1.80 | 5.90 | 4.10 | 110 |
| IM | 10.23 | 5.92 | 12.16 | 6.25 | 42 |
| IH | 2.44 | 1.46 | 5.45 | 3.99 | 106 |

- **IC**: the two published rulers disagree by 6.96 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IF**: the two published rulers disagree by 4.10 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IM**: the two published rulers disagree by 6.25 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.
- **IH**: the two published rulers disagree by 3.99 pp on the same window; a single carry figure inside that band is a caliber choice, not a measurement.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | x1.36 | 12.05 | -7.67 | -0.039 | 0.30 | +0.326 | SLEEVE_CANDIDATE |
| IF | x1.82 | 6.50 | -11.78 | 0.050 | 0.30 | +0.134 | REFUSE |
| IM | x1.17 | 12.05 | -5.90 | -0.064 | 0.30 | +0.390 | SLEEVE_CANDIDATE |
| IH | x1.80 | 4.30 | -13.24 | 0.054 | 0.30 | +0.087 | REFUSE |

- **IC**: carry 12.05% at target risk, corr -0.039, blend Sharpe +0.326
- **IF**: at 8.0% vol the sleeve earns 6.50% against the book's 11.20%
- **IM**: carry 12.05% at target risk, corr -0.064, blend Sharpe +0.390
- **IH**: at 8.0% vol the sleeve earns 4.30% against the book's 11.20%

## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | 13.38 | 3.58 | +9.80 | 0.88 | +8.91 |
| IF | 5.94 | 2.29 | +3.65 | 1.79 | +1.85 |
| IM | 5.23 | -4.20 | +9.43 | 2.96 | +6.46 |
| IH | 3.36 | - | - | 0.00 | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.
- **IC leg priced, level change disclosed**: 1 share conversion(s) removed (2015-04-15 x3.486); level change is not a return
- **IM leg priced, level change disclosed**: 1 share conversion(s) removed (2022-09-05 x2.763); level change is not a return
- **IH leg not priced**: no ETF mapped to this index in the panel, so there is nothing to price against -- an unread leg is printed as a refusal, not as a zero gap

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | 12.52 | 3.55 | +8.97 | +9.80 | +8.85 | +6.55 |
| IF | 5.00 | 2.67 | +2.33 | +3.65 | +2.19 | +0.50 |
| IM | 4.06 | -4.94 | +9.00 | +9.43 | +8.92 | +7.49 |
| IH | 2.88 | - | - | - | - | - |
- **IC**: holds at both ends of the cost band: +8.85 pp/yr at the exchange file, +6.55 pp/yr at the measured median (63 rolls, drag 0.12 / 2.42 pp/yr)
- **IF**: holds at both ends of the cost band: +2.19 pp/yr at the exchange file, +0.50 pp/yr at the measured median (74 rolls, drag 0.14 / 1.83 pp/yr)
- **IM**: holds at both ends of the cost band: +8.92 pp/yr at the exchange file, +7.49 pp/yr at the measured median (23 rolls, drag 0.08 / 1.51 pp/yr)
- **IH**: no open-to-open gap is printed because the other leg could not be priced (no ETF is mapped to this index, so there is no other leg to price); that is a missing price, not a zero gap
- **IC leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM leg priced, with the level change disclosed**: 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return
- **IH leg not priced at the open**: no ETF is mapped to this index, so there is no other leg to price

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | 56.09% on capital, DD 36.06% | 49.73% on capital, DD 31.97% | 42.50% on capital, DD 27.32% |
| IF | 21.81% on capital, DD 39.57% | 19.46% on capital, DD 35.31% | 16.75% on capital, DD 30.39% |
| IM | 67.97% on capital, DD 33.54% | 60.00% on capital, DD 29.61% | 51.02% on capital, DD 25.18% |
| IH | 14.02% on capital, DD 42.61% | 12.58% on capital, DD 38.22% | 10.89% on capital, DD 33.11% |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | 72.42 | 10.64% on capital, DD 87.87% | 10.39% on capital, DD 85.78% | 10.04% on capital, DD 82.84% |
| IF | 72.30 | 4.38% on capital, DD 87.85% | 4.28% on capital, DD 85.77% | 4.13% on capital, DD 82.82% |
| IM | 72.35 | 12.42% on capital, DD 87.86% | 12.13% on capital, DD 85.77% | 11.71% on capital, DD 82.83% |
| IH | 72.41 | 2.96% on capital, DD 87.86% | 2.89% on capital, DD 85.78% | 2.79% on capital, DD 82.84% |

The four holes sit within 0.11 pp of each other (72.30 to 72.42): these indices fell in the same crisis, so the buffer is one market-wide number, not four independent ones -- holding several products does not shrink it.

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

**IC**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 11.57 | 10.00 | 1.157 | -10.11 |
| 0.20 | x1.20 | 12.65 | 10.00 | 1.265 | -9.91 |
| 0.30 | x1.36 | 13.91 | 10.00 | 1.391 | -9.58 |

**IF**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 11.04 | 10.00 | 1.104 | -10.11 |
| 0.20 | x1.20 | 11.49 | 10.00 | 1.149 | -9.94 |
| 0.30 | x1.35 | 11.99 | 10.00 | 1.199 | -9.68 |

**IM**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x1.02 | 14.70 | 10.00 | 1.470 | -10.78 |
| 0.10 | x1.14 | 15.87 | 10.00 | 1.587 | -10.60 |
| 0.20 | x1.27 | 17.18 | 10.00 | 1.718 | -10.29 |
| 0.30 | x1.42 | 18.60 | 10.00 | 1.860 | -9.77 |

**IH**

| lam | leverage | ann % | vol % | Sharpe | max DD % |
|---|---|---|---|---|---|
| 0.00 | x0.97 | 10.65 | 10.00 | 1.065 | -10.22 |
| 0.10 | x1.07 | 10.92 | 10.00 | 1.092 | -10.13 |
| 0.20 | x1.19 | 11.21 | 10.00 | 1.121 | -9.98 |
| 0.30 | x1.34 | 11.52 | 10.00 | 1.152 | -9.75 |

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

