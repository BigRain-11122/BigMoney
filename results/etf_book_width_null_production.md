# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5278 bars x 1517 names, 2005-02-23..2026-11-11, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.63% | 5.87% (9.76..-5.48) | +11.46pp | +4.17pp | 0.95 | 17.4% |
| 5 | 15.78% | 3.00% (12.78..-5.95) | +11.08pp | +4.70pp | 1.01 | 16.4% |
| 8 | 15.24% | 2.31% (12.93..-3.47) | +8.76pp | +6.48pp | 1.01 | 15.9% |
| 12 | 14.30% | 2.33% (11.97..-1.92) | +5.74pp | +8.56pp | 0.98 | 15.3% |

Verdict: **WIDTH_SIGN_IS_THE_NOISE_SIGN**
rank corr(width, CAGR): real -0.8 / null -0.8

Reading: the width direction here is the direction a signal-free book has, so this panel cannot credit it to the score; the honest output is 'needs its own null', never 'confirmed' (E276 rule 3).

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
