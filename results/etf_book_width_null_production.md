# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5289 bars x 1536 names, 2005-02-23..2026-11-26, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 14.74% | -0.64% (15.38..-6.17) | +3.36pp | +11.38pp | 0.91 | 17.4% |
| 5 | 14.84% | -0.66% (15.50..-3.38) | +0.95pp | +13.89pp | 0.96 | 16.4% |
| 8 | 14.34% | -0.45% (14.79..-4.69) | +0.77pp | +13.57pp | 0.96 | 15.9% |
| 12 | 13.43% | -0.14% (13.57..-4.81) | +2.17pp | +11.26pp | 0.93 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.8

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
