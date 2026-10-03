# Monthly exam 2026-10 -- roster face: six-member month-open baseline

- ticket: T-2026-10-01-143 face 1 (O-20261001-2355 sec.3)
- month-open boundary: 2026-10-01; month-open bar: 2026-09-30
- capture: pinned during 2026-10 golden-week holiday window: no bars between 2026-09-30 and 2026-10-09, so this capture == month-open state; do not overwrite after 2026-10-09 (version a new file instead)
- window: zero bars in the 2026-10 exam window at capture (golden week; resumes 10-09); exam-day assembly is date-driven (face-6 runbook)
- B_MAXDIV crosscheck vs accounts baseline: MATCH (5998495.76 == 5998495.76)
- benchmark double-line: 510300 month-open close 4.4320 (unadjusted buy&hold caliber); 48EW daily-rebalanced (o1600 single-source) starts at first in-window bar 10-09

| trader | hire | month-open equity (CNY) | positions | unrealized PnL (CNY) | x2_watch | YTD | beat 300 (pp) | beat 48EW (pp) |
|---|---|---:|--:|--:|---|--:|--:|--:|
| COMPOSITE-CE-01 | 2026-09-23 | 1001009.96 | 5 | 2248.84 | ok | 5.83% | 14.34 | 12.63 |
| COMPOSITE-CE-02 | 2026-09-23 | 1000665.47 | 8 | 1903.83 | probation | 4.67% | 13.17 | 11.46 |
| DROUGHT-CE-01 | 2026-09-23 | 1000000.00 | 0 | 0.00 | ok | 3.99% | 12.50 | 10.78 |
| ENGULF-CE-01 | 2026-09-23 | 1000000.00 | 0 | 0.00 | probation | -0.87% | 7.63 | 5.92 |
| NEEDLE-DE-01 | 2026-09-23 | 1000000.00 | 0 | 0.00 | ok | 0.61% | 9.12 | 7.40 |
| VOLATILITY-CE-01 | 2026-09-23 | 996820.33 | 5 | -2527.62 | ok | 2.61% | 11.11 | 9.40 |

- honesty anchors: window_metrics status=insufficient_data (bars<20 suppression per D-20260930-27 Q3) is carried in the JSON face and must not be quoted as annualized stats; anchor IS/OOS block = hire-time registration anchor, not exam evidence; negative results as-is.
