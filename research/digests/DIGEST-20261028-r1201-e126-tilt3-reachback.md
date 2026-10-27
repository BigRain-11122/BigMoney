# E126 the tilt reads pre-2017 for the first time, and the narrow skin's price is published, not hidden (r1201 bm-b)

Face: `results/e43_tilt_4member/TILT3REACH-20261027.json` (new `tilt3reach` mode in
`scripts/e39_panel_census.py`: `TILT3_SMALL`, `_skin_months`, `run_tilt3`, `_tilt3_arm_cells`,
`_tilt3_arm_dates`; selftest 488 -> 504).

## What the family could not say before

E43's four-member skin reaches 2017-01, and its docstring claimed a 2013 reach-back. The binding
member there is `sh512100` (first bar 2016-11-04), so pre2017 carried **1 usable month** on both
the four- and five-member skins -- a reading that looked like an era and was a single observation
(429.4bp/yr on the four-member skin, published as a row).

Dropping to three members (the same 2 broad-cap leg vs `sh510500` alone, first bar 2013-03-15)
makes 2013-04..2016-12 measurable: **44 months**.

## The reading

| era | months (3m) | tilt bp/yr (3-member) | size-neutral bp/yr | 5-member tilt on the same months |
|---|---|---|---|---|
| pre2017 | 44 | **+1186.4** | +134.4 | not measurable (0 months) |
| 2017_2020 | 48 | **-923.9** | +289.0 | 1 month -- refused |
| 2021_2023 | 36 | +609.9 | +350.6 | +609.2 |
| 2024_now | 34 | +252.8 | +58.8 | +617.1 |
| full | 162 | +237.1 | +236.1 | 71 months -- refused |

Two things the wider skins could never say:

1. **The size tilt's sign is era-dependent, and the pre-2017 era is the extreme of it.** +1186bp/yr
   (small over large) 2013-2016, then **-924bp/yr** in 2017-2020, then back positive. Removing the
   size tilt leaves a much flatter 134...351bp band, i.e. most of the pre-2017 reading is the size
   leg, not book skill -- which is exactly what the raw number alone would have overstated.
2. **The composition price is large, and it is not constant.** On the months two skins share,
   4-member minus 3-member is -69.4bp (2017_2020), +343.7bp (2021_2023), -120.7bp (2024_now);
   5-member minus 3-member is -0.7bp (2021_2023) and +364.3bp (2024_now). Any single "the tilt is
   X bp" statement is therefore a statement about a skin, not about the market.

## Denominators are part of the answer

`skin_comparison` publishes `months_3member`, `months_4member_shared`, `months_5member_shared`
beside each number and prints a delta **only when both sides price the same months**; otherwise
the delta is `null` with the two denominators in a `*_reason` string. The pre2017 and full rows
are refused for exactly that reason (1 vs 44, 0 vs 44, 119 vs 162, 71 vs 162 months). A delta
computed across different month sets would be an artefact dressed as a skin price -- the
E127/NEIGHBORHOODSCREEN failure mode (90 of 163 beside a 9-cell control printing "30x").

## Honest limits

- The three-member skin is the narrowest reading in this family: its small leg is one name. It is
  published BESIDE the four- and five-member rows, never as the identity.
- Composition weights are stated (`spec.small_leg_member_weight_pct`): 510500 carries 100% / 50% /
  33.3% of the small leg in the 3/4/5-member skins.
- Ladder and wide curves are the E24/E27 engine's own (module import); only the tilt regressor
  changes, so movement in the neutral column is size adjustment, not a different book.
- Eras remain calendar partitions of one continuous monthly series and do not add up.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.