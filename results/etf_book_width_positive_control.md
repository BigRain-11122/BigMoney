# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5289 bars x 1536 names, 2005-02-23..2026-11-26, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 429.38% | -73.99% |
| 5 | 363.00% | -71.97% |
| 8 | 307.57% | -69.92% |
| 12 | 259.96% | -67.40% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 429.38% | 259.96% | -169.42pp | DETECTED |
| 1.0 | 50% | 52.56% | 39.05% | -13.51pp | DETECTED |
| 2.0 | 20% | 24.03% | 20.78% | -3.25pp | DETECTED |
| 4.0 | 6% | 11.36% | 11.51% | +0.15pp | NOT_DETECTED |
| 8.0 | 2% | 6.78% | 7.12% | +0.34pp | NOT_DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the width sign is still read correctly when the oracle carries only 20% of the score's variance, where the by-construction gap is 3.25pp; past that the ruler returns no sign. So the smallest width effect this ruler can see on this panel is about 3.25pp -- anything under it cannot be called an absence.

**Against the published book:** the real book's 1.31pp gap is SMALLER than the 3.25pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
