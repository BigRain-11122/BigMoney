# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5281 bars x 1521 names, 2005-02-23..2026-11-16, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 441.33% | -73.82% |
| 5 | 372.72% | -71.79% |
| 8 | 316.11% | -69.67% |
| 12 | 266.28% | -67.09% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 441.33% | 266.28% | -175.05pp | DETECTED |
| 1.0 | 50% | 41.26% | 38.06% | -3.20pp | DETECTED |
| 2.0 | 20% | 21.26% | 19.08% | -2.18pp | DETECTED |
| 4.0 | 6% | 11.99% | 9.85% | -2.14pp | DETECTED |
| 8.0 | 2% | 5.41% | 5.32% | -0.09pp | DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the ladder ran out before the ruler did: at the noisiest level sampled (oracle 2% of the score's variance) the by-construction gap is still only 0.09pp and the sign is still read correctly. So this ruler demonstrably sees a 0.09pp width effect; its true floor is somewhere BELOW that and is not measured here -- extend the ladder before quoting a floor.

**Against the published book:** the real book's 1.29pp gap is at or above the 0.09pp this ruler was shown to read in the control, so a verdict about the real pair is a statement about the book rather than about a blind instrument -- the ruler is sensitive enough to have seen a difference of that size
