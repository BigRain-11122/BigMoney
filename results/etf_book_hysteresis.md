# ETF book -- decision margins and a hysteresis buffer

Window ends 2026-11-10 | 12-name book, 20-bar cadence, 10bp/side, vol target 8%

## Control arm (must hold before any other arm is read)

k=0 reproduces the published n12_vt08 cell: 9.62% vs 9.62% (delta +0.000pp, within tolerance)

## How close are the decisions?

83 decisions; the 12th-vs-13th score gap as a fraction of that bar's own score sd:
* q0.1 = 0.001 sd
* q0.25 = 0.006 sd
* q0.5 = 0.018 sd
* q0.75 = 0.052 sd
* q0.9 = 0.112 sd

Decisions whose cut margin is under 0.10 sd: **87%**; under 0.25 sd: 0%.

Trades actually made: 590 pairs, median gap 0.974 sd; 3% of them were decided by less than 0.10 sd.

## Buffer arms

| k (sd) | turnover/decision | CAGR full | Sharpe | maxDD | IS CAGR | OOS CAGR | OOS Sharpe |
|---|---|---|---|---|---|---|---|
| 0.00 | 0.934 | 9.62% | 0.990 | -11.77% | 3.84% | 18.31% | 1.728 |
| 0.05 | 0.901 | 9.69% | 1.004 | -11.59% | 4.02% | 18.20% | 1.745 |
| 0.10 | 0.887 | 9.68% | 1.000 | -12.58% | 3.74% | 18.62% | 1.757 |
| 0.20 | 0.843 | 9.77% | 1.014 | -12.47% | 4.09% | 18.27% | 1.732 |
| 0.35 | 0.762 | 9.65% | 0.995 | -12.57% | 4.02% | 18.05% | 1.664 |
| 0.50 | 0.702 | 9.77% | 1.007 | -13.48% | 4.08% | 18.28% | 1.661 |

## Caveats

* exploratory: no preregistration, no verdict, no ledger booking
* MEASURED (results/etf_book_buffer_adoption.json): that path-dependence test was run on 60 cells -- verdict REJECT. Read the arms above as one decision sequence, not an edge.
* the buffer is path-dependent; a single better arm can be one decision sequence
* one panel / one window / one cost model; survivor-pool and 2024+ regime caveats unchanged
* an arm that lowers turnover and lowers return by less is a cost effect, not skill
