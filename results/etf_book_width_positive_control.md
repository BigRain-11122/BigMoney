# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5284 bars x 1526 names, 2005-02-23..2026-11-19, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 432.74% | -74.07% |
| 5 | 365.81% | -72.06% |
| 8 | 310.17% | -69.96% |
| 12 | 262.08% | -67.42% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 432.74% | 262.08% | -170.66pp | DETECTED |
| 1.0 | 50% | 46.19% | 42.12% | -4.07pp | DETECTED |
| 2.0 | 20% | 17.42% | 20.93% | +3.51pp | NOT_DETECTED |
| 4.0 | 6% | 11.85% | 9.49% | -2.36pp | DETECTED |
| 8.0 | 2% | 3.93% | 6.27% | +2.34pp | NOT_DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the width sign is still read correctly when the oracle carries only 6% of the score's variance, where the by-construction gap is 2.36pp; past that the ruler returns no sign. So the smallest width effect this ruler can see on this panel is about 2.36pp -- anything under it cannot be called an absence.

**Against the published book:** the real book's 1.28pp gap is SMALLER than the 2.36pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
