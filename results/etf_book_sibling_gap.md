# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-24` | ticket `TICKET-2026-11-24.json` | source `results\etf_book_sibling_entry.json`

**no pair carries a gap that can be read: 1 pair(s) unverifiable or immaterial**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|
| 510760 | 510980 上证指数ETF汇添富 | LBL:上证指数ETF | 0.1844 pp | -1.0111 pp | 4.1099 | 721 | 75.87 | NO_GAP |

## 510760 -> 510980 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2023-12-01..2026-11-24 (721 common sessions), reconstructed gap mean -1.0111 pp, median -3.1898 pp, sd 4.1099 pp
- today z = 0.291, percentile = 75.87, positive on 25% of sessions
- half-split means 1.3617 pp / -3.3774 pp; last 250 sessions mean -3.0552 pp
- NAV-base offset pinned today = -2.9046 pp (the raw close ratio level, -2.72 pp, is not a premium)
- 7 step(s) > 3.0 sd: 2024-05-27 -4.45pp, 2024-08-14 -4.81pp, 2024-09-30 +2.88pp, 2024-10-08 -2.96pp, 2024-12-24 -4.75pp, 2025-04-07 -1.35pp

## legs the sibling face could not price

- 512040: the board writes the same label, but the gap's median day change is 0.392 pp (> 0.30): these are not the same basket, so no swap is priced
- 159655: no other live ticker writes this label on the board
- 513690: no other live ticker writes this label on the board
- 159519: no other live ticker writes this label on the board

## the board's own labels, adjudicated by the prices (2026-11-24)

A leg the hand map could not name is retried here: if two live tickers carry the identical index label, the median day-over-day change of their gap decides whether they are one basket. The line is 0.30 pp (median, not sd: a 5:1 split is one step and must not be read as a tracking gap).

| leg | label | same-label | live alts | gap median day change | state |
|---|---|---|---|---|---|
| 510760 | 上证指数ETF | 5 | 4 | 0.148 pp | LABEL_IS_A_BASKET |
| 512040 | 价值ETF | 3 | 1 | 0.392 pp | LABEL_NOT_A_BASKET |
| 159655 | 标普ETF | 1 | 0 | - | NO_ALTERNATIVE |
| 513690 | 港股红利ETF | 1 | 0 | - | NO_ALTERNATIVE |
| 159519 | 港股国企 | 1 | 0 | - | NO_ALTERNATIVE |

- 510760: the board writes the same label and the gap's median day change is 0.148 pp (<= 0.30): the price history agrees these hold the same basket
- 512040: the board writes the same label, but the gap's median day change is 0.392 pp (> 0.30): these are not the same basket, so no swap is priced
- 159655: no other live ticker writes this label on the board
- 513690: no other live ticker writes this label on the board
- 159519: no other live ticker writes this label on the board

## caveats

- the reconstructed gap is anchored on ONE session's IOPV pair; every earlier value inherits the assumption that the two funds' NAV-per-unit ratio has not moved, and steps are published as the evidence against that assumption
- closes are as-traded, not total-return: a distribution to one fund only lands as a step and is flagged, not corrected
- same index, not same basket: tracking difference, fee, size, quotation width and FX-hedge policy are NOT priced here
- premium history from our own board starts at one session; this face uses the price ratio for history precisely because it is the only long series we have
- a step is a flag, not an error: the level after a step is still the level a buyer would pay today
- a leg the hand map could not name is retried on the board's own label, and the price history has to agree before a swap is priced (label_family block); a label match alone is never treated as the same basket
