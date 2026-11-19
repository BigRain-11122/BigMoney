# ETF book atlas -- the toll ladder

**NOT QUOTABLE: the 12-cell ordering clears its own phase noise only below 0.85bp/side, and the buffer knob never clears it on a dose -- both knobs are zero-cost objects. The only stable statement in the grid is directional, not numerical: wider is worth more at every rung (rank corr +1.00) while the fast cadence inverts at 40bp/side -- and even the width sign is worth at most 1.58pp, inside the band.**

## Toll ladder (buffer k=0)

| toll bp | spread pp | band pp | clears | argmax | cadence eff | width eff |
|---|---|---|---|---|---|---|
| 0 | 6.96 | 6.82 | yes | n8/R10 | +5.49 | +0.71 |
| 5 | 6.11 | 6.78 | no | n8/R10 | +4.65 | +0.83 |
| 10 | 5.29 | 6.75 | no | n8/R10 | +3.79 | +0.95 |
| 20 | 3.69 | 6.68 | no | n8/R10 | +2.10 | +1.17 |
| 40 | 3.30 | 6.58 | no | n8/R20 | -1.32 | +1.58 |

verdict: **ORDERING_IS_A_TOLL_ARTEFACT**

- spread falls from 6.96pp at 0bp to 3.30pp at 40bp (rank corr -1.000)
- median cell band stays 6.82 -> 6.58pp across the same rungs (band is not the mover)
- the two series cross at 0.85bp/side
- at the production toll (8bp) interpolated spread 5.61pp vs band 6.76pp
- the FAST cadence is worth +5.49pp at 0bp and -1.32pp at 40bp -- the ranking of the cadence knob inverts at 40bp/side
- the width knob moves the other way: +0.71 -> +1.58pp (rank corr +1.000), i.e. wider is worth more as the toll rises
- the ordering is monotone in the toll and gone by the production toll: no width/cadence sentence from this grid is quotable at 8bp/side

## Buffer ladder (production toll 10bp/side)

| buffer k | spread pp | band pp | clears |
|---|---|---|---|
| 0.00 | 5.29 | 6.75 | no |
| 0.02 | 5.14 | 6.80 | no |
| 0.05 | 7.37 | 7.23 | yes |
| 0.10 | 6.20 | 6.42 | no |
| 0.20 | 5.39 | 6.27 | no |
| 0.30 | 6.25 | 5.89 | yes |
| 0.40 | 5.93 | 6.11 | no |

verdict: **CROSSINGS_WITHOUT_DOSE**

- 2 of 7 buffer strengths clear the band (one draw in 7 if the label were coin-flip)
- spread has no dose: 5.29 / 5.14 / 7.37 / 6.20 / 5.39 / 6.25 / 5.93 across k=0.00 / 0.02 / 0.05 / 0.10 / 0.20 / 0.30 / 0.40 (rank corr 0.429)
- band is flat (5.89 .. 7.23pp), so the label moves on spread alone
- 2 rungs clear the band and the spread still is not ordered by k (rank corr 0.429 < 0.70): scattered crossings are the same draw as one, but they are not a single rung and must not be named as one

## Excluded (moves two knobs at once)
- etf_book_phase_atlas_buffer_k05_cost05.json -- moves two knobs at once (cost=0.00050 k=0.050): not a rung of a one-dimensional ladder
- etf_book_phase_atlas_buffer_k05_cost20.json -- moves two knobs at once (cost=0.00200 k=0.050): not a rung of a one-dimensional ladder
