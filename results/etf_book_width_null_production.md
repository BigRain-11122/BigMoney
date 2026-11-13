# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5280 bars x 1520 names, 2005-02-23..2026-11-13, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.55% | -2.40% (17.95..-9.71) | +4.30pp | +11.25pp | 0.95 | 17.4% |
| 5 | 15.67% | -0.19% (15.87..-9.24) | +4.13pp | +11.54pp | 1.01 | 16.4% |
| 8 | 15.15% | 1.19% (13.96..-4.23) | +4.45pp | +10.70pp | 1.00 | 15.9% |
| 12 | 14.21% | 2.10% (12.12..-1.49) | +3.75pp | +10.46pp | 0.98 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 1.0

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
