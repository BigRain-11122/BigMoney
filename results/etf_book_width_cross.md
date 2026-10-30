# E276 -- does the width sign survive off its own grid? (r1362 bm-c)

Panel: E198 declared 17-ETF cross + its 510300 benchmark (18 usable names)
Cutoff: 2026-10-29

## Verdict: `WIDTH_SIGN_IS_FAMILY_NAMING`

Family reading (quoted): wider books earned [0.685, 0.73, 0.77, 1.14, 1.56]pp more per rung at rank corr 1.0 inside a 1653-name pool. On the 18-name cross: the sign does not travel -- it flips on this panel (cagr rank corr -1.0 at 0.0bp, -1.0 at 8.0bp), so the width direction is that family's naming, not a portable mechanism. Random-score control (N=160 runs): real-minus-null [11.51, 7.28, 5.92, 3.3]pp across widths (rank corr -1.0), so the width sign belongs to the score, not to noise. The quoted family direction (1.0) is the same direction the noise arm takes on this panel (1.0), so the family width sign is not yet evidence about the signal: it needs its own null.

| cost | width | CAGR med | CAGR range | vol | Sharpe | MaxDD | turnover | phases |
|---|---|---|---|---|---|---|---|---|
| 0.0bp | 3 | 13.69% | 11.26..15.98% | 13.8% | 1.128 | -21.2% | 0.89 | 5 |
| 0.0bp | 5 | 9.87% | 8.00..13.72% | 15.6% | 0.766 | -28.9% | 0.79 | 5 |
| 0.0bp | 8 | 9.38% | 8.25..11.28% | 17.0% | 0.635 | -29.6% | 0.56 | 5 |
| 0.0bp | 12 | 6.67% | 5.30..8.31% | 18.5% | 0.459 | -35.4% | 0.33 | 5 |
| 8.0bp | 3 | 12.76% | 10.29..15.02% | 13.8% | 1.060 | -21.5% | 0.89 | 5 |
| 8.0bp | 5 | 9.04% | 7.15..12.88% | 15.5% | 0.710 | -29.1% | 0.79 | 5 |
| 8.0bp | 8 | 8.77% | 7.69..10.69% | 17.0% | 0.600 | -30.6% | 0.56 | 5 |
| 8.0bp | 12 | 6.34% | 4.94..7.98% | 18.5% | 0.441 | -36.0% | 0.33 | 5 |

## Paired phase reads (widest vs narrowest, same phase)

| cost | arm state | rank corr(width, CAGR) | CAGR share up | Sharpe share up | vol share up |
|---|---|---|---|---|---|
| 0.0bp | flips | -1.0 | 0.0 (5 paired) | 0.0 | 1.0 |
| 8.0bp | flips | -1.0 | 0.0 (5 paired) | 0.0 | 1.0 |

## Random-score baseline (seeded, same panel/engine/widths)

cost 8.0bp, 20 seeds x 2 phases = 160 trials

| width | real CAGR | null CAGR | real - null |
|---|---|---|---|
| 3 | 12.76 | 1.25 | 11.51 |
| 5 | 9.04 | 1.76 | 7.28 |
| 8 | 8.77 | 2.85 | 5.92 |
| 12 | 6.34 | 3.04 | 3.3 |

rank corr with width: real -1.0 / null 1.0 / delta -1.0 -> the width sign is not reproduced by noise, so it belongs to the score

family direction 1.0 vs noise direction 1.0 -> the family's width direction is the direction noise produces -- it cannot be credited to the family signal until the null runs on the family panel

## Coverage

* names loaded: 18 (missing declared: 510180, 510880)
* eligible names per decision: min 13 / median 18 / max 18
* decision days: 1652

## Honest limits

* The score is re-ranked inside 18 names, so this is a different instrument, not the same book on new data: a null here says the sign does not travel, not that the family reading was wrong.
* CAGR is confounded with volatility -- fewer names means a more volatile book. Vol and Sharpe are published per rung for that reason; the paired Sharpe/vol shares are printed beside the CAGR share and can disagree with it.
* 80 monthly bars per name is thin for a CAGR claim; the phase draws are the same data shifted, not new data, so the phase range is a stability read and not a p-value.
* 510880 and 510180 have no local file and were declared missing, not replaced.
* Zero-cost arm is a diagnostic rung (the arm the family sign was read at), not a tradeable configuration.
* The null runs on THIS panel only. It can show that the family's direction is the direction noise produces, but only a null on the family panel can price the family's own width effect (that is the next round, not a claim made here).
