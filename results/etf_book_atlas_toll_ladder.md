# ETF book atlas -- the toll ladder

**NOT QUOTABLE at the production toll: the ordering dies at 3.87bp/side.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 8.24 | 6.01 | yes | n3/R10 | +6.33 | -0.67 |
| 5 | 6.08 | 6.74 | no | n8/R10 | +4.56 | +0.99 |
| 10 | 5.25 | 6.71 | no | n8/R10 | +3.73 | +1.05 |
| 20 | 3.63 | 6.66 | no | n8/R10 | +2.06 | +1.25 |
| 40 | 3.31 | 6.58 | no | n8/R40 | -1.39 | +1.68 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 8.24pp at 0bp to 3.31pp at 40bp (rank corr -1.000)
- median cell band stays 6.01 -> 6.58pp across the same rungs (band is not the mover)
- the two series cross at 3.87bp/side
- at the production toll (8bp) interpolated spread 5.58pp vs band 6.72pp
- the FAST cadence is worth +6.33pp at 0bp and -1.39pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: -0.67 -> +1.68pp (rank corr +1.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.25 | 6.71 | no |
| 0.02 | 5.18 | 6.68 | no |
| 0.05 | 5.64 | 6.63 | no |
| 0.10 | 6.18 | 6.51 | no |
| 0.20 | 5.49 | 6.24 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 6.39 | 6.10 | yes |

verdict: **BUFFER_WIDENS_THE_ORDERING**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 5.25 / 5.18 / 5.64 / 6.18 / 5.49 / 6.25 / 6.39 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.857)
- band is flat (5.89 .. 6.71pp), so the label moves on spread alone

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
