# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 1.04bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects. The only stable statement in the grid is directional, not numerical: wider is worth more at every rung (rank corr +1.00) while the fast cadence inverts at 40bp/side -- and even the width sign is worth at most 1.56pp, inside the band.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.92 | 6.75 | yes | n8/R10 | +5.54 | +0.69 |
| 5 | 6.06 | 6.71 | no | n8/R10 | +4.71 | +0.73 |
| 10 | 5.22 | 6.68 | no | n8/R10 | +3.89 | +0.77 |
| 20 | 3.55 | 6.60 | no | n8/R10 | +2.10 | +1.14 |
| 40 | 3.00 | 6.47 | no | n8/R40 | -1.32 | +1.56 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.92pp at 0bp to 3.00pp at 40bp (rank corr -1.000)
- median cell band stays 6.75 -> 6.47pp across the same rungs (band is not the mover)
- the two series cross at 1.04bp/side
- at the production toll (8bp) interpolated spread 5.56pp vs band 6.70pp
- the FAST cadence is worth +5.54pp at 0bp and -1.32pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.69 -> +1.56pp (rank corr +1.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.22 | 6.68 | no |
| 0.02 | 5.21 | 6.62 | no |
| 0.05 | 5.60 | 6.47 | no |
| 0.10 | 6.34 | 6.52 | no |
| 0.20 | 5.67 | 6.16 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 5.89 | 5.92 | no |

verdict: **SINGLE_RUNG_CROSSING_IS_ONE_DRAW**

- 1 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread drifts up with k (rank corr 0.714) but only 1 rung ever clears the band, so the correlation is carried by rungs that never clear it
- band is flat (5.89 .. 6.68pp), so the label moves on spread alone
- a strength ladder whose only crossing is non-monotone is the r1325 single-arm reading again: the ladder, not the arm, is the ruler

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
