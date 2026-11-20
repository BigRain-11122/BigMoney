# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-20.json` (session 2026-11-20, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (512040,159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1501 | 0.04 | -4.35 | 0.526 | 0.3 | 52.1 | 0.98 | **MEAN_REVERTING** |
| 512040 | equity | 1911 | 0.02 | -1.28 | 0.507 | 0.2 | 47.7 | 1.40 | **LAG_DOMINATED** |
| 159655 | crossborder | 989 | 1.26 | 0.17 | 0.780 | 7.2 | 21.3 | 3.62 | **LAG_DOMINATED** |
| 513690 | crossborder | 1336 | -0.02 | -4.05 | 0.491 | 1.3 | 35.5 | 0.49 | **MEAN_REVERTING** |
| 159519 | crossborder | 779 | 0.22 | -3.83 | 0.565 | 0.8 | 34.1 | 0.71 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
