# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5285 bars x 1528 names, 2005-02-23..2026-11-20, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.00% | 2.24% (12.76..-1.08) | +3.38pp | +11.62pp | 0.92 | 17.4% |
| 5 | 15.18% | 1.30% (13.88..-0.58) | +3.45pp | +11.73pp | 0.98 | 16.4% |
| 8 | 14.66% | 1.38% (13.29..-2.11) | +4.17pp | +10.49pp | 0.97 | 15.9% |
| 12 | 13.71% | 1.45% (12.26..-0.82) | +5.40pp | +8.31pp | 0.95 | 15.3% |

Verdict: **WIDTH_SIGN_IS_THE_NOISE_SIGN**
rank corr(width, CAGR): real -0.8 / null -0.2

Reading: the width direction here is the direction a signal-free book has, so this panel cannot credit it to the score; the honest output is 'needs its own null', never 'confirmed' (E276 rule 3).

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
