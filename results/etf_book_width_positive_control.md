# ETF book: can the width ruler see an effect that must be there?

Control = rank by each name's own next-20-bar return (perfect foresight, not tradeable).
Panel 5280 bars x 1520 names, 2005-02-23..2026-11-13, cadence 20, toll 10bp.

| width | oracle CAGR | anti-oracle CAGR |
|---|---|---|
| 3 | 443.78% | -73.56% |
| 5 | 374.86% | -71.50% |
| 8 | 317.73% | -69.37% |
| 12 | 267.34% | -66.78% |

| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |
|---|---|---|---|---|
| 0.0 | 100% | 443.78% | 267.34% | -176.44pp | DETECTED |
| 1.0 | 50% | 59.13% | 39.17% | -19.96pp | DETECTED |
| 2.0 | 20% | 27.73% | 18.98% | -8.75pp | DETECTED |
| 4.0 | 6% | 9.32% | 7.75% | -1.57pp | DETECTED |
| 8.0 | 2% | 4.98% | 3.72% | -1.26pp | DETECTED |

**RULER_SEES_BOTH_DIRECTIONS** — oracle recovers DETECTED (rank corr -1.0), anti-oracle recovers DETECTED (rank corr 1.0).

**Resolution:** the ladder ran out before the ruler did: at the noisiest level sampled (oracle 2% of the score's variance) the by-construction gap is still only 1.26pp and the sign is still read correctly. So this ruler demonstrably sees a 1.26pp width effect; its true floor is somewhere BELOW that and is not measured here -- extend the ladder before quoting a floor.

**Against the published book:** the real book's 1.34pp gap is at or above the 1.26pp this ruler was shown to read in the control, so a verdict about the real pair is a statement about the book rather than about a blind instrument -- the ruler is sensitive enough to have seen a difference of that size
