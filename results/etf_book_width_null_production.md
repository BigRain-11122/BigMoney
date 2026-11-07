# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5275 bars x 1515 names, 2005-02-23..2026-11-06, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.39% | 1.62% (13.77..-3.00) | +4.99pp | +10.40pp | 0.94 | 17.5% |
| 5 | 15.51% | 0.03% (15.48..-2.81) | +3.17pp | +12.34pp | 1.00 | 16.4% |
| 8 | 14.86% | 0.85% (14.02..-1.48) | +2.97pp | +11.89pp | 0.98 | 15.9% |
| 12 | 13.92% | 1.84% (12.08..-1.40) | +5.73pp | +8.19pp | 0.96 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.4

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): omitted

The book in force is width 5; this face does not change it.
