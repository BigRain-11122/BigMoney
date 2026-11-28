# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5290 bars x 1539 names, 2005-02-23..2026-11-27, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 426.45% | -73.96% |
| 5 | 360.63% | -71.94% |
| 8 | 305.67% | -69.89% |
| 12 | 258.58% | -67.37% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 426.45% | 258.58% | -167.87pp | DETECTED |
| 1.0 | 50% | 44.88% | 34.84% | -10.04pp | DETECTED |
| 2.0 | 20% | 21.93% | 16.89% | -5.04pp | DETECTED |
| 4.0 | 6% | 10.08% | 8.06% | -2.02pp | DETECTED |
| 8.0 | 2% | 5.10% | 2.88% | -2.22pp | DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the ladder ran out before the ruler did: at the noisiest level sampled (oracle 2% of the score's variance) the by-construction gap is still only 2.22pp and the sign is still read correctly. So this ruler demonstrably sees a 2.22pp width effect; its true floor is somewhere BELOW that and is not measured here -- extend the ladder before quoting a floor.

**Against the published book:** the real book's 1.27pp gap is SMALLER than the 2.22pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
