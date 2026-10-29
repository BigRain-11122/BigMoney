# ETF book -- is the 20-bar vol estimator a level, or one calendar?

Question: r1327 priced the 20-bar estimator at +1.60pp over the 60-bar control on one decision calendar -- does that survive four phases of that calendar?

Window ends 2026-10-28 | 4 windows x 4 decision phases = 16 engine runs | 10bp/side | target vol 8%

**Verdict**: within noise: the arm wins on 4/4 phases with a median +1.50pp, but the control's own CAGR spans 1.81pp across those same phases -- the direction holds and the size cannot be told apart from calendar luck; keep the production window and print the range

## Every cell (arm minus the 60-bar control of its own phase)

| phase | start | ctrl CAGR | w20 dCAGR | w40 dCAGR | w120 dCAGR |
|---|---|---|---|---|---|
| 0 | 2020-01-02 | 9.70% | +1.60 | +0.58 | -2.39 |
| 1 | 2020-01-09 | 9.60% | +2.76 | +0.65 | -1.42 |
| 2 | 2020-01-16 | 9.12% | +1.40 | +0.66 | -2.05 |
| 3 | 2020-01-23 | 10.93% | +0.54 | +0.34 | -1.96 |

## The arm under test

w20 beats its own-phase control on **4/4** phases; median +1.50pp (min +0.54, max +2.76, spread 2.22pp); median dSharpe +0.120, median dMaxDD +0.41pp; sign test p=0.125.

## The ruler it has to clear

The 60-bar control itself spans +9.12..+10.93 across these four phases -- **1.81pp of pure calendar noise** (IQR 0.53pp). The claim under test is +1.60pp; it holds at that size in 50% of phases.

Read the two numbers together: a median effect smaller than the control's own phase spread cannot be told apart from having picked a lucky start date, which is exactly the trap r1325 found one layer up.

## Control

n12_r20 vol_window=60 @ phase0 -> published 9.70%, recomputed 9.70%, delta 0.00 pp (tolerance 0.50 pp). phase 0 is the published calendar, so it must reproduce the published arm.

## Caveats
- one panel, one cost model (10bp/side, next-open), survivor-pool caveat unchanged
- the arms differ ONLY in vol_window; selection, holdings and the cost model are shared, so a difference is the estimator's, not the book's
- four phases of ONE calendar is a ruler, not a sample: it bounds calendar luck, it does not test data dependence
- a sizing overlay is not an alpha; even a 'level' verdict here is a risk-shape proposal that needs a signed config decision
