# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5279 bars x 1519 names, 2005-02-23..2026-11-12, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.61% | 1.86% (13.75..-4.94) | +9.46pp | +6.15pp | 0.95 | 17.4% |
| 5 | 15.75% | 2.15% (13.60..-4.69) | +5.57pp | +10.18pp | 1.01 | 16.4% |
| 8 | 15.22% | 3.25% (11.97..-1.90) | +6.53pp | +8.69pp | 1.01 | 15.9% |
| 12 | 14.28% | 2.01% (12.27..-2.09) | +5.23pp | +9.05pp | 0.98 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.4

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
