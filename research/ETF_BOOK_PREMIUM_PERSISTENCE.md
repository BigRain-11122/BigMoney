# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-12.json` (session None)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 3 leg(s) (510760,512040,159655) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1495 | 0.05 | -0.77 | 0.528 | 0.2 | 52.3 | 1.02 | **LAG_DOMINATED** |
| 512040 | equity | 1905 | 0.02 | -0.94 | 0.507 | 0.2 | 47.7 | 1.40 | **LAG_DOMINATED** |
| 159655 | crossborder | 983 | 1.25 | 9.44 | 0.778 | 7.6 | 21.4 | 5.00 | **LAG_DOMINATED** |
| 513690 | crossborder | 1330 | -0.01 | -1.04 | 0.493 | 1.3 | 35.7 | 0.51 | **MEAN_REVERTING** |
| 159519 | crossborder | 773 | 0.23 | -1.57 | 0.569 | 0.7 | 34.3 | 0.73 | **MEAN_REVERTING** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
