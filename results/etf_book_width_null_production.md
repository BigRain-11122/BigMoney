# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5282 bars x 1522 names, 2005-02-23..2026-11-17, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.29% | 4.40% (10.89..-2.67) | +17.39pp | -2.10pp | 0.94 | 17.4% |
| 5 | 15.50% | 2.80% (12.71..-1.83) | +10.25pp | +5.25pp | 1.00 | 16.4% |
| 8 | 14.95% | 1.50% (13.45..-1.66) | +5.52pp | +9.43pp | 0.99 | 15.9% |
| 12 | 14.01% | 0.44% (13.57..-0.45) | +3.22pp | +10.79pp | 0.97 | 15.3% |

Verdict: **WIDTH_SIGN_IS_THE_NOISE_SIGN**
rank corr(width, CAGR): real -0.8 / null -1.0

Reading: the width direction here is the direction a signal-free book has, so this panel cannot credit it to the score; the honest output is 'needs its own null', never 'confirmed' (E276 rule 3).

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
