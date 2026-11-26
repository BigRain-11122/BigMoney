# ETF book -- decision margins and a hysteresis buffer

Window ends 2026-11-25 | 12-name book, 20-bar cadence, 10bp/side, vol target 8%

## Control arm (must hold before any other arm is read)

k=0 reproduces the published n12_vt08 cell: 8.98% vs 8.98% (delta +0.000pp, within tolerance)

## How close are the decisions?

84 decisions; the 12th-vs-13th score gap as a fraction of that bar's own score sd:
* q0.1 = 0.001 sd
* q0.25 = 0.006 sd
* q0.5 = 0.018 sd
* q0.75 = 0.052 sd
* q0.9 = 0.112 sd

Decisions whose cut margin is under 0.10 sd: **87%**; under 0.25 sd: 0%.

Trades actually made: 599 pairs, median gap 0.975 sd; 3% of them were decided by less than 0.10 sd.

## Buffer arms

| k (sd) | turnover/decision | CAGR full | Sharpe | maxDD | IS CAGR | OOS CAGR | OOS Sharpe |
|---|---|---|---|---|---|---|---|
| 0.00 | 0.938 | 8.98% | 0.928 | -11.77% | 3.84% | 16.56% | 1.570 |
| 0.05 | 0.905 | 9.05% | 0.942 | -11.59% | 4.02% | 16.45% | 1.584 |
| 0.10 | 0.891 | 9.04% | 0.938 | -12.58% | 3.74% | 16.85% | 1.598 |
| 0.20 | 0.848 | 9.13% | 0.951 | -12.47% | 4.09% | 16.50% | 1.571 |
| 0.35 | 0.767 | 8.95% | 0.927 | -12.57% | 4.02% | 16.14% | 1.498 |
| 0.50 | 0.707 | 9.13% | 0.946 | -13.48% | 4.08% | 16.52% | 1.516 |

## Caveats

* exploratory: no preregistration, no verdict, no ledger booking
* MEASURED (results/etf_book_buffer_adoption.json): that path-dependence test was run on 60 cells -- verdict REJECT. Read the arms above as one decision sequence, not an edge.
* the buffer is path-dependent; a single better arm can be one decision sequence
* one panel / one window / one cost model; survivor-pool and 2024+ regime caveats unchanged
* an arm that lowers turnover and lowers return by less is a cost effect, not skill
