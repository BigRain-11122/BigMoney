# Index futures: the roll, observed from open interest

The carry numbers on the basis pages are priced with a roll mask.  Both masks in use are guesses -- one from the size of a basis step, one from where the most negative step falls near expiry.  This page replaces the guess with the observation: which contract the market was actually holding, read from open interest, and what the two legs were worth on the day they were both quoted.

Evidence cutoff: `2026-11-17`  ·  generated 2026-11-17T21:43:18

## Does each mask land on the real rolls?

| mask | recall of observed rolls | precision |
|---|---|---|
| published_size | 100.0% | 4.2% |
| calendar | 75.0% | 0.9% |

Recall = share of real rolls the mask actually hides.  Precision = share of the days it hides that were real rolls (the rest are market days it ate).

## Per product

Carry is the same measurement under three masks, on the same days (the window below), in pct/yr. Admission line = 3.0 pct.

| product | window | days named | rolls in window | carry: size | calendar | observed | admit: size / cal / obs | jump ratio |
|---|---|---|---|---|---|---|---|---|
| IC | 2017-01-17 → 2026-11-17 | 4.4% | 1 | 2.88 | 9.80 | 0.47 | False / True / False | 15.4 |
| IF | 2017-01-17 → 2026-11-17 | 4.4% | 1 | 1.88 | 5.84 | 0.36 | False / True / False | 15.9 |
| IH | 2017-01-17 → 2026-11-17 | 4.3% | 1 | 1.56 | 5.39 | 0.34 | False / True / False | 18.7 |
| IM | 2022-07-22 → 2026-11-17 | 9.9% | 1 | 5.88 | 12.01 | 1.05 | True / True / False | 16.9 |

「days named」 is the share of trading days in the window whose contract could be identified by matching the continuous close to a contract close to the tick. 「jump ratio」 is the median absolute basis step on the days we call rolls over the same statistic on all other days -- the price's corroboration of the naming (a ratio near 1 would mean the naming and the series disagree about where the seam is).

## How many observations behind each number

- **IC**: 2017-01-17 to 2026-11-17, 2385 bars; 1 splices over the whole span (4.4% of days named); 1 with a measured gap, median -226.0 pts; OI agrees on 99.0% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.0%), 2019 (0.0%), 2020 (0.0%), 2021 (0.0%), 2022 (0.0%), 2023 (0.0%), 2024 (0.0%), 2025 (0.0%), 2026 (49.5%)
- **IF**: 2017-01-17 to 2026-11-17, 2385 bars; 1 splices over the whole span (4.4% of days named); 1 with a measured gap, median -90.2 pts; OI agrees on 99.1% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.0%), 2019 (0.0%), 2020 (0.0%), 2021 (0.0%), 2022 (0.0%), 2023 (0.0%), 2024 (0.0%), 2025 (0.0%), 2026 (50.5%)
- **IH**: 2017-01-17 to 2026-11-17, 2385 bars; 1 splices over the whole span (4.3% of days named); 1 with a measured gap, median -63.2 pts; OI agrees on 99.0% of named days
  - years excluded from the comparison for want of contract data: 2017 (0.0%), 2018 (0.0%), 2019 (0.0%), 2020 (0.0%), 2021 (0.0%), 2022 (0.0%), 2023 (0.0%), 2024 (0.0%), 2025 (0.0%), 2026 (49.0%)
- **IM**: 2022-07-22 to 2026-11-17, 1047 bars; 1 splices over the whole span (9.9% of days named); 1 with a measured gap, median -240.4 pts; OI agrees on 99.0% of named days
  - years excluded from the comparison for want of contract data: 2022 (0.0%), 2023 (0.0%), 2024 (0.0%), 2025 (0.0%), 2026 (49.5%)

## Adoption

`admitted_by_mask` is derived from the carry figures, never typed.  The observed column is the honest one -- the masked days are exactly the days the published series changed contract, so nothing but a splice is removed.  Both heuristics are wrong in opposite directions: the size rule catches too few days (it needs a big step) and the calendar rule catches days that are not splices (it fires on large market moves near expiry), which is why the calendar column reads high.

A product that admits under the observed mask is a **candidate whose admission the published mask hid**, not an adopted book: the gap is a points reading from a quote provider, not a broker statement, and nothing here sizes a position.

Flips vs the published mask: IM (True -> False)

