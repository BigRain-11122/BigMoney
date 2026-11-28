# Two NAV sources, one session label

Board session `2026-11-27` (600 values, no per-row date) vs sina `fu_` (502 values, each carries its own date).

**SPLIT: 173 of 502 tickers differ by >= 0.10% (worst 159546: board 0.6088 vs dated 2026-11-27 0.5320 = 14.436%). The board file carries no per-row date, so for these rows the board number cannot be called that session's; only the dated source can.**

| compared | median abs gap | over 0.10% | sina date off board session |
|---|---|---|---|
| 502 | 0.0335% | 173 | 12 |

## Widest gaps (board vs dated)

| code | board | sina (dated) | sina date | gap |
|---|---|---|---|---|
| 159546 | 0.6088 | 0.5320 | 2026-11-27 | +14.4361% |
| 159012 | 0.6458 | 0.5650 | 2026-11-27 | +14.3009% |
| 159369 | 0.9485 | 0.8445 | 2026-11-27 | +12.3150% |
| 159675 | 1.0230 | 0.9171 | 2026-11-27 | +11.5473% |
| 159677 | 1.1612 | 1.0660 | 2026-11-27 | +8.9306% |
| 159147 | 0.6320 | 0.5838 | 2026-11-27 | +8.2563% |
| 159231 | 0.4057 | 0.3749 | 2026-11-27 | +8.2155% |
| 159628 | 1.0922 | 1.0121 | 2026-11-27 | +7.9142% |
| 159679 | 1.0464 | 0.9730 | 2026-11-27 | +7.5437% |
| 159608 | 0.7608 | 0.7098 | 2026-11-27 | +7.1851% |

## Dated source disagrees about WHICH day it is

| code | board session | sina date | gap |
|---|---|---|---|
| 159202 | 2026-11-27 | 2026-11-26 | +5.8400% |
| 159303 | 2026-11-27 | 2026-11-26 | +5.1774% |
| 159519 | 2026-11-27 | 2026-11-26 | +0.2121% |
| 159557 | 2026-11-27 | 2026-11-26 | +5.2552% |
| 159615 | 2026-11-27 | 2026-11-26 | +5.5698% |
| 159688 | 2026-11-27 | 2026-11-26 | +5.9986% |
| 159699 | 2026-11-27 | 2026-11-26 | +0.2039% |
| 159740 | 2026-11-27 | 2026-11-26 | +6.3679% |
| 159741 | 2026-11-27 | 2026-11-26 | +6.3790% |
| 159742 | 2026-11-27 | 2026-11-26 | +6.2213% |

## What this does and does not settle

- Settles: whether the board's whole-batch session label is defensible row by row.
- Does not settle: which of the two is the officially published NAV. A gap means one of them is not that session's number; identity requires the fund's own filing.
- A row absent from this table was not compared, not "agreed".
