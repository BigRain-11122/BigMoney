# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-13.json` (session 2026-11-13, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (510760,512040) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1496 | 0.05 | -1.63 | 0.528 | 0.3 | 52.2 | 1.01 | **LAG_DOMINATED** |
| 512040 | equity | 1906 | 0.02 | -0.78 | 0.506 | 0.2 | 47.7 | 1.40 | **LAG_DOMINATED** |
| 159655 | crossborder | 984 | 1.25 | 8.28 | 0.778 | 7.5 | 21.4 | 3.92 | **MIXED** |
| 513690 | crossborder | 1331 | -0.01 | -1.56 | 0.493 | 1.3 | 35.6 | 0.51 | **MEAN_REVERTING** |
| 159519 | crossborder | 774 | 0.23 | -1.63 | 0.568 | 0.7 | 34.3 | 0.73 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
