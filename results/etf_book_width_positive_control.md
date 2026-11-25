# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5287 bars x 1531 names, 2005-02-23..2026-11-24, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 434.22% | -73.75% |
| 5 | 367.11% | -71.68% |
| 8 | 311.19% | -69.60% |
| 12 | 262.28% | -67.04% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 434.22% | 262.28% | -171.94pp | DETECTED |
| 1.0 | 50% | 39.61% | 39.10% | -0.51pp | NOT_DETECTED |
| 2.0 | 20% | 16.81% | 18.77% | +1.96pp | NOT_DETECTED |
| 4.0 | 6% | 5.28% | 9.16% | +3.88pp | NOT_DETECTED |
| 8.0 | 2% | 0.03% | 4.78% | +4.75pp | NOT_DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the width sign is still read correctly when the oracle carries only 100% of the score's variance, where the by-construction gap is 171.94pp; past that the ruler returns no sign. So the smallest width effect this ruler can see on this panel is about 171.94pp -- anything under it cannot be called an absence.

**Against the published book:** the real book's 1.38pp gap is SMALLER than the 171.94pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
