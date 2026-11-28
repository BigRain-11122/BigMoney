# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5290 bars x 1539 names, 2005-02-23..2026-11-27, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 14.72% | 1.00% (13.72..-1.79) | +4.19pp | +10.53pp | 0.91 | 17.4% |
| 5 | 14.90% | 0.09% (14.82..-2.55) | +4.77pp | +10.13pp | 0.97 | 16.4% |
| 8 | 14.37% | 1.66% (12.71..-4.23) | +4.32pp | +10.05pp | 0.96 | 15.9% |
| 12 | 13.45% | 0.11% (13.34..-2.94) | +2.70pp | +10.75pp | 0.94 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.0

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
