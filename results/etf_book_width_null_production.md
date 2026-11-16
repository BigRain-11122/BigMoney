# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5281 bars x 1521 names, 2005-02-23..2026-11-16, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.40% | -1.28% (16.68..-4.59) | +6.58pp | +8.82pp | 0.94 | 17.4% |
| 5 | 15.55% | -1.48% (17.03..-3.59) | +2.78pp | +12.77pp | 1.00 | 16.4% |
| 8 | 15.04% | 1.38% (13.66..-1.99) | +3.29pp | +11.75pp | 1.00 | 15.9% |
| 12 | 14.11% | 0.40% (13.71..-1.81) | +3.50pp | +10.61pp | 0.97 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.6

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
