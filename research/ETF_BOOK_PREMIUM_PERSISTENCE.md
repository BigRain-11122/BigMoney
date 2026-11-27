# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-26.json` (session 2026-11-26, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 1 leg(s) (159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1505 | 0.04 | -5.83 | 0.525 | 0.4 | 51.9 | 0.97 | **MEAN_REVERTING** |
| 512040 | equity | 1915 | 0.02 | -2.95 | 0.505 | 0.2 | 47.6 | 1.37 | **MEAN_REVERTING** |
| 159655 | crossborder | 993 | 1.25 | 1.20 | 0.779 | 7.1 | 21.4 | 3.66 | **LAG_DOMINATED** |
| 513690 | crossborder | 1340 | -0.02 | -4.48 | 0.490 | 1.4 | 35.4 | 0.49 | **MEAN_REVERTING** |
| 159519 | crossborder | 783 | 0.22 | -4.51 | 0.562 | 0.8 | 33.9 | 0.71 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
