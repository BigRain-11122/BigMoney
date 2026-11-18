# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5283 bars x 1523 names, 2005-02-23..2026-11-18, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 435.25% | -74.03% |
| 5 | 367.85% | -72.03% |
| 8 | 311.82% | -69.94% |
| 12 | 263.29% | -67.39% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 435.25% | 263.29% | -171.96pp | DETECTED |
| 1.0 | 50% | 42.73% | 37.78% | -4.95pp | DETECTED |
| 2.0 | 20% | 15.31% | 18.80% | +3.49pp | NOT_DETECTED |
| 4.0 | 6% | 6.79% | 10.58% | +3.79pp | NOT_DETECTED |
| 8.0 | 2% | 1.90% | 5.47% | +3.57pp | NOT_DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the width sign is still read correctly when the oracle carries only 50% of the score's variance, where the by-construction gap is 4.95pp; past that the ruler returns no sign. So the smallest width effect this ruler can see on this panel is about 4.95pp -- anything under it cannot be called an absence.

**Against the published book:** the real book's 1.28pp gap is SMALLER than the 4.95pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
