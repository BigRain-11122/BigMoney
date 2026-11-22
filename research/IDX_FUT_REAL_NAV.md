# Index futures: what the discount pays a book that actually rolls

Every carry number on the basis pages is a daily difference between the continuous series and its index with the splice days deleted -- a model of rolling, not a roll. This page books the roll: hold the contract with the most open interest, move to its successor when another one takes that over by 5.0%, and mark both legs at the same close, so the seam costs nothing by construction rather than by being masked out.

Evidence cutoff: `2026-11-20`  ·  generated 2026-11-22T18:38:45

## The roll book against the published mask

| product | years | rolls/yr | futures %/yr | index %/yr | discount (gross) | discount net @ 1.5bp | published (observed mask) |
|---|---|---|---|---|---|---|---|
| IF | 8.04 | 9.21 | 5.78 | 2.39 | **3.469** | **3.331** | 3.481 |
| IC | 8.04 | 7.84 | 13.02 | 4.15 | **8.697** | **8.579** | 7.181 |
| IH | 8.04 | 11.07 | 3.3 | 1.16 | **2.28** | **2.114** | 2.22 |
| IM | 4.3 | 5.35 | 4.33 | -4.98 | **10.01** | **9.93** | 8.623 |

A negative futures column with a positive discount is the normal shape: the contract converges into the index without the index paying a dividend.

## What a roll may cost

Cost is a ladder, not a claim: the floor is the exchange fee (0.46bp) plus one tick each leg, and the table says where the line stops.

| product | breakeven bp/roll | 0.0bp | 1.5bp | 4.0bp | 8.0bp | 15.0bp |
|---|---|---|---|---|---|---|
| IF | 5.09 | 3.469 | 3.331 | 3.101 | 2.732 ✗ | 2.088 ✗ |
| IC | 72.67 | 8.697 | 8.579 | 8.383 | 8.069 | 7.521 |
| IH | 0.0 | 2.28 ✗ | 2.114 ✗ | 1.837 ✗ | 1.394 ✗ | 0.619 ✗ |
| IM | 131.03 | 10.01 | 9.93 | 9.796 | 9.582 | 9.208 |

**No line breaks inside the floor cost band**: the weakest allows 5.09 bp per roll, i.e. roughly 3.4x the commission-plus-tick floor of 1.5 bp. The cost assumption was never what decided these lines -- the mask was.

## Admission

| line | value |
|---|---|
| at/above 3.0% gross of cost | IC, IF, IM |
| still above 3.0% net at 1.5bp/roll | IC, IF, IM |
| below the line before any cost | IH |

## Per year

The discount is not a constant, and an average over the whole span hides the years it was absent.

| year | IF | IC | IH | IM |
|---|---|---|---|---|
| 2018 | -3.129 (49d) | -0.667 (49d) | -3.624 (49d) | — |
| 2019 | 2.907 (244d) | 11.111 (244d) | 1.634 (244d) | — |
| 2020 | 6.738 (243d) | 12.298 (243d) | 7.543 (243d) | — |
| 2021 | 5.648 (243d) | 12.372 (243d) | 3.141 (243d) | — |
| 2022 | 2.507 (242d) | 6.714 (242d) | 2.01 (242d) | 10.465 (109d) |
| 2023 | 0.201 (242d) | 2.626 (242d) | -0.055 (242d) | 4.402 (242d) |
| 2024 | 2.478 (242d) | 5.644 (242d) | 1.366 (242d) | 10.164 (242d) |
| 2025 | 4.004 (243d) | 10.758 (243d) | 1.92 (243d) | 13.59 (243d) |
| 2026 | 5.083 (213d) | 8.35 (213d) | 2.462 (213d) | 10.718 (213d) |

## What this does not measure

The book marks at closes, so it pays no spread and no slippage -- that is what the cost ladder is for. It also assumes the position can always be moved on the day open interest flips; in practice a roll is done over a day or two, which costs a little basis but no exposure. And the roll itself is a quote-source fact, not a broker statement: the contract codes come from the same daily endpoint as the continuous series.

Products where the cache covers too few years are reported, not silently dropped: see `status` in the JSON.