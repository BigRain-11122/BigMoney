# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5285 bars x 1528 names, 2005-02-23..2026-11-20, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 429.58% | -74.13% |
| 5 | 363.32% | -72.13% |
| 8 | 308.02% | -70.07% |
| 12 | 260.40% | -67.56% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 429.58% | 260.40% | -169.18pp | DETECTED |
| 1.0 | 50% | 52.14% | 41.23% | -10.91pp | DETECTED |
| 2.0 | 20% | 32.71% | 20.43% | -12.28pp | DETECTED |
| 4.0 | 6% | 19.57% | 12.79% | -6.78pp | DETECTED |
| 8.0 | 2% | 14.43% | 7.38% | -7.05pp | DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the ladder ran out before the ruler did: at the noisiest level sampled (oracle 2% of the score's variance) the by-construction gap is still only 7.05pp and the sign is still read correctly. So this ruler demonstrably sees a 7.05pp width effect; its true floor is somewhere BELOW that and is not measured here -- extend the ladder before quoting a floor.

**Against the published book:** the real book's 1.29pp gap is SMALLER than the 7.05pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
