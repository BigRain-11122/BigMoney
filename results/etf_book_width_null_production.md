# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5277 bars x 1516 names, 2005-02-23..2026-11-10, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.60% | 1.90% (13.71..-2.32) | +10.11pp | +5.49pp | 0.95 | 17.4% |
| 5 | 15.76% | 0.70% (15.06..0.01) | +5.90pp | +9.86pp | 1.01 | 16.4% |
| 8 | 15.19% | 1.73% (13.46..-2.34) | +5.98pp | +9.21pp | 1.00 | 15.9% |
| 12 | 14.24% | 2.25% (11.98..-1.24) | +3.51pp | +10.73pp | 0.98 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.4

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
