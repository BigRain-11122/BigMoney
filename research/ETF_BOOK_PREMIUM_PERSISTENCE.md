# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-19.json` (session 2026-11-19, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (512040,159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1500 | 0.04 | -3.03 | 0.527 | 0.3 | 52.1 | 1.00 | **MEAN_REVERTING** |
| 512040 | equity | 1910 | 0.02 | -0.03 | 0.507 | 0.2 | 47.7 | 1.41 | **LAG_DOMINATED** |
| 159655 | crossborder | 988 | 1.26 | 4.87 | 0.779 | 7.4 | 21.3 | 3.79 | **LAG_DOMINATED** |
| 513690 | crossborder | 1335 | -0.02 | -3.02 | 0.491 | 1.3 | 35.5 | 0.50 | **MEAN_REVERTING** |
| 159519 | crossborder | 778 | 0.23 | -2.64 | 0.566 | 0.7 | 34.1 | 0.72 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
