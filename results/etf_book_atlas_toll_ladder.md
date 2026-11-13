# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 0.61bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects. The only stable statement in the grid is directional, not numerical: wider is worth more at every rung (rank corr +1.00) while the fast cadence inverts at 40bp/side -- and even the width sign is worth at most 1.74pp, inside the band.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.90 | 6.80 | yes | n8/R10 | +5.37 | +0.90 |
| 5 | 6.03 | 6.78 | no | n8/R10 | +4.54 | +1.01 |
| 10 | 5.18 | 6.74 | no | n8/R10 | +3.71 | +1.04 |
| 20 | 3.52 | 6.69 | no | n8/R10 | +2.04 | +1.18 |
| 40 | 3.21 | 6.60 | no | n8/R40 | -1.40 | +1.74 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.90pp at 0bp to 3.21pp at 40bp (rank corr -1.000)
- median cell band stays 6.80 -> 6.60pp across the same rungs (band is not the mover)
- the two series cross at 0.61bp/side
- at the production toll (8bp) interpolated spread 5.52pp vs band 6.76pp
- the FAST cadence is worth +5.37pp at 0bp and -1.40pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.90 -> +1.74pp (rank corr +1.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.18 | 6.74 | no |
| 0.02 | 5.14 | 6.66 | no |
| 0.05 | 5.54 | 6.56 | no |
| 0.10 | 6.11 | 6.61 | no |
| 0.20 | 5.47 | 6.29 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 5.79 | 5.91 | no |

verdict: **SINGLE_RUNG_CROSSING_IS_ONE_DRAW**

- 1 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread drifts up with k (rank corr 0.714) but only 1 rung ever clears the band, so the correlation is carried by rungs that never clear it
- band is flat (5.89 .. 6.74pp), so the label moves on spread alone
- a strength ladder whose only crossing is non-monotone is the r1325 single-arm reading again: the ladder, not the arm, is the ruler

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
