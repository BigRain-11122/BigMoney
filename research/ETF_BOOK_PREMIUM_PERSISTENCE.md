# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-17.json` (session 2026-11-17, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (512040,159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1498 | 0.04 | -2.95 | 0.527 | 0.3 | 52.2 | 1.00 | **MEAN_REVERTING** |
| 512040 | equity | 1908 | 0.02 | 0.73 | 0.507 | 0.2 | 47.7 | 1.43 | **LAG_DOMINATED** |
| 159655 | crossborder | 986 | 1.25 | 4.66 | 0.779 | 7.4 | 21.3 | 3.79 | **LAG_DOMINATED** |
| 513690 | crossborder | 1333 | -0.02 | -1.38 | 0.492 | 1.3 | 35.6 | 0.51 | **MEAN_REVERTING** |
| 159519 | crossborder | 776 | 0.23 | -1.23 | 0.567 | 0.7 | 34.2 | 0.73 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
