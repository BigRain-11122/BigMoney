# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-17` | ticket `TICKET-2026-11-17.json` | source `results\etf_book_sibling_entry.json`

**no pair carries a gap that can be read: 2 pair(s) unverifiable or immaterial**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|
| 510760 | 510210 上证指数ETF富国 | LBL:上证指数ETF | 0.1188 pp | -19.9894 pp | 42.8887 | 1497 | 84.03 | NO_GAP |
| 159655 | 513650 标普500ETF南方 | LBL:标普500ETF | -0.0533 pp | 1.12 pp | 1.6998 | 877 | 18.59 | NO_GAP |

## 510760 -> 510210 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2020-09-09..2026-11-17 (1497 common sessions), reconstructed gap mean -19.9894 pp, median -4.783 pp, sd 42.8887 pp
- today z = 0.469, percentile = 84.03, positive on 17% of sessions
- half-split means -39.0631 pp / -0.9411 pp; last 250 sessions mean -2.3835 pp
- NAV-base offset pinned today = 29.1321 pp (the raw close ratio level, 29.25 pp, is not a premium)
- 1 step(s) > 3.0 sd: 2021-01-25 +160.72pp

## 159655 -> 513650 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2023-04-04..2026-11-17 (877 common sessions), reconstructed gap mean 1.12 pp, median 0.5775 pp, sd 1.6998 pp
- today z = -0.69, percentile = 18.59, positive on 80% of sessions
- half-split means 1.8713 pp / 0.3705 pp; last 250 sessions mean 0.0011 pp
- NAV-base offset pinned today = 0.4153 pp (the raw close ratio level, 0.36 pp, is not a premium)
- 10 step(s) > 3.0 sd: 2024-01-23 +7.36pp, 2024-01-24 +6.92pp, 2024-01-25 -10.32pp, 2024-01-26 +4.89pp, 2024-01-31 -7.82pp, 2024-09-04 +3.02pp

## legs the sibling face could not price

- 512040: the board writes the same label, but the gap's median day change is 0.385 pp (> 0.30): these are not the same basket, so no swap is priced
- 513690: the board writes the same label, but the gap's median day change is 0.390 pp (> 0.30): these are not the same basket, so no swap is priced
- 159519: no other live ticker writes this label on the board

## the board's own labels, adjudicated by the prices (2026-11-17)

A leg the hand map could not name is retried here: if two live tickers carry the identical index label, the median day-over-day change of their gap decides whether they are one basket. The line is 0.30 pp (median, not sd: a 5:1 split is one step and must not be read as a tracking gap).

| leg | label | same-label | live alts | gap median day change | state |
|---|---|---|---|---|---|
| 510760 | 上证指数ETF | 5 | 4 | 0.170 pp | LABEL_IS_A_BASKET |
| 512040 | 价值ETF | 10 | 1 | 0.385 pp | LABEL_NOT_A_BASKET |
| 159655 | 标普500ETF | 4 | 2 | 0.162 pp | LABEL_IS_A_BASKET |
| 513690 | 港股红利ETF | 2 | 1 | 0.390 pp | LABEL_NOT_A_BASKET |
| 159519 | 港股国企ETF | 2 | 0 | - | NO_ALTERNATIVE |

- 510760: the board writes the same label and the gap's median day change is 0.170 pp (<= 0.30): the price history agrees these hold the same basket
- 512040: the board writes the same label, but the gap's median day change is 0.385 pp (> 0.30): these are not the same basket, so no swap is priced
- 159655: the board writes the same label and the gap's median day change is 0.162 pp (<= 0.30): the price history agrees these hold the same basket
- 513690: the board writes the same label, but the gap's median day change is 0.390 pp (> 0.30): these are not the same basket, so no swap is priced
- 159519: no other live ticker writes this label on the board

## caveats

- the reconstructed gap is anchored on ONE session's IOPV pair; every earlier value inherits the assumption that the two funds' NAV-per-unit ratio has not moved, and steps are published as the evidence against that assumption
- closes are as-traded, not total-return: a distribution to one fund only lands as a step and is flagged, not corrected
- same index, not same basket: tracking difference, fee, size, quotation width and FX-hedge policy are NOT priced here
- premium history from our own board starts at one session; this face uses the price ratio for history precisely because it is the only long series we have
- a step is a flag, not an error: the level after a step is still the level a buyer would pay today
- a leg the hand map could not name is retried on the board's own label, and the price history has to agree before a swap is priced (label_family block); a label match alone is never treated as the same basket
