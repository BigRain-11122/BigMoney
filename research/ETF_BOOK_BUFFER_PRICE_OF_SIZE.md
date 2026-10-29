# ETF book -- the buffer's breakeven, read as a size

Face: `results/etf_book_buffer_price_of_size.json` (parent cutoff **2026-10-29**)

## Cost curve (published sqrt impact law)

- the p90 trade is already 1% of ADV at about 0.94M of capital; a buffer that only pays above that size cannot be used, because the book cannot be run there without breaking the 1% participation cap

| NAV | per-side cost (bp) |
|---|---|
| 1M | 11.88 |
| 5M | 16.67 |
| 10M | 20.26 |
| 30M | 29.23 |
| 50M | 35.41 |
| 100M | 46.77 |

## Arms (median breakeven across cells, and the capital that implies)

| k | parent verdict | median breakeven (bp/side) | median crossing NAV | pays at 1M | 5M | 10M | 30M | 50M | 100M |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | REJECT | 50.7 | 121.72M | no | no | no | no | no | no |
| 0.10 | COST_KNOB_ONLY | -8.8 | 0.00M | no | no | no | no | no | no |
| 0.20 | COST_KNOB_ONLY | -5.4 | 0.00M | no | no | no | yes | yes | yes |
| 0.35 | REJECT | 5.4 | 0.00M | no | yes | yes | yes | yes | yes |

"Pays at S" = at least 80% of the arm's cells have crossed their breakeven by S. A median crossing of 0.00M means more than half the arm's cells need no cost story at all -- the pays-at columns still apply the 80% share rule, which is why an arm can have a zero median and still not pay.


## Honest limits

- the cost curve is the N5 book's, so the wide cells' real bill is LOWER and every crossing NAV here is an optimistic bound
- exploratory re-reading of two published faces: no preregistration, no verdict booking
- NAV* inherits the parent face's phase luck (see its median phase IQR)
- an arm that pays at size still failed the parent face's frozen per-cell rule
