# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 0.66bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.84 | 6.74 | yes | n8/R10 | +5.44 | +0.55 |
| 5 | 6.00 | 6.69 | no | n8/R10 | +4.62 | +0.80 |
| 10 | 5.21 | 6.68 | no | n8/R10 | +3.77 | +0.89 |
| 20 | 3.58 | 6.55 | no | n8/R10 | +2.00 | +1.10 |
| 40 | 3.49 | 6.33 | no | n5/R20 | -1.59 | +0.52 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.84pp at 0bp to 3.49pp at 40bp (rank corr -1.000)
- median cell band stays 6.74 -> 6.33pp across the same rungs (band is not the mover)
- the two series cross at 0.66bp/side
- at the production toll (8bp) interpolated spread 5.53pp vs band 6.68pp
- the FAST cadence is worth +5.44pp at 0bp and -1.59pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.55 -> +0.52pp (rank corr +0.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.21 | 6.68 | no |
| 0.02 | 5.07 | 6.70 | no |
| 0.05 | 7.15 | 6.62 | yes |
| 0.10 | 6.24 | 6.28 | no |
| 0.20 | 5.42 | 6.12 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 6.12 | 6.17 | no |

verdict: **CROSSINGS_WITHOUT_DOSE**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 5.21 / 5.07 / 7.15 / 6.24 / 5.42 / 6.25 / 6.12 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.429)
- band is flat (5.89 .. 6.70pp), so the label moves on spread alone
- 2 rungs clear the band and the spread still is not ordered by k (rank corr 0.429 < 0.70): scattered crossings are the same draw as one, but they are not a single rung and must not be named as one

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
