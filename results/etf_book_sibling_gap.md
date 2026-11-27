# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-26` | ticket `TICKET-2026-11-26.json` | source `results\etf_book_sibling_entry.json`

**no pair carries a gap that can be read: 1 pair(s) unverifiable or immaterial**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|
| 510760 | 510910 上证指数ETF南方 | LBL:上证指数ETF | 0.118 pp | -2.9243 pp | 2.1975 | 120 | 94.17 | NO_GAP |

## 510760 -> 510910 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2026-06-03..2026-11-26 (120 common sessions), reconstructed gap mean -2.9243 pp, median -2.6985 pp, sd 2.1975 pp
- today z = 1.384, percentile = 94.17, positive on 10% of sessions
- half-split means -4.7537 pp / -1.0949 pp; last 250 sessions mean -2.9243 pp
- NAV-base offset pinned today = 33.3639 pp (the raw close ratio level, 33.48 pp, is not a premium)
- 3 step(s) > 3.0 sd: 2026-06-08 -1.44pp, 2026-06-09 +1.26pp, 2026-06-26 -1.19pp

## legs the sibling face could not price

- 512040: the board writes the same label, but the gap's median day change is 0.385 pp (> 0.30): these are not the same basket, so no swap is priced
- 159655: no other live ticker writes this label on the board
- 513690: no other live ticker writes this label on the board
- 159519: no other live ticker writes this label on the board

## the board's own labels, adjudicated by the prices (2026-11-26)

A leg the hand map could not name is retried here: if two live tickers carry the identical index label, the median day-over-day change of their gap decides whether they are one basket. The line is 0.30 pp (median, not sd: a 5:1 split is one step and must not be read as a tracking gap).

| leg | label | same-label | live alts | gap median day change | state |
|---|---|---|---|---|---|
| 510760 | 上证指数ETF | 5 | 4 | 0.194 pp | LABEL_IS_A_BASKET |
| 512040 | 价值ETF | 3 | 1 | 0.385 pp | LABEL_NOT_A_BASKET |
| 159655 | 标普ETF | 1 | 0 | - | NO_ALTERNATIVE |
| 513690 | 港股红利ETF | 1 | 0 | - | NO_ALTERNATIVE |
| 159519 | 港股国企 | 1 | 0 | - | NO_ALTERNATIVE |

- 510760: the board writes the same label and the gap's median day change is 0.194 pp (<= 0.30): the price history agrees these hold the same basket
- 512040: the board writes the same label, but the gap's median day change is 0.385 pp (> 0.30): these are not the same basket, so no swap is priced
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
