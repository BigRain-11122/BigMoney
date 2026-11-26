# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5288 bars x 1532 names, 2005-02-23..2026-11-25, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 432.31% | -74.06% |
| 5 | 365.33% | -72.04% |
| 8 | 309.56% | -69.97% |
| 12 | 261.37% | -67.46% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 432.31% | 261.37% | -170.94pp | DETECTED |
| 1.0 | 50% | 46.89% | 37.59% | -9.30pp | DETECTED |
| 2.0 | 20% | 25.20% | 18.55% | -6.65pp | DETECTED |
| 4.0 | 6% | 13.08% | 8.79% | -4.29pp | DETECTED |
| 8.0 | 2% | 6.62% | 4.17% | -2.45pp | DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the ladder ran out before the ruler did: at the noisiest level sampled (oracle 2% of the score's variance) the by-construction gap is still only 2.45pp and the sign is still read correctly. So this ruler demonstrably sees a 2.45pp width effect; its true floor is somewhere BELOW that and is not measured here -- extend the ladder before quoting a floor.

**Against the published book:** the real book's 1.33pp gap is SMALLER than the 2.45pp gap this ruler was shown to read in the control, so a real-book verdict that the widths are not separable cannot be told apart from the ruler's own blindness at that size -- it is not evidence of 'no width effect'
