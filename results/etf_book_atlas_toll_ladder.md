# ETF book atlas -- the toll ladder

**The toll ladder survives; the buffer ladder is still one draw from a grid.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.89 | 6.91 | no | n8/R10 | +5.54 | +0.65 |
| 5 | 6.05 | 6.85 | no | n8/R10 | +4.66 | +0.76 |
| 10 | 6.75 | 6.63 | yes | n3/R10 | +3.76 | -1.79 |
| 20 | 6.08 | 7.23 | no | n3/R10 | +2.33 | -1.09 |
| 40 | 3.29 | 6.59 | no | n8/R20 | -1.35 | +1.49 |

verdict: **ORDERING_DECAYS_WITHOUT_A_CLEAN_DOSE**

- spread falls from 6.89pp at 0bp to 3.29pp at 40bp (rank corr -0.700)
- median cell band stays 6.91 -> 6.59pp across the same rungs (band is not the mover)
- the two series cross at 9.35bp/side
- at the production toll (8bp) interpolated spread 6.47pp vs band 6.72pp
- the FAST cadence is worth +5.54pp at 0bp and -1.35pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.65 -> +1.49pp (rank corr +0.200), i.e. wider is worth more as the toll rises
- the ordering does not survive the production toll, but the decay is not monotone -- a single crossing cannot name a mechanism

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 6.75 | 6.63 | yes |
| 0.02 | 5.04 | 6.66 | no |
| 0.05 | 5.47 | 6.36 | no |
| 0.10 | 6.17 | 6.41 | no |
| 0.20 | 5.44 | 6.38 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 6.01 | 6.32 | no |

verdict: **CROSSINGS_WITHOUT_DOSE**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 6.75 / 5.04 / 5.47 / 6.17 / 5.44 / 6.25 / 6.01 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.000)
- band is flat (5.89 .. 6.66pp), so the label moves on spread alone
- 2 rungs clear the band and the spread still is not ordered by k (rank corr 0.000 < 0.70): scattered crossings are the same draw as one, but they are not a single rung and must not be named as one

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
