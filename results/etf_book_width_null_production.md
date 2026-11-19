# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5284 bars x 1526 names, 2005-02-23..2026-11-19, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.26% | -0.13% (15.39..-5.36) | +3.50pp | +11.76pp | 0.94 | 17.4% |
| 5 | 15.45% | 0.83% (14.62..-2.28) | +5.82pp | +9.63pp | 1.00 | 16.4% |
| 8 | 14.93% | 0.09% (14.85..-4.26) | +6.30pp | +8.63pp | 0.99 | 15.9% |
| 12 | 13.98% | 0.32% (13.66..-0.50) | +4.39pp | +9.59pp | 0.97 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.4

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
