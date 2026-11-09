# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-06` | ticket `TICKET-2026-11-06.json` | source `results\etf_book_sibling_entry.json`

**today the swap is worth 9,762 CNY of which 1,879 is repeatable at the historical average gap and 7,883 is a one-off: 2 pair(s) persistent (the toll repeats)**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|
| 159501 | 159513 纳斯达克100ETF大成 | NDX100 | 8.6708 pp | 1.0498 pp | 1.9692 | 794 | 99.75 | PERSISTENT_GAP |
| 513100 | 159513 纳斯达克100ETF大成 | NDX100 | 6.2867 pp | 1.6859 pp | 1.7295 | 794 | 98.87 | PERSISTENT_GAP |
| 159577 | 513850 美国50ETF易方达 | US50 | 0.1903 pp | -0.1868 pp | 0.647 | 657 | 80.37 | NO_GAP |

## 159501 -> 159513 (PERSISTENT_GAP)

the dearer ticker has been dearer on 76% of 794 sessions and the average gap is 1.0498 pp: re-tickering the book is a permanent fix, not a daily decision -- but today's 8.6708 pp is the 99.75-th percentile of that history, so only the average repeats and today's excess is an episode

- window 2023-07-28..2026-11-09 (794 common sessions), reconstructed gap mean 1.0498 pp, median 0.6786 pp, sd 1.9692 pp
- today z = 3.87, percentile = 99.75, positive on 76% of sessions
- half-split means -0.0832 pp / 2.1828 pp; last 250 sessions mean 3.1893 pp
- NAV-base offset pinned today = 10.4706 pp (the raw close ratio level, 19.14 pp, is not a premium)
- today 5,612 CNY of basket gain: 723 repeatable at the average gap, 4,890 one-off
- 14 step(s) > 3.0 sd: 2024-07-09 +1.09pp, 2025-01-07 -1.03pp, 2025-02-10 +1.15pp, 2025-11-14 +1.08pp, 2026-05-28 +1.12pp, 2026-06-10 -1.53pp

## 513100 -> 159513 (PERSISTENT_GAP)

the dearer ticker has been dearer on 88% of 794 sessions and the average gap is 1.6859 pp: re-tickering the book is a permanent fix, not a daily decision -- but today's 6.2867 pp is the 98.87-th percentile of that history, so only the average repeats and today's excess is an episode

- window 2023-07-28..2026-11-09 (794 common sessions), reconstructed gap mean 1.6859 pp, median 1.6895 pp, sd 1.7295 pp
- today z = 2.66, percentile = 98.87, positive on 88% of sessions
- half-split means 0.7534 pp / 2.6184 pp; last 250 sessions mean 3.2431 pp
- NAV-base offset pinned today = 17.0011 pp (the raw close ratio level, 23.29 pp, is not a premium)
- today 4,149 CNY of basket gain: 1,156 repeatable at the average gap, 2,994 one-off
- 10 step(s) > 3.0 sd: 2024-07-08 +1.10pp, 2024-07-11 -1.26pp, 2024-07-15 +1.12pp, 2024-09-04 -1.22pp, 2024-09-06 +1.14pp, 2025-03-14 +1.06pp

## 159577 -> 513850 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2024-02-23..2026-11-09 (657 common sessions), reconstructed gap mean -0.1868 pp, median -0.0073 pp, sd 0.647 pp
- today z = 0.583, percentile = 80.37, positive on 49% of sessions
- half-split means -0.3557 pp / -0.0183 pp; last 250 sessions mean -0.0529 pp
- NAV-base offset pinned today = -10.776 pp (the raw close ratio level, -10.59 pp, is not a premium)
- 7 step(s) > 3.0 sd: 2024-07-05 -1.67pp, 2024-07-29 -1.08pp, 2024-08-13 -1.39pp, 2024-08-14 -0.99pp, 2024-09-04 +1.07pp, 2026-05-27 -3.52pp

## legs the sibling face could not price

- 513690: label 港股红利ETF names no other live ticker on this board (no sibling group)
- 159263: label 价值ETF names no other live ticker on this board (no sibling group)

## caveats

- the reconstructed gap is anchored on ONE session's IOPV pair; every earlier value inherits the assumption that the two funds' NAV-per-unit ratio has not moved, and steps are published as the evidence against that assumption
- closes are as-traded, not total-return: a distribution to one fund only lands as a step and is flagged, not corrected
- same index, not same basket: tracking difference, fee, size, quotation width and FX-hedge policy are NOT priced here
- premium history from our own board starts at one session; this face uses the price ratio for history precisely because it is the only long series we have
- a step is a flag, not an error: the level after a step is still the level a buyer would pay today
