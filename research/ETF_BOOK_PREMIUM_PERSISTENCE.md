# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-24.json` (session 2026-11-24, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (512040,159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1503 | 0.04 | -3.96 | 0.526 | 0.3 | 52.0 | 0.99 | **MEAN_REVERTING** |
| 512040 | equity | 1913 | 0.02 | -1.78 | 0.506 | 0.2 | 47.6 | 1.39 | **LAG_DOMINATED** |
| 159655 | crossborder | 991 | 1.26 | 2.55 | 0.779 | 7.2 | 21.4 | 3.71 | **LAG_DOMINATED** |
| 513690 | crossborder | 1338 | -0.02 | -5.17 | 0.490 | 1.3 | 35.5 | 0.49 | **MEAN_REVERTING** |
| 159519 | crossborder | 781 | 0.22 | -5.13 | 0.563 | 0.8 | 34.0 | 0.70 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
