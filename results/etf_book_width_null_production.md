# ETF book: does the width sign survive a signal-free book on the same panel?

Panel 5287 bars x 1531 names, 2005-02-23..2026-11-24, cadence 20, toll 10bp. Real score vs 6 seeded
random scores on the same eligibility mask.

| width | real CAGR | null median (min..max) | real-null | real - best null | real Sharpe | real vol |
|---|---|---|---|---|---|
| 3 | 15.06% | -1.92% (16.98..-4.37) | +8.56pp | +6.50pp | 0.92 | 17.5% |
| 5 | 15.12% | 1.05% (14.06..-2.27) | +6.96pp | +8.16pp | 0.98 | 16.4% |
| 8 | 14.64% | 0.81% (13.83..-2.08) | +2.32pp | +12.32pp | 0.97 | 15.9% |
| 12 | 13.68% | 0.65% (13.04..-2.90) | +4.05pp | +9.63pp | 0.95 | 15.3% |

Verdict: **WIDTH_SIGN_DIFFERS_FROM_NOISE**
rank corr(width, CAGR): real -0.8 / null 0.2

Reading: the real score's width direction differs from the signal-free book's, so the direction is not purely diversification arithmetic on this panel.

The null is an estimate: its per-seed range is published, and the last money column is the gap to its BEST draw (not its median).

Cross-rule check (r1291: a width difference means nothing until the leverage rule is fixed): RULES_DISAGREE_ON_THE_WIDTH_SIGN

The book in force is width 5; this face does not change it.
