# Index futures: the roll, observed from open interest

The carry numbers on the basis pages are priced with a roll mask.  Both masks in use are guesses -- one from the size of a basis step, one from where the most negative step falls near expiry.  This page replaces the guess with the observation: which contract the market was actually holding, read from open interest, and what the two legs were worth on the day they were both quoted.

Evidence cutoff: `2026-11-20`  ·  generated 2026-11-22T13:58:19

## Does each mask land on the real rolls?

| mask | recall of observed rolls | precision |
|---|---|---|
| published_size | 16.2% | 43.1% |
| calendar | 49.6% | 35.0% |

Recall = share of real rolls the mask actually hides.  Precision = share of the days it hides that were real rolls (the rest are market days it ate).

## Per product

Carry is the same measurement under three masks, on the same days (the window below), in pct/yr. Admission line = 3.0 pct.

| product | window | days named | rolls in window | carry: size | calendar | observed | admit: size / cal / obs | jump ratio |
|---|---|---|---|---|---|---|---|---|
| IC | 2020-01-02 → 2026-11-20 | 100.0% | 74 | 3.31 | 9.29 | 7.18 | True / True / True | 3.3 |
| IF | 2020-01-02 → 2026-11-20 | 100.0% | 70 | 2.10 | 5.50 | 3.48 | False / True / True | 2.9 |
| IH | 2020-01-02 → 2026-11-20 | 100.0% | 74 | 2.03 | 5.49 | 2.22 | False / True / False | 1.9 |
| IM | 2022-07-22 → 2026-11-20 | 100.0% | 36 | 5.71 | 11.96 | 8.62 | True / True / True | 4.0 |

「days named」 is the share of trading days in the window whose contract could be identified by matching the continuous close to a contract close to the tick. 「jump ratio」 is the median absolute basis step on the days we call rolls over the same statistic on all other days -- the price's corroboration of the naming (a ratio near 1 would mean the naming and the series disagree about where the seam is).

## How many observations behind each number

- **IC**: 2017-01-17 to 2026-11-20, 2388 bars; 84 splices over the whole span (77.2% of days named); 83 with a measured gap, median -33.6 pts; OI agrees on 61.4% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.0%), 2019 (71.7%)
- **IF**: 2017-01-17 to 2026-11-20, 2388 bars; 81 splices over the whole span (77.3% of days named); 79 with a measured gap, median -11.4 pts; OI agrees on 69.5% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.4%), 2019 (72.5%)
- **IH**: 2017-01-17 to 2026-11-20, 2388 bars; 85 splices over the whole span (77.2% of days named); 84 with a measured gap, median -0.2 pts; OI agrees on 74.7% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.0%), 2019 (72.1%)
- **IM**: 2022-07-22 to 2026-11-20, 1050 bars; 36 splices over the whole span (100.0% of days named); 36 with a measured gap, median -48.4 pts; OI agrees on 69.6% of named days
  - years excluded from the comparison for want of contract data: none

## Adoption

`admitted_by_mask` is derived from the carry figures, never typed.  The observed column is the honest one -- the masked days are exactly the days the published series changed contract, so nothing but a splice is removed.  Both heuristics are wrong in opposite directions: the size rule catches too few days (it needs a big step) and the calendar rule catches days that are not splices (it fires on large market moves near expiry), which is why the calendar column reads high.

A product that admits under the observed mask is a **candidate whose admission the published mask hid**, not an adopted book: the gap is a points reading from a quote provider, not a broker statement, and nothing here sizes a position.

Flips vs the published mask: IF (False -> True)

