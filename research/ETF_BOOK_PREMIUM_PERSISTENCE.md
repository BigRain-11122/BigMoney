# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-11.json` (session None)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 4 leg(s) (510760,159655,513690,159519) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 1494 | 0.05 | 0.30 | 0.529 | 0.3 | 52.2 | 1.03 | **LAG_DOMINATED** |
| 512040 | equity | 1904 | 0.02 | -0.60 | 0.507 | 0.2 | 47.8 | 0.84 | **MEAN_REVERTING** |
| 159655 | crossborder | 982 | 1.23 | 9.55 | 0.778 | 7.6 | 21.4 | 5.01 | **LAG_DOMINATED** |
| 513690 | crossborder | 1329 | -0.01 | -1.06 | 0.494 | 1.3 | 35.7 | 1.54 | **LAG_DOMINATED** |
| 159519 | crossborder | 772 | 0.24 | -0.96 | 0.570 | 0.7 | 34.4 | 1.16 | **LAG_DOMINATED** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
