# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 0.60bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects. The only stable statement in the grid is directional, not numerical: wider is worth more at every rung (rank corr +1.00) while the fast cadence inverts at 40bp/side -- and even the width sign is worth at most 1.17pp, inside the band.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.93 | 6.84 | yes | n8/R10 | +5.47 | +0.73 |
| 5 | 6.11 | 6.79 | no | n8/R10 | +4.62 | +0.84 |
| 10 | 5.29 | 6.75 | no | n8/R10 | +3.79 | +0.95 |
| 20 | 3.69 | 6.70 | no | n8/R10 | +2.07 | +1.16 |
| 40 | 2.11 | 7.08 | no | n5/R20 | -0.66 | +1.17 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.93pp at 0bp to 2.11pp at 40bp (rank corr -1.000)
- median cell band stays 6.84 -> 7.08pp across the same rungs (band is not the mover)
- the two series cross at 0.61bp/side
- at the production toll (8bp) interpolated spread 5.61pp vs band 6.77pp
- the FAST cadence is worth +5.47pp at 0bp and -0.66pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.73 -> +1.17pp (rank corr +1.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.29 | 6.75 | no |
| 0.02 | 5.14 | 6.80 | no |
| 0.05 | 7.37 | 7.23 | yes |
| 0.10 | 6.22 | 6.44 | no |
| 0.20 | 5.45 | 6.32 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 6.01 | 6.19 | no |

verdict: **CROSSINGS_WITHOUT_DOSE**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 5.29 / 5.14 / 7.37 / 6.22 / 5.45 / 6.25 / 6.01 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.429)
- band is flat (5.89 .. 7.23pp), so the label moves on spread alone
- 2 rungs clear the band and the spread still is not ordered by k (rank corr 0.429 < 0.70): scattered crossings are the same draw as one, but they are not a single rung and must not be named as one

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
