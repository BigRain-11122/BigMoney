# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 0.87bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.96 | 6.82 | yes | n8/R10 | +5.49 | +0.71 |
| 5 | 6.08 | 6.74 | no | n8/R10 | +4.56 | +0.99 |
| 10 | 5.41 | 7.12 | no | n8/R10 | +3.57 | +1.23 |
| 20 | 3.63 | 6.66 | no | n8/R10 | +2.06 | +1.25 |
| 40 | 2.88 | 6.83 | no | n3/R10 | -1.14 | -0.79 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.96pp at 0bp to 2.88pp at 40bp (rank corr -1.000)
- median cell band stays 6.82 -> 6.83pp across the same rungs (band is not the mover)
- the two series cross at 0.87bp/side
- at the production toll (8bp) interpolated spread 5.67pp vs band 6.97pp
- the FAST cadence is worth +5.49pp at 0bp and -1.14pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.71 -> -0.79pp (rank corr +0.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.41 | 7.12 | no |
| 0.02 | 5.19 | 6.72 | no |
| 0.05 | 5.65 | 6.54 | no |
| 0.10 | 6.46 | 6.10 | yes |
| 0.20 | 5.38 | 6.25 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 5.95 | 5.99 | no |

verdict: **CROSSINGS_WITHOUT_DOSE**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 5.41 / 5.19 / 5.65 / 6.46 / 5.38 / 6.25 / 5.95 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.500)
- band is flat (5.89 .. 7.12pp), so the label moves on spread alone
- 2 rungs clear the band and the spread still is not ordered by k (rank corr 0.500 < 0.70): scattered crossings are the same draw as one, but they are not a single rung and must not be named as one

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
