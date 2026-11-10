# Premium persistence -- is today's cross-border premium a condition or a convention?

Ticket: `results\etf_book_order\TICKET-2026-11-09.json` (session None)

## Answer

**TODAYS_PREMIUM_IS_A_CONVENTION** -- 2 leg(s) (159577,159263) move more when the NAV stamp shifts than the premium they print

| leg | class | n | median % | today % | share>0 | half-life (sess) | crossings/100 | lag spread (today) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 159501 | crossborder | 824 | 1.28 | 21.16 | 0.801 | 28.4 | 18.3 | 7.84 | **MIXED** |
| 513100 | crossborder | 1901 | 1.26 | 18.63 | 0.795 | 10.7 | 16.6 | 7.66 | **MIXED** |
| 513690 | crossborder | 1327 | -0.01 | 0.00 | 0.494 | 1.3 | 35.7 | 3.23 | **MEAN_REVERTING** |
| 159577 | crossborder | 657 | 1.76 | 8.90 | 0.903 | 4.7 | 11.3 | 5.46 | **LAG_DOMINATED** |
| 159263 | equity | 325 | 0.11 | -0.65 | 0.538 | 0.1 | 48.8 | 1.40 | **LAG_DOMINATED** |

## What this face will not say

- the NAV panel carries no subscription-status column, so the 限购 hypothesis is tested through its observable implication (a standing positive level) and against the NAV-stamp alternative; standing level is consistent with, not proof of, a limited fund

A high premium is not a sell signal: a limited fund can stay expensive for years. The stamp ladder only bounds how much of the reading is accounting.
