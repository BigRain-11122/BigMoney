# Index futures: what the discount pays a book that actually rolls

Every carry number on the basis pages is a daily difference between the continuous series and its index with the splice days deleted -- a model of rolling, not a roll. This page books the roll: hold the contract with the most open interest, move to its successor when another one takes that over by 5.0%, and mark both legs at the same close, so the seam costs nothing by construction rather than by being masked out.

Evidence cutoff: `None`  ·  generated 2026-11-17T21:43:19

## The roll book against the published mask

| product | years | rolls/yr | futures %/yr | index %/yr | discount (gross) | discount net @ 1.5bp | published (observed mask) |
|---|---|---|---|---|---|---|---|

A negative futures column with a positive discount is the normal shape: the contract converges into the index without the index paying a dividend.

## What a roll may cost

Cost is a ladder, not a claim: the floor is the exchange fee (0.46bp) plus one tick each leg, and the table says where the line stops.

| product | breakeven bp/roll | 0.0bp | 1.5bp | 4.0bp | 8.0bp | 15.0bp |
|---|---|---|---|---|---|---|

## Admission

| line | value |
|---|---|
| at/above 3.0% gross of cost | none |
| still above 3.0% net at 1.5bp/roll | none |
| below the line before any cost | none |

## Per year

The discount is not a constant, and an average over the whole span hides the years it was absent.

| year |  |
|---|

## What this does not measure

The book marks at closes, so it pays no spread and no slippage -- that is what the cost ladder is for. It also assumes the position can always be moved on the day open interest flips; in practice a roll is done over a day or two, which costs a little basis but no exposure. And the roll itself is a quote-source fact, not a broker statement: the contract codes come from the same daily endpoint as the continuous series.

Products where the cache covers too few years are reported, not silently dropped: see `status` in the JSON.