# Index futures: what the discount pays a book that actually rolls

Every carry number on the basis pages is a daily difference between the continuous series and its index with the splice days deleted -- a model of rolling, not a roll. This page books the roll: hold the contract with the most open interest, move to its successor when another one takes that over by 5.0%, and mark both legs at the same close, so the seam costs nothing by construction rather than by being masked out.

Evidence cutoff: `2026-11-25`  ·  generated 2026-11-25T20:20:44

## The roll book against the published mask

| product | years | rolls/yr | futures %/yr | index %/yr | discount (gross) | discount net @ 1.5bp | published (observed mask) |
|---|---|---|---|---|---|---|---|
| IF | 8.05 | 9.19 | 5.62 | 2.21 | **3.499** | **3.361** | 3.518 |
| IC | 8.05 | 7.83 | 12.68 | 3.89 | **8.642** | **8.525** | 7.122 |
| IH | 8.05 | 11.06 | 3.24 | 1.0 | **2.371** | **2.205** | 2.331 |
| IM | 4.31 | 5.33 | 3.83 | -5.38 | **9.965** | **9.885** | 8.585 |

A negative futures column with a positive discount is the normal shape: the contract converges into the index without the index paying a dividend.

## What a roll may cost

Cost is a ladder, not a claim: the floor is the exchange fee (0.46bp) plus one tick each leg, and the table says where the line stops.

| product | breakeven bp/roll | 0.0bp | 1.5bp | 4.0bp | 8.0bp | 15.0bp |
|---|---|---|---|---|---|---|
| IF | 5.43 | 3.499 | 3.361 | 3.131 | 2.764 ✗ | 2.12 ✗ |
| IC | 72.09 | 8.642 | 8.525 | 8.329 | 8.016 | 7.468 |
| IH | 0.0 | 2.371 ✗ | 2.205 ✗ | 1.928 ✗ | 1.486 ✗ | 0.712 ✗ |
| IM | 130.56 | 9.965 | 9.885 | 9.751 | 9.538 | 9.165 |

**No line breaks inside the floor cost band**: the weakest allows 5.43 bp per roll, i.e. roughly 3.6x the commission-plus-tick floor of 1.5 bp. The cost assumption was never what decided these lines -- the mask was.

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
| 2026 | 5.335 (216d) | 7.901 (216d) | 3.28 (216d) | 10.509 (216d) |

## What this does not measure

The book marks at closes, so it pays no spread and no slippage -- that is what the cost ladder is for. It also assumes the position can always be moved on the day open interest flips; in practice a roll is done over a day or two, which costs a little basis but no exposure. And the roll itself is a quote-source fact, not a broker statement: the contract codes come from the same daily endpoint as the continuous series.

Products where the cache covers too few years are reported, not silently dropped: see `status` in the JSON.