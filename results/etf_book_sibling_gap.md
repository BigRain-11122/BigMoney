# ETF book -- the sibling premium gap: a price today, or a rule?

session `2026-11-06` | ticket `TICKET-2026-11-06.json` | source `results\etf_book_sibling_entry.json`

**today the swap is worth 9,762 CNY of which 1,540 is repeatable at the historical average gap and 8,222 is a one-off: 2 pair(s) persistent (the toll repeats)**

| leg | sibling | index | today gap | history mean | sd | days | percentile | verdict |
|---|---|---|---|---|---|---|---|---|
| 159501 | 159513 纳斯达克100ETF大成 | NDX100 | 8.6708 pp | 0.8316 pp | 1.9518 | 793 | 100.0 | PERSISTENT_GAP |
| 513100 | 159513 纳斯达克100ETF大成 | NDX100 | 6.2867 pp | 1.4062 pp | 1.7228 | 793 | 99.62 | PERSISTENT_GAP |
| 159577 | 513850 美国50ETF易方达 | US50 | 0.1903 pp | -0.0758 pp | 0.6473 | 656 | 63.72 | NO_GAP |

## 159501 -> 159513 (PERSISTENT_GAP)

the dearer ticker has been dearer on 70% of 793 sessions and the average gap is 0.8316 pp: re-tickering the book is a permanent fix, not a daily decision -- but today's 8.6708 pp is the 100.0-th percentile of that history, so only the average repeats and today's excess is an episode

- window 2023-07-28..2026-11-06 (793 common sessions), reconstructed gap mean 0.8316 pp, median 0.47 pp, sd 1.9518 pp
- today z = 4.017, percentile = 100.0, positive on 70% of sessions
- half-split means -0.2921 pp / 1.9524 pp; last 250 sessions mean 2.9513 pp
- NAV-base offset pinned today = 10.6792 pp (the raw close ratio level, 19.35 pp, is not a premium)
- today 5,612 CNY of basket gain: 574 repeatable at the average gap, 5,039 one-off
- 14 step(s) > 3.0 sd: 2024-07-09 +1.09pp, 2025-01-07 -1.03pp, 2025-02-10 +1.15pp, 2025-11-14 +1.08pp, 2026-05-28 +1.12pp, 2026-06-10 -1.53pp

## 513100 -> 159513 (PERSISTENT_GAP)

the dearer ticker has been dearer on 86% of 793 sessions and the average gap is 1.4062 pp: re-tickering the book is a permanent fix, not a daily decision -- but today's 6.2867 pp is the 99.62-th percentile of that history, so only the average repeats and today's excess is an episode

- window 2023-07-28..2026-11-06 (793 common sessions), reconstructed gap mean 1.4062 pp, median 1.4128 pp, sd 1.7228 pp
- today z = 2.833, percentile = 99.62, positive on 86% of sessions
- half-split means 0.476 pp / 2.3341 pp; last 250 sessions mean 2.9562 pp
- NAV-base offset pinned today = 17.275 pp (the raw close ratio level, 23.56 pp, is not a premium)
- today 4,149 CNY of basket gain: 966 repeatable at the average gap, 3,183 one-off
- 10 step(s) > 3.0 sd: 2024-07-08 +1.10pp, 2024-07-11 -1.26pp, 2024-07-15 +1.12pp, 2024-09-04 -1.22pp, 2024-09-06 +1.14pp, 2025-03-14 +1.06pp

## 159577 -> 513850 (NO_GAP)

today's gap is under the 0.5 pp materiality line: nothing to swap

- window 2024-02-23..2026-11-06 (656 common sessions), reconstructed gap mean -0.0758 pp, median 0.1042 pp, sd 0.6473 pp
- today z = 0.411, percentile = 63.72, positive on 62% of sessions
- half-split means -0.2442 pp / 0.0926 pp; last 250 sessions mean 0.0595 pp
- NAV-base offset pinned today = -10.8875 pp (the raw close ratio level, -10.7 pp, is not a premium)
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
