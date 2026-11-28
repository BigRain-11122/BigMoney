# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-27.json` (session 2026-11-27, read from `base_bar`)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 4 leg(s) (510760,512040,513690,159519) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1506 | 0.04 | 3.80 | 0.526 | 0.3 | 52.1 | 2.07 | **LAG_DOMINATED** |
| 512040 | equity | 1916 | 0.02 | 1.76 | 0.506 | 0.2 | 47.6 | 1.76 | **LAG_DOMINATED** |
| 159655 | crossborder | 994 | 1.30 | 10.55 | 0.781 | 7.8 | 21.1 | 5.02 | **MIXED** |
| 513690 | crossborder | 1341 | -0.02 | -1.30 | 0.490 | 1.3 | 35.5 | 2.01 | **LAG_DOMINATED** |
| 159519 | crossborder | 784 | 0.22 | -0.70 | 0.562 | 0.7 | 34.1 | 3.08 | **LAG_DOMINATED** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

- Stamp freshness: a leg with `stamp_skipped` printed a NAV the panel had already superseded, so its 'today' premium is that many stamps old. Refresh the premium face (fetch) before quoting it.

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
