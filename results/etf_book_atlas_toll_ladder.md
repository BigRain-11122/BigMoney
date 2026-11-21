# ETF book atlas -- the toll ladder

**The toll ladder survives; the buffer ladder is still one draw from a grid.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.89 | 6.91 | no | n8/R10 | +5.54 | +0.65 |
| 5 | 6.05 | 6.85 | no | n8/R10 | +4.66 | +0.76 |
| 10 | 5.24 | 6.80 | no | n8/R10 | +3.83 | +0.86 |
| 20 | 6.08 | 7.23 | no | n3/R10 | +2.33 | -1.09 |
| 40 | 3.29 | 6.59 | no | n8/R20 | -1.35 | +1.49 |

verdict: **ORDERING_DECAYS_WITHOUT_A_CLEAN_DOSE**

- spread falls from 6.89pp at 0bp to 3.29pp at 40bp (rank corr -0.700)
- median cell band stays 6.91 -> 6.59pp across the same rungs (band is not the mover)
- at the production toll (8bp) interpolated spread 5.56pp vs band 6.82pp
- the FAST cadence is worth +5.54pp at 0bp and -1.35pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.65 -> +1.49pp (rank corr +0.400), i.e. wider is worth more as the toll rises
- the ordering does not survive the production toll, but the decay is not monotone -- a single crossing cannot name a mechanism

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.24 | 6.80 | no |
| 0.02 | 5.12 | 6.87 | no |
| 0.05 | 5.54 | 6.48 | no |
| 0.10 | 6.17 | 6.41 | no |
| 0.20 | 5.44 | 6.38 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 6.01 | 6.32 | no |

verdict: **SINGLE_RUNG_CROSSING_IS_ONE_DRAW**

- 1 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread drifts up with k (rank corr 0.714) but only 1 rung ever clears the band, so the correlation is carried by rungs that never clear it
- band is flat (5.89 .. 6.87pp), so the label moves on spread alone
- a strength ladder whose only crossing is non-monotone is the r1325 single-arm reading again: the ladder, not the arm, is the ruler

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
