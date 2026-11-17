# index-futures carry: what it is worth in risk units

Generated 2026-11-17T21:43:20 · evidence cutoff 2026-11-17 · `scripts/idx_fut_carry_risk.py`

The roll book (hold the deepest-open-interest contract, switch at the same close) is the one `idx_fut_real_nav` publishes in rupees of carry per year. This page asks the only question that allocates money: at the desk's own 8% volatility target, does that carry buy anything the adopted book does not already buy, and does it move with it?

## the book it is compared against

- nobond_vt08_adopted: 11.51% a year compounded, vol 10.33%, Sharpe 1.107, max drawdown -10.56%, worst year 2.80%, underwater run up to 207 bars
- the last drawdown **has not healed**: still under water for 69 bars at the last bar (a censored duration is not a fast recovery)

## each product, in its own risk units

| product | years | carry %/yr | vol % | Sharpe | max DD % | underwater bars (still open) | worst year % |
|---|---|---|---|---|---|---|---|
| IC | - | - | - | - | - | - | - |
| IF | - | - | - | - | - | - | - |
| IM | - | - | - | - | - | - | - |
| IH | - | - | - | - | - | - | - |
## the caliber the carry column rides on

Which days count as roll days moves the annualised carry by more than this sleeve's whole margin over the book, so the column above travels with both rulers the roll-mask face publishes for the same products (`results/idx_fut_roll_gap.json`, read, not recomputed). This face's own series performs every max-open-interest switch and drops no days, so neither ruler below is this face's own treatment.

| product | this face carry %/yr | threshold ruler %/yr | calendar ruler %/yr | rulers disagree by pp | roll days the threshold ruler misses |
|---|---|---|---|---|---|
| IC | - | - | - | ? | ? |
| IF | - | - | - | ? | ? |
| IM | - | - | - | ? | ? |
| IH | - | - | - | ? | ? |

- **IC**: the roll-mask face is unreadable on this host, so the caliber is unknown here -- an unread ruler is not 'the rulers agree'.
- **IF**: the roll-mask face is unreadable on this host, so the caliber is unknown here -- an unread ruler is not 'the rulers agree'.
- **IM**: the roll-mask face is unreadable on this host, so the caliber is unknown here -- an unread ruler is not 'the rulers agree'.
- **IH**: the roll-mask face is unreadable on this host, so the caliber is unknown here -- an unread ruler is not 'the rulers agree'.

## at the desk's 8% volatility target

| product | leverage to 8% vol | carry %/yr | max DD % | corr with the book | best blend lam | blend Sharpe gain | verdict |
|---|---|---|---|---|---|---|---|
| IC | - | - | - | - | - | - | no_contract_book |
| IF | - | - | - | - | - | - | no_contract_book |
| IM | - | - | - | - | - | - | no_contract_book |
| IH | - | - | - | - | - | - | no_contract_book |


## the form this desk can actually hold

The daily spread above is futures minus index: it is the *excess* return, and isolating it needs a short leg on the index, which this desk cannot borrow. The implementable version of the same idea is owning the future **instead of** the matching ETF -- that is long the index too -- so the column that matters is the gap against the ETF itself over the same window.

| product | long the future %/yr | the matching ETF %/yr | gap pp | dividend drift pp | gap net of dividend pp |
|---|---|---|---|---|---|
| IC | - | - | - | - | - |
| IF | - | - | - | - | - |
| IM | - | - | - | - | - |
| IH | - | - | - | - | - |

The gap column is GROSS of a structural drift that is not a futures market reading: the ETF is paid the basket's cash dividend and the price index the future tracks is not. The drift column is the basis face's own C3 control arm (results/idx_fut_basis.json), measured on this repo's panel -- it is not a dividend announcement. Where that control could not be read the net column is blank, not equal to the gross one.

## the same book filled at the next open

Every number above buys at the close it decides at. A desk decides after the close and fills the next session, so the book is re-run with the fill one session later at that session's open (both legs, rolls included), and the roll cost the cost face measured is subtracted. If the gap against the ETF only exists at closes, it is not a gap anyone can collect.

| product | futures open→open %/yr | ETF open→open %/yr | gap pp | gap at closes pp | gap after cost (file floor) pp | gap after cost (measured median) pp |
|---|---|---|---|---|---|---|
| IC | - | - | - | - | - | not built |
| IF | - | - | - | - | - | not built |
| IM | - | - | - | - | - | not built |
| IH | - | - | - | - | - | not built |

## what one contract actually ties up (margin is an assumption)

Margin is not the capital: a book that cannot fund its own drawdown is not holding the position. Capital = margin + |max drawdown|, so the return on it is carry/(margin+DD) and the drawdown is DD/(margin+DD) of everything you put in.

| product | margin 10% | margin 12% | margin 15% |
|---|---|---|---|
| IC | - | - | - |
| IF | - | - | - |
| IM | - | - | - |
| IH | - | - | - |

### the same carry sized against the index's worst drawdown

The table above buffers the margin with the drawdown this window produced. That buffer is a property of the sample, not of the contract: the position is long the index, so the hole it can be asked to fund is the index's own worst drawdown over its full quoted history. Same carry, same margin, only the buffer changes -- and the buffer is the whole difference between a capital number you can finance and one you cannot.

| product | index worst DD % | margin 10% | margin 12% | margin 15% |
|---|---|---|---|---|
| IC | - | - | - | - |
| IF | - | - | - | - |
| IM | - | - | - | - |
| IH | - | - | - | - |

## blend grid

(1-lam) x adopted book + lam x carry, rescaled to one 10% risk level so the columns are comparable: leverage is doing the risk normalisation, not the book.

## honest limits

- every reading is in-sample; this page says whether the sleeve is worth pricing forward, not whether it will earn.
- the carry series is futures-minus-index on the quote source's closes, with the roll performed at one close; a broker's fill and the margin surcharge are not in it.
- correlation is measured on shared calendar days only; a product whose contract history is short is judged on fewer days, printed per row.
- a sleeve candidate here is a candidate for the **hedged** sleeve. Without the short leg the same carry is only available bundled with index risk, which is what the two-column gap above prices.
- the sleeve candidate test uses the book's own realised vol, so a change in the book's risk engine moves this verdict without touching the carry.

