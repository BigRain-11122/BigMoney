# Did the paper ledger rewrite a bar it had already printed?

GENERATED-PROBE `2026-11-29T00:23:49+08:00` | evidence cutoff `2026-11-27`

**verdict: `LEDGER_RESTATES_SAME_BAR`**

5 of 6 paper traders restated a bar they had already printed (9 events, -51395.05 CNY of equity rewritten). 5 reader/trader gaps are open and 5 of them close against the restatement arithmetic to the cent -- the gap is the restatement, not an arithmetic error.

| traders | restated | events | equity rewritten | reader gaps | gaps closed by restatement |
|---|---|---|---|---|---|
| 6 | 5 | 9 | -51395.05 CNY | 5 | 5 |

## Bars printed twice

| trader | cutoff | first printed | last printed | equity | positions | cash | pocket |
|---|---|---|---|---|---|---|---|
| COMPOSITE-CE-01 | 2026-10-27 | 2026-10-27 21:26:16 | 2026-10-28 08:57:49 | -726.28 | +94397.62 | -95123.90 | POSITIONS_AND_CASH |
| COMPOSITE-CE-01 | 2026-11-27 | 2026-11-27 15:35:24 | 2026-11-28 22:20:04 | -3196.39 | +0.00 | -3196.39 | CASH_ONLY |
| COMPOSITE-CE-02 | 2026-10-27 | 2026-10-27 21:26:17 | 2026-10-28 08:57:50 | -2056.47 | +116798.35 | -118854.82 | POSITIONS_AND_CASH |
| COMPOSITE-CE-02 | 2026-11-27 | 2026-11-27 15:35:25 | 2026-11-28 22:20:06 | -11486.91 | +122051.62 | -133538.53 | POSITIONS_AND_CASH |
| DROUGHT-CE-01 | 2026-10-27 | 2026-10-27 21:26:17 | 2026-10-28 08:57:52 | -6146.93 | +47628.45 | -53775.38 | POSITIONS_AND_CASH |
| DROUGHT-CE-01 | 2026-11-27 | 2026-11-27 15:35:28 | 2026-11-28 22:20:08 | -5549.56 | +0.00 | -5549.56 | CASH_ONLY |
| ENGULF-CE-01 | 2026-10-27 | 2026-10-27 21:26:18 | 2026-10-28 08:57:53 | -8226.55 | +91903.87 | -100130.42 | POSITIONS_AND_CASH |
| ENGULF-CE-01 | 2026-11-27 | 2026-11-27 15:35:30 | 2026-11-28 22:20:10 | -11165.70 | +102110.54 | -113276.24 | POSITIONS_AND_CASH |
| VOLATILITY-CE-01 | 2026-11-27 | 2026-11-27 15:35:33 | 2026-11-28 22:20:14 | -2840.26 | +103108.79 | -105949.05 | POSITIONS_AND_CASH |

The two stamps are the ledger's own `updated` field, so a reader can date the rewrites without this face.

## Reader faces against the ledger as it stands today

| reader | stamp | ledger minus reader (s, + = reader first) | tolerance (CNY) | traders compared | behind | gap closed by restatement |
|---|---|---|---|---|---|---|
| strategy_scorecard | 2026-11-28T22:18:07 | 127.0 | 0.01 | 6 | 5 | 5 |
| paper_export | 2026-11-28 22:20:14 | 0.0 | 0.01 | 6 | 0 | 0 |
| ceo_live_page | 2026-11-28T22:26:08 | -354.0 | 0.50 | 6 | 0 | 0 |

### strategy_scorecard, item by item

| trader | reader | ledger | gap | restatement | matches |
|---|---|---|---|---|---|
| COMPOSITE-CE-01 | 982830.47 | 979634.08 | +3196.39 | +3196.39 | yes |
| COMPOSITE-CE-02 | 977953.38 | 966466.47 | +11486.91 | +11486.91 | yes |
| DROUGHT-CE-01 | 994450.43 | 988900.87 | +5549.56 | +5549.56 | yes |
| ENGULF-CE-01 | 988834.31 | 977668.61 | +11165.70 | +11165.70 | yes |
| VOLATILITY-CE-01 | 990675.40 | 987835.14 | +2840.26 | +2840.26 | yes |

## Notes

- Only (trader, cutoff) pairs printed with more than one capital signature count as a restatement; a normal bar advance is a new cutoff.
- POSITIONS_AND_CASH means marks stayed put while quantities moved -- the shape of a fill booked after the bar was published. CASH_ONLY moves the equity line without touching holdings.
- Cause is not determinable from the ledger alone: the paper books carry no trade tape, so this face reports the pocket, never the reason.
- A reader whose gap equals the restatement to the cent was reading the pre-restatement printing; one whose gap does not is a separate defect.
