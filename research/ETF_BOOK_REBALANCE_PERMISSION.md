# May the 2026-11-11 rebalance keep this size?

ticket `TICKET-2026-11-06.json` | evidence cutoff 2026-11-06 | decision date 2026-11-11 | beta target 0.2

**KEEP_STANDS_ON_NON_PATH_ARGUMENT** — keeping k=0.460253 stands only on denominator, which is a static mix and not a decision path; all 3 path reading(s) sit below the money (highest k=0.432195), so the 2026-11-11 rebalance must size at k=0.393073 (CNY 392,616, a cut of CNY 67,180 = 6.72pp) unless a caliber prereg lands first

| reading | k | vs money (pp) | kind | why |
|---|---|---|---|---|
| baseline_published | 0.460253 | +0.00 | circular | the construction the ticket was priced from (k == k_now by identity) |
| window | 0.412669 | -4.76 | path | measured on 306 bars |
| universe | 0.432195 | -2.81 | path | measured on 1658 bars |
| window_x_universe | 0.393073 | -6.72 | path | measured on 306 bars |
| denominator | 0.544424 | +8.42 | static | static composition, not a path: only comparable with the path rows because it is divided by covered weight |

- money in force: k=0.460253 = CNY 459,796 of a CNY 1,000,000 NAV
- permitted floor over 3 path reading(s): k=0.393073 = CNY 392,616
- cut if reprice is required: k -0.067180 (6.72pp) = CNY 67,180
- supporters at the money: denominator (path: none / non-path: denominator)
- the trap: reading 'some ruler permits a larger size' as permission reads k=0.544424 -> keep=True

## supply side (carried, not re-judged)

- book `nobond_vt08_adopted`: **CONDITIONAL** (failed: Y4_top2_share)
- top-2 year share 0.7108 vs line 0.7

## not measured by this face

- the wrapper's yearly shape: beta overlay + GC001 cash leg have never been through the year gate (r1438), so a smaller k is not automatically a passing book
- which reading is the RIGHT measurement: the four-cell spread is a ruler choice and no caliber prereg has landed (r1446 four requirements)
- the cost of the cut: the ticket's own reprice delta (CNY 91.7 at the 11-06 bar) is not carried into the gate, and a 6.72pp cut pays one more round of 8bp

