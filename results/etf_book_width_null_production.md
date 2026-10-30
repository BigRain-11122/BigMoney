# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5270 bars x 1504 names, 2005-02-23..2026-10-30, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.58% | 0.77% (14.82..-6.53) | +3.39pp | +12.19pp | 0.95 | 17.4% |
| 5 | 15.73% | 0.30% (15.43..-2.89) | +2.23pp | +13.50pp | 1.01 | 16.4% |
| 8 | 15.15% | 0.48% (14.67..-1.70) | +2.64pp | +12.51pp | 1.00 | 15.9% |
| 12 | 14.21% | 1.77% (12.44..-1.63) | +3.68pp | +10.53pp | 0.98 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.4

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
