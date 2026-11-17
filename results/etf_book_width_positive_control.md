# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5282 bars x 1522 names, 2005-02-23..2026-11-17, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 437.94% | -74.08% |
| 5 | 370.00% | -72.08% |
| 8 | 313.81% | -69.97% |
| 12 | 264.57% | -67.42% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 437.94% | 264.57% | -173.37pp | DETECTED |
| 1.0 | 50% | 46.42% | 40.30% | -6.12pp | DETECTED |
| 2.0 | 20% | 20.28% | 20.37% | +0.09pp | NOT_DETECTED |
| 4.0 | 6% | 7.54% | 11.27% | +3.73pp | NOT_DETECTED |
| 8.0 | 2% | 2.69% | 6.01% | +3.32pp | NOT_DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the width sign is still read correctly when the oracle carries only 50% of the score's variance, where the by-construction gap is 6.12pp; past that the ruler returns no sign. So the smallest width effect this ruler can see on this panel is about 6.12pp -- anything under it cannot be called an absence.

**Against the published book:** the real book's 1.28pp gap is SMALLER than the 6.12pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
