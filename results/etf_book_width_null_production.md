# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5283 bars x 1523 names, 2005-02-23..2026-11-18, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.31% | 1.31% (14.00..-4.28) | +4.27pp | +11.04pp | 0.94 | 17.4% |
| 5 | 15.49% | 1.34% (14.15..-6.96) | +3.52pp | +11.97pp | 1.00 | 16.4% |
| 8 | 14.96% | -0.69% (15.65..-3.98) | +1.93pp | +13.03pp | 0.99 | 15.9% |
| 12 | 14.03% | -0.54% (14.57..-3.00) | +2.05pp | +11.98pp | 0.97 | 15.3% |

Verdict: **WIDTH_SIGN_IS_THE_NOISE_SIGN**
rank corr(width, CAGR): real -0.8 / null -0.6

Reading: the width direction here is the direction a signal-free book has, so this panel cannot credit it to the score; the honest output is 'needs its own null', never 'confirmed' (E276 rule 3).

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): omitted

The book in force is width 5; this face does not change it.
