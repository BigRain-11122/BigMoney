# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5288 bars x 1532 names, 2005-02-23..2026-11-25, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 14.83% | 1.40% (13.44..-3.97) | +5.97pp | +8.86pp | 0.91 | 17.5% |
| 5 | 14.93% | 1.29% (13.64..-1.51) | +4.87pp | +10.06pp | 0.97 | 16.4% |
| 8 | 14.43% | 0.95% (13.48..0.13) | +2.59pp | +11.84pp | 0.96 | 15.9% |
| 12 | 13.50% | -0.24% (13.74..-0.71) | +1.41pp | +12.09pp | 0.94 | 15.3% |

Verdict: **WIDTH_SIGN_IS_THE_NOISE_SIGN**
rank corr(width, CAGR): real -0.8 / null -1.0

Reading: the width direction here is the direction a signal-free book has, so this panel cannot credit it to the score; the honest output is 'needs its own null', never 'confirmed' (E276 rule 3).

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
